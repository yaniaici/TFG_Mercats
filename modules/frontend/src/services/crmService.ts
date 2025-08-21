import axios from 'axios';

const crmApi = axios.create({ 
  baseURL: process.env.REACT_APP_ENVIRONMENT === 'production' 
    ? 'http://mercatmediterrani.com:8006' 
    : 'http://localhost:8006'
});

export const setCrmToken = (token: string | null) => {
  if (token) crmApi.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  else delete crmApi.defaults.headers.common['Authorization'];
};

// Segments
export const createSegment = async (payload: any) => {
  const { data } = await crmApi.post('/segments', payload);
  return data;
};
export const listSegments = async () => {
  const { data } = await crmApi.get('/segments');
  return data;
};
export const previewSegmentUsers = async (segmentId: string, limit = 100) => {
  const { data } = await crmApi.post(`/segments/${segmentId}/preview-users?limit=${limit}`);
  return data as string[];
};

// Campaigns
export const createCampaign = async (payload: any) => {
  const { data } = await crmApi.post('/campaigns', payload);
  return data;
};
export const listCampaigns = async () => {
  const { data } = await crmApi.get('/campaigns');
  return data;
};
export const previewCampaignUsers = async (campaignId: string, limit = 100) => {
  const { data } = await crmApi.post(`/campaigns/${campaignId}/preview-users?limit=${limit}`);
  return data as string[];
};
export const dispatchCampaign = async (campaignId: string) => {
  const { data } = await crmApi.post(`/campaigns/${campaignId}/dispatch`);
  return data;
};

// Notifications
export const listNotifications = async (status?: string) => {
  const { data } = await crmApi.get(`/notifications${status ? `?status=${status}` : ''}`);
  return data;
};
export const markNotificationSent = async (notificationId: string, deliveryInfo: any = {}) => {
  const { data } = await crmApi.post(`/notifications/${notificationId}/mark-sent`, { delivery_info: deliveryInfo });
  return data;
};


