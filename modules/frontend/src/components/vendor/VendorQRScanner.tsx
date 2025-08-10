import React, { useEffect, useRef, useState, useCallback } from 'react';
import Webcam from 'react-webcam';
import jsQR from 'jsqr';
import { Upload, Camera } from 'lucide-react';

interface Props {
  onDetected: (text: string) => void;
}

const VendorQRScanner: React.FC<Props> = ({ onDetected }) => {
  const webcamRef = useRef<Webcam>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [showCamera, setShowCamera] = useState(true);

  const videoConstraints = {
    width: { ideal: 1280 },
    height: { ideal: 720 },
    facingMode: 'environment'
  } as const;

  const scanFrame = useCallback(() => {
    const video = webcamRef.current?.video as HTMLVideoElement | undefined;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;
    const width = video.videoWidth;
    const height = video.videoHeight;
    if (!width || !height) return;

    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.drawImage(video, 0, 0, width, height);
    const imageData = ctx.getImageData(0, 0, width, height);
    const code = jsQR(imageData.data, width, height);
    if (code?.data) {
      onDetected(code.data);
    }
  }, [onDetected]);

  useEffect(() => {
    if (!showCamera) return;
    const interval = setInterval(scanFrame, 500);
    return () => clearInterval(interval);
  }, [showCamera, scanFrame]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const img = new Image();
    img.onload = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const code = jsQR(imageData.data, canvas.width, canvas.height);
      if (code?.data) onDetected(code.data);
    };
    img.src = URL.createObjectURL(file);
  };

  return (
    <div className="space-y-4">
      {showCamera && (
        <div className="relative">
          <Webcam
            ref={webcamRef}
            audio={false}
            screenshotFormat="image/jpeg"
            videoConstraints={videoConstraints}
            className="w-full rounded-lg shadow"
          />
          <div className="absolute inset-0 border-4 border-primary-500 border-dashed rounded-lg pointer-events-none"></div>
        </div>
      )}
      <canvas ref={canvasRef} className="hidden" />
      <div className="flex gap-3">
        <button onClick={() => setShowCamera((v) => !v)} className="btn-market bg-market-600 text-white px-4 py-2 rounded-lg flex items-center gap-2">
          <Camera className="h-4 w-4" />
          {showCamera ? 'Aturar càmera' : 'Engegar càmera'}
        </button>
        <label className="btn-market bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 cursor-pointer">
          <Upload className="h-4 w-4" />
          Pujar Imatge (Debug)
          <input type="file" accept="image/*" className="hidden" onChange={handleFileUpload} />
        </label>
      </div>
    </div>
  );
};

export default VendorQRScanner;


