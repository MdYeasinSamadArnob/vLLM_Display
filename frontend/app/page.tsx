"use client";
import { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';
import UploadArea from '@/components/UploadArea';
import ScanningAnimation from '@/components/ScanningAnimation';
import ResultsDisplay from '@/components/ResultsDisplay';
import ModelSelector from '@/components/ModelSelector';
import TemplateInput from '@/components/TemplateInput';
import { processImage, OCRResponse } from '@/lib/api';
import { Play, RotateCcw, Zap, FileText } from 'lucide-react';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [result, setResult] = useState<OCRResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [template, setTemplate] = useState<string>('');
  const [selectedModel, setSelectedModel] = useState<string | undefined>(undefined);
  const [startTime, setStartTime] = useState<number | null>(null);
  const [elapsedTime, setElapsedTime] = useState<number>(0);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isScanning && startTime) {
      interval = setInterval(() => {
        setElapsedTime(Date.now() - startTime);
      }, 100);
    }
    return () => clearInterval(interval);
  }, [isScanning, startTime]);

  const formatTime = (ms: number) => {
    if (ms < 1000) return '0s';
    const seconds = Math.floor(ms / 1000);
    if (seconds < 60) return `${(ms / 1000).toFixed(1)}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile);
    setResult(null);
    setError(null);
  };

  const handleScan = async () => {
    if (!file) return;

    setIsScanning(true);
    setStartTime(Date.now());
    setElapsedTime(0);
    setError(null);
    setResult(null);

    try {
      // Simulate minimum scanning time for the animation to show off
      const [apiResult] = await Promise.all([
        processImage(file, selectedModel, undefined, template),
        new Promise(resolve => setTimeout(resolve, 2000)) 
      ]);
      setResult(apiResult);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to process image");
      console.error(err);
    } finally {
      setIsScanning(false);
    }
  };

  const handleClear = () => {
    setFile(null);
    setResult(null);
    setError(null);
  };

  return (
    <main className="min-h-screen bg-gray-50 pb-20">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Intelligent Document Processing</h1>
            <p className="text-gray-500 mt-1">Extract text from images using state-of-the-art VLLM models.</p>
          </div>
          <div className="flex items-center gap-4">
             <ModelSelector onModelChange={setSelectedModel} />
          </div>
        </div>

        {/* Main Workspace */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:h-[calc(100vh-200px)] h-auto lg:overflow-hidden">
          
          {/* Left Panel: Input */}
          <div className="flex flex-col gap-6 h-full overflow-hidden">
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 flex-1 flex flex-col overflow-hidden">
              <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2 shrink-0">
                <Zap className="w-5 h-5 text-yellow-500" />
                Input Source
              </h2>
              
              <div className="flex-1 flex flex-col gap-4 overflow-hidden min-h-0">
                 {!file ? (
                    <UploadArea 
                        onFileSelect={handleFileSelect} 
                        selectedFile={null} 
                        onClear={handleClear} 
                    />
                 ) : (
                    <div className="flex-1 relative bg-black rounded-xl overflow-hidden flex flex-col min-h-0">
                        <ScanningAnimation 
                            imageUrl={URL.createObjectURL(file)} 
                            isScanning={isScanning} 
                            polygons={result?.bounding_boxes}
                        />
                    </div>
                 )}
              </div>

              <div className="shrink-0 mt-4">
                  <TemplateInput template={template} setTemplate={setTemplate} />
              </div>

              {/* Action Bar */}
              <div className="mt-6 flex justify-end items-center gap-3 shrink-0">
                 {elapsedTime > 0 && (
                    <span className="text-xs text-gray-400 font-mono mr-2">
                        {formatTime(elapsedTime)}
                    </span>
                 )}
                 {file && (
                    <button 
                        onClick={handleClear}
                        disabled={isScanning}
                        className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg font-medium transition-colors flex items-center gap-2"
                    >
                        <RotateCcw className="w-4 h-4" />
                        Reset
                    </button>
                 )}
                 <button 
                    onClick={handleScan}
                    disabled={!file || isScanning}
                    className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed text-white rounded-lg font-medium shadow-lg shadow-blue-500/30 transition-all flex items-center gap-2"
                 >
                    {isScanning ? (
                        <>Processing...</>
                    ) : (
                        <>
                           <Play className="w-4 h-4 fill-current" />
                           Start Extraction
                        </>
                    )}
                 </button>
              </div>
              
              {error && (
                <div className="mt-4 p-3 bg-red-50 text-red-600 text-sm rounded-lg border border-red-100">
                    {error}
                </div>
              )}
            </div>
          </div>

          {/* Right Panel: Output */}
          <div className="h-full">
            {result ? (
                <ResultsDisplay result={result} />
            ) : (
                <div className="h-full bg-white rounded-2xl shadow-sm border border-gray-200 p-8 flex flex-col items-center justify-center text-center">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                        <FileText className="w-8 h-8 text-gray-400" />
                    </div>
                    <h3 className="text-lg font-medium text-gray-900">No Results Yet</h3>
                    <p className="text-gray-500 max-w-xs mt-2">
                        Upload a document and click "Start Extraction" to see the magic happen.
                    </p>
                </div>
            )}
          </div>

        </div>
      </div>
    </main>
  );
}
