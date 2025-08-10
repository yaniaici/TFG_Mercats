import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

// API del auth-service
const authApi = axios.create({
  baseURL: 'http://localhost:8001'
});

authApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('vendor_token');
      window.location.href = '/vendor/login';
    }
    return Promise.reject(error);
  }
);

interface VendorUser {
  id: string;
  email: string;
  preferences?: { [key: string]: any };
}

interface VendorAuthContextType {
  vendor: VendorUser | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const VendorAuthContext = createContext<VendorAuthContextType | undefined>(undefined);

export const useVendorAuth = () => {
  const context = useContext(VendorAuthContext);
  if (context === undefined) {
    throw new Error('useVendorAuth debe usarse dentro de un VendorAuthProvider');
  }
  return context;
};

interface VendorAuthProviderProps { children: ReactNode }

export const VendorAuthProvider: React.FC<VendorAuthProviderProps> = ({ children }) => {
  const [vendor, setVendor] = useState<VendorUser | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('vendor_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      authApi.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      verifyToken();
    } else {
      setLoading(false);
    }
  }, [token]);

  const verifyToken = async () => {
    try {
      const response = await authApi.get('/users/me');
      // Verificar rol en preferences.role === 'vendor'
      const data = response.data as VendorUser;
      const role = (data as any)?.preferences?.role;
      if (role !== 'vendor') {
        throw new Error('No autorizado como vendedor');
      }
      setVendor(data);
      setLoading(false);
    } catch (error) {
      logout();
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const response = await authApi.post('/auth/login', { email, password });
    const { access_token, user } = response.data;
    // Exigir rol vendedor
    const role = user?.preferences?.role;
    if (role !== 'vendor') {
      throw new Error('Este usuario no tiene rol de vendedor');
    }
    setToken(access_token);
    setVendor(user);
    localStorage.setItem('vendor_token', access_token);
    authApi.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
  };

  const logout = () => {
    setVendor(null);
    setToken(null);
    localStorage.removeItem('vendor_token');
    delete authApi.defaults.headers.common['Authorization'];
  };

  const value: VendorAuthContextType = {
    vendor,
    token,
    login,
    logout,
    loading,
  };

  return (
    <VendorAuthContext.Provider value={value}>{children}</VendorAuthContext.Provider>
  );
};


