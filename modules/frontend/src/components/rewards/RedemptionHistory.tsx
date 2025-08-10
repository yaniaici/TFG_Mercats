import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { gamificationService, RewardRedemption } from '../../services/gamificationService';
import { 
  ArrowLeft, 
  Clock, 
  CheckCircle, 
  XCircle,
  Copy,
  Car,
  Coffee,
  ShoppingBag,
  Gift,
  Star,
  Loader,
  Calendar
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const RedemptionHistory: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [redemptions, setRedemptions] = useState<RewardRedemption[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  useEffect(() => {
    loadRedemptions();
  }, []);

  const loadRedemptions = async () => {
    if (!user?.id) return;

    try {
      setLoading(true);
      const data = await gamificationService.getUserRedemptions(user.id);
      setRedemptions(data);
    } catch (err) {
      console.error('Error cargando historial:', err);
      setError('No se pudo cargar el historial de canjes');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (code: string) => {
    try {
      await navigator.clipboard.writeText(code);
      setCopiedCode(code);
      setTimeout(() => setCopiedCode(null), 2000);
    } catch (err) {
      console.error('Error copiando código:', err);
    }
  };

  const getRewardIcon = (rewardType: string) => {
    switch (rewardType) {
      case 'parking':
        return <Car className="h-5 w-5" />;
      case 'food':
        return <Coffee className="h-5 w-5" />;
      case 'discount':
        return <ShoppingBag className="h-5 w-5" />;
      case 'merchandise':
        return <Gift className="h-5 w-5" />;
      case 'experience':
        return <Star className="h-5 w-5" />;
      default:
        return <Gift className="h-5 w-5" />;
    }
  };

  const getRewardTypeColor = (rewardType: string) => {
    switch (rewardType) {
      case 'parking':
        return 'bg-blue-100 text-blue-600';
      case 'food':
        return 'bg-orange-100 text-orange-600';
      case 'discount':
        return 'bg-green-100 text-green-600';
      case 'merchandise':
        return 'bg-purple-100 text-purple-600';
      case 'experience':
        return 'bg-yellow-100 text-yellow-600';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ca-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const isExpired = (expiresAt?: string) => {
    if (!expiresAt) return false;
    return new Date(expiresAt) < new Date();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader className="h-8 w-8 animate-spin mx-auto mb-4 text-market-500" />
          <p className="text-gray-600">Carregant historial...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16">
            <button
              onClick={() => navigate('/dashboard')}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
              <span>Tornar</span>
            </button>
            <h1 className="ml-6 text-xl font-semibold text-gray-900">
              Historial de Canjes
            </h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-2">
            <XCircle className="h-5 w-5 text-red-400" />
            <span className="text-red-800 text-sm">{error}</span>
          </div>
        )}

        {/* Redemptions List */}
        <div className="space-y-4">
          {redemptions.map((redemption) => {
            const expired = isExpired(redemption.expires_at);
            const status = redemption.is_used 
              ? 'used' 
              : expired 
                ? 'expired' 
                : 'active';

            return (
              <div key={redemption.id} className="card">
                <div className="p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg ${getRewardTypeColor(redemption.reward_type)}`}>
                        {getRewardIcon(redemption.reward_type)}
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {redemption.reward_name}
                        </h3>
                        <p className="text-sm text-gray-600">
                          {redemption.reward_description}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center space-x-1 text-market-600 mb-1">
                        <span className="font-semibold">-{redemption.points_spent}</span>
                        <span className="text-xs">punts</span>
                      </div>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        status === 'used' 
                          ? 'bg-green-100 text-green-600'
                          : status === 'expired'
                            ? 'bg-red-100 text-red-600'
                            : 'bg-blue-100 text-blue-600'
                      }`}>
                        {status === 'used' ? 'Utilitzada' : status === 'expired' ? 'Expirada' : 'Activa'}
                      </span>
                    </div>
                  </div>

                  {/* Reward Details */}
                  <div className="bg-gray-50 rounded-lg p-3 mb-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">
                        {redemption.reward_value}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded-full ${getRewardTypeColor(redemption.reward_type)}`}>
                        {redemption.reward_type}
                      </span>
                    </div>
                  </div>

                  {/* Redemption Code */}
                  <div className="bg-market-50 border border-market-200 rounded-lg p-3 mb-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-market-800">Codi de canvi</p>
                        <p className="text-lg font-mono text-market-600">{redemption.redemption_code}</p>
                      </div>
                      {!redemption.is_used && !expired && (
                        <button
                          onClick={() => copyToClipboard(redemption.redemption_code)}
                          className="flex items-center space-x-1 text-market-600 hover:text-market-700 transition-colors"
                        >
                          <Copy className="h-4 w-4" />
                          <span className="text-sm">
                            {copiedCode === redemption.redemption_code ? 'Copiat!' : 'Copiar'}
                          </span>
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Dates */}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="flex items-center space-x-2">
                      <Calendar className="h-4 w-4 text-gray-400" />
                      <div>
                        <p className="text-gray-500">Canjeat el</p>
                        <p className="font-medium">{formatDate(redemption.created_at)}</p>
                      </div>
                    </div>
                    {redemption.expires_at && (
                      <div className="flex items-center space-x-2">
                        <Clock className="h-4 w-4 text-gray-400" />
                        <div>
                          <p className="text-gray-500">Expira el</p>
                          <p className={`font-medium ${expired ? 'text-red-600' : ''}`}>
                            {formatDate(redemption.expires_at)}
                          </p>
                        </div>
                      </div>
                    )}
                    {redemption.used_at && (
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-400" />
                        <div>
                          <p className="text-gray-500">Utilitzada el</p>
                          <p className="font-medium text-green-600">{formatDate(redemption.used_at)}</p>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Status Message */}
                  {status === 'expired' && (
                    <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-3">
                      <div className="flex items-center space-x-2">
                        <XCircle className="h-4 w-4 text-red-400" />
                        <span className="text-sm text-red-800">
                          Aquesta recompensa ha expirat i ja no es pot utilitzar.
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Empty State */}
        {redemptions.length === 0 && !loading && (
          <div className="text-center py-12">
            <Gift className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No tens canjes encara
            </h3>
            <p className="text-gray-600 mb-6">
              Quan canviïs recompenses, apareixeran aquí.
            </p>
            <button
              onClick={() => navigate('/rewards')}
              className="btn-market bg-market-500 hover:bg-market-600 text-white px-6 py-3 rounded-lg font-semibold"
            >
              Veure Recompenses
            </button>
          </div>
        )}
      </main>
    </div>
  );
};

export default RedemptionHistory;
