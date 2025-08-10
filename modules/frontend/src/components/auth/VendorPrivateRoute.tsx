import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useVendorAuth } from '../../contexts/VendorAuthContext';

interface VendorPrivateRouteProps {
  children: React.ReactNode;
}

const VendorPrivateRoute: React.FC<VendorPrivateRouteProps> = ({ children }) => {
  const { token, loading } = useVendorAuth();
  const location = useLocation();

  if (loading) return null;

  if (!token) {
    return <Navigate to="/vendor/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export default VendorPrivateRoute;


