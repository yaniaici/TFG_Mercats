import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { gamificationService, Reward, GamificationStats, SpecialReward, SpecialRewardWithStatus } from '../../services/gamificationService';
import { 
  ArrowLeft, 
  Coins, 
  Clock, 
  CheckCircle, 
  XCircle,
  ShoppingBag,
  Car,
  Coffee,
  Gift,
  Star,
  AlertCircle,
  Loader,
  Sparkles
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import QRModal from './QRModal';

const RewardsPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [rewards, setRewards] = useState<Reward[]>([]);
  const [specialRewards, setSpecialRewards] = useState<SpecialRewardWithStatus[]>([]);
  const [userStats, setUserStats] = useState<GamificationStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [redeeming, setRedeeming] = useState<string | null>(null);
  const [redeemingSpecial, setRedeemingSpecial] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [qrModal, setQrModal] = useState<{
    isOpen: boolean;
    redemptionCode: string;
    rewardName: string;
    rewardDescription: string;
    pointsSpent: number;
    expiresAt: string;
  } | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    if (!user?.id) return;

    try {
      setLoading(true);
      const [rewardsData, specialRewardsData, statsData] = await Promise.all([
        gamificationService.getRewards(),
        gamificationService.getUserSpecialRewardsWithStatus(user.id),
        gamificationService.getUserStats(user.id)
      ]);
      setRewards(rewardsData);
      setSpecialRewards(specialRewardsData);
      setUserStats(statsData);
    } catch (err) {
      console.error('Error carregant dades:', err);
      setError('No es van poder carregar les recompenses');
    } finally {
      setLoading(false);
    }
  };

  const handleRedeem = async (reward: Reward) => {
    if (!user?.id) return;

    try {
      setRedeeming(reward.id);
      setError(null);
      setSuccess(null);

      const result = await gamificationService.redeemReward(user.id, reward.id);
      
      // Mostrar modal QR en lugar de mensaje de éxito
      setQrModal({
        isOpen: true,
        redemptionCode: result.redemption_code,
        rewardName: reward.name,
        rewardDescription: reward.description,
        pointsSpent: result.points_spent,
        expiresAt: result.expires_at
      });
      
      // Recargar estadísticas del usuario para actualizar puntos
      const newStats = await gamificationService.getUserStats(user.id);
      setUserStats(newStats);
      
      // Actualizar la recompensa en la lista
      setRewards(prev => prev.map(r => 
        r.id === reward.id 
          ? { ...r, current_redemptions: r.current_redemptions + 1 }
          : r
      ));

    } catch (err: any) {
      setError(err.message);
    } finally {
      setRedeeming(null);
    }
  };

  const handleRedeemSpecial = async (specialRewardWithStatus: SpecialRewardWithStatus) => {
    if (!user?.id) return;

    try {
      setRedeemingSpecial(specialRewardWithStatus.reward.id);
      setError(null);
      setSuccess(null);

      const result = await gamificationService.redeemSpecialReward(user.id, specialRewardWithStatus.reward.id);
      
      // Mostrar modal QR para recompensa especial
      setQrModal({
        isOpen: true,
        redemptionCode: result.redemption_code,
        rewardName: specialRewardWithStatus.reward.name,
        rewardDescription: specialRewardWithStatus.reward.description,
        pointsSpent: 0, // Las recompensas especiales no cuestan puntos
        expiresAt: '' // Las recompensas especiales no expiran por defecto
      });
      
      // Recargar recompensas especiales con estado
      const newSpecialRewards = await gamificationService.getUserSpecialRewardsWithStatus(user.id);
      setSpecialRewards(newSpecialRewards);

    } catch (err: any) {
      setError(err.message);
    } finally {
      setRedeemingSpecial(null);
    }
  };

  const getRewardIcon = (rewardType: string) => {
    switch (rewardType) {
      case 'parking':
        return <Car className="h-6 w-6" />;
      case 'food':
        return <Coffee className="h-6 w-6" />;
      case 'discount':
        return <ShoppingBag className="h-6 w-6" />;
      case 'merchandise':
        return <Gift className="h-6 w-6" />;
      case 'experience':
        return <Star className="h-6 w-6" />;
      default:
        return <Gift className="h-6 w-6" />;
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

  const getSpecialRewardTypeColor = (rewardType: string) => {
    switch (rewardType) {
      case 'parking':
        return 'bg-blue-200 text-blue-700';
      case 'food':
        return 'bg-orange-200 text-orange-700';
      case 'discount':
        return 'bg-green-200 text-green-700';
      case 'merchandise':
        return 'bg-purple-200 text-purple-700';
      case 'experience':
        return 'bg-yellow-200 text-yellow-700';
      default:
        return 'bg-gray-200 text-gray-700';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader className="h-8 w-8 animate-spin mx-auto mb-4 text-market-500" />
          <p className="text-gray-600">Carregant recompenses...</p>
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
              Recompenses
            </h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* User Points Section */}
        {userStats && (
          <div className="mb-8">
            <div className="card-market p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Coins className="h-8 w-8 text-market-500" />
                  <div>
                    <h2 className="text-2xl font-bold text-market-800">
                      {userStats.experience.toLocaleString()}
                    </h2>
                    <p className="text-market-600">punts disponibles</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600">Pots canviar</p>
                  <p className="text-lg font-semibold text-market-600">
                    {Math.floor(userStats.experience / 50)} recompenses
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error/Success Messages */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-2">
            <XCircle className="h-5 w-5 text-red-400" />
            <span className="text-red-800 text-sm">{error}</span>
          </div>
        )}

        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4 flex items-center space-x-2">
            <CheckCircle className="h-5 w-5 text-green-400" />
            <span className="text-green-800 text-sm">{success}</span>
          </div>
        )}

        {/* Special Rewards Section */}
        {specialRewards.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center space-x-2 mb-4">
              <Sparkles className="h-6 w-6 text-purple-500" />
              <h2 className="text-xl font-semibold text-gray-900">Recompenses Especials</h2>
              <span className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full">
                Gratuïtes
              </span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {specialRewards.map((rewardWithStatus) => {
                const reward = rewardWithStatus.reward;
                const isRedeemed = rewardWithStatus.is_redeemed;
                const canRedeem = rewardWithStatus.can_redeem;
                
                return (
                  <div key={reward.id} className={`card hover:shadow-lg transition-shadow border-2 ${
                    isRedeemed 
                      ? 'border-gray-300 bg-gradient-to-br from-gray-50 to-white' 
                      : 'border-purple-200 bg-gradient-to-br from-purple-50 to-white'
                  }`}>
                    <div className="p-6">
                      {/* Reward Header */}
                      <div className="flex items-start justify-between mb-4">
                        <div className={`p-2 rounded-lg ${getSpecialRewardTypeColor(reward.reward_type)}`}>
                          {getRewardIcon(reward.reward_type)}
                        </div>
                        <div className="text-right">
                          <div className="flex items-center space-x-1 text-purple-600">
                            <Sparkles className="h-4 w-4" />
                            <span className="font-semibold">Gratuïta</span>
                          </div>
                          <span className="text-xs text-gray-500">0 punts</span>
                        </div>
                      </div>

                      {/* Status Badge */}
                      {isRedeemed && (
                        <div className="mb-4">
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Ja canviada
                          </span>
                        </div>
                      )}

                      {/* Reward Info */}
                      <h3 className={`text-lg font-semibold mb-2 ${
                        isRedeemed ? 'text-gray-500' : 'text-gray-900'
                      }`}>
                        {reward.name}
                      </h3>
                      <p className={`text-sm mb-4 ${
                        isRedeemed ? 'text-gray-400' : 'text-gray-600'
                      }`}>
                        {reward.description}
                      </p>

                      {/* Reward Value */}
                      <div className={`rounded-lg p-3 mb-4 ${
                        isRedeemed ? 'bg-gray-50' : 'bg-purple-50'
                      }`}>
                        <div className="flex items-center justify-between">
                          <span className={`text-sm font-medium ${
                            isRedeemed ? 'text-gray-500' : 'text-gray-700'
                          }`}>
                            {reward.reward_value}
                          </span>
                          <span className={`text-xs px-2 py-1 rounded-full ${getSpecialRewardTypeColor(reward.reward_type)}`}>
                            {reward.reward_type}
                          </span>
                        </div>
                      </div>

                      {/* Special Badge */}
                      <div className="mb-4">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          isRedeemed 
                            ? 'bg-gray-100 text-gray-600' 
                            : 'bg-purple-100 text-purple-800'
                        }`}>
                          <Sparkles className="h-3 w-3 mr-1" />
                          Recompensa Especial
                        </span>
                      </div>

                      {/* Action Button */}
                      {canRedeem && !isRedeemed ? (
                        <button
                          onClick={() => handleRedeemSpecial(rewardWithStatus)}
                          disabled={redeemingSpecial === reward.id}
                          className="w-full py-3 px-4 rounded-lg font-semibold transition-all duration-200 bg-purple-500 hover:bg-purple-600 text-white shadow-lg hover:shadow-xl transform hover:scale-105 disabled:opacity-60 disabled:cursor-not-allowed"
                        >
                          {redeemingSpecial === reward.id ? (
                            <div className="flex items-center justify-center space-x-2">
                              <Loader className="h-4 w-4 animate-spin" />
                              <span>Canviant...</span>
                            </div>
                          ) : (
                            <div className="flex items-center justify-center space-x-2">
                              <Sparkles className="h-4 w-4" />
                              <span>Canviar Recompensa Especial</span>
                            </div>
                          )}
                        </button>
                      ) : isRedeemed ? (
                        <div className="w-full py-3 px-4 rounded-lg font-semibold bg-gray-200 text-gray-600 text-center">
                          <div className="flex items-center justify-center space-x-2">
                            <CheckCircle className="h-4 w-4" />
                            <span>Ja canviada</span>
                          </div>
                        </div>
                      ) : (
                        <div className="w-full py-3 px-4 rounded-lg font-semibold bg-red-100 text-red-600 text-center">
                          <div className="flex items-center justify-center space-x-2">
                            <XCircle className="h-4 w-4" />
                            <span>No disponible</span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Regular Rewards Section */}
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recompenses amb Punts</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {rewards.map((reward) => {
              const canAfford = userStats ? userStats.experience >= reward.points_cost : false;
              const isAvailable = reward.is_active && 
                (!reward.max_redemptions || reward.current_redemptions < reward.max_redemptions);

              return (
                <div key={reward.id} className="card hover:shadow-lg transition-shadow">
                  <div className="p-6">
                    {/* Reward Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className={`p-2 rounded-lg ${getRewardTypeColor(reward.reward_type)}`}>
                        {getRewardIcon(reward.reward_type)}
                      </div>
                      <div className="text-right">
                        <div className="flex items-center space-x-1 text-market-600">
                          <Coins className="h-4 w-4" />
                          <span className="font-semibold">{reward.points_cost}</span>
                        </div>
                        <span className="text-xs text-gray-500">punts</span>
                      </div>
                    </div>

                    {/* Reward Info */}
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {reward.name}
                    </h3>
                    <p className="text-gray-600 text-sm mb-4">
                      {reward.description}
                    </p>

                    {/* Reward Value */}
                    <div className="bg-gray-50 rounded-lg p-3 mb-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700">
                          {reward.reward_value}
                        </span>
                        <span className={`text-xs px-2 py-1 rounded-full ${getRewardTypeColor(reward.reward_type)}`}>
                          {reward.reward_type}
                        </span>
                      </div>
                    </div>

                    {/* Availability Info */}
                    {reward.max_redemptions && (
                      <div className="text-xs text-gray-500 mb-4">
                        {reward.current_redemptions} / {reward.max_redemptions} canjes disponibles
                      </div>
                    )}

                    {/* Action Button */}
                    <button
                      onClick={() => handleRedeem(reward)}
                      disabled={!canAfford || !isAvailable || redeeming === reward.id}
                      className={`w-full py-3 px-4 rounded-lg font-semibold transition-all duration-200 ${
                        canAfford && isAvailable
                          ? 'bg-market-500 hover:bg-market-600 text-white shadow-lg hover:shadow-xl transform hover:scale-105'
                          : 'bg-gray-200 text-gray-500 cursor-not-allowed'
                      }`}
                    >
                      {redeeming === reward.id ? (
                        <div className="flex items-center justify-center space-x-2">
                          <Loader className="h-4 w-4 animate-spin" />
                          <span>Canviant...</span>
                        </div>
                      ) : !canAfford ? (
                        <div className="flex items-center justify-center space-x-2">
                          <AlertCircle className="h-4 w-4" />
                          <span>Punts insuficients</span>
                        </div>
                      ) : !isAvailable ? (
                        <div className="flex items-center justify-center space-x-2">
                          <XCircle className="h-4 w-4" />
                          <span>No disponible</span>
                        </div>
                      ) : (
                        <div className="flex items-center justify-center space-x-2">
                          <Gift className="h-4 w-4" />
                          <span>Canviar Recompensa</span>
                        </div>
                      )}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Empty State */}
        {rewards.length === 0 && specialRewards.length === 0 && !loading && (
          <div className="text-center py-12">
            <Gift className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No hi ha recompenses disponibles
            </h3>
            <p className="text-gray-600">
              Torna més tard per veure noves recompenses.
            </p>
          </div>
        )}
      </main>

      {/* QR Modal */}
      {qrModal && (
        <QRModal
          isOpen={qrModal.isOpen}
          onClose={() => setQrModal(null)}
          redemptionCode={qrModal.redemptionCode}
          rewardName={qrModal.rewardName}
          rewardDescription={qrModal.rewardDescription}
          pointsSpent={qrModal.pointsSpent}
          expiresAt={qrModal.expiresAt}
        />
      )}
    </div>
  );
};

export default RewardsPage;
