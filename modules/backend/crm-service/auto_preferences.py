"""
Script para inferir preferencias de usuarios automáticamente
basándose en su historial de compras
"""

import asyncio
import structlog
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from uuid import UUID

from database import get_db
from models import User, PurchaseHistory
from main import infer_user_preferences_from_purchases, update_user_preferences_automatically

logger = structlog.get_logger()

async def infer_preferences_for_new_users(db: Session, days_back: int = 30) -> Dict[str, Any]:
    """
    Infiere preferencias para usuarios que han hecho compras recientemente
    pero no tienen preferencias inferidas
    """
    try:
        from datetime import datetime, timedelta
        
        # Obtener usuarios con compras recientes
        threshold = datetime.utcnow() - timedelta(days=days_back)
        
        recent_users = db.query(PurchaseHistory.user_id).filter(
            PurchaseHistory.purchase_date >= threshold
        ).distinct().all()
        
        user_ids = [row[0] for row in recent_users]
        
        results = {
            "processed": 0,
            "updated": 0,
            "errors": 0,
            "details": []
        }
        
        for user_id in user_ids:
            try:
                # Verificar si el usuario ya tiene preferencias
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    continue
                
                # Si no tiene preferencias o están vacías, inferirlas
                if not user.preferences or user.preferences == {}:
                    preferences = await update_user_preferences_automatically(user_id, db)
                    
                    if preferences:
                        results["updated"] += 1
                        results["details"].append({
                            "user_id": str(user_id),
                            "status": "updated",
                            "preferences": preferences
                        })
                        logger.info("Updated preferences for user", 
                                   user_id=str(user_id), 
                                   preferences=preferences)
                    else:
                        results["details"].append({
                            "user_id": str(user_id),
                            "status": "no_preferences_found"
                        })
                else:
                    results["details"].append({
                        "user_id": str(user_id),
                        "status": "already_has_preferences",
                        "preferences": user.preferences
                    })
                
                results["processed"] += 1
                
            except Exception as e:
                results["errors"] += 1
                results["details"].append({
                    "user_id": str(user_id),
                    "status": "error",
                    "error": str(e)
                })
                logger.error("Error processing user preferences", 
                           user_id=str(user_id), 
                           error=str(e))
        
        return results
        
    except Exception as e:
        logger.error("Error in batch preference inference", error=str(e))
        return {"error": str(e)}

async def refresh_preferences_for_all_users(db: Session) -> Dict[str, Any]:
    """
    Refresca las preferencias de todos los usuarios con historial de compras
    """
    try:
        # Obtener todos los usuarios con historial de compras
        users_with_purchases = db.query(PurchaseHistory.user_id).distinct().all()
        user_ids = [row[0] for row in users_with_purchases]
        
        results = {
            "processed": 0,
            "updated": 0,
            "errors": 0,
            "details": []
        }
        
        for user_id in user_ids:
            try:
                preferences = await update_user_preferences_automatically(user_id, db)
                
                if preferences:
                    results["updated"] += 1
                    results["details"].append({
                        "user_id": str(user_id),
                        "status": "updated",
                        "preferences": preferences
                    })
                else:
                    results["details"].append({
                        "user_id": str(user_id),
                        "status": "no_preferences_found"
                    })
                
                results["processed"] += 1
                
            except Exception as e:
                results["errors"] += 1
                results["details"].append({
                    "user_id": str(user_id),
                    "status": "error",
                    "error": str(e)
                })
                logger.error("Error refreshing user preferences", 
                           user_id=str(user_id), 
                           error=str(e))
        
        return results
        
    except Exception as e:
        logger.error("Error in batch preference refresh", error=str(e))
        return {"error": str(e)}

async def get_preferences_summary(db: Session) -> Dict[str, Any]:
    """
    Obtiene un resumen de las preferencias de todos los usuarios
    """
    try:
        users = db.query(User).all()
        
        summary = {
            "total_users": len(users),
            "users_with_preferences": 0,
            "users_without_preferences": 0,
            "preferences_distribution": {},
            "top_preferences": {}
        }
        
        all_preferences = {}
        
        for user in users:
            if user.preferences and user.preferences != {}:
                summary["users_with_preferences"] += 1
                
                # Contar distribución de preferencias
                for key, value in user.preferences.items():
                    if key not in all_preferences:
                        all_preferences[key] = {}
                    
                    value_str = str(value)
                    if value_str not in all_preferences[key]:
                        all_preferences[key][value_str] = 0
                    all_preferences[key][value_str] += 1
            else:
                summary["users_without_preferences"] += 1
        
        # Calcular top preferencias
        for key, values in all_preferences.items():
            sorted_values = sorted(values.items(), key=lambda x: x[1], reverse=True)
            summary["top_preferences"][key] = sorted_values[:5]  # Top 5
        
        summary["preferences_distribution"] = all_preferences
        
        return summary
        
    except Exception as e:
        logger.error("Error getting preferences summary", error=str(e))
        return {"error": str(e)}

# Función para ejecutar desde línea de comandos
async def main():
    """
    Función principal para ejecutar desde línea de comandos
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Inferir preferencias de usuarios")
    parser.add_argument("--action", choices=["infer_new", "refresh_all", "summary"], 
                       default="infer_new", help="Acción a ejecutar")
    parser.add_argument("--days", type=int, default=30, 
                       help="Días hacia atrás para usuarios nuevos")
    
    args = parser.parse_args()
    
    # Obtener sesión de base de datos
    db = next(get_db())
    
    try:
        if args.action == "infer_new":
            result = await infer_preferences_for_new_users(db, args.days)
            print("Inferencia para usuarios nuevos:")
            print(f"Procesados: {result['processed']}")
            print(f"Actualizados: {result['updated']}")
            print(f"Errores: {result['errors']}")
            
        elif args.action == "refresh_all":
            result = await refresh_preferences_for_all_users(db)
            print("Refresco de preferencias para todos los usuarios:")
            print(f"Procesados: {result['processed']}")
            print(f"Actualizados: {result['updated']}")
            print(f"Errores: {result['errors']}")
            
        elif args.action == "summary":
            result = await get_preferences_summary(db)
            print("Resumen de preferencias:")
            print(f"Total usuarios: {result['total_users']}")
            print(f"Con preferencias: {result['users_with_preferences']}")
            print(f"Sin preferencias: {result['users_without_preferences']}")
            print("\nTop preferencias:")
            for key, values in result['top_preferences'].items():
                print(f"  {key}: {values}")
                
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
