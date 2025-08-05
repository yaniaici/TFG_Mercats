import React, { useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import Webcam from 'react-webcam';
import axios from 'axios';
import { 
  Camera, 
  X, 
  ArrowLeft, 
  AlertCircle,
  CheckCircle,
  Loader,
  Receipt,
  Upload
} from 'lucide-react';

const CreateTicket: React.FC = () => {
  const [image, setImage] = useState<string | null>(null);
  const [showCamera, setShowCamera] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  
  const webcamRef = useRef<Webcam>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const videoConstraints = {
    width: { ideal: 1280 },
    height: { ideal: 720 },
    facingMode: "environment" // Usar cámara trasera en móviles
  };

  const capture = useCallback(() => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      setImage(imageSrc);
      setShowCamera(false);
    }
  }, [webcamRef]);

  const retakePhoto = () => {
    setImage(null);
    setShowCamera(true);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setImage(e.target?.result as string);
        setShowCamera(false);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async () => {
    if (!image) {
      setError('Si us plau, escaneja el tiquet primer');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Convertir base64 a blob
      const base64Data = image.split(',')[1];
      const blob = await fetch(`data:image/jpeg;base64,${base64Data}`).then(res => res.blob());
      
      const formData = new FormData();
      formData.append('file', blob, 'tiquet-compra.jpg');

      await axios.post('/tickets/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setSuccess(true);
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al enviar el tiquet');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="card text-center max-w-md">
          <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            ¡Tiquet Enviat!
          </h2>
          <p className="text-gray-600 mb-4">
            El teu tiquet de compra ha estat enviat amb èxit. La IA està processant la informació.
          </p>
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16">
            <button
              onClick={() => navigate('/dashboard')}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
              <span>Tornar</span>
            </button>
            <h1 className="ml-6 text-xl font-semibold text-gray-900">
              Escanejar Tiquet de Compra
            </h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-2">
            <AlertCircle className="h-5 w-5 text-red-400" />
            <span className="text-red-800 text-sm">{error}</span>
          </div>
        )}

        <div className="card">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Escaneja el teu tiquet
            </h2>
            <p className="text-gray-600">
              Posiciona el tiquet de compra davant la càmera per escanejar-lo automàticament
            </p>
          </div>

          {showCamera ? (
            <div className="space-y-6">
              <div className="relative">
                <Webcam
                  ref={webcamRef}
                  audio={false}
                  screenshotFormat="image/jpeg"
                  videoConstraints={videoConstraints}
                  className="w-full rounded-lg shadow-lg"
                />
                <div className="absolute inset-0 border-4 border-primary-500 border-dashed rounded-lg pointer-events-none"></div>
              </div>
              
              <div className="flex justify-center space-x-4">
                <button
                  onClick={() => navigate('/dashboard')}
                  className="btn-secondary"
                >
                  Cancel·lar
                </button>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="btn-secondary flex items-center space-x-2"
                >
                  <Upload className="h-4 w-4" />
                  <span>Pujar Foto (Debug)</span>
                </button>
                <button
                  onClick={capture}
                  className="btn-primary flex items-center space-x-2"
                >
                  <Camera className="h-4 w-4" />
                  <span>Capturar Tiquet</span>
                </button>
              </div>
              
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                className="hidden"
              />
            </div>
          ) : (
            <div className="space-y-6">
              <div className="relative">
                <img
                  src={image || ''}
                  alt="Tiquet capturat"
                  className="w-full rounded-lg shadow-lg"
                />
                <button
                  onClick={retakePhoto}
                  className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
              
              <div className="text-center">
                <p className="text-gray-600 mb-4">
                  La IA processarà automàticament la informació del tiquet
                </p>
              </div>
              
              <div className="flex justify-center space-x-4">
                <button
                  onClick={retakePhoto}
                  className="btn-secondary"
                >
                  Tornar a Capturar
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={loading}
                  className="btn-primary flex items-center space-x-2"
                >
                  {loading ? (
                    <>
                      <Loader className="h-4 w-4 animate-spin" />
                      <span>Enviant...</span>
                    </>
                  ) : (
                    <>
                      <Receipt className="h-4 w-4" />
                      <span>Enviar Tiquet</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default CreateTicket; 