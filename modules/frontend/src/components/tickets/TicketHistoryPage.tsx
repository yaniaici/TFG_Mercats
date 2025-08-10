import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import TicketHistory from './TicketHistory';

const TicketHistoryPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-sea-50 via-white to-olive-50">
      {/* Header */}
      <header className="bg-white/90 backdrop-blur-sm shadow-lg border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16 sm:h-20">
            <Link
              to="/dashboard"
              className="flex items-center space-x-2 text-gray-600 hover:text-market-600 transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
              <span className="font-medium">Tornar al Dashboard</span>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        <TicketHistory />
      </main>
    </div>
  );
};

export default TicketHistoryPage;
