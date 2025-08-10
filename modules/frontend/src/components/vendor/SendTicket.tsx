import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  ArrowLeft,
  User,
  Store,
  Receipt,
  Plus,
  Trash2,
  Send,
  CheckCircle,
  AlertCircle,
  Loader,
  Info
} from 'lucide-react';

interface Product {
  id: string;
  name: string;
  quantity: number;
  price: number;
}

interface TicketData {
  store_name: string;
  total_amount: number;
  products: Product[];
  purchase_date: string;
}

interface UserInfo {
  id: string;
  email: string;
  name: string;
  registration_date: string;
}

const SendTicket: React.FC = () => {
  const { userId } = useParams<{ userId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [ticketData, setTicketData] = useState<TicketData>({
    store_name: '',
    total_amount: 0,
    products: [],
    purchase_date: new Date().toISOString().slice(0, 16)
  });

  const [newProduct, setNewProduct] = useState({
    name: '',
    quantity: 1,
    price: 0
  });

  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);

  useEffect(() => {
    const fetchUserInfo = async () => {
      if (!userId) {
        setError('ID de usuario no válido');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        
        // Obtener información del usuario desde el auth service
        const response = await axios.get(`http://localhost:8001/users/${userId}/public-info`);
        setUserInfo(response.data);
        
      } catch (err: any) {
        console.error('Error obteniendo información del usuario:', err);
        setError(err.response?.data?.detail || 'Error obtingent informació del client');
      } finally {
        setLoading(false);
      }
    };

    fetchUserInfo();
  }, [userId]);

  const addProduct = () => {
    if (newProduct.name && newProduct.price > 0) {
      const product: Product = {
        id: Date.now().toString(),
        name: newProduct.name,
        quantity: newProduct.quantity,
        price: newProduct.price
      };

      setTicketData(prev => ({
        ...prev,
        products: [...prev.products, product],
        total_amount: prev.total_amount + (newProduct.price * newProduct.quantity)
      }));

      setNewProduct({ name: '', quantity: 1, price: 0 });
    }
  };

  const removeProduct = (productId: string) => {
    const product = ticketData.products.find(p => p.id === productId);
    if (product) {
      setTicketData(prev => ({
        ...prev,
        products: prev.products.filter(p => p.id !== productId),
        total_amount: prev.total_amount - (product.price * product.quantity)
      }));
    }
  };

  const handleSendTicket = async () => {
    if (!ticketData.store_name || ticketData.products.length === 0) {
      setError('Si us plau, omple tots els camps obligatoris');
      return;
    }

    try {
      setSending(true);
      setError(null);

      // Enviar ticket digital al backend
      const ticketPayload = {
        user_id: userId,
        store_name: ticketData.store_name,
        total_amount: ticketData.total_amount,
        products: ticketData.products,
        purchase_date: ticketData.purchase_date
      };

      const response = await axios.post('http://localhost:8003/tickets/digital/', ticketPayload);
      
      console.log('Ticket digital enviado:', response.data);

      setSuccess(true);
      
      // Reset form after success
      setTimeout(() => {
        setTicketData({
          store_name: '',
          total_amount: 0,
          products: [],
          purchase_date: new Date().toISOString().slice(0, 16)
        });
        setSuccess(false);
      }, 3000);

    } catch (err: any) {
      console.error('Error enviando ticket digital:', err);
      setError(err.response?.data?.detail || 'Error enviant el ticket digital');
    } finally {
      setSending(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-sea-50 via-white to-olive-50 flex items-center justify-center">
        <div className="text-center">
          <Loader className="h-12 w-12 text-market-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Carregant informació del client...</p>
        </div>
      </div>
    );
  }

  if (error && !userInfo) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-sea-50 via-white to-olive-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="bg-market-600 text-white px-4 py-2 rounded-lg hover:bg-market-700 transition-colors"
          >
            Tornar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-sea-50 via-white to-olive-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/vendor/dashboard')}
              className="text-gray-600 hover:text-market-600 transition-colors"
            >
              <ArrowLeft className="h-6 w-6" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Enviar Ticket Digital</h1>
              <p className="text-gray-600">Crea i envia un ticket digital al client</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* User Info Card */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <div className="flex items-center space-x-3 mb-4">
                <div className="h-12 w-12 bg-market-500 rounded-full flex items-center justify-center">
                  <User className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Client</h3>
                  <p className="text-sm text-gray-600">Destinatari del ticket</p>
                </div>
              </div>
              
              {userInfo && (
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium text-gray-700">ID del Client</label>
                    <p className="text-sm text-gray-900 font-mono bg-gray-50 p-2 rounded">
                      {userInfo.id}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Email</label>
                    <p className="text-sm text-gray-900">{userInfo.email}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Nom</label>
                    <p className="text-sm text-gray-900">{userInfo.name}</p>
                  </div>
                </div>
              )}

              <div className="mt-6 p-3 bg-blue-50 rounded-lg">
                <div className="flex items-start space-x-2">
                  <Info className="h-4 w-4 text-blue-600 mt-0.5" />
                  <div>
                    <p className="text-xs text-blue-800">
                      <strong>Mode Debug:</strong> Aquest ticket s'afegirà automàticament al historial del client.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Ticket Form */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <div className="flex items-center space-x-3 mb-6">
                <div className="h-10 w-10 bg-olive-500 rounded-lg flex items-center justify-center">
                  <Receipt className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Detalls del Ticket</h3>
                  <p className="text-sm text-gray-600">Omple la informació de la compra</p>
                </div>
              </div>

              {/* Error/Success Messages */}
              {error && (
                <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-2">
                  <AlertCircle className="h-5 w-5 text-red-400" />
                  <span className="text-red-800 text-sm">{error}</span>
                </div>
              )}

              {success && (
                <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4 flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-400" />
                  <span className="text-green-800 text-sm">Ticket enviat correctament!</span>
                </div>
              )}

              {/* Store Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nom de la Botiga *
                  </label>
                  <input
                    type="text"
                    value={ticketData.store_name}
                    onChange={(e) => setTicketData(prev => ({ ...prev, store_name: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-market-500 focus:border-transparent"
                    placeholder="Ex: Mercat Central"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Data de Compra
                  </label>
                  <input
                    type="datetime-local"
                    value={ticketData.purchase_date}
                    onChange={(e) => setTicketData(prev => ({ ...prev, purchase_date: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-market-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Products Section */}
              <div className="mb-6">
                <h4 className="text-lg font-medium text-gray-900 mb-4">Productes</h4>
                
                {/* Add Product Form */}
                <div className="bg-gray-50 p-4 rounded-lg mb-4">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                    <div className="md:col-span-2">
                      <input
                        type="text"
                        value={newProduct.name}
                        onChange={(e) => setNewProduct(prev => ({ ...prev, name: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-market-500 focus:border-transparent"
                        placeholder="Nom del producte"
                      />
                    </div>
                    <div>
                      <input
                        type="number"
                        value={newProduct.quantity}
                        onChange={(e) => setNewProduct(prev => ({ ...prev, quantity: parseInt(e.target.value) || 1 }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-market-500 focus:border-transparent"
                        placeholder="Quantitat"
                        min="1"
                      />
                    </div>
                    <div>
                      <input
                        type="number"
                        step="0.01"
                        value={newProduct.price}
                        onChange={(e) => setNewProduct(prev => ({ ...prev, price: parseFloat(e.target.value) || 0 }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-market-500 focus:border-transparent"
                        placeholder="Preu €"
                        min="0"
                      />
                    </div>
                  </div>
                  <button
                    onClick={addProduct}
                    className="mt-3 flex items-center space-x-2 bg-market-600 text-white px-4 py-2 rounded-lg hover:bg-market-700 transition-colors"
                  >
                    <Plus className="h-4 w-4" />
                    <span>Afegir Producte</span>
                  </button>
                </div>

                {/* Products List */}
                {ticketData.products.length > 0 && (
                  <div className="space-y-2">
                    {ticketData.products.map((product) => (
                      <div key={product.id} className="flex items-center justify-between bg-white border border-gray-200 rounded-lg p-3">
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">{product.name}</p>
                          <p className="text-sm text-gray-600">
                            {product.quantity} x €{product.price.toFixed(2)} = €{(product.quantity * product.price).toFixed(2)}
                          </p>
                        </div>
                        <button
                          onClick={() => removeProduct(product.id)}
                          className="text-red-600 hover:text-red-700 transition-colors"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Total */}
              <div className="bg-gray-50 p-4 rounded-lg mb-6">
                <div className="flex justify-between items-center">
                  <span className="text-lg font-semibold text-gray-900">Total:</span>
                  <span className="text-2xl font-bold text-market-600">
                    €{ticketData.total_amount.toFixed(2)}
                  </span>
                </div>
              </div>

              {/* Send Button */}
              <button
                onClick={handleSendTicket}
                disabled={sending || !ticketData.store_name || ticketData.products.length === 0}
                className="w-full bg-market-600 text-white py-3 px-6 rounded-lg hover:bg-market-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                {sending ? (
                  <>
                    <Loader className="h-5 w-5 animate-spin" />
                    <span>Enviant...</span>
                  </>
                ) : (
                  <>
                    <Send className="h-5 w-5" />
                    <span>Enviar Ticket Digital</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SendTicket;
