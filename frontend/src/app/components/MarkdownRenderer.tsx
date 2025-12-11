'use client';

import React, { useState, useRef, memo } from 'react';
import dynamic from 'next/dynamic';
import Image from 'next/image';
import rehypeRaw from 'rehype-raw';
import rehypePrism from 'rehype-prism-plus';
import 'prismjs/themes/prism-tomorrow.css';

// Lazy load ReactMarkdown
const ReactMarkdown = dynamic(() => import('react-markdown'), {
  ssr: true,
  loading: () => <div className="animate-pulse">Loading content...</div>
});

interface CodeBlockProps {
  children: React.ReactNode;
  className?: string;
}

const CodeBlock: React.FC<CodeBlockProps> = memo(({ children, className }) => {
  const [isCopied, setIsCopied] = useState(false);
  const textInput = useRef<HTMLDivElement>(null);

  const handleCopy = () => {
    if (textInput.current) {
      const code = textInput.current.innerText;
      navigator.clipboard.writeText(code);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    }
  };

  const language = className?.replace(/language-/, '') || 'javascript';

  return (
    <div className="relative group">
      <button
        onClick={handleCopy}
        className="absolute top-2 right-2 bg-gray-700 text-white px-2 py-1 rounded text-sm opacity-0 group-hover:opacity-100 transition-opacity z-10"
        aria-label="Copy code"
      >
        {isCopied ? 'Copied!' : 'Copy'}
      </button>
      <div ref={textInput}>
        <pre className={`language-${language}`}>
          <code>{children}</code>
        </pre>
      </div>
    </div>
  );
});

interface MarkdownRendererProps {
  content: string;
}
const MarkdownRenderer: React.FC<MarkdownRendererProps> = memo(({ content }) => {
  return (
    <div className="markdown-content">
      <ReactMarkdown
        rehypePlugins={[rehypeRaw, rehypePrism]}
        components={{
          pre: ({ children, ...props }) => {
            const codeChild = React.Children.toArray(children).find(
              (child): child is React.ReactElement<{ className?: string; children?: React.ReactNode }> =>
                React.isValidElement(child) && child.type === 'code'
            );

            if (codeChild) {
              return (
                <CodeBlock className={codeChild.props.className}>
                  {codeChild.props.children}
                </CodeBlock>
              );
            }
            return <pre {...props}>{children}</pre>;
          },

          // Handle images
          img: ({ node, src, alt, ...props }) => {
            if (!src || typeof src !== 'string') return null;

            const isExternal = src.startsWith('http://') || src.startsWith('https://');
            
            if (isExternal) {
              return (
                <span className="block my-6">
                  <img
                    src={src}
                    alt={alt || ''}
                    className="rounded-lg max-w-full h-auto mx-auto"
                    loading="lazy"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      target.style.display = 'none';
                      const parent = target.parentElement;
                      if (parent) {
                        parent.innerHTML = `<div class="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg text-center text-gray-500">
                          <p>Image not available</p>
                          <p class="text-sm mt-2">${alt || 'No description'}</p>
                        </div>`;
                      }
                    }}
                    {...props}
                  />
                  {alt && (
                    <span className="block text-center text-sm text-gray-600 dark:text-gray-400 mt-2">
                      {alt}
                    </span>
                  )}
                </span>
              );
            }

            return (
              <span className="block my-6">
                <Image
                  src={src}
                  alt={alt || ''}
                  width={800}
                  height={600}
                  className="rounded-lg max-w-full h-auto mx-auto"
                  priority={false}
                />
                {alt && (
                  <span className="block text-center text-sm text-gray-600 dark:text-gray-400 mt-2">
                    {alt}
                  </span>
                )}
              </span>
            );
          },

          // Style links
          a: ({ node, href, children, ...props }) => (
            <a
              href={href}
              className="text-indigo-600 dark:text-indigo-400 hover:underline"
              target={href?.startsWith('http') ? '_blank' : undefined}
              rel={href?.startsWith('http') ? 'noopener noreferrer' : undefined}
              {...props}
            >
              {children}
            </a>
          ),

          // Style headings
          h1: ({ node, children, ...props }) => (
            <h1 className="text-4xl font-bold mt-8 mb-4" {...props}>{children}</h1>
          ),
          h2: ({ node, children, ...props }) => (
            <h2 className="text-3xl font-bold mt-6 mb-3" {...props}>{children}</h2>
          ),
          h3: ({ node, children, ...props }) => (
            <h3 className="text-2xl font-bold mt-4 mb-2" {...props}>{children}</h3>
          ),

          // Style lists
          ul: ({ node, children, ...props }) => (
            <ul className="list-disc list-inside my-4 space-y-2" {...props}>{children}</ul>
          ),
          ol: ({ node, children, ...props }) => (
            <ol className="list-decimal list-inside my-4 space-y-2" {...props}>{children}</ol>
          ),

          // Style blockquotes
          blockquote: ({ node, children, ...props }) => (
            <blockquote className="border-l-4 border-indigo-500 pl-4 italic my-4 text-gray-700 dark:text-gray-300" {...props}>
              {children}
            </blockquote>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
});

MarkdownRenderer.displayName = 'MarkdownRenderer';
CodeBlock.displayName = 'CodeBlock';

export default MarkdownRenderer;
