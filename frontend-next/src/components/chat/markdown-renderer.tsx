"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "@/lib/utils";
import { Citation } from "@/types/rag";
import { BookOpen } from "lucide-react";

interface MarkdownRendererProps {
  content: string;
  citations?: Citation[];
  onCitationClick?: (citation: Citation) => void;
}

export function MarkdownRenderer({
  content,
  citations = [],
  onCitationClick,
}: MarkdownRendererProps) {
  // Helper to render text with clickable citation badges
  const renderTextWithCitations = (text: string) => {
    // Regex matches [Page 12], [Page 12, Chunk #3], [Doc: xyz, Page: 12], [Page: 12]
    const citationRegex = /\[(?:Doc:\s*[^,]+,\s*)?Page:?\s*(\d+)(?:,\s*Chunk:?\s*#?(\d+))?\]/gi;
    
    const parts: (string | React.ReactNode)[] = [];
    let lastIndex = 0;
    let match: RegExpExecArray | null;

    while ((match = citationRegex.exec(text)) !== null) {
      const matchStart = match.index;
      const matchEnd = citationRegex.lastIndex;

      // Push text before match
      if (matchStart > lastIndex) {
        parts.push(text.substring(lastIndex, matchStart));
      }

      const pageNum = parseInt(match[1], 10);
      const chunkNum = match[2] ? parseInt(match[2], 10) : undefined;
      const fullTag = match[0];

      // Find matching citation
      const matchedCitation =
        citations.find((c) => c.page_number === pageNum) || {
          document_id: "",
          page_number: pageNum,
          snippet: `Referenced citation on page ${pageNum}`,
          relevance_score: 0.85,
          chunk_index: chunkNum,
        };

      parts.push(
        <button
          key={`cite-${matchStart}-${pageNum}`}
          type="button"
          onClick={() => onCitationClick?.(matchedCitation)}
          className="inline-flex items-center gap-1 mx-1 px-2 py-0.5 rounded text-xs font-bold bg-[rgba(184,29,36,0.18)] border border-[rgba(230,57,70,0.35)] text-[#FFA8B2] hover:bg-[rgba(184,29,36,0.3)] hover:border-[#E63946] transition-colors align-baseline cursor-pointer"
          title={`Click to inspect source citation on Page ${pageNum}`}
        >
          <BookOpen className="h-3 w-3 inline text-[#E63946]" />
          <span>Page {pageNum}{chunkNum ? ` (#${chunkNum})` : ""}</span>
        </button>
      );

      lastIndex = matchEnd;
    }

    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex));
    }

    return parts.length > 0 ? parts : text;
  };

  return (
    <div className="prose prose-invert max-w-none text-slate-200 text-sm leading-relaxed space-y-3">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          p({ children }) {
            // Check if single text child can be processed for citations
            if (typeof children === "string") {
              return <p className="mb-3 leading-relaxed">{renderTextWithCitations(children)}</p>;
            }
            // If children contains array of React nodes or strings
            if (Array.isArray(children)) {
              return (
                <p className="mb-3 leading-relaxed">
                  {children.map((child, idx) =>
                    typeof child === "string" ? (
                      <React.Fragment key={idx}>
                        {renderTextWithCitations(child)}
                      </React.Fragment>
                    ) : (
                      child
                    )
                  )}
                </p>
              );
            }
            return <p className="mb-3 leading-relaxed">{children}</p>;
          },
          h1({ children }) {
            return (
              <h1 className="text-lg font-bold text-white mt-4 mb-2 pb-1 border-b border-slate-800">
                {children}
              </h1>
            );
          },
          h2({ children }) {
            return (
              <h2 className="text-base font-bold text-white mt-3 mb-2 flex items-center gap-1.5">
                <span className="h-1.5 w-1.5 rounded-full bg-blue-400 inline-block" />
                {children}
              </h2>
            );
          },
          h3({ children }) {
            return (
              <h3 className="text-sm font-semibold text-slate-200 mt-2.5 mb-1.5">
                {children}
              </h3>
            );
          },
          ul({ children }) {
            return <ul className="list-disc pl-5 space-y-1 mb-3 text-slate-300">{children}</ul>;
          },
          ol({ children }) {
            return <ol className="list-decimal pl-5 space-y-1 mb-3 text-slate-300">{children}</ol>;
          },
          li({ children }) {
            return <li className="leading-relaxed">{children}</li>;
          },
          strong({ children }) {
            return <strong className="font-semibold text-white">{children}</strong>;
          },
          em({ children }) {
            return <em className="italic text-slate-300">{children}</em>;
          },
          blockquote({ children }) {
            return (
              <blockquote className="border-l-2 border-blue-500 pl-3 my-2 text-slate-400 italic bg-blue-500/5 py-1 rounded-r">
                {children}
              </blockquote>
            );
          },
          table({ children }) {
            return (
              <div className="my-4 overflow-x-auto rounded-lg border border-slate-800 bg-slate-950/70 shadow-sm">
                <table className="w-full text-left text-xs text-slate-300 border-collapse">
                  {children}
                </table>
              </div>
            );
          },
          thead({ children }) {
            return (
              <thead className="bg-slate-900/90 text-slate-200 uppercase tracking-wider text-[11px] font-semibold border-b border-slate-800">
                {children}
              </thead>
            );
          },
          tbody({ children }) {
            return <tbody className="divide-y divide-slate-800/60 font-mono">{children}</tbody>;
          },
          tr({ children }) {
            return <tr className="hover:bg-slate-900/40 transition-colors">{children}</tr>;
          },
          th({ children }) {
            return <th className="px-3.5 py-2.5 font-semibold text-slate-300">{children}</th>;
          },
          td({ children }) {
            return <td className="px-3.5 py-2 whitespace-nowrap text-slate-300">{children}</td>;
          },
          code({ className, children, ...props }) {
            const isInline = !className;
            if (isInline) {
              return (
                <code
                  className="px-1.5 py-0.5 rounded text-xs font-mono bg-slate-800 border border-slate-700/60 text-blue-300"
                  {...props}
                >
                  {children}
                </code>
              );
            }
            return (
              <div className="my-3 overflow-hidden rounded-lg border border-slate-800 bg-slate-950">
                <div className="bg-slate-900 px-3 py-1 text-[10px] uppercase font-mono text-slate-400 border-b border-slate-800">
                  Code
                </div>
                <pre className="p-3 text-xs font-mono text-slate-200 overflow-x-auto">
                  <code>{children}</code>
                </pre>
              </div>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
