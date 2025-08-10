import React from 'react';
import { 
  X, 
  Store, 
  Calendar, 
  Euro, 
  Package, 
  CheckCircle, 
  AlertCircle,
  Receipt
} from 'lucide-react';

interface Product {
  name: string;
  quantity: number;
  price: number;
}

interface TicketDetailsProps {
  ticket: {
    id: string;
    display_name?: string;
    store_name?: string;
    total_amount?: number;
    products?: Product[];
    status?: string;
    created_at?: string;
    is_digital?: boolean;
    processing_result?: any;
    ticket_metadata?: any;
  };
  isOpen: boolean;
  onClose: () => void;
}

const TicketDetails: React.FC<TicketDetailsProps> = ({ ticket, isOpen, onClose }) => {
  if (!isOpen) return null;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ca-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'done_approved':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'done_rejected':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
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
      case 'pending':
        return 'Pendent';
      default:
        return 'Desconegut';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'done_approved':
        return 'bg-green-100 text-green-800';
      case 'done_rejected':
        return 'bg-red-100 text-red-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 bg-market-500 rounded-lg flex items-center justify-center">
              <Receipt className="h-5 w-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-gray-900">Detalls del Ticket</h3>
              <p className="text-sm text-gray-600">{ticket.display_name}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Status */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-2">
              {getStatusIcon(ticket.status || '')}
              <span className="font-medium text-gray-900">Estat:</span>
            </div>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(ticket.status || '')}`}>
              {getStatusText(ticket.status || '')}
            </span>
          </div>

          {/* Store Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center space-x-3 p-4 bg-blue-50 rounded-lg">
              <Store className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-sm text-blue-600">Botiga</p>
                <p className="font-medium text-gray-900">{ticket.store_name || 'Desconeguda'}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 p-4 bg-green-50 rounded-lg">
              <Calendar className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm text-green-600">Data</p>
                <p className="font-medium text-gray-900">{ticket.created_at ? formatDate(ticket.created_at) : 'Desconeguda'}</p>
              </div>
            </div>
          </div>

          {/* Total */}
          <div className="flex items-center justify-between p-4 bg-gradient-to-r from-market-50 to-olive-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <Euro className="h-6 w-6 text-market-600" />
              <span className="text-lg font-medium text-gray-900">Total:</span>
            </div>
            <span className="text-2xl font-bold text-market-600">
              €{ticket.total_amount?.toFixed(2) || '0.00'}
            </span>
          </div>

          {/* Products */}
          {ticket.products && ticket.products.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Package className="h-5 w-5 text-gray-600" />
                <h4 className="text-lg font-semibold text-gray-900">Productes</h4>
              </div>
              
              <div className="space-y-3">
                {ticket.products.map((product, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{product.name}</p>
                      <p className="text-sm text-gray-600">
                        {product.quantity} x €{product.price.toFixed(2)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-gray-900">
                        €{(product.quantity * product.price).toFixed(2)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Digital Ticket Info */}
          {ticket.is_digital && (
            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="flex items-start space-x-2">
                <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <p className="font-medium text-blue-900">Ticket Digital</p>
                  <p className="text-sm text-blue-700">
                    Aquest ticket va ser creat digitalment per un venedor i s'ha afegit automàticament al teu historial.
                  </p>
                  {ticket.ticket_metadata?.purchase_date && (
                    <p className="text-xs text-blue-600 mt-1">
                      Data de compra: {new Date(ticket.ticket_metadata.purchase_date).toLocaleDateString('ca-ES')}
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Processing Result Info for Non-Digital Tickets */}
          {!ticket.is_digital && ticket.processing_result && (
            <div className="space-y-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Informació del Processament</h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                  {ticket.processing_result.fecha && (
                    <div>
                      <span className="text-gray-600">Data:</span>
                      <span className="ml-2 font-medium">{ticket.processing_result.fecha}</span>
                    </div>
                  )}
                  {ticket.processing_result.hora && (
                    <div>
                      <span className="text-gray-600">Hora:</span>
                      <span className="ml-2 font-medium">{ticket.processing_result.hora}</span>
                    </div>
                  )}
                  {ticket.processing_result.tipo_ticket && (
                    <div>
                      <span className="text-gray-600">Tipus:</span>
                      <span className="ml-2 font-medium">{ticket.processing_result.tipo_ticket}</span>
                    </div>
                  )}
                  {ticket.processing_result.num_productos && (
                    <div>
                      <span className="text-gray-600">Productes:</span>
                      <span className="ml-2 font-medium">{ticket.processing_result.num_productos}</span>
                    </div>
                  )}
                </div>
              </div>

              {ticket.processing_result.error && (
                <div className="p-4 bg-red-50 rounded-lg">
                  <div className="flex items-start space-x-2">
                    <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
                    <div>
                      <p className="font-medium text-red-900">Error de Processament</p>
                      <p className="text-sm text-red-700">{ticket.processing_result.error}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200">
          <button
            onClick={onClose}
            className="w-full bg-market-600 text-white py-3 px-6 rounded-lg hover:bg-market-700 transition-colors"
          >
            Tancar
          </button>
        </div>
      </div>
    </div>
  );
};

export default TicketDetails;
