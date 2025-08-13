import React, { useEffect, useRef, useState } from 'react';
import QRCode from 'qrcode';
import { 
  QrCode, 
  Download, 
  Copy, 
  CheckCircle, 
  User, 
  X,
  Smartphone,
  Store,
  Info
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface ProfileQRProps {
  isOpen: boolean;
  onClose: () => void;
}

const ProfileQR: React.FC<ProfileQRProps> = ({ isOpen, onClose }) => {
  const { user } = useAuth();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (isOpen && canvasRef.current && user?.id) {
      // Generar URL del perfil para recibir tickets digitales
      const profileUrl = `${window.location.origin}/send-ticket/${user.id}`;
      
      // Generar QR code
      QRCode.toCanvas(canvasRef.current, profileUrl, {
        width: 200, // Reducido de 256 a 200
        margin: 2,
        color: {
          dark: '#1f2937',
          light: '#ffffff'
        }
      }, (error) => {
        if (error) {
          console.error('Error generant QR del perfil:', error);
        }
      });
    }
  }, [isOpen, user?.id]);

  const handleCopyProfileUrl = async () => {
    if (user?.id) {
      const profileUrl = `${window.location.origin}/send-ticket/${user.id}`;
      try {
        await navigator.clipboard.writeText(profileUrl);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch (err) {
        console.error('Error copiant URL del perfil:', err);
      }
    }
  };

  const handleDownloadQR = () => {
    if (canvasRef.current) {
      const link = document.createElement('a');
      link.download = `qr-perfil-${user?.email?.split('@')[0] || 'usuari'}.png`;
      link.href = canvasRef.current.toDataURL();
      link.click();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-sm w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-4 border-b border-gray-200">
          <h3 className="text-lg font-bold text-gray-900">QR del Teu Perfil</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* User Info */}
          <div className="bg-gradient-to-r from-market-50 to-olive-50 p-3 rounded-xl">
            <div className="flex items-center space-x-3">
              <div className="h-10 w-10 bg-market-500 rounded-full flex items-center justify-center">
                <User className="h-5 w-5 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <h4 className="font-semibold text-gray-900 truncate">
                  {user?.email || 'Usuari'}
                </h4>
                <p className="text-xs text-gray-600">Perfil per rebre tickets digitals</p>
              </div>
            </div>
          </div>

          {/* QR Code */}
          <div className="flex justify-center">
            <div className="bg-gray-50 p-3 rounded-xl">
              <canvas ref={canvasRef} className="rounded-lg" />
            </div>
          </div>

          {/* Profile URL */}
          <div className="bg-gradient-to-r from-blue-50 to-green-50 p-3 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs font-medium text-gray-700">Enllaç del Perfil:</span>
              <button
                onClick={handleCopyProfileUrl}
                className="flex items-center space-x-1 text-blue-600 hover:text-blue-700 transition-colors"
              >
                {copied ? (
                  <>
                    <CheckCircle className="h-3 w-3" />
                    <span className="text-xs">Copiat!</span>
                  </>
                ) : (
                  <>
                    <Copy className="h-3 w-3" />
                    <span className="text-xs">Copiar</span>
                  </>
                )}
              </button>
            </div>
            <div className="font-mono text-xs text-gray-900 bg-white px-2 py-1 rounded border break-all">
              {user?.id ? `${window.location.origin}/send-ticket/${user.id}` : 'Carregant...'}
            </div>
          </div>

          {/* Instructions */}
          <div className="space-y-2">
            <div className="flex items-start space-x-2 p-2 bg-yellow-50 rounded-lg">
              <Smartphone className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
              <div>
                <h5 className="font-medium text-yellow-900 mb-1 text-sm">Com funciona</h5>
                <p className="text-xs text-yellow-800">
                  Mostra aquest QR al venedor perquè pugui enviar-te tickets digitals directament al teu perfil.
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-2 p-2 bg-green-50 rounded-lg">
              <Store className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
              <div>
                <h5 className="font-medium text-green-900 mb-1 text-sm">Avantatges</h5>
                <p className="text-xs text-green-800">
                  Els tickets digitals s'afegeixen automàticament al teu historial i pots consultar el contingut complet.
                </p>
              </div>
            </div>
          </div>

          {/* Debug Info */}
          <div className="p-2 bg-gray-50 rounded-lg">
            <div className="flex items-start space-x-2">
              <Info className="h-3 w-3 text-gray-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-xs text-gray-600">
                  <strong>Mode Debug:</strong> Els venedors poden utilitzar aquest QR per crear tickets digitals de prova.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Actions - Fixed at bottom */}
        <div className="p-4 border-t border-gray-200 flex space-x-3">
          <button
            onClick={handleDownloadQR}
            className="flex-1 flex items-center justify-center space-x-2 bg-market-600 text-white py-2 px-3 rounded-lg hover:bg-market-700 transition-colors text-sm"
          >
            <Download className="h-3 w-3" />
            <span>Descarregar QR</span>
          </button>
          <button
            onClick={onClose}
            className="flex-1 bg-gray-100 text-gray-700 py-2 px-3 rounded-lg hover:bg-gray-200 transition-colors text-sm"
          >
            Tancar
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProfileQR;
