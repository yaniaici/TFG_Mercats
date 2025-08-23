import { API_CONFIG } from '../config/api';

const GAMIFICATION_API_URL = API_CONFIG.GAMIFICATION_SERVICE_URL;

export interface GamificationStats {
  level: number;
  experience: number;
  next_level_experience: number;
  experience_to_next_level: number;
  progress_percentage: number;
  total_tickets: number;
  valid_tickets: number;
  total_spent: number;
  streak_days: number;
  badges_earned: number;
  recent_badges: UserBadge[];
}

export interface UserBadge {
  id: string;
  user_id: string;
  badge_type: string;
  badge_name: string;
  badge_description: string;
  earned_at: string;
  is_active: boolean;
}

export interface ExperienceLog {
  id: string;
  user_id: string;
  ticket_id?: string;
  experience_gained: number;
  reason: string;
  created_at: string;
}

// Interfaces para recompensas normales
export interface Reward {
  id: string;
  name: string;
  description: string;
  points_cost: number;
  reward_type: string;
  reward_value: string;
  is_active: boolean;
  max_redemptions?: number;
  current_redemptions: number;
  created_at: string;
  updated_at: string;
}

export interface RewardRedemption {
  id: string;
  user_id: string;
  reward_id: string;
  points_spent: number;
  redemption_code: string;
  is_used: boolean;
  used_at?: string;
  expires_at?: string;
  created_at: string;
  updated_at: string;
  reward_name: string;
  reward_description: string;
  reward_type: string;
  reward_value: string;
}

export interface RedeemRewardResponse {
  message: string;
  redemption_code: string;
  reward_name: string;
  points_spent: number;
  remaining_points: number;
  expires_at: string;
}

// Interfaces para recompensas especiales
export interface SpecialReward {
  id: string;
  name: string;
  description: string;
  reward_type: string;
  reward_value: string;
  is_global: boolean;
  target_users: string[];
  target_segments: string[];
  max_redemptions?: number;
  expires_at?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SpecialRewardRedemption {
  id: string;
  user_id: string;
  special_reward_id: string;
  redemption_code: string;
  is_used: boolean;
  used_at?: string;
  created_at: string;
  updated_at: string;
  special_reward: SpecialReward;
}

export interface SpecialRewardWithStatus {
  reward: SpecialReward;
  is_redeemed: boolean;
  is_available: boolean;
  is_expired: boolean;
  redemption_count: number;
  can_redeem: boolean;
  last_redemption?: SpecialRewardRedemption;
}

export interface RedeemSpecialRewardResponse {
  message: string;
  redemption_code: string;
  created_at: string;
}

// Interfaces para notificaciones personales
export interface UserNotification {
  id: string;
  user_id: string;
  title: string;
  message: string;
  notification_type: string;
  is_read: boolean;
  related_id?: string;
  created_at: string;
  read_at?: string;
}

export interface NotificationStats {
  total_notifications: number;
  unread_notifications: number;
  type_counts?: {
    [key: string]: {
      total: number;
      unread: number;
    };
  };
}

export interface AllNotificationStats {
  total_notifications: number;
  unread_notifications: number;
  type_counts: {
    [key: string]: {
      total: number;
      unread: number;
    };
  };
}

// Interfaces para el admin
export interface SpecialRewardDistributionRequest {
  special_reward_id: string;
  target_type: 'global' | 'users' | 'segments';
  target_ids: string[];
  send_notifications: boolean;
}

export interface SpecialRewardDistributionResponse {
  success: boolean;
  message: string;
  users_affected: number;
  notifications_sent: number;
}

class GamificationService {
  private baseUrl = GAMIFICATION_API_URL;

