from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import uuid
from sqlalchemy.orm import Session
from models import UserGamification, UserBadge, ExperienceLog
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
        today = datetime.now().date()
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
            experience_gained = 10  # 10 XP por ticket inválido (participación)
            reason = "Ticket invàlid escanejat (participació)"
        
        # Añadir experiencia
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