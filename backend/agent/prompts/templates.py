"""
Prompt templates for dynamic content generation.

Templates with variable substitution for each agent role.
"""

import sys
from pathlib import Path
from string import Template

# Handle both module and direct execution contexts
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from .system_prompts import AGENT_CONTEXT_PREP, QUALITY_GATE
except ImportError:
    from system_prompts import AGENT_CONTEXT_PREP, QUALITY_GATE


# Researcher Agent Templates
RESEARCHER_PROMPT_TEMPLATE = Template("""
Phân tích cơ sở tri thức blog hiện có và tạo bản tóm tắt nghiên cứu toàn diện cho một bài viết blog mới về chủ đề này:

CHỦ ĐỀ: $topic

$context_prep

NGỮCẢNH HIỆN CÓ:
$relevant_context

THÔNG SỐ TẠO NỘI DUNG:
- Phong cách: $style
- Độ dài mục tiêu: $word_count_range từ
- Đối tượng mục tiêu: $audience
- Yêu cầu chính: $requirements

Tạo bản tóm tắt nghiên cứu bao gồm:
1. Các chủ đề và khái niệm chính từ nội dung hiện có
2. Các sự kiện và phát hiện liên quan để kết hợp
3. Các chủ đề liên quan được đề cập trong cơ sở tri thức
4. Khoảng trống nội dung và cơ hội
5. Các lĩnh vực trọng tâm được đề xuất cho bài viết mới
6. Cơ hội kết nối với các bài viết hiện có

Cấu trúc phản hồi của bạn với các tiêu đề phần rõ ràng.
$quality_gate
""")

# Outliner Agent Templates
OUTLINER_PROMPT_TEMPLATE = Template("""
Tạo dàn ý chi tiết, được tối ưu hóa SEO cho một bài viết blog dựa trên bản tóm tắt nghiên cứu và thông số kỹ thuật.

CHỦ ĐỀ: $topic

BẢN TÓM TẮT NGHIÊN CỨU:
$research_brief

THÔNG SỐ TẠO NỘI DUNG:
- Phong cách: $style
- Độ dài mục tiêu: $word_count_range từ
- Danh mục: $categories
- Từ khóa: $keywords

Tạo dàn ý bao gồm:
1. Tiêu đề H1 hấp dẫn với từ khóa chính
2. 3-7 phần chính H2 với tiêu đề mô tả
3. Các phần nhỏ dưới mỗi H2 (sử dụng H3 nếu phù hợp)
4. Các điểm chính cần đề cập trong mỗi phần
5. Mục tiêu số từ cho mỗi phần
6. Ghi chú tối ưu hóa SEO (đặt từ khóa, liên kết nội bộ)
7. Mục tiêu giới thiệu và kết luận

Định dạng dàn ý bằng markdown với phân cấp phần rõ ràng.
$context_prep
$quality_gate

Đảm bảo dàn ý sẽ tạo ra nội dung tổng cộng $word_count_range từ.
""")

# Writer Agent Templates
WRITER_PROMPT_TEMPLATE = Template("""
Viết một bài viết blog hoàn chỉnh theo dàn ý được cung cấp và kết hợp hiểu biết từ bản tóm tắt nghiên cứu.

DÀN Ý CẦN TUÂN THU:
$outline

BẢN TÓM TẮT NGHIÊN CỨU & NGỮCẢNH:
$research_context

THÔNG SỐ VIẾT:
- Phong cách: $style
- Tổng độ dài mục tiêu: $word_count_range từ
- Giọng điệu: $tone
- Từ khóa cần kết hợp tự nhiên: $keywords
- Danh mục: $categories

Yêu cầu viết:
- Bắt đầu với phần giới thiệu hấp dẫn (150-250 từ)
- Tuân theo cấu trúc dàn ý chính xác
- Kết hợp hiểu biết từ các bài viết hiện có một cách tự nhiên
- Kết thúc với kết luận hấp dẫn với lời kêu gọi hành động
- Sử dụng định dạng rõ ràng, dễ quét (tiêu đề, danh sách, nhấn mạnh in đậm)
- Duy trì độ chính xác kỹ thuật nhất quán
- Bao gồm các ví dụ thực tế và lời khuyên có thể hành động
- Viết với giọng văn hấp dẫn, chuyên nghiệp

Chỉ xuất ra nội dung bài viết blog hoàn chỉnh ở định dạng markdown.
$context_prep
$quality_gate
""")
# - Follow the outline structure exactly
# - Incorporate insights from existing posts naturally
# - End with a compelling conclusion with call-to-action
# - Use clear, scannable formatting (headings, lists, bold emphasis)
# - Maintain consistent technical accuracy
# - Include practical examples and actionable advice
# - Write in engaging, professional voice

# Output only the complete blog post content in markdown format.
# $context_prep
# $quality_gate
# """)

