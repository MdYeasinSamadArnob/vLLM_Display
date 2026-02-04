"use client";
import { useState } from 'react';
import { Copy, Check, FileJson, FileText, FileCode } from 'lucide-react';
import { clsx } from 'clsx';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ResultsDisplayProps {
  result: {
    text: string;
    format: string;
    metadata: any;
  };
}

export default function ResultsDisplay({ result }: ResultsDisplayProps) {
  const [activeTab, setActiveTab] = useState<'text' | 'json' | 'preview' | 'html'>('text'); // Default to Text
  const [copied, setCopied] = useState(false);

  // Clean up markdown/html code blocks if present in text
  const cleanContent = (content: string) => {
    // Try to extract content inside ```html ... ``` or ``` ... ```
    const codeBlockMatch = content.match(/```(?:html)?\s*([\s\S]*?)```/);
    if (codeBlockMatch && codeBlockMatch[1]) {
      return codeBlockMatch[1].trim();
    }
    // Fallback: strip start/end markers if they exist at edges
    return content.replace(/^```html\s*/, '').replace(/^```\s*/, '').replace(/```$/, '').trim();
  };

  const isHtml = result.format === 'html' || result.text.trim().startsWith('<') || result.text.includes('```html');

  const handleCopy = () => {
    navigator.clipboard.writeText(result.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-3 bg-gray-50 border-b border-gray-200">
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('text')}
            className={clsx(
              "px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-2",
              activeTab === 'text' ? "bg-white text-blue-600 shadow-sm border border-gray-200" : "text-gray-500 hover:text-gray-700"
            )}
          >
            <FileText className="w-4 h-4" />
            Text
          </button>
          <button
            onClick={() => setActiveTab('preview')}
            className={clsx(
              "px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-2",
              activeTab === 'preview' ? "bg-white text-blue-600 shadow-sm border border-gray-200" : "text-gray-500 hover:text-gray-700"
            )}
          >
            <FileCode className="w-4 h-4" />
            Preview
          </button>
          <button
            onClick={() => setActiveTab('html')}
            className={clsx(
              "px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-2",
              activeTab === 'html' ? "bg-white text-blue-600 shadow-sm border border-gray-200" : "text-gray-500 hover:text-gray-700"
            )}
          >
            <FileCode className="w-4 h-4" />
            HTML Source
          </button>
          <button
            onClick={() => setActiveTab('json')}
            className={clsx(
              "px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-2",
              activeTab === 'json' ? "bg-white text-blue-600 shadow-sm border border-gray-200" : "text-gray-500 hover:text-gray-700"
            )}
          >
            <FileJson className="w-4 h-4" />
            JSON
          </button>
        </div>
        
        <button 
          onClick={handleCopy}
          className="p-2 hover:bg-gray-200 rounded-lg text-gray-500 transition-colors"
          title="Copy to clipboard"
        >
          {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
        </button>
      </div>

      <div className="flex-1 overflow-hidden relative bg-gray-50/50"> 
        {/* Added overflow-hidden and relative to container to strictly manage scroll areas */}
        
        {activeTab === 'text' && (
            <div className="absolute inset-0 overflow-auto p-6 font-mono text-sm whitespace-pre-wrap text-gray-800 bg-white">
                {result.text}
            </div>
        )}
        
        {activeTab === 'json' && (
            <div className="absolute inset-0 overflow-auto p-6 bg-gray-900 text-green-400 font-mono text-sm">
                <pre>{JSON.stringify({ content: result.text, metadata: result.metadata }, null, 2)}</pre>
            </div>
        )}

        {activeTab === 'html' && (
            <div className="absolute inset-0 overflow-auto p-6 bg-gray-900 text-blue-300 font-mono text-sm">
                <pre>{cleanContent(result.text)}</pre>
            </div>
        )}

        {activeTab === 'preview' && (
            <div className="absolute inset-0 overflow-auto p-8 bg-white text-gray-900">
                {isHtml ? (
                   <>
                     <style jsx global>{`
                       .html-preview table { border-collapse: collapse; width: 100%; margin-bottom: 1rem; }
                       .html-preview th, .html-preview td { border: 1px solid #e2e8f0; padding: 0.75rem; text-align: left; }
                       .html-preview th { bg-gray-50; font-weight: 600; }
                       .html-preview h1, .html-preview h2, .html-preview h3 { margin-top: 1.5rem; margin-bottom: 1rem; font-weight: bold; }
                       .html-preview h1 { font-size: 2em; }
                       .html-preview h2 { font-size: 1.5em; }
                       .html-preview p { margin-bottom: 1rem; line-height: 1.6; }
                       .html-preview ul, .html-preview ol { margin-bottom: 1rem; padding-left: 2rem; }
                       .html-preview ul { list-style-type: disc; }
                       .html-preview ol { list-style-type: decimal; }
                     `}</style>
                     <div 
                       className="html-preview"
                       dangerouslySetInnerHTML={{ __html: cleanContent(result.text) }} 
                     />
                   </>
                ) : (
                    <div className="prose prose-slate max-w-none">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {result.text}
                        </ReactMarkdown>
                    </div>
                )}
            </div>
        )}
      </div>

      
      <div className="bg-gray-100 px-4 py-2 border-t border-gray-200 text-xs text-gray-500 flex gap-4">
        <span>Time: {result.metadata?.api_process_time ? (result.metadata.api_process_time * 1000).toFixed(0) : 0}ms</span>
        <span>Model: {result.metadata?.model || 'Unknown'}</span>
        <span>Confidence: High</span>
      </div>
    </div>
  );
}
