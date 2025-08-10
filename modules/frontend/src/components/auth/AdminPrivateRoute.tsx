import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface AdminPrivateRouteProps {
  children: React.ReactNode;
}

const AdminPrivateRoute: React.FC<AdminPrivateRouteProps> = ({ children }) => {
  const { user, token, loading } = useAuth();
  const location = useLocation();

  if (loading) return null;

  if (!token || !user || user.role !== 'admin') {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export default AdminPrivateRoute;


