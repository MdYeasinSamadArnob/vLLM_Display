"use client";
import { useState, useCallback } from 'react';
import { Upload, FileImage, X } from 'lucide-react';
import { clsx } from 'clsx';

interface UploadAreaProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
  onClear: () => void;
}

export default function UploadArea({ onFileSelect, selectedFile, onClear }: UploadAreaProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  }, [onFileSelect]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0]);
    }
  }, [onFileSelect]);

  if (selectedFile) {
    return (
      <div className="relative w-full h-64 bg-gray-50 rounded-xl border-2 border-dashed border-blue-200 flex flex-col items-center justify-center overflow-hidden">
        <img 
          src={URL.createObjectURL(selectedFile)} 
          alt="Preview" 
          className="h-full w-full object-contain opacity-50"
        />
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/5">
           <div className="bg-white p-4 rounded-lg shadow-md flex items-center gap-3">
             <FileImage className="w-6 h-6 text-blue-600" />
             <span className="font-medium text-gray-700">{selectedFile.name}</span>
             <button 
               onClick={onClear}
               className="p-1 hover:bg-gray-100 rounded-full transition-colors"
             >
               <X className="w-4 h-4 text-gray-500" />
             </button>
           </div>
        </div>
      </div>
    );
  }

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={clsx(
        "w-full h-64 rounded-xl border-2 border-dashed transition-all duration-200 flex flex-col items-center justify-center cursor-pointer group",
        isDragging ? "border-blue-500 bg-blue-50" : "border-gray-300 bg-gray-50 hover:border-blue-400 hover:bg-gray-100"
      )}
    >
      <input 
        type="file" 
        accept="image/*" 
        className="hidden" 
        id="file-upload"
        onChange={handleChange}
      />
      <label htmlFor="file-upload" className="flex flex-col items-center cursor-pointer w-full h-full justify-center">
        <div className={clsx(
          "p-4 rounded-full mb-4 transition-colors",
          isDragging ? "bg-blue-100 text-blue-600" : "bg-white text-gray-400 group-hover:text-blue-500 group-hover:scale-110 transform duration-200 shadow-sm"
        )}>
          <Upload className="w-8 h-8" />
        </div>
        <p className="text-lg font-medium text-gray-700">
          {isDragging ? "Drop image here" : "Upload Document"}
        </p>
        <p className="text-sm text-gray-500 mt-2">
          Drag & drop or click to browse
        </p>
        <div className="mt-4 flex gap-2">
            <span className="text-xs px-2 py-1 bg-gray-200 rounded text-gray-600">JPG</span>
            <span className="text-xs px-2 py-1 bg-gray-200 rounded text-gray-600">PNG</span>
            <span className="text-xs px-2 py-1 bg-gray-200 rounded text-gray-600">WEBP</span>
        </div>
      </label>
    </div>
  );
}