  private async request<T>(path: string, init?: RequestInit): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) },
      ...init,
    });
    if (!res.ok) {
      let detail = '';
      try {
        const data = await res.json();
        detail = data?.detail || JSON.stringify(data);
      } catch {}
      throw new Error(detail || `HTTP ${res.status}`);
    }
    return (await res.json()) as T;
  }

  /**
   * Obtiene las estadísticas de gamificación del usuario
   */
  async getUserStats(userId: string): Promise<GamificationStats> {
    try {
      return await this.request<GamificationStats>(`/users/${userId}/stats`);
    } catch (error) {
      console.error('Error obtenint estadístiques de gamificació:', error);
      throw new Error('No es van poder obtenir les estadístiques de gamificació');
    }
  }

  /**
   * Obtiene las insignias del usuario
   */
  async getUserBadges(userId: string): Promise<UserBadge[]> {
    try {
      return await this.request<UserBadge[]>(`/users/${userId}/badges`);
    } catch (error) {
      console.error('Error obtenint insígnies:', error);
      throw new Error('No es van poder obtenir les insígnies');
    }
  }

  /**
   * Obtiene el historial de experiencia del usuario
   */
  async getUserExperienceLog(userId: string, limit: number = 20): Promise<ExperienceLog[]> {
    try {
      return await this.request<ExperienceLog[]>(`/users/${userId}/experience-log?limit=${limit}`);
    } catch (error) {
      console.error('Error obtenint historial d\'experiència:', error);
      throw new Error('No es va poder obtenir l\'historial d\'experiència');
    }
  }

  /**
   * Verifica la salud del servicio de gamificación
   */
  async checkHealth(): Promise<boolean> {
    try {
      await this.request<any>('/health');
      return true;
    } catch (error) {
      console.error('Servei de gamificació no disponible:', error);
      return false;
    }
  }

  // Métodos para recompensas normales

  /**
   * Obtiene todas las recompensas disponibles
   */
  async getRewards(): Promise<Reward[]> {
    try {
      return await this.request<Reward[]>('/rewards');
    } catch (error) {
      console.error('Error obtenint recompenses:', error);
      throw new Error('No es van poder obtenir les recompenses');
    }
  }

  /**
   * Obtiene una recompensa específica
   */
  async getReward(rewardId: string): Promise<Reward> {
    try {
      return await this.request<Reward>(`/rewards/${rewardId}`);
    } catch (error) {
      console.error('Error obtenint recompensa:', error);
      throw new Error('No es va poder obtenir la recompensa');
    }
  }

  /**
   * Canjea una recompensa
   */
  async redeemReward(userId: string, rewardId: string): Promise<RedeemRewardResponse> {
    try {
      return await this.request<RedeemRewardResponse>(`/users/${userId}/redeem-reward/${rewardId}`, { method: 'POST' });
    } catch (error: any) {
      console.error('Error canviant recompensa:', error);
      const errorMessage = error.response?.data?.detail || 'Error变更 recompensa';
      throw new Error(errorMessage);
    }
  }

  /**
   * Obtiene el historial de canjes del usuario
   */
  async getUserRedemptions(userId: string): Promise<RewardRedemption[]> {
    try {
      return await this.request<RewardRedemption[]>(`/users/${userId}/redemptions`);
    } catch (error) {
      console.error('Error obtenint historial de canjes:', error);
      throw new Error('No es va poder obtenir l\'historial de canjes');
    }
  }

  /**
   * Marca una recompensa como utilizada
   */
  async useRedemption(redemptionCode: string): Promise<{ message: string; used_at: string }> {
    try {
      return await this.request<{ message: string; used_at: string }>(`/redemptions/${redemptionCode}/use`, { method: 'POST' });
    } catch (error: any) {
      console.error('Error utilitzant recompensa:', error);
      const errorMessage = error.response?.data?.detail || 'Error utilitzant recompensa';
      throw new Error(errorMessage);
    }
  }

  /**
   * Valida un código de canje sin consumirlo
   */
  async validateRedemption(redemptionCode: string): Promise<{
    valid: boolean;
    message: string;
    rewardName?: string;
    rewardDescription?: string;
    usedAt?: string;
    expiresAt?: string;
  }> {
    try {
      const d = await this.request<any>(`/redemptions/${redemptionCode}`);
      return {
        valid: d.valid,
        message: d.message,
        rewardName: d.reward_name,
        rewardDescription: d.reward_description,
        usedAt: d.used_at,
        expiresAt: d.expires_at,
      };
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Error validant recompensa';
      throw new Error(message);
    }
  }

  // Métodos para recompensas especiales

  /**
   * Obtiene todas las recompensas especiales disponibles
   */
  async getSpecialRewards(): Promise<SpecialReward[]> {
    try {
      return await this.request<SpecialReward[]>('/special-rewards');
    } catch (error) {
      console.error('Error obtenint recompenses especials:', error);
      throw new Error('No es van poder obtenir les recompenses especials');
    }
  }

  /**
   * Obtiene las recompensas especiales disponibles para un usuario específico
   */
  async getUserSpecialRewards(userId: string, userSegments: string[] = []): Promise<SpecialReward[]> {
    try {
      const segmentsParam = userSegments.map(s => `user_segments=${encodeURIComponent(s)}`).join('&');
      const url = `/users/${userId}/special-rewards${segmentsParam ? `?${segmentsParam}` : ''}`;
      return await this.request<SpecialReward[]>(url);
    } catch (error) {
      console.error('Error obtenint recompenses especials de l\'usuari:', error);
      throw new Error('No es van poder obtenir les recompenses especials');
    }
  }

  /**
   * Obtiene todas las recompensas especiales del usuario con información de estado
   */
  async getUserSpecialRewardsWithStatus(userId: string, userSegments: string[] = []): Promise<SpecialRewardWithStatus[]> {
    try {
      const segmentsParam = userSegments.map(s => `user_segments=${encodeURIComponent(s)}`).join('&');
      const url = `/users/${userId}/special-rewards-with-status${segmentsParam ? `?${segmentsParam}` : ''}`;
      return await this.request<SpecialRewardWithStatus[]>(url);
    } catch (error) {
      console.error('Error obtenint recompenses especials amb estat de l\'usuari:', error);
      throw new Error('No es van poder obtenir les recompenses especials amb estat');
    }
  }

  /**
   * Crea una nueva recompensa especial (solo admin)
   */
  async createSpecialReward(rewardData: Omit<SpecialReward, 'id' | 'created_at' | 'updated_at'>): Promise<SpecialReward> {
    try {
      return await this.request<SpecialReward>('/special-rewards', {
        method: 'POST',
        body: JSON.stringify(rewardData)
      });
    } catch (error) {
      console.error('Error creant recompensa especial:', error);
      throw new Error('No es va poder crear la recompensa especial');
    }
  }

  /**
   * Canjea una recompensa especial
   */
  async redeemSpecialReward(userId: string, specialRewardId: string): Promise<RedeemSpecialRewardResponse> {
    try {
      return await this.request<RedeemSpecialRewardResponse>(`/users/${userId}/redeem-special-reward/${specialRewardId}`, { 
        method: 'POST' 
      });
    } catch (error: any) {
      console.error('Error canviant recompensa especial:', error);
      const errorMessage = error.response?.data?.detail || 'Error变更 recompensa especial';
      throw new Error(errorMessage);
    }
  }

  /**
   * Distribuye una recompensa especial a múltiples usuarios (solo admin)
   */
  async distributeSpecialReward(request: SpecialRewardDistributionRequest): Promise<SpecialRewardDistributionResponse> {
    try {
      return await this.request<SpecialRewardDistributionResponse>('/special-rewards/distribute', {
        method: 'POST',
        body: JSON.stringify(request)
      });
    } catch (error) {
      console.error('Error distribuint recompensa especial:', error);
      throw new Error('No es va poder distribuir la recompensa especial');
    }
  }

  /**
   * Elimina una recompensa especial (solo admin)
   */
  async deleteSpecialReward(specialRewardId: string): Promise<{ success: boolean; message: string }> {
    try {
      return await this.request<{ success: boolean; message: string }>(`/special-rewards/${specialRewardId}`, {
        method: 'DELETE'
      });
    } catch (error) {
      console.error('Error eliminant recompensa especial:', error);
      throw new Error('No es va poder eliminar la recompensa especial');
    }
  }

  // Métodos para notificaciones personales

  /**
   * Obtiene las notificaciones personales del usuario
   */
  async getUserNotifications(
    userId: string, 
    limit: number = 50, 
    offset: number = 0, 
    unreadOnly: boolean = false
  ): Promise<UserNotification[]> {
    try {
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: offset.toString(),
        unread_only: unreadOnly.toString()
      });
      return await this.request<UserNotification[]>(`/users/${userId}/notifications?${params}`);
    } catch (error) {
      console.error('Error obtenint notificacions:', error);
      throw new Error('No es van poder obtenir les notificacions');
    }
  }

  /**
   * Obtiene estadísticas de notificaciones del usuario
   */
  async getNotificationStats(userId: string): Promise<NotificationStats> {
    try {
      return await this.request<NotificationStats>(`/users/${userId}/notifications/stats`);
    } catch (error) {
      console.error('Error obtenint estadístiques de notificacions:', error);
      throw new Error('No es van poder obtenir les estadístiques de notificacions');
    }
  }

  /**
   * Marca una notificación como leída
   */
  async markNotificationAsRead(userId: string, notificationId: string): Promise<UserNotification> {
    try {
      return await this.request<UserNotification>(`/users/${userId}/notifications/${notificationId}/read`, {
        method: 'POST'
      });
    } catch (error) {
      console.error('Error marcant notificació com a llegida:', error);
      throw new Error('No es va poder marcar la notificació com a llegida');
    }
  }

  /**
   * Marca todas las notificaciones del usuario como leídas
   */
  async markAllNotificationsAsRead(userId: string): Promise<{ message: string; notifications_updated: number }> {
    try {
      return await this.request<{ message: string; notifications_updated: number }>(`/users/${userId}/notifications/read-all`, {
        method: 'POST'
      });
    } catch (error) {
      console.error('Error marcant totes les notificacions com a llegides:', error);
      throw new Error('No es van poder marcar les notificacions com a llegides');
    }
  }

  /**
   * Crea una notificación personal para un usuario (solo admin)
   */
  async createUserNotification(
    userId: string,
    notificationData: Omit<UserNotification, 'id' | 'user_id' | 'created_at' | 'read_at'>
  ): Promise<UserNotification> {
    try {
      return await this.request<UserNotification>(`/users/${userId}/notifications`, {
        method: 'POST',
        body: JSON.stringify(notificationData)
      });
    } catch (error) {
      console.error('Error creant notificació personal:', error);
      throw new Error('No es va poder crear la notificació personal');
    }
  }

  // Métodos para centro unificado de notificaciones

  /**
   * Obtiene todas las notificaciones del usuario (centro unificado)
   */
  async getAllUserNotifications(
    userId: string,
    limit: number = 20,
    offset: number = 0,
    unreadOnly: boolean = false
  ): Promise<UserNotification[]> {
    try {
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: offset.toString(),
        unread_only: unreadOnly.toString()
      });
      return await this.request<UserNotification[]>(`/users/${userId}/all-notifications?${params}`);
    } catch (error) {
      console.error('Error obtenint totes les notificacions:', error);
      throw new Error('No es van poder obtenir totes les notificacions');
    }
  }

  /**
   * Obtiene estadísticas de todas las notificaciones del usuario
   */
  async getAllNotificationStats(userId: string): Promise<AllNotificationStats> {
    try {
      return await this.request<AllNotificationStats>(`/users/${userId}/all-notifications/stats`);
    } catch (error) {
      console.error('Error obtenint estadístiques completes de notificacions:', error);
      throw new Error('No es van poder obtenir les estadístiques completes de notificacions');
    }
  }
}

export const gamificationService = new GamificationService(); 