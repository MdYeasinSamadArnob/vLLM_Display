import Link from 'next/link';
import { Activity, FileText, BarChart } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <FileText className="w-8 h-8 text-blue-600" />
        <span className="text-xl font-bold text-gray-800">VLLM-OCR Pro</span>
      </div>
      <div className="flex gap-6">
        <Link href="/" className="flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors">
          <Activity className="w-4 h-4" />
          <span>Scanner</span>
        </Link>
        <Link href="/benchmark" className="flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors">
          <BarChart className="w-4 h-4" />
          <span>Benchmarks</span>
        </Link>
      </div>
    </nav>
  );
}
