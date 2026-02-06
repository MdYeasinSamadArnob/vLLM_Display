"use client";
import { useState, useCallback } from 'react';
import { Upload, FileImage, X } from 'lucide-react';
import { clsx } from 'clsx';
import ScanningAnimation from './ScanningAnimation';

interface UploadAreaProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
  onClear: () => void;
  isScanning?: boolean;
}

export default function UploadArea({ onFileSelect, selectedFile, onClear, isScanning = false }: UploadAreaProps) {
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
      <div className="relative w-full h-96 bg-gray-900 rounded-xl border border-gray-700 flex flex-col items-center justify-center overflow-hidden shadow-inner">
        <ScanningAnimation 
            imageUrl={URL.createObjectURL(selectedFile)} 
            isScanning={isScanning} 
        />
        
        {/* Top Bar with Filename and Clear Button */}
        <div className="absolute top-0 left-0 right-0 p-4 flex justify-between items-start z-[60] pointer-events-none">
           <div className="bg-black/50 backdrop-blur-md px-3 py-1.5 rounded-lg flex items-center gap-2 border border-white/10">
             <FileImage className="w-4 h-4 text-blue-400" />
             <span className="text-sm font-medium text-gray-200">{selectedFile.name}</span>
           </div>
           
           <button 
             onClick={onClear}
             className="pointer-events-auto p-2 bg-black/50 hover:bg-red-500/80 text-white rounded-full backdrop-blur-md transition-colors border border-white/10"
             title="Remove image"
           >
             <X className="w-4 h-4" />
           </button>
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