# Editor Agent Templates
EDITOR_PROMPT_TEMPLATE = Template("""
Chỉnh sửa và đánh bóng bản thảo bài viết blog sau để tối đa hóa sự rõ ràng, tương tác và chất lượng chuyên nghiệp.

BẢN THẢO GỐC:
$draft_content

YÊU CẦU CHỈNH SỮA:
- Cải thiện sự rõ ràng và chính xác trong các giải thích kỹ thuật
- Tăng cường khả năng đọc trong khi duy trì độ chính xác kỹ thuật
- Củng cố chuyển tiếp giữa các phần
- Xác minh giọng văn và giọng điệu nhất quán xuyên suốt
- Đánh bóng ngôn ngữ cho độ chính xác ngữ pháp và sự thanh lịch
- Đảm bảo định dạng markdown phù hợp
- Tối ưu hóa khả năng quét với tiêu đề, danh sách và nhấn mạnh
- Loại bỏ sự dư thừa và lời lẽ rườm rà
- Củng cố các lập luận yếu bằng các giải thích rõ ràng hơn

Không thay đổi ý nghĩa cốt lõi hoặc sự kiện, nhưng cải thiện đáng kể cách trình bày.
Duy trì độ dài mục tiêu $word_count_range từ.

Xuất ra phiên bản đã chỉnh sửa hoàn toàn sẵn sàng cho xuất bản.
$context_prep
$quality_gate
""")

# SEO Optimizer Templates
SEO_OPTIMIZER_PROMPT_TEMPLATE = Template("""
Phân tích và tối ưu hóa bài viết blog sau để có khả năng hiển thị công cụ tìm kiếm và sự tương tác của người dùng.

NỘI DUNG CẦN TỐI ƯU HÓA:
$edited_content

THÔNG SỐ TỐI ƯU HÓA:
- Từ khóa mục tiêu: $keywords
- Danh mục nội dung: $categories
- Độ dài mục tiêu: $word_count_range từ

PHÂN TÍCH & TỐI ƯU HÓA SEO:
1. Tối ưu tiêu đề (30-60 ký tự): Đề xuất tiêu đề cải thiện với từ khóa chính
2. Mô tả meta (150-160 ký tự): Tạo tóm tắt hấp dẫn
3. Cấu trúc tiêu đề: Xem xét phân cấp H1-H3 và phân phối từ khóa
4. Sử dụng từ khóa: Đánh giá mật độ từ khóa tự nhiên ($keyword_density_target)
5. Liên kết nội bộ: Đề xuất 3-5 liên kết đến các bài viết liên quan từ cơ sở tri thức
6. Cấu trúc nội dung: Đảm bảo độ sâu và bao quát phù hợp
7. SEO kỹ thuật: Xác minh định dạng thân thiện di động và khả năng đọc

Cung cấp các đề xuất cụ thể và metadata được tối ưu hóa.
$context_prep
$quality_gate
""")

# Validation Templates
RETRIEVER_PROMPT_TEMPLATE = Template("""
Dựa trên ngữ cảnh được cung cấp từ cơ sở tri thức, tạo bản tóm tắt súc tích và trích xuất các đoạn trích liên quan cho chủ đề bài viết blog mới.

CHỦ ĐỀ: $topic

NGỮCẢNH ĐƯỢC TRUY XUẤT:
$context

HƯỚNG DẮN:
1. Tạo bản tóm tắt súc tích (100-200 từ) nắm bắt bản chất của nội dung liên quan hiện có và mối quan hệ với chủ đề
2. Trích xuất $excerpt_limit đoạn trích liên quan nhất sẽ thông tin cho bài viết mới
3. Làm nổi bật các chủ đề chính, hiểu biết và kết nối từ các bài viết hiện có
4. Tập trung vào nội dung thực chất, có thể hành động tạo giá trị cho bài viết mới

Định dạng phản hồi của bạn như:
TÓM TẮT: [Bản tổng hợp súc tích của bạn ở đây]

CÁC ĐOẠN TRÍCH LIÊN QUAN:
- [Trích dẫn hoặc diễn giải từ phần liên quan nhất]
- [Đoạn trích liên quan tiếp theo]
- [Tiếp tục khi cần thiết]

Đảm bảo các đoạn trích có ích trực tiếp để tạo nội dung mới, có giá trị và độc đáo.
""")

