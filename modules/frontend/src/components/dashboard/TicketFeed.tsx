import React, { useState, useEffect } from 'react';
import { Receipt, Calendar, Clock, CheckCircle, XCircle, AlertCircle, Store, Euro, Package, Leaf, Eye } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import TicketDetails from '../tickets/TicketDetails';

interface Ticket {
  id: string;
  display_name?: string;
  store_name?: string;
  total_amount?: number;
  products?: any[];
  status?: string;
  created_at?: string;
  is_digital?: boolean;
}

const TicketFeed: React.FC = () => {
  const { user } = useAuth();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    if (user?.id) {
      fetchUserTickets();
    }
  }, [user?.id]);

  const fetchUserTickets = async () => {
    try {
      setLoading(true);
      setError(null);
      
              const response = await fetch(`${process.env.REACT_APP_ENVIRONMENT === 'production' ? 'http://mercatmediterrani.com:8003' : 'http://localhost:8003'}/tickets/?user_id=${user?.id}`);
      
      if (!response.ok) {
        throw new Error('Error al obtenir tiquets');
      }
      
      const data = await response.json();
      
      // Validar y limpiar los datos recibidos
      const validatedTickets = Array.isArray(data) ? data.filter(ticket => {
        return ticket && ticket.id && typeof ticket.id === 'string';
      }).map(ticket => ({
        id: ticket.id || '',
        display_name: ticket.display_name || 'Ticket sense nom',
        store_name: ticket.store_name || 'Botiga desconeguda',
        total_amount: typeof ticket.total_amount === 'number' ? ticket.total_amount : 0,
        products: Array.isArray(ticket.products) ? ticket.products : [],
        status: ticket.status || 'unknown',
        created_at: ticket.created_at || new Date().toISOString(),
        is_digital: Boolean(ticket.is_digital)
      })) : [];
      
      setTickets(validatedTickets);
    } catch (err) {
      console.error('Error fetching user tickets:', err);
      setError(err instanceof Error ? err.message : 'Error desconegut');
      setTickets([]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'done_approved':
        return <CheckCircle className="h-6 w-6 text-olive-600" />;
      case 'done_rejected':
        return <XCircle className="h-6 w-6 text-terracotta-600" />;
      case 'pending':
        return <Clock className="h-6 w-6 text-market-600" />;
      case 'failed':
        return <AlertCircle className="h-6 w-6 text-terracotta-600" />;
      case 'duplicate':
        return <AlertCircle className="h-6 w-6 text-orange-600" />;
      default:
        return <Receipt className="h-6 w-6 text-gray-600" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'done_approved':
        return 'Aprovat';
      case 'done_rejected':
        return 'Rebutjat';
      case 'pending':
        return 'Pendent';
      case 'failed':
        return 'Error';
      case 'duplicate':
        return 'Duplicat';
      default:
        return 'Desconegut';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'done_approved':
        return 'badge-success';
      case 'done_rejected':
        return 'badge-warning';
      case 'pending':
        return 'badge-info';
      case 'failed':
        return 'badge-warning';
      case 'duplicate':
        return 'badge-warning';
      default:
        return 'badge-info';
    }
  };

  const formatDate = (dateString: string) => {
    try {
      if (!dateString) return 'Data desconeguda';
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return 'Data invàlida';
      
      return date.toLocaleDateString('ca-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (error) {
      console.error('Error formatting date:', error);
      return 'Data invàlida';
    }
  };

  const handleViewDetails = (ticket: Ticket) => {
    if (ticket && ticket.id) {
      setSelectedTicket(ticket);
      setShowDetails(true);
    }
  };

  if (loading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-market-600"></div>
          <span className="ml-3 text-lg text-gray-600">Carregant tiquets...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="text-center py-12">
          <AlertCircle className="h-16 w-16 text-terracotta-400 mx-auto mb-6" />
          <h4 className="text-xl font-bold text-gray-900 mb-3">Error al carregar tiquets</h4>
          <p className="text-gray-600 mb-6 text-lg">{error}</p>
          <button
            onClick={fetchUserTickets}
            className="btn-primary"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 sm:mb-8 space-y-3 sm:space-y-0">
        <div className="text-center sm:text-left">
          <p className="text-gray-600 mt-1 text-sm sm:text-base">Historial de compres al mercat</p>
        </div>
        <div className="flex items-center justify-center sm:justify-end space-x-3 text-sm text-gray-600 bg-white/50 px-3 sm:px-4 py-2 rounded-xl">
          <Receipt className="h-4 w-4 sm:h-5 sm:w-5 text-market-500" />
          <span className="font-semibold">{tickets.length} tiquets</span>
        </div>
      </div>

      {tickets.length > 0 ? (
        <div className="space-y-3 sm:space-y-4">
          {tickets.map((ticket) => (
            <div 
              key={ticket.id} 
              className={`group hover:shadow-lg transition-all duration-300 rounded-2xl p-4 sm:p-6 border ${
                ticket.is_digital 
                  ? 'bg-gradient-to-r from-blue-50 to-indigo-50/50 border-blue-200 hover:border-blue-300 cursor-pointer' 
                  : 'bg-gradient-to-r from-white to-gray-50/50 border-gray-100 hover:border-gray-200'
              }`}
              onClick={ticket.is_digital ? () => handleViewDetails(ticket) : undefined}
            >
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
                <div className="flex items-center space-x-3 sm:space-x-4">
                  <div className="h-12 w-12 sm:h-14 sm:w-14 bg-gradient-to-br from-market-100 to-market-200 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    {getStatusIcon(ticket.status || 'unknown')}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      <h4 className="text-base sm:text-lg font-bold text-gray-900 truncate">
                        {ticket.display_name || 'Ticket sense nom'}
                      </h4>
                      {ticket.is_digital && (
                        <span className="badge badge-info text-xs font-semibold">
                          Digital
                        </span>
                      )}
                    </div>
                    <div className="flex flex-col sm:flex-row sm:items-center space-y-1 sm:space-y-0 sm:space-x-4 text-xs sm:text-sm text-gray-600">
                      <div className="flex items-center space-x-1">
                        <Calendar className="h-3 w-3 sm:h-4 sm:w-4 text-market-500" />
                        <span>{formatDate(ticket.created_at || '')}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Store className="h-3 w-3 sm:h-4 sm:w-4 text-market-500" />
                        <span>{ticket.store_name || 'Botiga desconeguda'}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="text-center sm:text-right">
                  {ticket.total_amount && ticket.total_amount > 0 && (
                    <div className="flex items-center justify-center sm:justify-end space-x-1 mb-2">
                      <Euro className="h-3 w-3 sm:h-4 sm:w-4 text-olive-600" />
                      <p className="text-lg sm:text-xl font-bold text-gray-900">€{ticket.total_amount.toFixed(2)}</p>
                    </div>
                  )}
                  <span className={`badge ${getStatusBadge(ticket.status || 'unknown')} text-xs sm:text-sm font-semibold`}>
                    {getStatusText(ticket.status || 'unknown')}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 sm:py-16">
          <div className="h-20 w-20 sm:h-24 sm:w-24 bg-gradient-to-br from-market-100 to-market-200 rounded-2xl flex items-center justify-center mx-auto mb-4 sm:mb-6">
            <Receipt className="h-10 w-10 sm:h-12 sm:w-12 text-market-500" />
          </div>
          <h4 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2 sm:mb-3">
            Encara no has escanejat cap tiquet
          </h4>
          <p className="text-gray-600 text-base sm:text-lg mb-4 sm:mb-6 px-4">
            Comença escanejant el teu primer tiquet de compra al mercat.
          </p>
          <div className="flex items-center justify-center space-x-2 text-xs sm:text-sm text-market-600">
            <Leaf className="h-3 w-3 sm:h-4 sm:w-4" />
            <span>Guanya experiència i insígnies!</span>
          </div>
        </div>
      )}

      {/* Ticket Details Modal */}
      {selectedTicket && (
        <TicketDetails
          ticket={selectedTicket}
          isOpen={showDetails}
          onClose={() => {
            setShowDetails(false);
            setSelectedTicket(null);
          }}
        />
      )}
    </>
  );
};

export default TicketFeed; 