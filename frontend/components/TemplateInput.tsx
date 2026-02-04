import React, { useState } from 'react';
import { Settings, ChevronDown, ChevronUp } from 'lucide-react';
import { clsx } from 'clsx';

interface TemplateInputProps {
  template: string;
  setTemplate: (template: string) => void;
}

export default function TemplateInput({ template, setTemplate }: TemplateInputProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 mt-4">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between text-left"
      >
        <div className="flex items-center gap-2 text-gray-800 font-semibold">
          <Settings className="w-5 h-5 text-gray-500" />
          <span>Extraction Template (Optional)</span>
        </div>
        {isOpen ? <ChevronUp className="w-4 h-4 text-gray-500" /> : <ChevronDown className="w-4 h-4 text-gray-500" />}
      </button>

      {isOpen && (
        <div className="mt-4 animate-in slide-in-from-top-2 duration-200">
            <p className="text-sm text-gray-500 mb-2">
                Provide a JSON schema to enforce specific output structure. 
            </p>
            <textarea
                value={template}
                onChange={(e) => setTemplate(e.target.value)}
                placeholder='e.g. { "name": "string", "dob": "date", "items": [{"name": "string", "price": "number"}] }'
                className="w-full h-32 p-3 text-sm font-mono border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-y text-gray-900"
            />
        </div>
      )}
    </div>
  );
}
