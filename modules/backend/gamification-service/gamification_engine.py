from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
import uuid
from sqlalchemy.orm import Session
from models import UserGamification, UserBadge, ExperienceLog, SpecialReward, SpecialRewardRedemption, UserNotification
from schemas import TicketProcessedEvent
import structlog

logger = structlog.get_logger()

class GamificationEngine:
    """Motor de gamificación que maneja la lógica de niveles, experiencia e insignias"""
    
    # Configuración de niveles (experiencia necesaria para cada nivel)
    LEVEL_EXPERIENCE = {
        1: 0,      # Nivel inicial
        2: 100,    # 100 XP
        3: 250,    # 250 XP
        4: 450,    # 450 XP
        5: 700,    # 700 XP
        6: 1000,   # 1000 XP
        7: 1350,   # 1350 XP
        8: 1750,   # 1750 XP
        9: 2200,   # 2200 XP
        10: 2700,  # 2700 XP
        # Continúa con más niveles...
    }
    
    # Configuración de insignias
    BADGES = {
        "first_scan": {
            "name": "Primer Escaneig",
            "description": "Has escanejat el teu primer tiquet",
            "condition": lambda stats: stats["total_tickets"] >= 1
        },
        "first_valid": {
            "name": "Primera Compra Vàlida",
            "description": "Has escanejat el teu primer tiquet vàlid",
            "condition": lambda stats: stats["valid_tickets"] >= 1
        },
        "ticket_collector": {
            "name": "Col·leccionista de Tiquets",
            "description": "Has escanejat 10 tiquets",
            "condition": lambda stats: stats["total_tickets"] >= 10
        },
        "valid_collector": {
            "name": "Col·leccionista Vàlid",
            "description": "Has escanejat 10 tiquets vàlids",
            "condition": lambda stats: stats["valid_tickets"] >= 10
        },
        "big_spender": {
            "name": "Gran Comprador",
            "description": "Has gastat més de 100€ en tiquets vàlids",
            "condition": lambda stats: stats["total_spent"] >= 100.0
        },
        "streak_3": {
            "name": "Ratxa de 3 Dies",
            "description": "Has escanejat tiquets durant 3 dies consecutius",
            "condition": lambda stats: stats["streak_days"] >= 3
        },
        "streak_7": {
            "name": "Ratxa de 7 Dies",
            "description": "Has escanejat tiquets durant 7 dies consecutius",
            "condition": lambda stats: stats["streak_days"] >= 7
        },
        "level_5": {
            "name": "Nivell 5",
            "description": "Has arribat al nivell 5",
            "condition": lambda stats: stats["level"] >= 5
        },
        "level_10": {
            "name": "Nivell 10",
            "description": "Has arribat al nivell 10",
            "condition": lambda stats: stats["level"] >= 10
        }
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_user_profile(self, user_id: uuid.UUID) -> UserGamification:
        """Obtiene o crea el perfil de gamificación del usuario"""
        profile = self.db.query(UserGamification).filter(UserGamification.user_id == user_id).first()
        
        if not profile:
            profile = UserGamification(
                user_id=user_id,
                level=1,
                experience=0,
                total_tickets=0,
                valid_tickets=0,
                total_spent=0.0,
                streak_days=0,
                badges_earned=0
            )
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
            
            logger.info("Perfil de gamificación creado", user_id=str(user_id))
        
        return profile
    
    def calculate_level(self, experience: int) -> Tuple[int, int, int, float]:
        """Calcula el nivel actual, experiencia para el siguiente nivel y progreso"""
        current_level = 1
        next_level_experience = 100
        
        # Encontrar el nivel actual
        for level, exp_required in self.LEVEL_EXPERIENCE.items():
            if experience >= exp_required:
                current_level = level
                # Buscar el siguiente nivel
                if level + 1 in self.LEVEL_EXPERIENCE:
                    next_level_experience = self.LEVEL_EXPERIENCE[level + 1]
                else:
                    # Si no hay siguiente nivel, usar el actual + 100
                    next_level_experience = exp_required + 100
        
        experience_to_next = next_level_experience - experience
        progress_percentage = min(100.0, (experience / next_level_experience) * 100) if next_level_experience > 0 else 100.0
        
        return current_level, next_level_experience, experience_to_next, progress_percentage
    
    def add_experience(self, user_id: uuid.UUID, experience_gained: int, reason: str, ticket_id: Optional[uuid.UUID] = None) -> UserGamification:
        """Añade experiencia al usuario y actualiza su nivel"""
        profile = self.get_or_create_user_profile(user_id)
        
        # Añadir experiencia
        old_level = profile.level
        profile.experience += experience_gained
        
        # Recalcular nivel
        new_level, next_level_exp, exp_to_next, progress = self.calculate_level(profile.experience)
        profile.level = new_level
        
        # Guardar log de experiencia
        experience_log = ExperienceLog(
            user_id=user_id,
            ticket_id=ticket_id,
            experience_gained=experience_gained,
            reason=reason
        )
        self.db.add(experience_log)
        
        # Verificar si subió de nivel
        level_up = new_level > old_level
        
        self.db.commit()
        self.db.refresh(profile)
        
        logger.info("Experiencia añadida", 
                   user_id=str(user_id),
                   experience_gained=experience_gained,
                   reason=reason,
                   old_level=old_level,
                   new_level=new_level,
                   level_up=level_up)
        
        return profile
    
    def process_ticket_event(self, event: TicketProcessedEvent) -> UserGamification:
        """Procesa un evento de ticket procesado y actualiza la gamificación"""
        profile = self.get_or_create_user_profile(event.user_id)
        
        # Actualizar contadores básicos
        profile.total_tickets += 1
        
        if event.is_valid:
            profile.valid_tickets += 1
            if event.total_amount:
                profile.total_spent += event.total_amount
        
        # Actualizar streak de días
        today = datetime.now(timezone.utc).date()
        if profile.last_scan_date:
            last_scan_date = profile.last_scan_date.date()
            if today == last_scan_date:
                # Ya escaneó hoy, no cambiar streak
                pass
            elif today == last_scan_date + timedelta(days=1):
                # Día consecutivo
                profile.streak_days += 1
            else:
                # Rompió la racha
                profile.streak_days = 1
        else:
            # Primera vez que escanea
            profile.streak_days = 1
        
        profile.last_scan_date = event.processing_date
        
        # Añadir experiencia
        experience_gained = 0
        reason = ""
        
        if event.is_valid:
            experience_gained = 50  # 50 XP por ticket válido
            reason = f"Ticket vàlid escanejat: {event.store_name or 'Tenda desconeguda'}"
            
            # Bonus por cantidad gastada
            if event.total_amount and event.total_amount > 50:
                bonus = int(event.total_amount / 10)  # 1 XP por cada 10€ gastados
                experience_gained += bonus
                reason += f" + {bonus} XP bonus per compra alta"
        else:
            # No se dan puntos por tickets inválidos
            experience_gained = 0
            reason = "Ticket invàlid escanejat (sense punts)"
        
        # Añadir experiencia solo si hay puntos que añadir
        if experience_gained > 0:
            profile = self.add_experience(event.user_id, experience_gained, reason, event.ticket_id)
        
        # Verificar insignias
        new_badges = self.check_and_award_badges(profile)
        
        # Actualizar contador de insignias
        profile.badges_earned = len(new_badges) + profile.badges_earned
        
        self.db.commit()
        self.db.refresh(profile)
        
        logger.info("Evento de ticket procesado", 
                   user_id=str(event.user_id),
                   ticket_id=str(event.ticket_id),
                   is_valid=event.is_valid,
                   experience_gained=experience_gained,
                   new_badges_count=len(new_badges))
        
        return profile
    
    def check_and_award_badges(self, profile: UserGamification) -> List[UserBadge]:
        """Verifica y otorga insignias al usuario"""
        new_badges = []
        
        # Obtener estadísticas actuales
        stats = {
            "total_tickets": profile.total_tickets,
            "valid_tickets": profile.valid_tickets,
            "total_spent": profile.total_spent,
            "streak_days": profile.streak_days,
            "level": profile.level
        }
        
        # Verificar cada insignia
        for badge_type, badge_config in self.BADGES.items():
            # Verificar si ya tiene esta insignia
            existing_badge = self.db.query(UserBadge).filter(
                UserBadge.user_id == profile.user_id,
                UserBadge.badge_type == badge_type,
                UserBadge.is_active == True
            ).first()
            
            if not existing_badge and badge_config["condition"](stats):
                # Otorgar nueva insignia
                new_badge = UserBadge(
                    user_id=profile.user_id,
                    badge_type=badge_type,
                    badge_name=badge_config["name"],
                    badge_description=badge_config["description"]
                )
                self.db.add(new_badge)
                new_badges.append(new_badge)
                
                logger.info("Nueva insignia otorgada", 
                           user_id=str(profile.user_id),
                           badge_type=badge_type,
                           badge_name=badge_config["name"])
        
        return new_badges
    
    def get_user_stats(self, user_id: uuid.UUID) -> dict:
        """Obtiene las estadísticas completas de gamificación del usuario"""
        profile = self.get_or_create_user_profile(user_id)
        
        # Calcular estadísticas de nivel
        level, next_level_exp, exp_to_next, progress = self.calculate_level(profile.experience)
        
        # Obtener insignias recientes (últimas 5)
        recent_badges = self.db.query(UserBadge).filter(
            UserBadge.user_id == user_id,
            UserBadge.is_active == True
        ).order_by(UserBadge.earned_at.desc()).limit(5).all()
        
        return {
            "level": level,
            "experience": profile.experience,
            "next_level_experience": next_level_exp,
            "experience_to_next_level": exp_to_next,
            "progress_percentage": progress,
            "total_tickets": profile.total_tickets,
            "valid_tickets": profile.valid_tickets,
            "total_spent": profile.total_spent,
            "streak_days": profile.streak_days,
            "badges_earned": profile.badges_earned,
            "recent_badges": recent_badges
        }

    # ========================================
    # MÉTODOS PARA RECOMPENSAS ESPECIALES
    # ========================================

    def create_special_reward(self, reward_data: dict) -> SpecialReward:
        """Crea una nueva recompensa especial"""
        special_reward = SpecialReward(**reward_data)
        self.db.add(special_reward)
        self.db.commit()
        self.db.refresh(special_reward)
        
        logger.info("Recompensa especial creada", 
                   reward_id=str(special_reward.id),
                   name=special_reward.name,
                   is_global=special_reward.is_global)
        
        return special_reward

    def get_available_special_rewards(self, user_id: uuid.UUID, user_segments: List[str] = None) -> List[SpecialReward]:
        """Obtiene las recompensas especiales disponibles para un usuario"""
        now = datetime.now(timezone.utc)
        
        # Obtener recompensas activas y no expiradas
        query = self.db.query(SpecialReward).filter(
            SpecialReward.is_active == True,
            (SpecialReward.expires_at == None) | (SpecialReward.expires_at > now)
        )
        
        available_rewards = []
        
        for reward in query.all():
            # Verificar si el usuario puede acceder a esta recompensa
            if self._can_user_access_special_reward(user_id, reward, user_segments):
                # Verificar si ya ha canjeado el máximo permitido
                if not self._has_user_reached_max_redemptions(user_id, reward):
                    available_rewards.append(reward)
        
        return available_rewards

    def get_all_user_special_rewards(self, user_id: uuid.UUID, user_segments: List[str] = None) -> List[dict]:
        """Obtiene todas las recompensas especiales del usuario con información de estado"""
        now = datetime.now(timezone.utc)
        
        # Obtener todas las recompensas especiales activas (incluyendo las expiradas)
        query = self.db.query(SpecialReward).filter(
            SpecialReward.is_active == True
        )
        
        all_rewards = []
        
        for reward in query.all():
            # Obtener información de canjes del usuario para esta recompensa
            redemptions = self.db.query(SpecialRewardRedemption).filter(
                SpecialRewardRedemption.user_id == user_id,
                SpecialRewardRedemption.special_reward_id == reward.id
            ).all()
            
            # Verificar si el usuario puede acceder a esta recompensa
            can_access = self._can_user_access_special_reward(user_id, reward, user_segments)
            
            # Determinar el estado de la recompensa
            # Una recompensa está "canjeada" solo si tiene al menos un canje marcado como usado
            used_redemptions = [r for r in redemptions if r.is_used]
            is_redeemed = len(used_redemptions) > 0
            is_available = not self._has_user_reached_max_redemptions(user_id, reward)
            is_expired = bool(reward.expires_at and reward.expires_at < now)
            
            # Obtener información del último canje usado si existe
            last_redemption = used_redemptions[-1] if used_redemptions else None
            
            reward_info = {
                "reward": reward,
                "is_redeemed": is_redeemed,
                "is_available": is_available,
                "is_expired": is_expired,
                "redemption_count": len(used_redemptions),  # Solo contar canjes usados
                "last_redemption": last_redemption,
                "can_redeem": can_access and is_available and not is_expired and len(redemptions) > 0 and not is_redeemed
            }
            
            all_rewards.append(reward_info)
        
        return all_rewards

    def _can_user_access_special_reward(self, user_id: uuid.UUID, reward: SpecialReward, user_segments: List[str] = None) -> bool:
        """Verifica si un usuario puede acceder a una recompensa especial"""
        user_id_str = str(user_id)
        
        # Si es global, todos pueden acceder
        if reward.is_global:
            return True
        
        # Verificar usuarios específicos
        if user_id_str in reward.target_users:
            return True
        
        # Verificar segmentos
        if user_segments and any(segment in reward.target_segments for segment in user_segments):
            return True
        
        # Verificar si el usuario ya tiene un registro de distribución para esta recompensa
        existing_redemption = self.db.query(SpecialRewardRedemption).filter(
            SpecialRewardRedemption.user_id == user_id,
            SpecialRewardRedemption.special_reward_id == reward.id
        ).first()
        
        if existing_redemption:
            return True
        
        return False

    def _has_user_reached_max_redemptions(self, user_id: uuid.UUID, reward: SpecialReward) -> bool:
        """Verifica si el usuario ha alcanzado el máximo de canjes para una recompensa especial"""
        if not reward.max_redemptions:
            return False
        
        # Solo contar canjes que han sido usados
        current_redemptions = self.db.query(SpecialRewardRedemption).filter(
            SpecialRewardRedemption.user_id == user_id,
            SpecialRewardRedemption.special_reward_id == reward.id,
            SpecialRewardRedemption.is_used == True
        ).count()
        
        return current_redemptions >= reward.max_redemptions

    def redeem_special_reward(self, user_id: uuid.UUID, special_reward_id: uuid.UUID) -> SpecialRewardRedemption:
        """Canjea una recompensa especial para un usuario"""
        # Verificar que la recompensa existe y está activa
        reward = self.db.query(SpecialReward).filter(
            SpecialReward.id == special_reward_id,
            SpecialReward.is_active == True
        ).first()
        
        if not reward:
            raise ValueError("Recompensa especial no encontrada o inactiva")
        
        # Verificar que no ha expirado
        if reward.expires_at and reward.expires_at < datetime.now(timezone.utc):
            raise ValueError("La recompensa especial ha expirado")
        
        # Verificar que no ha alcanzado el máximo de canjes
        if self._has_user_reached_max_redemptions(user_id, reward):
            raise ValueError("Has alcanzat el màxim de canjes per a aquesta recompensa")
        
        # Generar código único de canje
        redemption_code = f"SR{str(uuid.uuid4())[:8].upper()}"
        
        # Crear el canje
        redemption = SpecialRewardRedemption(
            user_id=user_id,
            special_reward_id=special_reward_id,
            redemption_code=redemption_code
        )
        
        self.db.add(redemption)
        self.db.commit()
        self.db.refresh(redemption)
        
        # Para recompensas especiales, marcarlas como usadas inmediatamente (un solo uso)
        redemption.is_used = True
        redemption.used_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(redemption)
        
        logger.info("Recompensa especial canjeada y marcada como usada", 
                   user_id=str(user_id),
                   reward_id=str(special_reward_id),
                   redemption_code=redemption_code)
        
        return redemption

    def distribute_special_reward(self, special_reward_id: uuid.UUID, target_users: List[uuid.UUID], send_notifications: bool = True) -> dict:
        """Distribuye una recompensa especial a una lista de usuarios"""
        reward = self.db.query(SpecialReward).filter(SpecialReward.id == special_reward_id).first()
        if not reward:
            raise ValueError("Recompensa especial no encontrada")
        
        users_affected = 0
        notifications_sent = 0
        
        for user_id in target_users:
            try:
                # Verificar que el usuario puede acceder y no ha alcanzado el máximo
                if not self._has_user_reached_max_redemptions(user_id, reward):
                    # Crear el registro de distribución (NO canje)
                    redemption_code = f"SR{str(uuid.uuid4())[:8].upper()}"
                    
                    redemption = SpecialRewardRedemption(
                        user_id=user_id,
                        special_reward_id=special_reward_id,
                        redemption_code=redemption_code,
                        is_used=False  # NO marcarlo como usado
                    )
                    
                    self.db.add(redemption)
                    self.db.commit()
                    self.db.refresh(redemption)
                    
                    users_affected += 1
                    
                    # Crear notificación si se solicita
                    if send_notifications:
                        self.create_user_notification(
                            user_id=user_id,
                            title="Nova recompensa especial!",
                            message=f"Has rebut una recompensa especial: {reward.name}",
                            notification_type="special_reward",
                            related_id=special_reward_id
                        )
                        notifications_sent += 1
                        
            except Exception as e:
                logger.error("Error distribuyendo recompensa especial", 
                           user_id=str(user_id),
                           reward_id=str(special_reward_id),
                           error=str(e))
        
        return {
            "success": True,
            "message": f"Recompensa distribuïda a {users_affected} usuaris",
            "users_affected": users_affected,
            "notifications_sent": notifications_sent
        }

    # ========================================
    # MÉTODOS PARA NOTIFICACIONES PERSONALES
    # ========================================

    def get_all_user_notifications(self, user_id: uuid.UUID, limit: int = 20, offset: int = 0, unread_only: bool = False) -> List[UserNotification]:
        """Obtiene todas las notificaciones del usuario (personales + campañas)"""
        query = self.db.query(UserNotification).filter(UserNotification.user_id == user_id)
        
        if unread_only:
            query = query.filter(UserNotification.is_read == False)
        
        return query.order_by(UserNotification.created_at.desc()).offset(offset).limit(limit).all()

    def get_all_notification_stats(self, user_id: uuid.UUID) -> dict:
        """Obtiene estadísticas de todas las notificaciones del usuario"""
        total_notifications = self.db.query(UserNotification).filter(
            UserNotification.user_id == user_id
        ).count()
        
        unread_notifications = self.db.query(UserNotification).filter(
            UserNotification.user_id == user_id,
            UserNotification.is_read == False
        ).count()
        
        # Contar por tipo
        type_counts = {}
        notifications = self.db.query(UserNotification).filter(
            UserNotification.user_id == user_id
        ).all()
        
        for notification in notifications:
            notification_type = notification.notification_type
            if notification_type not in type_counts:
                type_counts[notification_type] = {"total": 0, "unread": 0}
            type_counts[notification_type]["total"] += 1
            if not notification.is_read:
                type_counts[notification_type]["unread"] += 1
        
        return {
            "total_notifications": total_notifications,
            "unread_notifications": unread_notifications,
            "type_counts": type_counts
        }

    def create_user_notification(self, user_id: uuid.UUID, title: str, message: str, 
                                notification_type: str, related_id: Optional[uuid.UUID] = None) -> UserNotification:
        """Crea una notificación personal para un usuario"""
        notification = UserNotification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            related_id=related_id
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        logger.info("Notificación personal creada", 
                   user_id=str(user_id),
                   notification_id=str(notification.id),
                   type=notification_type)
        
        return notification

    def get_user_notifications(self, user_id: uuid.UUID, limit: int = 50, offset: int = 0, 
                              unread_only: bool = False) -> List[UserNotification]:
        """Obtiene las notificaciones de un usuario"""
        query = self.db.query(UserNotification).filter(UserNotification.user_id == user_id)
        
        if unread_only:
            query = query.filter(UserNotification.is_read == False)
        
        return query.order_by(UserNotification.created_at.desc()).offset(offset).limit(limit).all()

    def mark_notification_as_read(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> UserNotification:
        """Marca una notificación como leída"""
        notification = self.db.query(UserNotification).filter(
            UserNotification.id == notification_id,
            UserNotification.user_id == user_id
        ).first()
        
        if not notification:
            raise ValueError("Notificació no trobada")
        
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(notification)
            
            logger.info("Notificación marcada como leída", 
                       user_id=str(user_id),
                       notification_id=str(notification_id))
        
        return notification

    def mark_all_notifications_as_read(self, user_id: uuid.UUID) -> int:
        """Marca todas las notificaciones de un usuario como leídas"""
        result = self.db.query(UserNotification).filter(
            UserNotification.user_id == user_id,
            UserNotification.is_read == False
        ).update({
            "is_read": True,
            "read_at": datetime.now(timezone.utc)
        })
        
        self.db.commit()
        
        logger.info("Totes les notificacions marcades com a llegides", 
                   user_id=str(user_id),
                   notifications_updated=result)
        
        return result

    def get_notification_stats(self, user_id: uuid.UUID) -> dict:
        """Obtiene estadísticas de notificaciones del usuario"""
        total_notifications = self.db.query(UserNotification).filter(
            UserNotification.user_id == user_id
        ).count()
        
        unread_notifications = self.db.query(UserNotification).filter(
            UserNotification.user_id == user_id,
            UserNotification.is_read == False
        ).count()
        
        # Contar por tipo
        notifications_by_type = {}
        type_counts = self.db.query(
            UserNotification.notification_type,
            self.db.func.count(UserNotification.id)
        ).filter(
            UserNotification.user_id == user_id
        ).group_by(UserNotification.notification_type).all()
        
        for notification_type, count in type_counts:
            notifications_by_type[notification_type] = count
        
        return {
            "total_notifications": total_notifications,
            "unread_notifications": unread_notifications,
            "notifications_by_type": notifications_by_type
        } 