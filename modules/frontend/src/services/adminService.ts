import axios from 'axios';

const authApi = axios.create({ 
  baseURL: process.env.REACT_APP_ENVIRONMENT === 'production' 
    ? 'https://mercatmediterrani.com' 
    : 'http://localhost:8001'
});

export const setAdminToken = (token: string | null) => {
  if (token) authApi.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  else delete authApi.defaults.headers.common['Authorization'];
};

export const adminOverview = async () => {
  const { data } = await authApi.get('/admin/overview');
  return data as {
    total_users: number;
    total_vendors: number;
    total_admins: number;
    total_purchases: number;
    total_spent: number;
  };
};

export const listUsers = async (limit = 50, offset = 0) => {
  const { data } = await authApi.get(`/admin/users?limit=${limit}&offset=${offset}`);
  return data;
};

export const listVendors = async (limit = 50, offset = 0) => {
  const { data } = await authApi.get(`/admin/vendors?limit=${limit}&offset=${offset}`);
  return data;
};

export const promoteToVendor = async (userId: string) => {
  const { data } = await authApi.post(`/admin/users/${userId}/promote-vendor`);
  return data;
};

export const promoteToAdmin = async (userId: string) => {
  const { data } = await authApi.post(`/admin/users/${userId}/promote-admin`);
  return data;
};

export const userPurchaseSummaryAdmin = async (userId: string) => {
  const { data } = await authApi.get(`/admin/users/${userId}/purchase-summary`);
  return data;
};

export const userPurchaseHistoryAdmin = async (userId: string, limit = 50, offset = 0) => {
  const { data } = await authApi.get(`/admin/users/${userId}/purchase-history?limit=${limit}&offset=${offset}`);
  return data;
};