COMPOSER_PROMPT_TEMPLATE = Template("""
Tạo bản thảo bài viết blog ban đầu dựa trên tổng hợp ngữ cảnh của retriever và thông số tạo.

CHỦ ĐỀ: $topic

NGỮCẢNH TỪ RETRIEVER:
Tóm tắt: $summary

Các đoạn trích liên quan:
$excerpts

THÔNG SỐ TẠO NỘI DUNG:
- Phong cách: $style
- Độ dài mục tiêu: $length từ (phạm vi $min_words - $max_words)
- Giọng điệu: $tone
- Danh mục: $categories
- Thẻ: $tags

YÊU CẦU CẤU TRÚC:
1. Tiêu đề H1 với từ khóa chính (sử dụng # )
2. Phần giới thiệu hấp dẫn thu hút người đọc
3. 3-5 phần nội dung chính với tiêu đề H2 (sử dụng ## )
4. Kết luận với các điểm chính rút ra và các bước tiếp theo
5. Định dạng markdown phù hợp xuyên suốt

HƯỚNG DẮN NỘI DUNG:
- Kết hợp hiểu biết từ ngữ cảnh retriever một cách tự nhiên
- Viết với giọng văn có thẩm quyền, hấp dẫn
- Cân bằng độ sâu kỹ thuật với khả năng tiếp cận
- Bao gồm các ví dụ thực tế và lời khuyên có thể hành động
- Đảm bảo luồng logic và chuyển tiếp mượt mà
- Nhắm mục tiêu phạm vi số từ được chỉ định

QUAN TRọNG: KHÔNG bao gồm bất kỳ frontmatter YAML, tiêu đề metadata hoặc dấu phân cách --- nào. Bắt đầu trực tiếp với tiêu đề H1 và chỉ xuất nội dung thân markdown.
""")

REFINER_PROMPT_TEMPLATE = Template("""
Xem xét và tinh chỉnh bản thảo bài viết blog để cải thiện cấu trúc, sự rõ ràng và sự tương tác.

BẢN THẢO GỐC:
$draft_content

NHIỆM VỤ TINH CHỈNH:
1. Nâng cao cấu trúc và luồng logic
2. Cải thiện khả năng đọc và sự tương tác
3. Mở rộng các phần thiếu chi tiết đầy đủ
4. Củng cố các lập luận yếu bằng giải thích tốt hơn
5. Loại bỏ sự dư thừa và cải thiện tính mạch lạc
6. Đánh bóng ngôn ngữ cho chất lượng chuyên nghiệp
7. Xác minh độ chính xác kỹ thuật và thuật ngữ
8. Tối ưu hóa cho sự hiểu biết của đối tượng mục tiêu

ĐỘ DÀI MỤC TIÊU: $length từ (duy trì phạm vi $min_words - $max_words)

THÔNG SỐ CẦN DUY TRÌ:
- Phong cách: $style
- Giọng điệu: $tone
- Danh mục: $categories
- Thẻ: $tags

QUAN TRọNG: KHÔNG bao gồm bất kỳ frontmatter YAML hoặc tiêu đề metadata nào. Chỉ xuất nội dung thân markdown tinh chỉnh bắt đầu với tiêu đề H1.

Xuất ra phiên bản tinh chỉnh với các cải tiến rõ ràng trong khi bảo tồn nội dung và cấu trúc cốt lõi.
""")

EVALUATOR_PROMPT_TEMPLATE = Template("""
Đánh giá bản thảo bài viết blog dựa trên tiêu chuẩn chất lượng và xác định xem nó có đáp ứng tiêu chí xuất bản hay không.

NỘI DUNG CẦN ĐÁNH GIÁ:
$draft_content

TIÊU CHÍ ĐÁNH GIÁ:
-  Cấu trúc: Định dạng giới thiệu-thân-kết luận rõ ràng
-  Số từ: Trong phạm vi $min_words - $max_words (hiện tại: $current_words)
-  Định dạng Markdown: Tiêu đề, danh sách, khối mã, liên kết phù hợp
-  Tính mạch lạc: Luồng logic, chuyển tiếp mượt mà, giọng điệu nhất quán
-  Độ chính xác thực tế: Các tuyên bố đúng kỹ thuật và được hỗ trợ
-  Tính độc đáo: Thêm giá trị rõ ràng vượt ra ngoài nội dung hiện có
-  Sự tương tác: Nội dung hấp dẫn, dễ đọc, có thể hành động

YÊU CẦU PHÊ DUYỆT:
- Phải vượt qua TẤT CẢ các kiểm tra cấu trúc
- Phải đáp ứng yêu cầu số từ
- Phải sử dụng markdown đúng xuyên suốt
- Phải thể hiện chất lượng đầy đủ về tính mạch lạc và độ chính xác

Nếu ĐƯỢC PHÊ DUYỆT: Chỉ xuất "PHÊ DUYỆT" theo sau là lý do ngắn gọn.

Nếu BỊ TỪ CHỐI: Xuất "TỪ CHỐI" theo sau là phản hồi cụ thể, có thể hành động:
- Liệt kê mỗi tiêu chí không đạt
- Cung cấp vị trí chính xác của vấn đề
- Đề xuất các cải tiến cụ thể
- Ưu tiên các sửa chữa theo tác động và nỗ lực
""")

