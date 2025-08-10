import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Eye, EyeOff, Mail, Lock, User, AlertCircle } from 'lucide-react';

const Register: React.FC = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    username: '',
    role: 'user' as 'user' | 'vendor' | 'admin'
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Les contrasenyes no coincideixen');
      return;
    }

    if (formData.password.length < 6) {
      setError('La contrasenya ha de tenir almenys 6 caràcters');
      return;
    }

    setLoading(true);

    try {
      await register(formData.email, formData.password, formData.username, formData.role);
      if (formData.role === 'vendor') {
        navigate('/vendor/login');
      } else if (formData.role === 'admin') {
        navigate('/admin');
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
    <div className="min-h-screen relative overflow-hidden">
      {/* Fondo decorativo mediterráneo */}
      <div className="absolute inset-0 bg-gradient-to-br from-sea-50 via-white to-olive-50"></div>
      <div className="absolute top-20 right-10 w-40 h-40 bg-market-200 rounded-full opacity-10 floating"></div>
      <div className="absolute bottom-20 left-10 w-32 h-32 bg-olive-200 rounded-full opacity-10 floating" style={{animationDelay: '1s'}}></div>
      
      <div className="relative z-10 flex items-center justify-center min-h-screen py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div>
            <div className="mx-auto h-16 w-16 bg-gradient-to-br from-market-500 to-market-600 rounded-2xl flex items-center justify-center shadow-lg">
              <div className="flex items-center space-x-1">
                <span className="text-white text-2xl font-bold">M</span>
                <div className="w-2 h-2 bg-olive-200 rounded-full"></div>
              </div>
            </div>
            <h2 className="mt-6 text-center text-3xl sm:text-4xl font-bold bg-gradient-to-r from-market-600 to-olive-600 bg-clip-text text-transparent font-display">
              Crear Compte
            </h2>
            <p className="mt-2 text-center text-base sm:text-lg text-gray-600">
              Mercat Mediterrani
            </p>
            <p className="mt-4 text-center text-sm sm:text-base text-gray-600">
              Ja tens compte?{' '}
              <Link
                to="/login"
                className="font-medium text-market-600 hover:text-market-500 transition-colors"
              >
                Inicia sessió aquí
              </Link>
            </p>
          </div>
          
          <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="card bg-red-50 border border-red-200 p-4 flex items-center space-x-2">
                <AlertCircle className="h-5 w-5 text-red-400" />
                <span className="text-red-800 text-sm">{error}</span>
              </div>
            )}
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-market-700 mb-2">
                  Tipus de compte
                </label>
                <div className="grid grid-cols-3 gap-3">
                  <button
                    type="button"
                    onClick={() => setFormData({ ...formData, role: 'user' })}
                    className={`card-market py-2 ${formData.role === 'user' ? 'ring-2 ring-market-500' : ''}`}
                  >
                    Usuari
                  </button>
                  <button
                    type="button"
                    onClick={() => setFormData({ ...formData, role: 'vendor' })}
                    className={`card-market py-2 ${formData.role === 'vendor' ? 'ring-2 ring-market-500' : ''}`}
                  >
                    Venedor
                  </button>
                  <button
                    type="button"
                    onClick={() => setFormData({ ...formData, role: 'admin' })}
                    className={`card-market py-2 ${formData.role === 'admin' ? 'ring-2 ring-market-500' : ''}`}
                  >
                    Admin
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-1">Si tries Venedor, accediràs al panell de venedor. Si tries Admin, accediràs al panell d'admin.</p>
              </div>
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-market-700 mb-2">
                  Nom d'usuari
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <User className="h-5 w-5 text-market-400" />
                  </div>
                  <input
                    id="username"
                    name="username"
                    type="text"
                    autoComplete="username"
                    required
                    value={formData.username}
                    onChange={handleChange}
                    className="card-market w-full pl-10 pr-4 py-3 border-0 focus:ring-2 focus:ring-market-500 focus:ring-opacity-50"
                    placeholder="El teu nom d'usuari"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-market-700 mb-2">
                  Correu electrònic
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-market-400" />
                  </div>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={formData.email}
                    onChange={handleChange}
                    className="card-market w-full pl-10 pr-4 py-3 border-0 focus:ring-2 focus:ring-market-500 focus:ring-opacity-50"
                    placeholder="el@teu.cat"
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-market-700 mb-2">
                  Contrasenya
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-market-400" />
                  </div>
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="new-password"
                    required
                    value={formData.password}
                    onChange={handleChange}
                    className="card-market w-full pl-10 pr-10 py-3 border-0 focus:ring-2 focus:ring-market-500 focus:ring-opacity-50"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center hover:text-market-600 transition-colors"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5 text-market-400" />
                    ) : (
                      <Eye className="h-5 w-5 text-market-400" />
                    )}
                  </button>
                </div>
              </div>

              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-market-700 mb-2">
                  Confirmar contrasenya
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-market-400" />
                  </div>
                  <input
                    id="confirmPassword"
                    name="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    autoComplete="new-password"
                    required
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    className="card-market w-full pl-10 pr-10 py-3 border-0 focus:ring-2 focus:ring-market-500 focus:ring-opacity-50"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center hover:text-market-600 transition-colors"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-5 w-5 text-market-400" />
                    ) : (
                      <Eye className="h-5 w-5 text-market-400" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="card-market w-full flex justify-center py-4 text-base font-medium bg-gradient-to-r from-market-500 to-market-600 hover:from-market-600 hover:to-market-700 text-white transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                ) : (
                  'Crear Compte'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Register; 