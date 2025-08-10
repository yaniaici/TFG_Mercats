#!/usr/bin/env python3
"""
Script para poblar las tiendas del mercado con datos iniciales
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db, engine
from models import Base, MarketStore
from market_store_service import MarketStoreService
import uuid

def seed_market_stores():
    """Poblar las tiendas del mercado con datos iniciales"""
    
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
    
    # Obtener sesión de base de datos
    db = next(get_db())
    
    try:
        service = MarketStoreService(db)
        
        # Lista de tiendas del mercado
        market_stores = [
            {
                "name": "Mercadona",
                "description": "Supermercado Mercadona"
            },
            {
                "name": "Eroski",
                "description": "Supermercado Eroski"
            },
            {
                "name": "Carrefour",
                "description": "Supermercado Carrefour"
            },
            {
                "name": "EROSKI ALCOY",
                "description": "EROSKI PERO EN ALCOY"
            }
        ]
        
        # Crear cada tienda
        for store_data in market_stores:
            # Verificar si ya existe
            existing_store = service.get_market_store_by_name(store_data["name"])
            
            if not existing_store:
                print(f"✅ Creando tienda: {store_data['name']}")
                # Crear objeto MarketStoreCreate
                from schemas import MarketStoreCreate
                market_store_create = MarketStoreCreate(
                    name=store_data["name"],
                    description=store_data["description"]
                )
                service.create_market_store(market_store_create)
            else:
                print(f"⏭️  Tienda ya existe: {store_data['name']}")
        
        # Mostrar todas las tiendas
        all_stores = service.get_all_market_stores()
        print(f"\n📋 Tiendas del mercado disponibles ({len(all_stores)}):")
        for store in all_stores:
            print(f"  - {store.name} ({store.description})")
            
        print("\n✅ Poblado de tiendas del mercado completado")
        
    except Exception as e:
        print(f"❌ Error poblando tiendas del mercado: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🌱 Iniciando poblado de tiendas del mercado...")
    seed_market_stores() 