INGESTOR_PROMPT_TEMPLATE = Template("""
Bài viết blog đã được phê duyệt cho xuất bản. Chuẩn bị các tệp đạu ra cuối cùng và metadata nhập.

NỘI DUNG ĐƯỢC PHÊ DUYỆT:
$final_content

YÊU CẦU NHẬP:
1. Tạo slug từ tiêu đề cho tên tệp an toàn URL
2. Tạo tệp ./content/posts/{slug}.md
3. Đảm bảo frontmatter được bao gồm phù hợp
4. Chuẩn bị các phần nội dung cho lưu trữ vector
5. Tạo embeddings cho khả năng tìm kiếm
6. Cập nhật cơ sở tri thức với nội dung mới

KIỂM TRA XÁC THỰC:
- Xác nhận tệp đã được lưu thành công
- Xác minh sự hoàn chỉnh của frontmatter
- Đảm bảo nội dung được phân đoạn phù hợp
- Xác nhận embeddings đã được tạo
- Xác thực khả năng truy xuất nội dung mới

Xuất xác nhận khi nhập hoàn tất và cung cấp đường dẫn tệp cuối cùng.
""")

VALIDATION_FEEDBACK_TEMPLATE = Template("""
Cung cấp phản hồi cụ thể về các vấn đề xác thực nội dung sau:

KẾT QUẢ XÁC THỰC:
$validation_results

BẢN THẢO NỘI DUNG:
$draft_content

HƯỚNG DẮN CẦN THIẾT:
- Giải quyết các lỗi nghiêm trọng ngăn cản xuất bản
- Đề xuất các sửa chữa cho cảnh báo để cải thiện chất lượng
- Cung cấp các ví dụ cụ thể cho cải tiến
- Ưu tiên các thay đổi theo tác động và mức độ khẩn cấp

Xuất phản hồi có thể hành động với các đề xuất ưu tiên.
""")


# Helper functions for template rendering
def render_researcher_prompt(topic, relevant_context, spec):
    """Render researcher prompt with variables."""
    return RESEARCHER_PROMPT_TEMPLATE.substitute(
        topic=topic,
        context_prep=AGENT_CONTEXT_PREP,
        relevant_context=relevant_context,
        style=spec.get('style', 'technical'),
        word_count_range=f"{spec.get('min_words', 800)}-{spec.get('max_words', 2000)}",
        audience=spec.get('audience', 'technical professionals'),
        requirements=spec.get('requirements', 'Comprehensive technical coverage'),
        quality_gate=QUALITY_GATE
    )


def render_outliner_prompt(topic, research_brief, spec):
    """Render outliner prompt with variables."""
    return OUTLINER_PROMPT_TEMPLATE.substitute(
        topic=topic,
        research_brief=research_brief,
        style=spec.get('style', 'technical'),
        word_count_range=f"{spec.get('min_words', 800)}-{spec.get('max_words', 2000)}",
        categories=', '.join(spec.get('categories', [])),
        keywords=', '.join(spec.get('keywords', [])),
        context_prep=AGENT_CONTEXT_PREP,
        quality_gate=QUALITY_GATE,
        total_word_target=spec.get('word_target', 1500)
    )


def render_writer_prompt(outline, research_context, spec):
    """Render writer prompt with variables."""
    return WRITER_PROMPT_TEMPLATE.substitute(
        outline=outline,
        research_context=research_context,
        style=spec.get('style', 'technical'),
        word_count_range=f"{spec.get('min_words', 800)}-{spec.get('max_words', 2000)}",
        tone=spec.get('tone', 'informative'),
        keywords=', '.join(spec.get('keywords', [])),
        categories=', '.join(spec.get('categories', [])),
        context_prep=AGENT_CONTEXT_PREP,
        quality_gate=QUALITY_GATE
    )


def render_editor_prompt(draft_content, spec):
    """Render editor prompt with variables."""
    return EDITOR_PROMPT_TEMPLATE.substitute(
        draft_content=draft_content,
        word_count_range=f"{spec.get('min_words', 800)}-{spec.get('max_words', 2000)}",
        context_prep=AGENT_CONTEXT_PREP,
        quality_gate=QUALITY_GATE
    )


def render_seo_optimizer_prompt(edited_content, spec):
    """Render SEO optimizer prompt with variables."""
    return SEO_OPTIMIZER_PROMPT_TEMPLATE.substitute(
        edited_content=edited_content,
        keywords=', '.join(spec.get('keywords', [])),
        categories=', '.join(spec.get('categories', [])),
        word_count_range=f"{spec.get('min_words', 800)}-{spec.get('max_words', 2000)}",
        keyword_density_target=f"{spec.get('keyword_density', 0.02) * 100:.1f}%",
        context_prep=AGENT_CONTEXT_PREP,
        quality_gate=QUALITY_GATE
    )
