import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { API_CONFIG } from '../../config/api';
import axios from 'axios';
import { 
  Receipt, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  Eye,
  Filter,
  RefreshCw
} from 'lucide-react';
import TicketDetails from './TicketDetails';

interface Ticket {
  id: string;
  display_name: string;
  store_name: string;
  total_amount: number;
  products: any[];
  status: string;
  created_at: string;
  is_digital: boolean;
}

const TicketStatus: React.FC = () => {
  const { user } = useAuth();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const fetchTickets = async () => {
    if (!user?.id) return;

    try {
      setLoading(true);
      setError(null);
      
              const response = await axios.get(`${API_CONFIG.TICKET_SERVICE_URL}/all/?user_id=${user.id}`);
      setTickets(response.data);
    } catch (err: any) {
      console.error('Error obteniendo tickets:', err);
      setError(err.response?.data?.detail || 'Error obtenint els tickets');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTickets();
  }, [user?.id]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'done_approved':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'done_rejected':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'duplicate':
        return <AlertCircle className="h-5 w-5 text-orange-500" />;
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      default:
        return <Receipt className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'done_approved':
        return 'Aprovat';
      case 'done_rejected':
        return 'Rebutjat';
      case 'duplicate':
        return 'Duplicat';
      case 'pending':
        return 'Pendent';
      default:
        return status;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'done_approved':
        return 'bg-green-100 text-green-800';
      case 'done_rejected':
        return 'bg-red-100 text-red-800';
      case 'duplicate':
        return 'bg-orange-100 text-orange-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
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

  const filteredTickets = tickets.filter(ticket => {
    if (statusFilter === 'all') return true;
    return ticket.status === statusFilter;
  });

  const handleViewDetails = (ticket: Ticket) => {
    setSelectedTicket(ticket);
    setShowDetails(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <RefreshCw className="h-8 w-8 text-market-600 animate-spin" />
        <span className="ml-2 text-gray-600">Carregant tickets...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center p-8">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Error</h3>
        <p className="text-gray-600 mb-4">{error}</p>
        <button
          onClick={fetchTickets}
          className="bg-market-600 text-white px-4 py-2 rounded-lg hover:bg-market-700 transition-colors"
        >
          Tornar a provar
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Estat dels Tickets</h2>
          <p className="text-gray-600">Consulta tots els teus tickets enviats</p>
        </div>
        <button
          onClick={fetchTickets}
          className="flex items-center space-x-2 bg-market-600 text-white px-4 py-2 rounded-lg hover:bg-market-700 transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          <span>Actualitzar</span>
        </button>
      </div>

      {/* Filter */}
      <div className="flex items-center space-x-4">
        <Filter className="h-5 w-5 text-gray-600" />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-market-500 focus:border-transparent"
        >
          <option value="all">Tots els tickets</option>
          <option value="done_approved">Aprovats</option>
          <option value="done_rejected">Rebutjats</option>
          <option value="pending">Pendents</option>
        </select>
      </div>

      {/* Tickets List */}
      {filteredTickets.length === 0 ? (
        <div className="text-center p-8">
          <Receipt className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Cap ticket trobat</h3>
          <p className="text-gray-600">
            {statusFilter === 'all' 
              ? 'Encara no has enviat cap ticket.'
              : `No tens tickets amb estat "${getStatusText(statusFilter)}".`
            }
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredTickets.map((ticket) => (
            <div
              key={ticket.id}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => handleViewDetails(ticket)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="h-12 w-12 bg-gradient-to-br from-market-500 to-olive-500 rounded-lg flex items-center justify-center">
                    {getStatusIcon(ticket.status)}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{ticket.display_name}</h3>
                    <p className="text-sm text-gray-600">{ticket.store_name}</p>
                    <p className="text-xs text-gray-500">{formatDate(ticket.created_at)}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className="font-semibold text-gray-900">€{ticket.total_amount.toFixed(2)}</p>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(ticket.status)}`}>
                      {getStatusText(ticket.status)}
                    </span>
                  </div>
                  <Eye className="h-5 w-5 text-gray-400" />
                </div>
              </div>
            </div>
          ))}
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

export default TicketStatus;
