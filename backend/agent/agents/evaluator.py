"""Evaluator Agent: Assesses content quality and provides approval/rejection."""

import re
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List

# Handle both module and direct execution contexts
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from models import GenerationSpec, ValidationResult
from llm_client import llm_client
from prompts.system_prompts import EVALUATOR_SYSTEM_PROMPT
from prompts.templates import EVALUATOR_PROMPT_TEMPLATE
from utils.validator import validate_generation_spec

logger = logging.getLogger(__name__)


class EvaluatorAgent:
    """Agent responsible for evaluating blog post quality and providing approval."""

    def __init__(self, llm_client_instance=None):
        self.llm_client = llm_client_instance or llm_client
        self.system_prompt = EVALUATOR_SYSTEM_PROMPT

    async def evaluate_draft(self, draft: Dict[str, Any], spec: GenerationSpec) -> Dict[str, Any]:
        """
        Evaluate the blog post draft against quality standards.

        Args:
            draft: Draft content and metadata
            spec: Generation specifications

        Returns:
            Evaluation result with approval status and feedback
        """
        logger.info(f"Evaluator agent assessing draft: {draft.get('word_count', 0)} words, iteration {draft.get('iteration', 1)}")

        try:
            # Basic validation checks first
            basic_checks = self._perform_basic_validation(draft, spec)

            if not basic_checks['passed']:
                return {
                    "approved": False,
                    "feedback": basic_checks['feedback'],
                    "validation_details": basic_checks
                }

            # Advanced evaluation using LLM
            prompt = EVALUATOR_PROMPT_TEMPLATE.substitute(
                draft_content=draft['content'],
                min_words=spec.min_words,
                max_words=spec.max_words,
                current_words=draft.get('word_count', 0)
            )

            response = await self.llm_client.chat([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ], temperature=0.1)  # Low temperature for consistent evaluation

            # Parse evaluation response
            evaluation = self._parse_evaluation_response(response)

            result = {
                "approved": evaluation['approved'],
                "feedback": evaluation['feedback'],
                "validation_details": basic_checks,
                "llm_evaluation": evaluation
            }

            logger.info(f"Evaluation result: {'APPROVED' if evaluation['approved'] else 'REJECTED'}")

            return result

        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return {
                "approved": False,
                "feedback": f"Evaluation failed: {str(e)}",
                "error": str(e)
            }

    def _perform_basic_validation(self, draft: Dict[str, Any], spec: GenerationSpec) -> Dict[str, Any]:
        """Perform basic structural validation."""
        content = draft.get('content', '')
        word_count = draft.get('word_count', 0)

        checks = {
            "structure": self._check_structure(content),
            "word_count": self._check_word_count(word_count, spec),
            "markdown": self._check_markdown_formatting(content),
            "seo_score": self._calculate_seo_score(content, spec)
            # Removed frontmatter check since frontmatter is added later
        }

        passed = all(check['passed'] if isinstance(check, dict) else check for check in checks.values())
        feedback_parts = []

        if not checks["word_count"]:
            feedback_parts.append(f"Word count ({word_count}) not in range {spec.min_words}-{spec.max_words}")
        if not checks["structure"]:
            feedback_parts.append("Missing proper introduction, body, or conclusion sections")
        if not checks["markdown"]:
            feedback_parts.append("Markdown formatting issues detected")
        
        # Add SEO score feedback
        seo_data = checks["seo_score"]
        if seo_data['score'] < 70:
            feedback_parts.append(f"SEO score ({seo_data['score']}/100) needs improvement: {', '.join(seo_data['issues'])}")

        return {
            "passed": passed,
            "checks": checks,
            "seo_score": seo_data['score'],
            "seo_details": seo_data,
            "feedback": "; ".join(feedback_parts) if feedback_parts else "All basic checks passed"
        }

    def _check_structure(self, content: str) -> bool:
        """Check if content has proper introduction, body, and conclusion."""
        # Look for at least H1 title, some paragraphs, and sections
        has_h1 = bool(re.search(r'^#\s+', content.strip(), re.MULTILINE))
        has_sections = len(re.findall(r'^##\s+', content, re.MULTILINE)) >= 2
        has_content_length = len(content.split()) >= 100

        return has_h1 and has_sections and has_content_length

    def _check_word_count(self, word_count: int, spec: GenerationSpec) -> bool:
        """Check if word count is within acceptable range."""
        return spec.min_words <= word_count <= spec.max_words

    def _check_markdown_formatting(self, content: str) -> bool:
        """Check basic markdown formatting."""
        # Check for proper headers and basic markdown structure
        has_proper_headers = bool(re.search(r'^#+\s+', content, re.MULTILINE))
        # Links are optional in blog posts, so only check for basic formatting
        return has_proper_headers

    def _check_frontmatter(self, content: str) -> bool:
        """Check if frontmatter is properly formatted."""
        lines = content.strip().split('\n')
        return len(lines) >= 3 and lines[0] == '---' and '---' in lines[1:]

    def _parse_evaluation_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM evaluation response."""
        response_upper = response.upper()

        if response_upper.startswith('APPROVED'):
            return {
                "approved": True,
                "feedback": "Content meets quality standards"
            }
        elif response_upper.startswith('REJECTED'):
            # Extract feedback after "REJECTED"
            feedback = response.split('\n', 1)[1] if '\n' in response else "Content needs improvement"
            return {
                "approved": False,
                "feedback": feedback.strip()
            }
        else:
            # Fallback parsing
            return {
                "approved": False,
                "feedback": "Unable to determine approval status from evaluation response"
            }

    def _calculate_seo_score(self, content: str, spec: GenerationSpec) -> Dict[str, Any]:
        """
        Calculate SEO score based on multiple factors.
        
        Returns:
            Dictionary with score (0-100) and detailed breakdown
        """
        score = 0
        max_score = 100
        issues = []
        details = {}
        
        # 1. Title (H1) check (15 points)
        h1_matches = re.findall(r'^#\s+(.+)$', content, re.MULTILINE)
        if h1_matches:
            title = h1_matches[0]
            title_length = len(title)
            if 30 <= title_length <= 60:
                score += 15
                details['title'] = {'status': 'optimal', 'length': title_length}
            elif title_length < 30:
                score += 8
                issues.append("Title too short (< 30 chars)")
                details['title'] = {'status': 'too_short', 'length': title_length}
            else:
                score += 10
                issues.append("Title too long (> 60 chars)")
                details['title'] = {'status': 'too_long', 'length': title_length}
        else:
            issues.append("Missing H1 title")
            details['title'] = {'status': 'missing', 'length': 0}
        
        # 2. Headings structure (20 points)
        h2_count = len(re.findall(r'^##\s+', content, re.MULTILINE))
        h3_count = len(re.findall(r'^###\s+', content, re.MULTILINE))
        
        if h2_count >= 3:
            score += 15
            details['headings'] = {'status': 'good', 'h2': h2_count, 'h3': h3_count}
        elif h2_count >= 2:
            score += 10
            issues.append("Add more H2 headings (3+ recommended)")
            details['headings'] = {'status': 'fair', 'h2': h2_count, 'h3': h3_count}
        else:
            score += 5
            issues.append("Insufficient headings structure")
            details['headings'] = {'status': 'poor', 'h2': h2_count, 'h3': h3_count}
        
        if h3_count >= 2:
            score += 5
        
        # 3. Content length (15 points)
        word_count = len(content.split())
        if word_count >= 1000:
            score += 15
            details['word_count'] = {'status': 'excellent', 'count': word_count}
        elif word_count >= 600:
            score += 10
            details['word_count'] = {'status': 'good', 'count': word_count}
        else:
            score += 5
            issues.append("Content too short for SEO")
            details['word_count'] = {'status': 'poor', 'count': word_count}
        
        # 4. Internal/External links (15 points)
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        link_count = len(links)
        
        if link_count >= 5:
            score += 15
            details['links'] = {'status': 'excellent', 'count': link_count}
        elif link_count >= 3:
            score += 10
            details['links'] = {'status': 'good', 'count': link_count}
        elif link_count >= 1:
            score += 5
            issues.append("Add more internal/external links")
            details['links'] = {'status': 'fair', 'count': link_count}
        else:
            issues.append("No links found")
            details['links'] = {'status': 'poor', 'count': 0}
        
        # 5. Images/Media (10 points)
        images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
        if len(images) >= 3:
            score += 10
            details['images'] = {'status': 'excellent', 'count': len(images)}
        elif len(images) >= 1:
            score += 5
            details['images'] = {'status': 'good', 'count': len(images)}
        else:
            issues.append("No images found")
            details['images'] = {'status': 'none', 'count': 0}
        
        # 6. Lists (10 points)
        bullet_lists = len(re.findall(r'^\s*[-*+]\s+', content, re.MULTILINE))
        numbered_lists = len(re.findall(r'^\s*\d+\.\s+', content, re.MULTILINE))
        
        if bullet_lists + numbered_lists >= 5:
            score += 10
            details['lists'] = {'status': 'excellent', 'total': bullet_lists + numbered_lists}
        elif bullet_lists + numbered_lists >= 2:
            score += 5
            details['lists'] = {'status': 'good', 'total': bullet_lists + numbered_lists}
        else:
            issues.append("Add lists for better readability")
            details['lists'] = {'status': 'poor', 'total': bullet_lists + numbered_lists}
        
        # 7. Paragraph length (10 points)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not p.strip().startswith('#')]
        avg_paragraph_length = sum(len(p.split()) for p in paragraphs) / max(len(paragraphs), 1)
        
        if 50 <= avg_paragraph_length <= 150:
            score += 10
            details['paragraphs'] = {'status': 'optimal', 'avg_length': int(avg_paragraph_length)}
        else:
            score += 5
            if avg_paragraph_length > 150:
                issues.append("Paragraphs too long")
            details['paragraphs'] = {'status': 'suboptimal', 'avg_length': int(avg_paragraph_length)}
        
        # 8. Bold/Emphasis usage (5 points)
        bold_count = len(re.findall(r'\*\*[^*]+\*\*|__[^_]+__', content))
        if bold_count >= 5:
            score += 5
            details['emphasis'] = {'status': 'good', 'count': bold_count}
        elif bold_count >= 2:
            score += 3
            details['emphasis'] = {'status': 'fair', 'count': bold_count}
        else:
            details['emphasis'] = {'status': 'low', 'count': bold_count}
        
        return {
            'passed': score >= 70,  # Pass threshold
            'score': min(score, max_score),
            'issues': issues,
            'details': details
        }

