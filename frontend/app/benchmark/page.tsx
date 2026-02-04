"use client";
import Navbar from '@/components/Navbar';
import { useEffect, useState } from 'react';
import { fetchBenchmarks } from '@/lib/api';
import { BarChart, Activity, Zap, HardDrive } from 'lucide-react';

export default function BenchmarkPage() {
  const [benchmarks, setBenchmarks] = useState<any[]>([]);

  useEffect(() => {
    fetchBenchmarks().then(setBenchmarks);
  }, []);

  return (
    <main className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-10">
          <h1 className="text-3xl font-bold text-gray-900">Performance Benchmarks</h1>
          <p className="text-gray-500 mt-2">Real-time performance metrics of available VLLM models.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
           <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
             <div className="flex items-center gap-4 mb-4">
                <div className="p-3 bg-blue-100 rounded-lg text-blue-600">
                    <Activity className="w-6 h-6" />
                </div>
                <div>
                    <div className="text-sm text-gray-500">Avg Latency</div>
                    <div className="text-2xl font-bold text-gray-900">0.9s</div>
                </div>
             </div>
           </div>
           <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
             <div className="flex items-center gap-4 mb-4">
                <div className="p-3 bg-green-100 rounded-lg text-green-600">
                    <Zap className="w-6 h-6" />
                </div>
                <div>
                    <div className="text-sm text-gray-500">Throughput</div>
                    <div className="text-2xl font-bold text-gray-900">65/min</div>
                </div>
             </div>
           </div>
           <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
             <div className="flex items-center gap-4 mb-4">
                <div className="p-3 bg-purple-100 rounded-lg text-purple-600">
                    <BarChart className="w-6 h-6" />
                </div>
                <div>
                    <div className="text-sm text-gray-500">Accuracy</div>
                    <div className="text-2xl font-bold text-gray-900">98.2%</div>
                </div>
             </div>
           </div>
           <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
             <div className="flex items-center gap-4 mb-4">
                <div className="p-3 bg-orange-100 rounded-lg text-orange-600">
                    <HardDrive className="w-6 h-6" />
                </div>
                <div>
                    <div className="text-sm text-gray-500">VRAM Usage</div>
                    <div className="text-2xl font-bold text-gray-900">4.2 GB</div>
                </div>
             </div>
           </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
            <h3 className="font-semibold text-gray-800">Model Comparison</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
                <thead>
                    <tr className="border-b border-gray-100">
                        <th className="px-6 py-4 font-medium text-gray-500 text-sm">Model Name</th>
                        <th className="px-6 py-4 font-medium text-gray-500 text-sm">Accuracy</th>
                        <th className="px-6 py-4 font-medium text-gray-500 text-sm">Latency</th>
                        <th className="px-6 py-4 font-medium text-gray-500 text-sm">Throughput</th>
                        <th className="px-6 py-4 font-medium text-gray-500 text-sm">Memory</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                    {benchmarks.map((bench, i) => (
                        <tr key={i} className="hover:bg-gray-50 transition-colors">
                            <td className="px-6 py-4 font-medium text-gray-900">{bench.model}</td>
                            <td className="px-6 py-4 text-gray-600">
                                <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-semibold">
                                    {bench.accuracy}
                                </span>
                            </td>
                            <td className="px-6 py-4 text-gray-600">{bench.avg_latency}</td>
                            <td className="px-6 py-4 text-gray-600">{bench.throughput}</td>
                            <td className="px-6 py-4 text-gray-600">{bench.memory_usage}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>
  );
}
