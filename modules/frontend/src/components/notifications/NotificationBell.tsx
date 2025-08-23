import React, { useState, useEffect } from 'react';
import { Bell, X, Check } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { gamificationService, UserNotification, AllNotificationStats } from '../../services/gamificationService';

interface NotificationBellProps {
  className?: string;
}

const NotificationBell: React.FC<NotificationBellProps> = ({ className = '' }) => {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<UserNotification[]>([]);
  const [stats, setStats] = useState<AllNotificationStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user?.id) {
      loadNotifications();
      loadStats();
    }
  }, [user?.id]);

  const loadNotifications = async () => {
    if (!user?.id) return;

    try {
      setLoading(true);
      setError(null);
      const data = await gamificationService.getAllUserNotifications(user.id, 20, 0);
      setNotifications(data);
    } catch (err) {
      console.error('Error carregant notificacions:', err);
      setError('No es van poder carregar les notificacions');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    if (!user?.id) return;

    try {
      const data = await gamificationService.getAllNotificationStats(user.id);
      setStats(data);
    } catch (err) {
      console.error('Error carregant estadístiques de notificacions:', err);
    }
  };

  const handleMarkAsRead = async (notificationId: string) => {
    if (!user?.id) return;

    try {
      await gamificationService.markNotificationAsRead(user.id, notificationId);
      setNotifications(prev => prev.map(n => 
        n.id === notificationId ? { ...n, is_read: true, read_at: new Date().toISOString() } : n
      ));
      loadStats();
    } catch (err) {
      console.error('Error marcant notificació com a llegida:', err);
    }
  };

  const handleMarkAllAsRead = async () => {
    if (!user?.id) return;

    try {
      await gamificationService.markAllNotificationsAsRead(user.id);
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true, read_at: new Date().toISOString() })));
      loadStats();
    } catch (err) {
      console.error('Error marcant totes les notificacions com a llegides:', err);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'reward':
        return '🎁';
      case 'special_reward':
        return '⭐';
      case 'system':
        return '🔧';
      case 'promotion':
        return '📢';
      case 'campaign':
        return '📢';
      case 'news':
        return '📰';
      case 'update':
        return '🔄';
      default:
        return '📌';
    }
  };

  const getNotificationTypeLabel = (type: string) => {
    switch (type) {
      case 'reward':
        return 'Recompensa';
      case 'special_reward':
        return 'Recompensa Especial';
      case 'system':
        return 'Sistema';
      case 'promotion':
        return 'Promoció';
      case 'campaign':
        return 'Campaña';
      case 'news':
        return 'Notícies';
      case 'update':
        return 'Actualització';
      default:
        return 'Notificació';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) {
      return 'Ara mateix';
    } else if (diffInHours < 24) {
      return `Fa ${diffInHours} h`;
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return `Fa ${diffInDays} dies`;
    }
  };

  const unreadCount = stats?.unread_notifications || 0;

  return (
    <div className={`relative ${className}`}>
      {/* Botón de la campanita */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-900 transition-colors"
        aria-label="Centre de notificacions"
      >
        <Bell className="h-6 w-6" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {/* Panel de notificaciones */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Centre de Notificacions</h3>
            <div className="flex items-center space-x-2">
              {unreadCount > 0 && (
                <button
                  onClick={handleMarkAllAsRead}
                  className="text-sm text-market-600 hover:text-market-700 transition-colors"
                >
                  Marcar totes com a llegides
                </button>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Contenido */}
          <div className="max-h-96 overflow-y-auto">
            {loading ? (
              <div className="p-4 text-center text-gray-500">
                Carregant notificacions...
              </div>
            ) : error ? (
              <div className="p-4 text-center text-red-500">
                {error}
              </div>
            ) : notifications.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                No tens notificacions
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={`p-4 hover:bg-gray-50 transition-colors ${
                      !notification.is_read ? 'bg-blue-50' : ''
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 text-2xl">
                        {getNotificationIcon(notification.notification_type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-1">
                              <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                                {getNotificationTypeLabel(notification.notification_type)}
                              </span>
                            </div>
                            <p className={`text-sm font-medium ${
                              !notification.is_read ? 'text-gray-900' : 'text-gray-700'
                            }`}>
                              {notification.title}
                            </p>
                            <p className="text-sm text-gray-600 mt-1">
                              {notification.message}
                            </p>
                            <p className="text-xs text-gray-400 mt-2">
                              {formatDate(notification.created_at)}
                            </p>
                          </div>
                          {!notification.is_read && (
                            <button
                              onClick={() => handleMarkAsRead(notification.id)}
                              className="flex-shrink-0 ml-2 p-1 text-gray-400 hover:text-green-600 transition-colors"
                              title="Marcar com a llegida"
                            >
                              <Check className="h-4 w-4" />
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="p-3 border-t border-gray-200 bg-gray-50">
              <div className="text-xs text-gray-500 text-center">
                {stats?.total_notifications || 0} notificacions totals
                {unreadCount > 0 && ` • ${unreadCount} no llegides`}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Overlay para cerrar al hacer clic fuera */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default NotificationBell;
