// Configuración centralizada de URLs de la API
const BASE_URL = process.env.REACT_APP_ENVIRONMENT === 'production' 
  ? 'http://mercatmediterrani.com' 
  : 'http://localhost';

export const API_CONFIG = {
  // URLs base según el entorno
  AUTH_SERVICE_URL: `${BASE_URL}:8001`,
  BACKEND_URL: `${BASE_URL}:8000`,
  TICKET_SERVICE_URL: `${BASE_URL}:8003`,
  GAMIFICATION_SERVICE_URL: `${BASE_URL}:8005`,
  CRM_SERVICE_URL: `${BASE_URL}:8006`,
  NOTIFICATION_SERVICE_URL: `${BASE_URL}:8007`,
  
  // Entorno
  ENVIRONMENT: process.env.REACT_APP_ENVIRONMENT || 'development',
  
  // Función helper para obtener URL completa
  getUrl: (service: keyof typeof API_CONFIG, endpoint: string = '') => {
    const baseUrl = API_CONFIG[service];
    return endpoint ? `${baseUrl}${endpoint}` : baseUrl;
  }
};

// Función para verificar si estamos en producción
export const isProduction = () => API_CONFIG.ENVIRONMENT === 'production';

// Función para obtener la URL base según el entorno
export const getBaseUrl = () => BASE_URL;
