import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { VendorAuthProvider } from './contexts/VendorAuthContext';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import Dashboard from './components/dashboard/Dashboard';
import CreateTicket from './components/tickets/CreateTicket';
import TicketHistoryPage from './components/tickets/TicketHistoryPage';
import RewardsPage from './components/rewards/RewardsPage';
import RedemptionHistory from './components/rewards/RedemptionHistory';
import ValidateReward from './components/rewards/ValidateReward';
import VendorLogin from './components/auth/VendorLogin';
import VendorDashboard from './components/vendor/VendorDashboard';
import VendorPrivateRoute from './components/auth/VendorPrivateRoute';
import CRMHome from './components/vendor/CRMHome';
import Customers from './components/vendor/Customers';
import VendorStats from './components/vendor/VendorStats';
import VendorSettings from './components/vendor/VendorSettings';
import SendTicket from './components/vendor/SendTicket';
import PrivateRoute from './components/auth/PrivateRoute';
import AdminPrivateRoute from './components/auth/AdminPrivateRoute';
import AdminDashboard from './components/admin/AdminDashboard';

function App() {
  return (
    <AuthProvider>
      <VendorAuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Routes>
            <Route path="/vendor/login" element={<VendorLogin />} />
            <Route 
              path="/vendor/dashboard" 
              element={
                <VendorPrivateRoute>
                  <VendorDashboard />
                </VendorPrivateRoute>
              } 
            />
            <Route 
              path="/vendor/crm" 
              element={
                <VendorPrivateRoute>
                  <CRMHome />
                </VendorPrivateRoute>
              } 
            />
            <Route 
              path="/vendor/customers" 
              element={
                <VendorPrivateRoute>
                  <Customers />
                </VendorPrivateRoute>
              } 
            />
            <Route 
              path="/vendor/stats" 
              element={
                <VendorPrivateRoute>
                  <VendorStats />
                </VendorPrivateRoute>
              } 
            />
            <Route 
              path="/vendor/settings" 
              element={
                <VendorPrivateRoute>
                  <VendorSettings />
                </VendorPrivateRoute>
              } 
            />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            {/* Admin area - todo lo que esté bajo /admin exige rol admin */}
            <Route 
              path="/admin/*" 
              element={
                <AdminPrivateRoute>
                  <AdminDashboard />
                </AdminPrivateRoute>
              } 
            />
            <Route 
              path="/dashboard" 
              element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              } 
            />
            <Route 
              path="/create-ticket" 
              element={
                <PrivateRoute>
                  <CreateTicket />
                </PrivateRoute>
              } 
            />
            <Route 
              path="/ticket-history" 
              element={
                <PrivateRoute>
                  <TicketHistoryPage />
                </PrivateRoute>
              } 
            />
            <Route 
              path="/rewards" 
              element={
                <PrivateRoute>
                  <RewardsPage />
                </PrivateRoute>
              } 
            />
            <Route 
              path="/redemption-history" 
              element={
                <PrivateRoute>
                  <RedemptionHistory />
                </PrivateRoute>
              } 
            />
            <Route 
              path="/validate-reward/:redemptionCode" 
              element={
                <VendorPrivateRoute>
                  <ValidateReward />
                </VendorPrivateRoute>
              } 
            />
            <Route 
              path="/send-ticket/:userId" 
              element={
                <VendorPrivateRoute>
                  <SendTicket />
                </VendorPrivateRoute>
              } 
            />
            <Route path="/" element={<Navigate to="/login" replace />} />
          </Routes>
        </div>
      </Router>
      </VendorAuthProvider>
    </AuthProvider>
  );
}

export default App; 