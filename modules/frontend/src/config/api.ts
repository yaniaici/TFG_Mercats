// Configuración centralizada de URLs de la API
console.log('REACT_APP_ENVIRONMENT:', process.env.REACT_APP_ENVIRONMENT);

// Detectar si estamos en producción basándonos en el hostname también
const isProductionEnv = process.env.REACT_APP_ENVIRONMENT === 'production' || 
                       window.location.hostname === 'mercatmediterrani.com' ||
                       window.location.hostname === 'www.mercatmediterrani.com';

const BASE_URL = isProductionEnv 
  ? 'https://mercatmediterrani.com' 
  : 'http://localhost';

console.log('isProductionEnv:', isProductionEnv);
console.log('BASE_URL:', BASE_URL);

// Definir el tipo para la configuración
interface ApiConfig {
  AUTH_SERVICE_URL: string;
  BACKEND_URL: string;
  TICKET_SERVICE_URL: string;
  GAMIFICATION_SERVICE_URL: string;
  CRM_SERVICE_URL: string;
  NOTIFICATION_SERVICE_URL: string;
  ENVIRONMENT: string;
  getUrl: (service: keyof Omit<ApiConfig, 'getUrl' | 'ENVIRONMENT'>, endpoint?: string) => string;
}

export const API_CONFIG: ApiConfig = {
  // URLs base según el entorno
  // En producción: usar rutas de Nginx sin puertos
  // En desarrollo: usar puertos directos
  AUTH_SERVICE_URL: isProductionEnv 
    ? `${BASE_URL}/auth` 
    : `${BASE_URL}:8001`,
  BACKEND_URL: isProductionEnv 
    ? `${BASE_URL}/api` 
    : `${BASE_URL}:8000`,
  TICKET_SERVICE_URL: isProductionEnv 
    ? `${BASE_URL}/tickets` 
    : `${BASE_URL}:8003`,
  GAMIFICATION_SERVICE_URL: isProductionEnv 
    ? `${BASE_URL}/gamification` 
    : `${BASE_URL}:8005`,
  CRM_SERVICE_URL: isProductionEnv 
    ? `${BASE_URL}/crm` 
    : `${BASE_URL}:8006`,
  NOTIFICATION_SERVICE_URL: isProductionEnv 
    ? `${BASE_URL}/notifications` 
    : `${BASE_URL}:8007`,
  
  // Entorno
  ENVIRONMENT: isProductionEnv ? 'production' : 'development',
  
  // Función helper para obtener URL completa
  getUrl: (service, endpoint = '') => {
    const baseUrl = API_CONFIG[service];
    return endpoint ? `${baseUrl}${endpoint}` : baseUrl;
  }
};

// Función para verificar si estamos en producción
export const isProduction = () => API_CONFIG.ENVIRONMENT === 'production';

// Función para obtener la URL base según el entorno
export const getBaseUrl = () => BASE_URL;
