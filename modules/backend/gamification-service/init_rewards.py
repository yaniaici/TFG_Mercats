#!/usr/bin/env python3
"""
Script per inicialitzar les recompenses per defecte al sistema de gamificació
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db
from models import Reward
from sqlalchemy.orm import Session

def init_rewards():
    """Inicialitza les recompenses per defecte"""
    
    # Llista de recompenses per defecte
    default_rewards = [
        {
            "name": "Ticket de Parking - 1 Hora",
            "description": "Canvia 100 punts per 1 hora gratis de parking al mercat",
            "points_cost": 100,
            "reward_type": "parking",
            "reward_value": "1 hora",
            "is_active": True,
            "max_redemptions": None
        },
        {
            "name": "Ticket de Parking - 2 Hores",
            "description": "Canvia 180 punts per 2 hores gratis de parking al mercat",
            "points_cost": 180,
            "reward_type": "parking",
            "reward_value": "2 hores",
            "is_active": True,
            "max_redemptions": None
        },
        {
            "name": "Descompte 5% - Productes Frescos",
            "description": "Canvia 200 punts per un 5% de descompte en productes frescos",
            "points_cost": 200,
            "reward_type": "discount",
            "reward_value": "5% descompte",
            "is_active": True,
            "max_redemptions": None
        },
        {
            "name": "Descompte 10% - Productes Frescos",
            "description": "Canvia 350 punts per un 10% de descompte en productes frescos",
            "points_cost": 350,
            "reward_type": "discount",
            "reward_value": "10% descompte",
            "is_active": True,
            "max_redemptions": None
        },
        {
            "name": "Cafè Gratuït",
            "description": "Canvia 50 punts per un cafè gratuït a la cafeteria del mercat",
            "points_cost": 50,
            "reward_type": "food",
            "reward_value": "1 cafè",
            "is_active": True,
            "max_redemptions": None
        },
        {
            "name": "Pastís Gratuït",
            "description": "Canvia 150 punts per un pastís gratuït de la pastisseria",
            "points_cost": 150,
            "reward_type": "food",
            "reward_value": "1 pastís",
            "is_active": True,
            "max_redemptions": None
        },
        {
            "name": "Bossa Reutilitzable",
            "description": "Canvia 80 punts per una bossa reutilitzable del mercat",
            "points_cost": 80,
            "reward_type": "merchandise",
            "reward_value": "1 bossa",
            "is_active": True,
            "max_redemptions": 100  # Límit de 100 bosses
        },
        {
            "name": "Visita Guiada - Mercat",
            "description": "Canvia 500 punts per una visita guiada al mercat",
            "points_cost": 500,
            "reward_type": "experience",
            "reward_value": "1 visita",
            "is_active": True,
            "max_redemptions": 20  # Límit de 20 visites
        },
        {
            "name": "Taller de Cuina",
            "description": "Canvia 800 punts per participar en un taller de cuina",
            "points_cost": 800,
            "reward_type": "experience",
            "reward_value": "1 taller",
            "is_active": True,
            "max_redemptions": 10  # Límit de 10 tallers
        },
        {
            "name": "Descompte 15% - Compra Total",
            "description": "Canvia 600 punts per un 15% de descompte en tota la compra",
            "points_cost": 600,
            "reward_type": "discount",
            "reward_value": "15% descompte total",
            "is_active": True,
            "max_redemptions": None
        }
    ]
    
    db = next(get_db())
    
    try:
        # Verificar si ja existeixen recompenses
        existing_rewards = db.query(Reward).count()
        if existing_rewards > 0:
            print(f"Ja existeixen {existing_rewards} recompenses. No s'afegeixen més.")
            return
        
        # Crear les recompenses per defecte
        for reward_data in default_rewards:
            reward = Reward(**reward_data)
            db.add(reward)
        
        db.commit()
        print(f"S'han creat {len(default_rewards)} recompenses per defecte.")
        
        # Mostrar les recompenses creades
        rewards = db.query(Reward).all()
        print("\nRecompenses disponibles:")
        for reward in rewards:
            print(f"- {reward.name}: {reward.points_cost} punts")
            
    except Exception as e:
        db.rollback()
        print(f"Error creant les recompenses: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_rewards()
