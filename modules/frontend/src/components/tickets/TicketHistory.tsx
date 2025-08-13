import React, { useState, useEffect } from 'react';
import { 
  Receipt, 
  Calendar, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Store, 
  Euro, 
  Package, 
  Filter,
  Eye,
  Download
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import TicketDetails from './TicketDetails';

interface Ticket {
  id: string;
  display_name?: string;
  store_name?: string;
  total_amount?: number;
  products?: any[];
  status?: string;
  created_at?: string;
  is_digital?: boolean;
  processing_result?: any;
}

const TicketHistory: React.FC = () => {
  const { user } = useAuth();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    if (user?.id) {
      fetchTicketHistory();
    }
  }, [user?.id, statusFilter]);

  const fetchTicketHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const url = statusFilter === 'all' 
        ? `http://localhost:8003/tickets/history/${user?.id}`
        : `http://localhost:8003/tickets/history/${user?.id}?status=${statusFilter}`;
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error('Error en obtenir l\'historial de tiquets');
      }
      
      const data = await response.json();
      
      // Validar y limpiar los datos recibidos
      const validatedTickets = Array.isArray(data) ? data.filter(ticket => {
        return ticket && ticket.id && typeof ticket.id === 'string';
      }).map(ticket => ({
        id: ticket.id || '',
        display_name: ticket.display_name || 'Tiquet sense nom',
        store_name: ticket.store_name || 'Botiga desconeguda',
        total_amount: typeof ticket.total_amount === 'number' ? ticket.total_amount : 0,
        products: Array.isArray(ticket.products) ? ticket.products : [],
        status: ticket.status || 'unknown',
        created_at: ticket.created_at || new Date().toISOString(),
        is_digital: Boolean(ticket.is_digital),
        processing_result: ticket.processing_result || null
      })) : [];
      
      setTickets(validatedTickets);
    } catch (err) {
      console.error('Error obtenint historial de tiquets:', err);
      setError(err instanceof Error ? err.message : 'Error desconegut');
      setTickets([]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'done_approved':
        return <CheckCircle className="h-6 w-6 text-green-600" />;
      case 'done_rejected':
        return <XCircle className="h-6 w-6 text-red-600" />;
      case 'pending':
        return <Clock className="h-6 w-6 text-yellow-600" />;
      case 'failed':
        return <AlertCircle className="h-6 w-6 text-red-600" />;
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
      default:
        return 'Desconegut';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'done_approved':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'done_rejected':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
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
      console.error('Error formatant data:', error);
      return 'Data invàlida';
    }
  };

  const handleViewDetails = (ticket: Ticket) => {
    if (ticket && ticket.id) {
      setSelectedTicket(ticket);
      setShowDetails(true);
    }
  };

  const getStatusCounts = () => {
    const counts = {
      all: tickets.length,
      done_approved: tickets.filter(t => t.status === 'done_approved').length,
      done_rejected: tickets.filter(t => t.status === 'done_rejected').length,
      pending: tickets.filter(t => t.status === 'pending').length,
      failed: tickets.filter(t => t.status === 'failed').length
    };
    return counts;
  };

  const statusCounts = getStatusCounts();

  if (loading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-market-600"></div>
          <span className="ml-3 text-lg text-gray-600">Carregant historial...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="text-center py-12">
          <AlertCircle className="h-16 w-16 text-red-400 mx-auto mb-6" />
          <h4 className="text-xl font-bold text-gray-900 mb-3">Error en carregar l'historial</h4>
          <p className="text-gray-600 mb-6 text-lg">{error}</p>
          <button
            onClick={fetchTicketHistory}
            className="btn-primary"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 space-y-3 sm:space-y-0">
        <div className="text-center sm:text-left">
          <h3 className="text-xl sm:text-2xl font-bold text-gray-900 font-display">
            Historial de Tiquets Enviats
          </h3>
          <p className="text-gray-600 mt-1 text-sm sm:text-base">
            Seguiment de tots els tiquets enviats i el seu estat
          </p>
        </div>
        <div className="flex items-center justify-center sm:justify-end space-x-3">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="btn-secondary flex items-center space-x-2"
          >
            <Filter className="h-4 w-4" />
            <span>Filtres</span>
          </button>
          <div className="text-sm text-gray-600 bg-white/50 px-3 py-2 rounded-xl">
            <span className="font-semibold">{tickets.length} tiquets</span>
          </div>
        </div>
      </div>

      {/* Filtros */}
      {showFilters && (
        <div className="mb-6 p-4 bg-gray-50 rounded-xl">
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            <button
              onClick={() => setStatusFilter('all')}
              className={`p-2 rounded-lg text-sm font-medium transition-colors ${
                statusFilter === 'all' 
                  ? 'bg-market-600 text-white' 
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              Tots ({statusCounts.all})
            </button>
            <button
              onClick={() => setStatusFilter('done_approved')}
              className={`p-2 rounded-lg text-sm font-medium transition-colors ${
                statusFilter === 'done_approved' 
                  ? 'bg-green-600 text-white' 
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              Aprovats ({statusCounts.done_approved})
            </button>
            <button
              onClick={() => setStatusFilter('done_rejected')}
              className={`p-2 rounded-lg text-sm font-medium transition-colors ${
                statusFilter === 'done_rejected' 
                  ? 'bg-red-600 text-white' 
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              Rebutjats ({statusCounts.done_rejected})
            </button>
            <button
              onClick={() => setStatusFilter('pending')}
              className={`p-2 rounded-lg text-sm font-medium transition-colors ${
                statusFilter === 'pending' 
                  ? 'bg-yellow-600 text-white' 
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              Pendants ({statusCounts.pending})
            </button>
            <button
              onClick={() => setStatusFilter('failed')}
              className={`p-2 rounded-lg text-sm font-medium transition-colors ${
                statusFilter === 'failed' 
                  ? 'bg-red-600 text-white' 
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              Errors ({statusCounts.failed})
            </button>
          </div>
        </div>
      )}

      {tickets.length > 0 ? (
        <div className="space-y-4">
          {tickets.map((ticket) => (
            <div 
              key={ticket.id} 
              className={`group hover:shadow-lg transition-all duration-300 bg-gradient-to-r from-white to-gray-50/50 rounded-2xl p-4 sm:p-6 border border-gray-100 ${
                ticket.is_digital ? 'cursor-pointer' : ''
              }`}
              onClick={ticket.is_digital ? () => handleViewDetails(ticket) : undefined}
            >
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
                <div className="flex items-center space-x-3 sm:space-x-4">
                  <div className="h-12 w-12 sm:h-14 sm:w-14 bg-gradient-to-br from-gray-100 to-gray-200 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    {getStatusIcon(ticket.status || 'unknown')}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-base sm:text-lg font-bold text-gray-900 mb-1 truncate">
                      {ticket.display_name || 'Tiquet sense nom'}
                    </h4>
                    <div className="flex flex-col sm:flex-row sm:items-center space-y-1 sm:space-y-0 sm:space-x-4 text-xs sm:text-sm text-gray-600">
                      <div className="flex items-center space-x-1">
                        <Calendar className="h-3 w-3 sm:h-4 sm:w-4 text-market-500" />
                        <span>{formatDate(ticket.created_at || '')}</span>
                      </div>
                      {ticket.is_digital && (
                        <div className="flex items-center space-x-1">
                          <Eye className="h-3 w-3 sm:h-4 sm:w-4 text-market-500" />
                          <span>Digital</span>
                        </div>
                      )}
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
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs sm:text-sm font-medium border ${getStatusBadge(ticket.status || 'unknown')}`}>
                    {getStatusText(ticket.status || 'unknown')}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 sm:py-16">
          <div className="h-20 w-20 sm:h-24 sm:w-24 bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl flex items-center justify-center mx-auto mb-4 sm:mb-6">
            <Receipt className="h-10 w-10 sm:h-12 sm:w-12 text-gray-500" />
          </div>
          <h4 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2 sm:mb-3">
            No hi ha tiquets en aquest estat
          </h4>
          <p className="text-gray-600 text-base sm:text-lg mb-4 sm:mb-6 px-4">
            {statusFilter === 'all' 
              ? 'Encara no has enviat cap tiquet.'
              : `No hi ha tiquets amb estat "${getStatusText(statusFilter)}".`
            }
          </p>
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
    </div>
  );
};

export default TicketHistory;
