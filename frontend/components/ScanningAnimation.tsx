"use client";
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';

interface ScanningAnimationProps {
  imageUrl: string;
  isScanning: boolean;
  polygons?: { x: number, y: number, w: number, h: number }[]; // Normalized coordinates 0-1
}

export default function ScanningAnimation({ imageUrl, isScanning, polygons }: ScanningAnimationProps) {
  // Mock polygons for visual effect if none provided
  const [mockPolygons, setMockPolygons] = useState<any[]>([]);
  const [scale, setScale] = useState(1);

  const handleZoomIn = () => setScale(s => Math.min(s + 0.5, 4));
  const handleZoomOut = () => setScale(s => Math.max(s - 0.5, 1));
  const handleReset = () => setScale(1);

  useEffect(() => {
    if (isScanning && (!polygons || polygons.length === 0)) {
        // Generate random boxes to simulate "detecting"
        const boxes = Array.from({ length: 8 }).map(() => ({
            x: Math.random() * 80 + 10,
            y: Math.random() * 80 + 10,
            w: Math.random() * 20 + 5,
            h: Math.random() * 5 + 2
        }));
        setMockPolygons(boxes);
    }
  }, [isScanning, polygons]);

  const displayPolygons = polygons?.length ? polygons : mockPolygons;

  return (
    <div className="relative w-full h-full bg-black rounded-xl overflow-hidden shadow-2xl group">
      <div 
        className="w-full h-full transition-transform duration-200 ease-out origin-center flex items-center justify-center"
        style={{ transform: `scale(${scale})` }}
      >
        <img 
            src={imageUrl} 
            alt="Scanning" 
            className="max-w-full max-h-full object-contain opacity-80"
        />
        
        {/* Scanning Overlay - Scaled with image */}
        {isScanning && (
            <div className="absolute inset-0 pointer-events-none">
                {/* ... existing overlay content ... */}
                {/* Grid Overlay */}
                <div className="absolute inset-0 bg-[linear-gradient(rgba(0,255,0,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(0,255,0,0.1)_1px,transparent_1px)] bg-[size:20px_20px] opacity-20"></div>
                
                {/* Moving Scan Line */}
                <motion.div
                    className="absolute left-0 right-0 h-1 bg-blue-500 shadow-[0_0_20px_rgba(59,130,246,0.8)] z-10"
                    initial={{ top: "0%" }}
                    animate={{ top: ["0%", "100%", "0%"] }}
                    transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                />
                
                {/* Radar Sweep Effect */}
                <motion.div 
                    className="absolute inset-0 bg-gradient-to-b from-blue-500/10 to-transparent z-0"
                    initial={{ top: "-100%" }}
                    animate={{ top: ["-100%", "100%"] }}
                    transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                />
                
                {/* Detected Polygons */}
                {displayPolygons.map((box, i) => (
                    <motion.div
                        key={i}
                        className="absolute border border-blue-400 bg-blue-400/20"
                        style={{
                            left: `${box.x}%`,
                            top: `${box.y}%`,
                            width: `${box.w}%`,
                            height: `${box.h}%`,
                        }}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: [0, 1, 1, 0], scale: 1 }}
                        transition={{ 
                            duration: 2, 
                            delay: i * 0.2, 
                            repeat: Infinity,
                            repeatDelay: 1 
                        }}
                    />
                ))}
            </div>
        )}
      </div>

      {/* Zoom Controls */}
      <div className="absolute bottom-4 right-4 flex items-center gap-2 z-50">
        <button onClick={handleZoomOut} className="p-2 bg-black/50 hover:bg-black/70 text-white rounded-full backdrop-blur-sm transition-colors">
            <ZoomOut className="w-4 h-4" />
        </button>
        <button onClick={handleReset} className="px-3 py-1 bg-black/50 hover:bg-black/70 text-white rounded-full backdrop-blur-sm text-xs font-mono transition-colors">
            {Math.round(scale * 100)}%
        </button>
        <button onClick={handleZoomIn} className="p-2 bg-black/50 hover:bg-black/70 text-white rounded-full backdrop-blur-sm transition-colors">
            <ZoomIn className="w-4 h-4" />
        </button>
      </div>

      {isScanning && (
        <div className="absolute top-4 right-4 bg-black/70 px-3 py-1 rounded text-blue-400 font-mono text-sm border border-blue-500/30 animate-pulse z-50">
            SCANNING...
        </div>
      )}
    </div>
  );
}
