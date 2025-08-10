#!/usr/bin/env python3
"""
Script para inicializar las recompensas por defecto en el sistema de gamificación
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db
from models import Reward
from sqlalchemy.orm import Session

def init_rewards():
    """Inicializa las recompensas por defecto"""
    
    # Lista de recompensas por defecto
    default_rewards = [
        {
            "name": "Ticket de Parking - 1 Hora",
            "description": "Canjea 100 puntos por 1 hora gratis de parking en el mercat",
            "points_cost": 100,
            "reward_type": "parking",
            "reward_value": "1 hora",
            "is_active": True,
            "max_redemptions": None
        },
        {
            "name": "Ticket de Parking - 2 Hores",
            "description": "Canjea 180 puntos por 2 hores gratis de parking en el mercat",
            "points_cost": 180,
            "reward_type": "parking",
            "reward_value": "2 hores",
            "is_active": True,
            "max_redemptions": None
        },
        {
            "name": "Descompte 5% - Productes Frescos",
            "description": "Canjea 200 puntos per un 5% de descompte en productes frescos",
            "points_cost": 200,
            "reward_type": "discount",
            "reward_value": "5% descompte",
            "is_active": True,
            "max_redemptions": None
        },
        {
            "name": "Descompte 10% - Productes Frescos",
            "description": "Canjea 350 puntos per un 10% de descompte en productes frescos",
            "points_cost": 350,
            "reward_type": "discount",
            "reward_value": "10% descompte",
            "is_active": True,
            "max_redemptions": None
        },
        {
            "name": "Cafè Gratuït",
            "description": "Canjea 50 puntos per un cafè gratuït a la cafeteria del mercat",
            "points_cost": 50,
            "reward_type": "food",
            "reward_value": "1 cafè",
            "is_active": True,
            "max_redemptions": None
        },
        {
            "name": "Pastís Gratuït",
            "description": "Canjea 150 puntos per un pastís gratuït de la pastisseria",
            "points_cost": 150,
            "reward_type": "food",
            "reward_value": "1 pastís",
            "is_active": True,
            "max_redemptions": None
        },
        {
            "name": "Bossa Reutilitzable",
            "description": "Canjea 80 puntos per una bossa reutilitzable del mercat",
            "points_cost": 80,
            "reward_type": "merchandise",
            "reward_value": "1 bossa",
            "is_active": True,
            "max_redemptions": 100  # Límite de 100 bolsas
        },
        {
            "name": "Visita Guiada - Mercat",
            "description": "Canjea 500 puntos per una visita guiada al mercat",
            "points_cost": 500,
            "reward_type": "experience",
            "reward_value": "1 visita",
            "is_active": True,
            "max_redemptions": 20  # Límite de 20 visitas
        },
        {
            "name": "Taller de Cuina",
            "description": "Canjea 800 puntos per participar en un taller de cuina",
            "points_cost": 800,
            "reward_type": "experience",
            "reward_value": "1 taller",
            "is_active": True,
            "max_redemptions": 10  # Límite de 10 talleres
        },
        {
            "name": "Descompte 15% - Compra Total",
            "description": "Canjea 600 puntos per un 15% de descompte en tota la compra",
            "points_cost": 600,
            "reward_type": "discount",
            "reward_value": "15% descompte total",
            "is_active": True,
            "max_redemptions": None
        }
    ]
    
    db = next(get_db())
    
    try:
        # Verificar si ya existen recompensas
        existing_rewards = db.query(Reward).count()
        if existing_rewards > 0:
            print(f"Ja existeixen {existing_rewards} recompenses. No s'afegeixen més.")
            return
        
        # Crear las recompensas por defecto
        for reward_data in default_rewards:
            reward = Reward(**reward_data)
            db.add(reward)
        
        db.commit()
        print(f"S'han creat {len(default_rewards)} recompenses per defecte.")
        
        # Mostrar las recompensas creadas
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
