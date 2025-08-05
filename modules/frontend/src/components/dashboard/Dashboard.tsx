import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { 
  Plus, 
  LogOut, 
  User, 
  Receipt, 
  Camera,
  ShoppingBag,
  Calendar
} from 'lucide-react';

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  // Mock data - en un cas real això vindria de l'API
  const scannedTickets = [
    {
      id: 1,
      date: '2024-12-15',
      market: 'Mercat Central',
      total: '€24.50',
      status: 'Processat'
    },
    {
      id: 2,
      date: '2024-12-14',
      market: 'Mercat del Serrallo',
      total: '€18.75',
      status: 'Processat'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white text-sm font-bold">M</span>
              </div>
              <h1 className="ml-3 text-xl font-semibold text-gray-900">
                Mercats de Tarragona
              </h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <User className="h-4 w-4" />
                <span>{user?.username}</span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-1 text-gray-600 hover:text-gray-900 transition-colors"
              >
                <LogOut className="h-4 w-4" />
                <span className="hidden sm:inline">Tancar sessió</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Benvingut, {user?.username}!
          </h2>
          <p className="text-gray-600">
            Escaneja els teus tiquets de compra dels mercats de Tarragona de manera fàcil i ràpida.
          </p>
        </div>

        {/* Quick Action */}
        <div className="mb-8">
          <Link
            to="/create-ticket"
            className="card hover:shadow-md transition-shadow cursor-pointer group block"
          >
            <div className="flex items-center space-x-4">
              <div className="h-16 w-16 bg-primary-100 rounded-lg flex items-center justify-center group-hover:bg-primary-200 transition-colors">
                <Camera className="h-8 w-8 text-primary-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900">
                  Escanejar Nou Tiquet
                </h3>
                <p className="text-gray-600">
                  Escaneja el teu tiquet de compra amb la càmera
                </p>
              </div>
              <div className="ml-auto">
                <Plus className="h-6 w-6 text-primary-600" />
              </div>
            </div>
          </Link>
        </div>

        {/* Scanned Tickets */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">
              Tiquets Escanejats
            </h3>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Receipt className="h-4 w-4" />
              <span>{scannedTickets.length} tiquets</span>
            </div>
          </div>

          {scannedTickets.length > 0 ? (
            <div className="space-y-4">
              {scannedTickets.map((ticket) => (
                <div key={ticket.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="h-10 w-10 bg-green-100 rounded-lg flex items-center justify-center">
                      <Receipt className="h-5 w-5 text-green-600" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">{ticket.market}</h4>
                      <div className="flex items-center space-x-2 text-sm text-gray-600">
                        <Calendar className="h-3 w-3" />
                        <span>{ticket.date}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-900">{ticket.total}</p>
                    <p className="text-sm text-green-600">{ticket.status}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <Receipt className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h4 className="text-lg font-medium text-gray-900 mb-2">
                Encara no has escanejat cap tiquet
              </h4>
              <p className="text-gray-600 mb-6">
                Comença escanejant el teu primer tiquet de compra.
              </p>
              <Link
                to="/create-ticket"
                className="btn-primary inline-flex items-center space-x-2"
              >
                <Camera className="h-4 w-4" />
                <span>Escanejar Primer Tiquet</span>
              </Link>
            </div>
          )}
        </div>

        {/* Info Section */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="card">
            <div className="flex items-center space-x-3 mb-4">
              <div className="h-8 w-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <Camera className="h-4 w-4 text-blue-600" />
              </div>
              <h4 className="font-semibold text-gray-900">Escaneig Ràpid</h4>
            </div>
            <p className="text-gray-600 text-sm">
              Escaneja els teus tiquets de compra directament amb la càmera del teu dispositiu.
            </p>
          </div>

          <div className="card">
            <div className="flex items-center space-x-3 mb-4">
              <div className="h-8 w-8 bg-green-100 rounded-lg flex items-center justify-center">
                <ShoppingBag className="h-4 w-4 text-green-600" />
              </div>
              <h4 className="font-semibold text-gray-900">Mercats de Tarragona</h4>
            </div>
            <p className="text-gray-600 text-sm">
              Sistema específic per als mercats de Tarragona i els seus clients.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard; 