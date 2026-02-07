
"use client";
import { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';
import UploadArea from '@/components/UploadArea';
import { submitPipelineJob, getPipelineResult } from '@/lib/api';
import { Zap, Activity, CheckCircle, Clock } from 'lucide-react';

export default function PipelinePage() {
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [result, setResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [schema, setSchema] = useState<string>('');

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (jobId && status !== 'completed') {
      interval = setInterval(async () => {
        try {
          const data = await getPipelineResult(jobId);
          if (data.status === 'completed') {
            setStatus('completed');
            setResult(data.result);
            clearInterval(interval);
          } else {
            setStatus('processing');
          }
        } catch (err) {
          console.error("Polling error", err);
          setError("Failed to fetch status");
          clearInterval(interval);
        }
      }, 2000);
    }

    return () => clearInterval(interval);
  }, [jobId, status]);

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile);
    resetState();
  };

  const resetState = () => {
    setJobId(null);
    setStatus(null);
    setResult(null);
    setError(null);
  };

  const NID_SCHEMA = JSON.stringify({
    "name": "Full Name in English",
    "name_bn": "Full Name in Bangla",
    "father_name": "Father's Name",
    "mother_name": "Mother's Name",
    "dob": "Date of Birth (YYYY-MM-DD)",
    "nid_no": "NID Number (10, 13, or 17 digits)"
  }, null, 2);

  const NID_BACK_SCHEMA = JSON.stringify({
    "address_bn": "Address in Bangla (Thikana)",
    "blood_group": "Blood Group",
    "place_of_birth": "Place of Birth",
    "issue_date": "Issue Date",
    "mrz_line1": "MRZ Line 1",
    "mrz_line2": "MRZ Line 2",
    "mrz_line3": "MRZ Line 3"
  }, null, 2);

  const handleSubmit = async () => {
    if (!file) return;
    resetState();
    
    try {
      const response = await submitPipelineJob(file, schema || undefined);
      setJobId(response.job_id);
      setStatus(response.status);
    } catch (err: any) {
        console.error(err);
        setError("Failed to submit job");
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 pb-20">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Bank-Grade Pipeline</h1>
            <p className="text-gray-700 mt-1">Reliable, Traceable, Scalable OCR Processing</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Input Section */}
            <div className="flex flex-col gap-6">
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
                    <h2 className="text-lg font-semibold text-black mb-4 flex items-center gap-2">
                        <Zap className="w-5 h-5 text-blue-500" />
                        Input Image
                    </h2>
                    <UploadArea 
                        onFileSelect={handleFileSelect} 
                        selectedFile={file} 
                        onClear={() => setFile(null)}
                        isScanning={!!jobId && status !== 'completed'}
                    />
                    
                    <div className="mt-4">
                        <div className="flex justify-between items-center mb-1">
                            <label className="block text-sm font-medium text-black">
                                Schema (JSON, optional)
                            </label>
                            <div className="flex gap-2">
                                <button 
                                    onClick={() => setSchema(NID_SCHEMA)}
                                    className="text-xs bg-gray-100 hover:bg-gray-200 text-black px-2 py-1 rounded transition-colors"
                                >
                                    Load NID Front
                                </button>
                                <button 
                                    onClick={() => setSchema(NID_BACK_SCHEMA)}
                                    className="text-xs bg-gray-100 hover:bg-gray-200 text-black px-2 py-1 rounded transition-colors"
                                >
                                    Load NID Back
                                </button>
                            </div>
                        </div>
                        <textarea 
                            className="w-full h-32 p-3 border border-gray-300 rounded-lg font-mono text-sm text-gray-900"
                            placeholder='{"field": "description"}'
                            value={schema}
                            onChange={(e) => setSchema(e.target.value)}
                        />
                    </div>

                    <button
                        onClick={handleSubmit}
                        disabled={!file || (!!jobId && status !== 'completed')}
                        className={`mt-4 w-full py-3 px-4 rounded-lg text-white font-medium flex items-center justify-center gap-2 transition-colors ${
                            !file || (!!jobId && status !== 'completed')
                            ? 'bg-gray-300 cursor-not-allowed' 
                            : 'bg-blue-600 hover:bg-blue-700'
                        }`}
                    >
                        {jobId && status !== 'completed' ? 'Processing...' : (jobId ? 'Start Again' : 'Start Pipeline')}
                    </button>
                </div>
            </div>

            {/* Status & Results */}
            <div className="flex flex-col gap-6">
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 min-h-[400px]">
                    <h2 className="text-lg font-semibold text-black mb-4 flex items-center gap-2">
                        <Activity className="w-5 h-5 text-purple-500" />
                        Pipeline Status
                    </h2>

                    {jobId && (
                        <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-100 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                {status === 'completed' ? (
                                    <CheckCircle className="w-5 h-5 text-green-500" />
                                ) : (
                                    <Clock className="w-5 h-5 text-blue-500 animate-pulse" />
                                )}
                                <div>
                                    <div className="font-medium text-gray-900">Job ID: {jobId}</div>
                                    <div className="text-sm text-gray-500 capitalize">{status}</div>
                                </div>
                            </div>
                        </div>
                    )}

                    {error && (
                        <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-100 mb-4">
                            {error}
                        </div>
                    )}

                    {result && (
                        <div className="prose max-w-none">
                            <h3 className="text-md font-medium text-black mb-2">Extraction Result</h3>
                            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-auto max-h-[500px] text-sm font-mono">
                                {JSON.stringify(result, null, 2)}
                            </pre>
                        </div>
                    )}

                    {!jobId && !result && (
                        <div className="flex flex-col items-center justify-center h-64 text-gray-400">
                            <Activity className="w-12 h-12 mb-2 opacity-20" />
                            <p>Ready to process</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
      </div>
    </main>
  );
}
