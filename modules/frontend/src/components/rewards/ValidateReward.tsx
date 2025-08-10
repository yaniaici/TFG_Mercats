import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { gamificationService } from '../../services/gamificationService';
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertTriangle,
  ArrowLeft,
  QrCode,
  Copy,
  Loader
} from 'lucide-react';

const ValidateReward: React.FC = () => {
  const { redemptionCode } = useParams<{ redemptionCode: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [validating, setValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<{
    valid: boolean;
    message: string;
    rewardName?: string;
    rewardDescription?: string;
    usedAt?: string;
    expiresAt?: string;
  } | null>(null);

  useEffect(() => {
    if (redemptionCode) {
      validateRedemption(redemptionCode);
    }
  }, [redemptionCode]);

  const validateRedemption = async (code: string) => {
    try {
      setLoading(true);
      setValidating(true);
      const res = await gamificationService.validateRedemption(code);
      setValidationResult(res);
    } catch (error: any) {
      setValidationResult({ valid: false, message: error.message || 'Error validant la recompensa' });
    } finally {
      setLoading(false);
      setValidating(false);
    }
  };

  const handleUseReward = async () => {
    if (!redemptionCode) return;
    
    try {
      setValidating(true);
      const res = await gamificationService.useRedemption(redemptionCode);
      setValidationResult(prev => prev ? { ...prev, valid: false, message: 'Recompensa utilitzada correctament', usedAt: res.used_at } : null);
      
    } catch (error) {
      setValidationResult({
        valid: false,
        message: "Error utilitzant la recompensa"
      });
    } finally {
      setValidating(false);
    }
  };

  const handleCopyCode = async () => {
    if (redemptionCode) {
      try {
        await navigator.clipboard.writeText(redemptionCode);
        // Mostrar feedback
      } catch (err) {
        console.error('Error copiando código:', err);
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-sea-50 via-white to-olive-50 flex items-center justify-center">
        <div className="text-center">
          <Loader className="h-12 w-12 text-market-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Validant recompensa...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-sea-50 via-white to-olive-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/vendor/dashboard')}
              className="text-gray-600 hover:text-market-600 transition-colors"
            >
              <ArrowLeft className="h-6 w-6" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Validació de Recompensa</h1>
              <p className="text-gray-600">Verifica l'estat de la teva recompensa</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-2xl shadow-lg p-8">
          {/* QR Code Display */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-market-100 to-market-200 rounded-full mb-4">
              <QrCode className="h-12 w-12 text-market-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Codi de Recompensa</h2>
            <div className="flex items-center justify-center space-x-2">
              <code className="font-mono text-lg bg-gray-100 px-4 py-2 rounded-lg">
                {redemptionCode}
              </code>
              <button
                onClick={handleCopyCode}
                className="text-market-600 hover:text-market-700 transition-colors"
              >
                <Copy className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Validation Result */}
          {validationResult && (
            <div className="space-y-6">
              {/* Status Card */}
              <div className={`p-6 rounded-xl border-2 ${
                validationResult.valid 
                  ? 'border-green-200 bg-green-50' 
                  : 'border-red-200 bg-red-50'
              }`}>
                <div className="flex items-center space-x-3 mb-4">
                  {validationResult.valid ? (
                    <CheckCircle className="h-8 w-8 text-green-600" />
                  ) : (
                    <XCircle className="h-8 w-8 text-red-600" />
                  )}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {validationResult.valid ? 'Recompensa Vàlida' : 'Recompensa No Vàlida'}
                    </h3>
                    <p className="text-gray-600">{validationResult.message}</p>
                  </div>
                </div>
              </div>

              {/* Reward Details */}
              {validationResult.rewardName && (
                <div className="bg-gray-50 p-6 rounded-xl">
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">
                    {validationResult.rewardName}
                  </h4>
                  <p className="text-gray-600 mb-4">
                    {validationResult.rewardDescription}
                  </p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex items-center space-x-2">
                      <Clock className="h-5 w-5 text-gray-400" />
                      <div>
                        <p className="text-sm text-gray-500">Caduca</p>
                        <p className="font-medium text-gray-900">
                          {validationResult.expiresAt 
                            ? new Date(validationResult.expiresAt).toLocaleDateString('ca-ES')
                            : 'No caduca'
                          }
                        </p>
                      </div>
                    </div>
                    
                    {validationResult.usedAt && (
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="h-5 w-5 text-green-500" />
                        <div>
                          <p className="text-sm text-gray-500">Utilitzada</p>
                          <p className="font-medium text-gray-900">
                            {new Date(validationResult.usedAt).toLocaleDateString('ca-ES')}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex space-x-4">
                {validationResult.valid && !validationResult.usedAt && (
                  <button
                    onClick={handleUseReward}
                    disabled={validating}
                    className="flex-1 bg-market-600 text-white py-3 px-6 rounded-lg hover:bg-market-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                  >
                    {validating ? (
                      <>
                        <Loader className="h-5 w-5 animate-spin" />
                        <span>Utilitzant...</span>
                      </>
                    ) : (
                      <>
                        <CheckCircle className="h-5 w-5" />
                        <span>Utilitzar Recompensa</span>
                      </>
                    )}
                  </button>
                )}
                
                <button
                  onClick={() => navigate('/vendor/dashboard')}
                  className="flex-1 bg-gray-100 text-gray-700 py-3 px-6 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Tornar al panell de venedor
                </button>
              </div>
            </div>
          )}

          {/* Instructions */}
          <div className="mt-8 p-4 bg-blue-50 rounded-xl">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <h4 className="font-medium text-blue-900 mb-1">Com funciona la validació</h4>
                <p className="text-sm text-blue-800">
                  Aquesta pàgina permet als comerços verificar l'autenticitat de les recompenses. 
                  El QR conté un enllaç únic que valida que la recompensa no ha estat utilitzada i 
                  està dins del període de validesa.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ValidateReward;
