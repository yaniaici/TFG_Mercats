const GAMIFICATION_API_URL = process.env.REACT_APP_ENVIRONMENT === 'production' 
  ? 'http://mercatmediterrani.com:8005' 
  : 'http://localhost:8005';

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

// Nuevas interfaces para recompensas
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

  // Nuevos métodos para recompensas

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
      const errorMessage = error.response?.data?.detail || 'Error canviant recompensa';
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
}

export const gamificationService = new GamificationService(); 