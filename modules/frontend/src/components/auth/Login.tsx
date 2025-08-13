import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Eye, EyeOff, Mail, Lock, AlertCircle, ShoppingBag, Leaf } from 'lucide-react';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const u = await login(email, password);
      const role = (u as any)?.preferences?.role;
      if (role === 'vendor') {
        navigate('/vendor/dashboard');
      } else {
        navigate('/dashboard');
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-6 px-4 sm:py-12 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Fondo decorativo mediterráneo */}
      <div className="absolute inset-0 bg-gradient-to-br from-sea-50 via-white to-olive-50"></div>
      <div className="absolute top-4 left-4 sm:top-10 sm:left-10 w-20 h-20 sm:w-32 sm:h-32 bg-market-200 rounded-full opacity-20 floating"></div>
      <div className="absolute bottom-4 right-4 sm:bottom-10 sm:right-10 w-16 h-16 sm:w-24 sm:h-24 bg-olive-200 rounded-full opacity-20 floating" style={{animationDelay: '1s'}}></div>
      <div className="absolute top-1/2 left-1/4 w-12 h-12 sm:w-16 sm:h-16 bg-sea-200 rounded-full opacity-30 floating" style={{animationDelay: '2s'}}></div>
      
      <div className="w-full max-w-sm sm:max-w-md space-y-6 sm:space-y-8 relative z-10">
        <div className="text-center">
          {/* Logo mediterráneo */}
          <div className="mx-auto h-16 w-16 sm:h-20 sm:w-20 bg-gradient-to-br from-market-500 to-market-600 rounded-2xl flex items-center justify-center shadow-xl pulse-glow">
            <div className="flex items-center space-x-1">
              <ShoppingBag className="h-6 w-6 sm:h-8 sm:w-8 text-white" />
              <Leaf className="h-4 w-4 sm:h-6 sm:w-6 text-olive-200" />
            </div>
          </div>
          
          <h2 className="mt-6 sm:mt-8 text-center text-2xl sm:text-4xl font-bold text-gray-900 font-display">
            Benvingut al
          </h2>
          <h1 className="text-center text-3xl sm:text-5xl font-bold bg-gradient-to-r from-market-600 to-olive-600 bg-clip-text text-transparent font-display">
            Mercat Mediterrani
          </h1>
          <p className="mt-3 sm:mt-4 text-center text-base sm:text-lg text-gray-600 font-medium px-2">
            Descobreix els productes frescos del nostre mercat
          </p>
          <p className="mt-4 sm:mt-6 text-center text-sm text-gray-600">
            No tens compte?{' '}
            <Link
              to="/register"
              className="font-semibold text-market-600 hover:text-market-700 transition-colors"
            >
              Registra't aquí
            </Link>
          </p>
        </div>
        
        <div className="card">
          <form className="space-y-5 sm:space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-3 sm:p-4 flex items-center space-x-3">
                <AlertCircle className="h-4 w-4 sm:h-5 sm:w-5 text-red-400 flex-shrink-0" />
                <span className="text-red-800 text-sm">{error}</span>
              </div>
            )}
            
            <div className="space-y-4 sm:space-y-5">
              <div>
                <label htmlFor="email" className="block text-sm font-semibold text-gray-700 mb-2">
                  Correu electrònic
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 sm:pl-4 flex items-center pointer-events-none">
                    <Mail className="h-4 w-4 sm:h-5 sm:w-5 text-market-400" />
                  </div>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="card-market w-full pl-10 sm:pl-12 pr-4 py-3 border-0 focus:ring-2 focus:ring-market-500 focus:ring-opacity-50"
                    placeholder="el@teu.cat"
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="password" className="block text-sm font-semibold text-gray-700 mb-2">
                  Contrasenya
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 sm:pl-4 flex items-center pointer-events-none">
                    <Lock className="h-4 w-4 sm:h-5 sm:w-5 text-market-400" />
                  </div>
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="card-market w-full pl-10 sm:pl-12 pr-10 sm:pr-12 py-3 border-0 focus:ring-2 focus:ring-market-500 focus:ring-opacity-50"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 sm:pr-4 flex items-center hover:text-market-600 transition-colors"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 sm:h-5 sm:w-5" />
                    ) : (
                      <Eye className="h-4 w-4 sm:h-5 sm:w-5" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="card-market w-full flex justify-center py-4 text-base sm:text-lg font-semibold bg-gradient-to-r from-market-500 to-market-600 hover:from-market-600 hover:to-market-700 text-white transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-5 w-5 sm:h-6 sm:w-6 border-b-2 border-white"></div>
                ) : (
                  'Entrar al Mercat'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login; 