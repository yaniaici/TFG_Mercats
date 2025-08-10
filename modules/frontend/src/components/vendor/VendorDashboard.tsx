import React from 'react';
import { useNavigate } from 'react-router-dom';
import VendorQRScanner from './VendorQRScanner';
import { useVendorAuth } from '../../contexts/VendorAuthContext';
import { Users, BarChart3, Settings, QrCode } from 'lucide-react';

const VendorDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { vendor, logout } = useVendorAuth();

  const handleDetected = (text: string) => {
    try {
      const url = new URL(text);
      if (url.pathname.startsWith('/validate-reward/')) {
        navigate(url.pathname);
        return;
      }
      if (url.pathname.startsWith('/send-ticket/')) {
        navigate(url.pathname);
        return;
      }
      // Si el QR contiene solo el código, intentar tratarlo como código de recompensa
      if (/^[A-Z0-9]{8,}$/.test(text)) {
        navigate(`/validate-reward/${text}`);
        return;
      }
      // Fallback: intentar extraer código de canje de la URL
      const match = text.match(/validate-reward\/(\w+)/);
      if (match) {
        navigate(`/validate-reward/${match[1]}`);
        return;
      }
    } catch {
      // No es URL; tratar como posible código
      if (text) navigate(`/validate-reward/${text}`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-sea-50 via-white to-olive-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Panell de Venedor</h1>
            <p className="text-gray-600 text-sm">Escaneja QRs de recompenses o perfils de clients</p>
          </div>
          <div className="text-sm text-gray-700">
            {vendor?.email}
            <button onClick={logout} className="ml-3 text-red-600 hover:underline">Sortir</button>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Mòdul: Escàner */}
        <div className="bg-white rounded-2xl shadow p-6 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="h-10 w-10 rounded-lg bg-market-100 flex items-center justify-center">
                <QrCode className="h-5 w-5 text-market-700" />
              </div>
              <h2 className="text-lg font-semibold text-gray-900">Escàner QR</h2>
            </div>
          </div>
          <VendorQRScanner onDetected={handleDetected} />
        </div>

        {/* Accés ràpid CRM */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl shadow p-6">
            <h3 className="text-base font-semibold text-gray-900 mb-4">Mòdul CRM</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <button
                onClick={() => navigate('/vendor/crm')}
                className="flex items-center gap-3 p-4 rounded-xl border hover:border-market-300 hover:bg-market-50 transition"
              >
                <Users className="h-5 w-5 text-market-700" />
                <span className="font-medium text-gray-800">Inici CRM</span>
              </button>
              <button
                onClick={() => navigate('/vendor/customers')}
                className="flex items-center gap-3 p-4 rounded-xl border hover:border-market-300 hover:bg-market-50 transition"
              >
                <Users className="h-5 w-5 text-market-700" />
                <span className="font-medium text-gray-800">Clients</span>
              </button>
              <button
                onClick={() => navigate('/vendor/stats')}
                className="flex items-center gap-3 p-4 rounded-xl border hover:border-market-300 hover:bg-market-50 transition"
              >
                <BarChart3 className="h-5 w-5 text-market-700" />
                <span className="font-medium text-gray-800">Estadístiques</span>
              </button>
              <button
                onClick={() => navigate('/vendor/settings')}
                className="flex items-center gap-3 p-4 rounded-xl border hover:border-market-300 hover:bg-market-50 transition"
              >
                <Settings className="h-5 w-5 text-market-700" />
                <span className="font-medium text-gray-800">Ajustos</span>
              </button>
            </div>
          </div>
          <div className="bg-white rounded-2xl shadow p-6">
            <h3 className="text-base font-semibold text-gray-900 mb-2">Resum ràpid</h3>
            <ul className="text-sm text-gray-700 space-y-1">
              <li>Últimes validacions de recompensa</li>
              <li>Últims tickets digitals enviats</li>
              <li>Clients recents</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VendorDashboard;


