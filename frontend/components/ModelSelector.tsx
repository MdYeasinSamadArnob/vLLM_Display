"use client";
import { useEffect, useState } from 'react';
import { fetchModels, setActiveModel, Model } from '../lib/api';
import { ChevronDown, Cpu } from 'lucide-react';

export default function ModelSelector({ onModelChange }: { onModelChange?: (model: string) => void }) {
  const [models, setModels] = useState<Model[]>([]);
  const [selected, setSelected] = useState<string>('');
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      const data = await fetchModels();
      setModels(data);
      const active = data.find(m => m.active);
      if (active) setSelected(active.name);
      else if (data.length > 0) setSelected(data[0].name);
    } catch (err) {
      console.error("Failed to load models", err);
    }
  };

  const handleSelect = async (name: string) => {
    setSelected(name);
    setIsOpen(false);
    try {
      await setActiveModel(name);
      if (onModelChange) onModelChange(name);
    } catch (err) {
      console.error("Failed to set model", err);
    }
  };

  return (
    <div className="relative">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg shadow-sm hover:bg-gray-50 transition-colors"
      >
        <Cpu className="w-4 h-4 text-blue-600" />
        <span className="font-medium text-gray-700">{selected || "Select Model"}</span>
        <ChevronDown className="w-4 h-4 text-gray-400" />
      </button>

      {isOpen && (
        <div className="absolute top-full right-0 mt-2 w-64 bg-white border border-gray-200 rounded-lg shadow-xl z-50 overflow-hidden">
          <div className="p-2 bg-gray-50 border-b border-gray-100 text-xs font-semibold text-gray-500 uppercase tracking-wider">
            Available Models
          </div>
          {models.map((model) => (
            <button
              key={model.name}
              onClick={() => handleSelect(model.name)}
              className="w-full text-left px-4 py-3 hover:bg-blue-50 transition-colors flex items-center justify-between group"
            >
              <div>
                <div className="font-medium text-gray-800 group-hover:text-blue-700">{model.name}</div>
                <div className="text-xs text-gray-500">{model.provider}</div>
              </div>
              {model.name === selected && (
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              )}
            </button>
          ))}
          <div className="p-2 border-t border-gray-100 bg-gray-50 text-center">
            <button className="text-xs text-blue-600 hover:underline">
              + Add New Model (HuggingFace)
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
