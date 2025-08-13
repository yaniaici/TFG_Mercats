import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { gamificationService, GamificationStats } from '../../services/gamificationService';
import { 
  Plus, 
  LogOut, 
  User, 
  Receipt, 
  Camera,
  ShoppingBag,
  Calendar,
  Leaf,
  Zap,
  Coins,
  Gift,
  QrCode,
  History
} from 'lucide-react';
import TicketFeed from './TicketFeed';
import ProfileQR from '../profile/ProfileQR';

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [gamificationStats, setGamificationStats] = useState<GamificationStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showProfileQR, setShowProfileQR] = useState(false);

  const handleLogout = () => {
    logout();
  };

  // Cargar datos de gamificación
  useEffect(() => {
    const loadGamificationStats = async () => {
      if (!user?.id) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const stats = await gamificationService.getUserStats(user.id);
        setGamificationStats(stats);
        setError(null);
      } catch (err) {
        console.error('Error carregant estadístiques de gamificació:', err);
        setError('No es van poder carregar les estadístiques de gamificació');
      } finally {
        setLoading(false);
      }
    };

    loadGamificationStats();
  }, [user?.id]);

  // Datos de gamificación reales o por defecto
  const userStats = gamificationStats ? {
    experience: gamificationStats.experience,
    totalTickets: gamificationStats.total_tickets,
    validTickets: gamificationStats.valid_tickets,
    totalSpent: gamificationStats.total_spent,
    badges: gamificationStats.badges_earned,
    streak: gamificationStats.streak_days
  } : {
    experience: 0,
    totalTickets: 0,
    validTickets: 0,
    totalSpent: 0,
    badges: 0,
    streak: 0
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Fondo decorativo mediterráneo */}
      <div className="absolute inset-0 bg-gradient-to-br from-sea-50 via-white to-olive-50"></div>
      <div className="absolute top-20 right-10 w-40 h-40 bg-market-200 rounded-full opacity-10 floating"></div>
      <div className="absolute bottom-20 left-10 w-32 h-32 bg-olive-200 rounded-full opacity-10 floating" style={{animationDelay: '1s'}}></div>
      
      <div className="relative z-10">
        {/* Header mediterráneo */}
        <header className="bg-white/90 backdrop-blur-sm shadow-lg border-b border-white/20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16 sm:h-20">
              <div className="flex items-center space-x-2 sm:space-x-4">
                <div className="h-10 w-10 sm:h-12 sm:w-12 bg-gradient-to-br from-market-500 to-market-600 rounded-xl flex items-center justify-center shadow-lg">
                  <div className="flex items-center space-x-1">
                    <ShoppingBag className="h-5 w-5 sm:h-6 sm:w-6 text-white" />
                    <Leaf className="h-3 w-3 sm:h-4 sm:w-4 text-olive-200" />
                  </div>
                </div>
                <div className="hidden sm:block">
                  <h1 className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-market-600 to-olive-600 bg-clip-text text-transparent font-display">
                    Mercat Mediterrani
                  </h1>
                  <p className="text-xs sm:text-sm text-gray-600">Descobreix els productes frescos</p>
                </div>
                <div className="sm:hidden">
                  <h1 className="text-lg font-bold bg-gradient-to-r from-market-600 to-olive-600 bg-clip-text text-transparent font-display">
                    Mercat
                  </h1>
                </div>
              </div>
              
              <div className="flex items-center space-x-3 sm:space-x-6">
                <div className="hidden sm:flex items-center space-x-2 text-sm text-gray-600">
                  <User className="h-5 w-5 text-market-500" />
                  <span className="font-medium">{user?.email}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-1 sm:space-x-2 text-gray-600 hover:text-market-600 transition-colors"
                >
                  <LogOut className="h-4 w-4 sm:h-5 sm:w-5" />
                  <span className="hidden lg:inline font-medium">Tancar sessió</span>
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
          {/* Welcome Section con puntos como tema principal */}
          <div className="mb-6 sm:mb-8">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 sm:mb-6 space-y-4 sm:space-y-0">
              <div>
                <h2 className="text-2xl sm:text-4xl font-bold text-gray-900 font-display mb-2">
                  Benvingut, {user?.email?.split('@')[0]}! 🎉
                </h2>
                <p className="text-base sm:text-lg text-gray-600">
                  Continua explorant els productes frescos del nostre mercat
                </p>
              </div>
            </div>

            {/* Puntos principales - Tema central */}
            <div className="card-market p-6 sm:p-8 mb-6">
              <div className="text-center">
                <div className="flex items-center justify-center space-x-3 mb-4">
                  <Coins className="h-8 w-8 sm:h-12 sm:w-12 text-market-500" />
                  <h3 className="text-2xl sm:text-3xl font-bold text-market-800">Els Teus Punts</h3>
                </div>
                <div className="text-4xl sm:text-6xl font-bold text-market-600 mb-2">
                  {userStats.experience.toLocaleString()}
                </div>
                <div className="text-lg sm:text-xl text-market-700 mb-4">
                  punts acumulats
                </div>
                
                {/* Información de puntos */}
                <div className="max-w-md mx-auto">
                  <div className="text-sm text-market-600">
                    Continua fent compres per acumular més punts
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-2 gap-3 sm:gap-6 mb-6 sm:mb-8">
            <div className="card-olive p-3 sm:p-6">
              <div className="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-3">
                <div className="h-8 w-8 sm:h-12 sm:w-12 bg-olive-100 rounded-lg sm:rounded-xl flex items-center justify-center mx-auto sm:mx-0">
                  <Receipt className="h-4 w-4 sm:h-6 sm:w-6 text-olive-600" />
                </div>
                <div className="text-center sm:text-left">
                  <p className="text-xs sm:text-sm text-olive-600 font-medium">Tiquets Vàlids</p>
                  <p className="text-lg sm:text-2xl font-bold text-olive-800">{userStats.validTickets}</p>
                  <p className="text-xs text-olive-600">de {userStats.totalTickets} escanejats</p>
                </div>
              </div>
            </div>

            <div className="card p-3 sm:p-6">
              <div className="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-3">
                <div className="h-8 w-8 sm:h-12 sm:w-12 bg-terracotta-100 rounded-lg sm:rounded-xl flex items-center justify-center mx-auto sm:mx-0">
                  <Zap className="h-4 w-4 sm:h-6 sm:w-6 text-terracotta-600" />
                </div>
                <div className="text-center sm:text-left">
                  <p className="text-xs sm:text-sm text-terracotta-600 font-medium">Ratxa</p>
                  <p className="text-lg sm:text-2xl font-bold text-terracotta-800">{userStats.streak} dies</p>
                  <p className="text-xs text-terracotta-600">consecutius</p>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="mb-6 sm:mb-8 grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6">
            {/* Scan Ticket */}
            <Link
              to="/create-ticket"
              className="card hover:shadow-2xl transition-all duration-300 cursor-pointer group block overflow-hidden relative"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-market-500/5 to-olive-500/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="relative flex flex-col sm:flex-row sm:items-center space-y-4 sm:space-y-0 sm:space-x-6">
                <div className="h-16 w-16 sm:h-20 sm:w-20 bg-gradient-to-br from-market-500 to-market-600 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300 shadow-lg mx-auto sm:mx-0">
                  <Camera className="h-8 w-8 sm:h-10 sm:w-10 text-white" />
                </div>
                <div className="flex-1 text-center sm:text-left">
                  <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2">
                    Escanejar Nou Tiquet
                  </h3>
                  <p className="text-gray-600 text-base sm:text-lg">
                    Afegeix el teu tiquet de compra i acumula punts
                  </p>
                  <div className="flex items-center justify-center sm:justify-start space-x-2 mt-3">
                    <span className="badge badge-success">+50 punts</span>
                    <span className="badge badge-warning">Nova Insígnia</span>
                  </div>
                </div>
                <div className="text-market-500 group-hover:text-market-600 transition-colors flex justify-center sm:justify-end">
                  <Plus className="h-6 w-6 sm:h-8 sm:w-8" />
                </div>
              </div>
            </Link>

            {/* Rewards */}
            <Link
              to="/rewards"
              className="card hover:shadow-2xl transition-all duration-300 cursor-pointer group block overflow-hidden relative"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-olive-500/5 to-market-500/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="relative flex flex-col sm:flex-row sm:items-center space-y-4 sm:space-y-0 sm:space-x-6">
                <div className="h-16 w-16 sm:h-20 sm:w-20 bg-gradient-to-br from-olive-500 to-olive-600 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300 shadow-lg mx-auto sm:mx-0">
                  <Gift className="h-8 w-8 sm:h-10 sm:w-10 text-white" />
                </div>
                <div className="flex-1 text-center sm:text-left">
                  <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2">
                    Canviar Recompenses
                  </h3>
                  <p className="text-gray-600 text-base sm:text-lg">
                    Gasta els teus punts en recompenses i descomptes
                  </p>
                  <div className="flex items-center justify-center sm:justify-start space-x-2 mt-3">
                    <span className="badge badge-info">Parking</span>
                    <span className="badge badge-success">Descomptes</span>
                  </div>
                </div>
                <div className="text-olive-500 group-hover:text-olive-600 transition-colors flex justify-center sm:justify-end">
                  <Gift className="h-6 w-6 sm:h-8 sm:w-8" />
                </div>
              </div>
            </Link>

            {/* Profile QR */}
            <button
              onClick={() => setShowProfileQR(true)}
              className="card hover:shadow-2xl transition-all duration-300 cursor-pointer group block overflow-hidden relative"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="relative flex flex-col sm:flex-row sm:items-center space-y-4 sm:space-y-0 sm:space-x-6">
                <div className="h-16 w-16 sm:h-20 sm:w-20 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300 shadow-lg mx-auto sm:mx-0">
                  <QrCode className="h-8 w-8 sm:h-10 sm:w-10 text-white" />
                </div>
                <div className="flex-1 text-center sm:text-left">
                  <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2">
                    QR del Perfil
                  </h3>
                  <p className="text-gray-600 text-base sm:text-lg">
                    Mostra el teu QR per rebre tickets digitals
                  </p>
                  <div className="flex items-center justify-center sm:justify-start space-x-2 mt-3">
                    <span className="badge badge-info">Digital</span>
                    <span className="badge badge-success">Directe</span>
                  </div>
                </div>
                <div className="text-blue-500 group-hover:text-blue-600 transition-colors flex justify-center sm:justify-end">
                  <QrCode className="h-6 w-6 sm:h-8 sm:w-8" />
                </div>
              </div>
            </button>
          </div>

          {/* Tickets Section */}
          <div className="card">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 space-y-3 sm:space-y-0">
              <div className="text-center sm:text-left">
                <h3 className="text-xl sm:text-2xl font-bold text-gray-900 font-display">
                  Els Meus Tiquets
                </h3>
                <p className="text-gray-600 mt-1 text-sm sm:text-base">
                  Tiquets aprovats i digitals
                </p>
              </div>
              
              <div className="flex items-center justify-center sm:justify-end space-x-3">
                <Link
                  to="/ticket-history"
                  className="btn-secondary flex items-center space-x-2"
                >
                  <History className="h-4 w-4" />
                  <span>Historial Complet</span>
                </Link>
              </div>
            </div>

            {/* Tickets Feed */}
            <TicketFeed />
          </div>

          {/* Info Section mediterráneo */}
          <div className="mt-6 sm:mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6">
            <div className="card-olive text-center">
              <div className="flex flex-col items-center space-y-3 mb-4">
                <div className="h-10 w-10 sm:h-12 sm:w-12 bg-olive-100 rounded-xl flex items-center justify-center">
                  <Camera className="h-5 w-5 sm:h-6 sm:w-6 text-olive-600" />
                </div>
                <h4 className="font-bold text-gray-900 text-base sm:text-lg">Escaneig Ràpid</h4>
              </div>
              <p className="text-gray-600 text-sm sm:text-base">
                Escaneja els teus tiquets de compra directament amb la càmera del teu dispositiu.
              </p>
            </div>

            <div className="card-sea text-center">
              <div className="flex flex-col items-center space-y-3 mb-4">
                <div className="h-10 w-10 sm:h-12 sm:w-12 bg-sea-100 rounded-xl flex items-center justify-center">
                  <ShoppingBag className="h-5 w-5 sm:h-6 sm:w-6 text-sea-600" />
                </div>
                <h4 className="font-bold text-gray-900 text-base sm:text-lg">Productes Frescos</h4>
              </div>
              <p className="text-gray-600 text-sm sm:text-base">
                Descobreix els millors productes dels mercats mediterranis.
              </p>
            </div>

            <div className="card-market text-center">
              <div className="flex flex-col items-center space-y-3 mb-4">
                <div className="h-10 w-10 sm:h-12 sm:w-12 bg-market-100 rounded-xl flex items-center justify-center">
                  <Coins className="h-5 w-5 sm:h-6 sm:w-6 text-market-600" />
                </div>
                <h4 className="font-bold text-gray-900 text-base sm:text-lg">Punts i Recompenses</h4>
              </div>
              <p className="text-gray-600 text-sm sm:text-base">
                Acumula punts, guanya insígnies i descomptes per les teves compres.
              </p>
            </div>
          </div>
        </main>

        {/* Profile QR Modal */}
        <ProfileQR 
          isOpen={showProfileQR}
          onClose={() => setShowProfileQR(false)}
        />
      </div>
    </div>
  );
};

export default Dashboard; 
