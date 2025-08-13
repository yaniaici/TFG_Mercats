import React, { useEffect, useRef } from 'react';
import QRCode from 'qrcode';
import { X, Download, Copy, CheckCircle } from 'lucide-react';

interface QRModalProps {
  isOpen: boolean;
  onClose: () => void;
  redemptionCode: string;
  rewardName: string;
  rewardDescription: string;
  pointsSpent: number;
  expiresAt: string;
}

const QRModal: React.FC<QRModalProps> = ({
  isOpen,
  onClose,
  redemptionCode,
  rewardName,
  rewardDescription,
  pointsSpent,
  expiresAt
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [copied, setCopied] = React.useState(false);

  useEffect(() => {
    if (isOpen && canvasRef.current) {
      // Generar URL de validación
      const validationUrl = `${window.location.origin}/validate-reward/${redemptionCode}`;
      
      // Generar QR code
      QRCode.toCanvas(canvasRef.current, validationUrl, {
        width: 256,
        margin: 2,
        color: {
          dark: '#1f2937',
          light: '#ffffff'
        }
      }, (error) => {
        if (error) {
          console.error('Error generant QR:', error);
        }
      });
    }
  }, [isOpen, redemptionCode]);

  const handleCopyCode = async () => {
    try {
      await navigator.clipboard.writeText(redemptionCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Error copiant codi:', err);
    }
  };

  const handleDownloadQR = () => {
    if (canvasRef.current) {
      const link = document.createElement('a');
      link.download = `qr-recompensa-${redemptionCode}.png`;
      link.href = canvasRef.current.toDataURL();
      link.click();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold text-gray-900">Recompensa Canviada</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* QR Code */}
        <div className="flex justify-center mb-6">
          <div className="bg-gray-50 p-4 rounded-xl">
            <canvas ref={canvasRef} className="rounded-lg" />
          </div>
        </div>

        {/* Reward Info */}
        <div className="mb-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-2">{rewardName}</h4>
          <p className="text-gray-600 text-sm mb-3">{rewardDescription}</p>
          
          <div className="bg-gradient-to-r from-green-50 to-blue-50 p-4 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Codi de Canvi:</span>
              <button
                onClick={handleCopyCode}
                className="flex items-center space-x-1 text-blue-600 hover:text-blue-700 transition-colors"
              >
                {copied ? (
                  <>
                    <CheckCircle className="h-4 w-4" />
                    <span className="text-xs">Copiat!</span>
                  </>
                ) : (
                  <>
                    <Copy className="h-4 w-4" />
                    <span className="text-xs">Copiar</span>
                  </>
                )}
              </button>
            </div>
            <div className="font-mono text-lg font-bold text-gray-900 bg-white px-3 py-2 rounded border">
              {redemptionCode}
            </div>
          </div>
        </div>

        {/* Details */}
        <div className="space-y-3 mb-6">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Punts gastats:</span>
            <span className="font-semibold text-red-600">{pointsSpent} punts</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Caduca:</span>
            <span className="font-semibold text-gray-900">
              {new Date(expiresAt).toLocaleDateString('ca-ES')}
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex space-x-3">
          <button
            onClick={handleDownloadQR}
            className="flex-1 flex items-center justify-center space-x-2 bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Download className="h-4 w-4" />
            <span>Descarregar QR</span>
          </button>
          <button
            onClick={onClose}
            className="flex-1 bg-gray-100 text-gray-700 py-3 px-4 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Tancar
          </button>
        </div>

        {/* Instructions */}
        <div className="mt-4 p-3 bg-yellow-50 rounded-lg">
          <p className="text-xs text-yellow-800">
            <strong>Com utilitzar:</strong> Mostra aquest QR al comerç per validar la teva recompensa. 
            El codi també es pot introduir manualment si cal.
          </p>
        </div>
      </div>
    </div>
  );
};

export default QRModal;
