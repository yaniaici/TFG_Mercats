import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';
import { API_CONFIG } from '../config/api';
import { setCrmToken } from '../services/crmService';

// Crear instancia específica para auth-service
const authApi = axios.create({
  baseURL: API_CONFIG.AUTH_SERVICE_URL
});

// Interceptor para manejar errores de autenticación
authApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado, limpiar localStorage
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

interface User {
  id: string;
  email: string;
  username?: string;
  role: 'user' | 'vendor' | 'admin';
  preferences?: Record<string, any>;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<User>;
  register: (email: string, password: string, username: string, role?: 'user' | 'vendor' | 'admin') => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth ha de ser usat dins d\'un AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      // Configurar authApi con el token
      authApi.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      // Configurar token para otros servicios
      setCrmToken(token);
      
      // Verificar si el token es válido y obtener datos del usuario
      verifyToken();
    } else {
      setLoading(false);
      // Limpiar tokens de otros servicios
      setCrmToken(null);
    }
  }, [token]);

  const verifyToken = async () => {
    try {
      const response = await authApi.get('/users/me');
      setUser(response.data);
      setLoading(false);
    } catch (error: any) {
      console.error('Error verificant token:', error);
      
      // Si el token expiró (401), hacer logout
      if (error.response?.status === 401) {
        console.log('Token expirat, tancant sessió');
        logout();
      } else {
        // Para otros errores, mantener la sesión pero marcar como no cargado
        setLoading(false);
      }
    }
  };

  const login = async (email: string, password: string): Promise<User> => {
    try {
      const response = await authApi.post('/auth/login', {
        email: email, // El backend espera email
        password: password // El backend espera password
      });
      
      const { access_token, user: userData } = response.data;
      
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('token', access_token);
      authApi.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      return userData as User;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error en el login');
    }
  };

  const register = async (email: string, password: string, username: string, role: 'user' | 'vendor' | 'admin' = 'user') => {
    try {
      const response = await authApi.post('/auth/register', {
        email: email,
        password: password,
        preferences: { username },
        role
      });
      
      const { access_token, user: userData } = response.data;
      
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('token', access_token);
      authApi.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error en el registre');
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    delete authApi.defaults.headers.common['Authorization'];
  };

  const value = {
    user,
    token,
    login,
    register,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 