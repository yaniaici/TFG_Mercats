#!/usr/bin/env python3
"""
Script para verificar y corregir los datos de gamificación existentes.
Asegura que solo los tickets válidos (de tiendas del mercado) cuenten para los puntos.
"""

import sys
import os
import requests
import json
from datetime import datetime
from typing import List, Dict, Any

# Configuración
TICKET_SERVICE_URL = "http://ticket-service:8003"
GAMIFICATION_SERVICE_URL = "http://gamification-service:8005"

def get_all_tickets() -> List[Dict[str, Any]]:
    """Obtener todos los tickets del sistema"""
    try:
        response = requests.get(f"{TICKET_SERVICE_URL}/tickets/")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error obteniendo tickets: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error conectando con ticket service: {e}")
        return []

def get_user_gamification_stats(user_id: str) -> Dict[str, Any]:
    """Obtener estadísticas de gamificación de un usuario"""
    try:
        response = requests.get(f"{GAMIFICATION_SERVICE_URL}/users/{user_id}/stats")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error obteniendo stats de gamificación para {user_id}: {response.status_code}")
            return {}
    except Exception as e:
        print(f"❌ Error conectando con gamification service: {e}")
        return {}

def recalculate_user_gamification(user_id: str, tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Recalcular la gamificación de un usuario basándose en sus tickets"""
    print(f"\n🔄 Recalculando gamificación para usuario {user_id}")
    
    # Filtrar tickets del usuario
    user_tickets = [t for t in tickets if t.get('user_id') == user_id]
    print(f"   📋 Tickets encontrados: {len(user_tickets)}")
    
    # Contadores
    total_tickets = 0
    valid_tickets = 0
    total_spent = 0.0
    total_experience = 0
    
    # Procesar cada ticket
    for ticket in user_tickets:
        processing_result = ticket.get('processing_result', {})
        
        # Verificar si es un ticket válido
        is_valid = (
            processing_result.get('procesado_correctamente', False) and 
            processing_result.get('tienda') and 
            processing_result.get('es_tienda_mercado', False)
        )
        
        total_tickets += 1
        
        if is_valid:
            valid_tickets += 1
            
            # Calcular experiencia
            experience_gained = 50  # Base por ticket válido
            
            # Bonus por cantidad gastada
            total_amount = processing_result.get('total')
            if total_amount:
                try:
                    amount = float(total_amount)
                    total_spent += amount
                    if amount > 50:
                        bonus = int(amount / 10)  # 1 XP por cada 10€
                        experience_gained += bonus
                except (ValueError, TypeError):
                    pass
            
            total_experience += experience_gained
            
            print(f"   ✅ Ticket válido: {processing_result.get('tienda')} - {experience_gained} XP")
        else:
            print(f"   ❌ Ticket inválido: {processing_result.get('tienda', 'Sin tienda')} - 0 XP")
    
    # Calcular nivel basado en experiencia
    level = 1
    for lvl, exp_required in {
        1: 0, 2: 100, 3: 250, 4: 450, 5: 700, 6: 1000, 7: 1350, 8: 1750, 9: 2200, 10: 2700
    }.items():
        if total_experience >= exp_required:
            level = lvl
    
    return {
        "user_id": user_id,
        "level": level,
        "experience": total_experience,
        "total_tickets": total_tickets,
        "valid_tickets": valid_tickets,
        "total_spent": total_spent,
        "recalculated": True
    }

def update_user_gamification(user_id: str, new_stats: Dict[str, Any]) -> bool:
    """Actualizar las estadísticas de gamificación de un usuario"""
    try:
        # Primero, resetear el perfil del usuario
        reset_response = requests.post(f"{GAMIFICATION_SERVICE_URL}/users/{user_id}/reset")
        
        # Luego, añadir la experiencia correcta
        if new_stats['experience'] > 0:
            response = requests.post(
                f"{GAMIFICATION_SERVICE_URL}/users/{user_id}/add-experience",
                params={
                    "experience_gained": new_stats['experience'],
                    "reason": "Recalibració de dades de gamificació"
                }
            )
            
            if response.status_code == 200:
                print(f"   ✅ Gamificación actualizada: {new_stats['experience']} XP")
                return True
            else:
                print(f"   ❌ Error actualizando gamificación: {response.status_code}")
                return False
        else:
            print(f"   ⚠️ No hay experiencia para añadir")
            return True
            
    except Exception as e:
        print(f"   ❌ Error actualizando gamificación: {e}")
        return False

def main():
    """Función principal"""
    print("🔧 SCRIPT DE CORRECCIÓN DE DATOS DE GAMIFICACIÓN")
    print("=" * 50)
    
    # Verificar conectividad
    print("🔍 Verificando conectividad con servicios...")
    
    try:
        ticket_health = requests.get(f"{TICKET_SERVICE_URL}/health")
        gamification_health = requests.get(f"{GAMIFICATION_SERVICE_URL}/health")
        
        if ticket_health.status_code != 200 or gamification_health.status_code != 200:
            print("❌ Los servicios no están disponibles")
            return
        
        print("✅ Servicios disponibles")
    except Exception as e:
        print(f"❌ Error verificando servicios: {e}")
        return
    
    # Obtener todos los tickets
    print("\n📋 Obteniendo tickets del sistema...")
    tickets = get_all_tickets()
    
    if not tickets:
        print("❌ No se encontraron tickets")
        return
    
    print(f"✅ {len(tickets)} tickets encontrados")
    
    # Obtener usuarios únicos
    user_ids = list(set(t.get('user_id') for t in tickets if t.get('user_id')))
    print(f"👥 {len(user_ids)} usuarios únicos encontrados")
    
    # Procesar cada usuario
    corrected_count = 0
    error_count = 0
    
    for user_id in user_ids:
        try:
            # Obtener estadísticas actuales
            current_stats = get_user_gamification_stats(user_id)
            
            # Recalcular estadísticas correctas
            correct_stats = recalculate_user_gamification(user_id, tickets)
            
            # Comparar y actualizar si es necesario
            if (current_stats.get('experience', 0) != correct_stats['experience'] or
                current_stats.get('valid_tickets', 0) != correct_stats['valid_tickets']):
                
                print(f"   🔄 Datos incorrectos detectados, actualizando...")
                print(f"      Experiencia actual: {current_stats.get('experience', 0)}")
                print(f"      Experiencia correcta: {correct_stats['experience']}")
                print(f"      Tickets válidos actuales: {current_stats.get('valid_tickets', 0)}")
                print(f"      Tickets válidos correctos: {correct_stats['valid_tickets']}")
                
                if update_user_gamification(user_id, correct_stats):
                    corrected_count += 1
                else:
                    error_count += 1
            else:
                print(f"   ✅ Datos correctos para usuario {user_id}")
                
        except Exception as e:
            print(f"   ❌ Error procesando usuario {user_id}: {e}")
            error_count += 1
    
    # Resumen final
    print(f"\n📊 RESUMEN:")
    print(f"   Usuarios procesados: {len(user_ids)}")
    print(f"   Usuarios corregidos: {corrected_count}")
    print(f"   Errores: {error_count}")
    print(f"   ✅ Proceso completado")

if __name__ == "__main__":
    main() 