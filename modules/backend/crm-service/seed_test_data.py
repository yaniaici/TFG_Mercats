#!/usr/bin/env python3
"""
Script para generar datos de prueba con usuarios y compras variadas
para probar el sistema de inferencia automática de preferencias
"""

import asyncio
import random
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session
from database import get_db
from models import User, PurchaseHistory

# Datos de prueba
STORES = ["Mercadona", "Carrefour", "Lidl", "Dia", "Eroski", "Alcampo"]
PRODUCT_CATEGORIES = {
    "fruits": ["manzanas", "plátanos", "fresas", "naranjas", "peras", "uvas"],
    "vegetables": ["tomates", "lechuga", "zanahorias", "cebollas", "patatas", "pimientos"],
    "dairy": ["leche", "yogur", "queso", "mantequilla", "nata", "helado"],
    "meat": ["pollo", "ternera", "cerdo", "pescado", "jamón", "salchichas"],
    "bread": ["pan", "bollos", "galletas", "cereales", "pasta", "arroz"],
    "beverages": ["agua", "refrescos", "zumos", "vino", "cerveza", "café"],
    "snacks": ["patatas", "frutos secos", "chocolate", "gominolas", "galletas saladas"],
    "organic": ["manzanas orgánicas", "leche ecológica", "pan integral", "huevos camperos"],
    "gourmet": ["queso parmesano", "jamón ibérico", "vino reserva", "trufa negra"],
    "baby": ["papillas", "leche infantil", "potitos", "galletas bebé", "pañales"]
}

USER_PROFILES = [
    {"name": "María García", "email": "maria@test.com", "preferences": {"language": "es", "theme": "light"}},
    {"name": "Carlos López", "email": "carlos@test.com", "preferences": {"language": "es", "theme": "dark"}},
    {"name": "Ana Martín", "email": "ana@test.com", "preferences": {"language": "es", "theme": "light"}},
    {"name": "David Rodríguez", "email": "david@test.com", "preferences": {"language": "es", "theme": "dark"}},
    {"name": "Laura Sánchez", "email": "laura@test.com", "preferences": {"language": "es", "theme": "light"}},
    {"name": "Javier Pérez", "email": "javier@test.com", "preferences": {"language": "es", "theme": "dark"}},
    {"name": "Carmen González", "email": "carmen@test.com", "preferences": {"language": "es", "theme": "light"}},
    {"name": "Miguel Fernández", "email": "miguel@test.com", "preferences": {"language": "es", "theme": "dark"}},
    {"name": "Isabel Torres", "email": "isabel@test.com", "preferences": {"language": "es", "theme": "light"}},
    {"name": "Roberto Jiménez", "email": "roberto@test.com", "preferences": {"language": "es", "theme": "dark"}},
    {"name": "Elena Ruiz", "email": "elena@test.com", "preferences": {"language": "es", "theme": "light"}},
    {"name": "Francisco Moreno", "email": "francisco@test.com", "preferences": {"language": "es", "theme": "dark"}},
    {"name": "Sofia Herrera", "email": "sofia@test.com", "preferences": {"language": "es", "theme": "light"}},
    {"name": "Daniel Castro", "email": "daniel@test.com", "preferences": {"language": "es", "theme": "dark"}},
    {"name": "Patricia Morales", "email": "patricia@test.com", "preferences": {"language": "es", "theme": "light"}},
    {"name": "Alberto Ortiz", "email": "alberto@test.com", "preferences": {"language": "es", "theme": "dark"}},
    {"name": "Nuria Silva", "email": "nuria@test.com", "preferences": {"language": "es", "theme": "light"}},
    {"name": "Héctor Vargas", "email": "hector@test.com", "preferences": {"language": "es", "theme": "dark"}},
    {"name": "Cristina Romero", "email": "cristina@test.com", "preferences": {"language": "es", "theme": "light"}},
    {"name": "Víctor Navarro", "email": "victor@test.com", "preferences": {"language": "es", "theme": "dark"}}
]

def generate_purchase_data(user_id, user_profile_index):
    """Genera datos de compra específicos para cada perfil de usuario"""
    
    # Definir patrones de compra por perfil
    patterns = [
        # 0-4: Amantes de Mercadona y frutas
        {"store": "Mercadona", "categories": ["fruits", "vegetables"], "budget": (20, 50)},
        # 5-9: Compradores premium gourmet
        {"store": "Carrefour", "categories": ["gourmet", "organic"], "budget": (50, 150)},
        # 10-14: Familias con bebés
        {"store": "Dia", "categories": ["baby", "dairy", "bread"], "budget": (30, 80)},
        # 15-19: Jóvenes con snacks y bebidas
        {"store": "Lidl", "categories": ["snacks", "beverages"], "budget": (15, 40)}
    ]
    
    pattern = patterns[user_profile_index // 5]
    
    purchases = []
    num_purchases = random.randint(8, 15)  # 8-15 compras por usuario
    
    for i in range(num_purchases):
        # Fecha aleatoria en los últimos 60 días
        days_ago = random.randint(0, 60)
        purchase_date = datetime.utcnow() - timedelta(days=days_ago)
        
        # Seleccionar categorías según el patrón
        categories = pattern["categories"]
        if random.random() < 0.3:  # 30% de probabilidad de añadir categoría extra
            categories.append(random.choice(list(PRODUCT_CATEGORIES.keys())))
        
        # Generar productos
        products = []
        for category in categories:
            if category in PRODUCT_CATEGORIES:
                num_products = random.randint(1, 3)
                category_products = random.sample(PRODUCT_CATEGORIES[category], min(num_products, len(PRODUCT_CATEGORIES[category])))
                products.extend(category_products)
        
        # Calcular total
        total_amount = random.uniform(*pattern["budget"])
        
        # Ocasionalmente cambiar de tienda (20% de probabilidad)
        store = pattern["store"]
        if random.random() < 0.2:
            store = random.choice(STORES)
        
        purchase = PurchaseHistory(
            id=uuid4(),
            user_id=user_id,
            store_name=store,
            total_amount=total_amount,
            products=products,
            purchase_date=purchase_date
        )
        
        purchases.append(purchase)
    
    return purchases

async def seed_test_data():
    """Genera datos de prueba completos"""
    
    print("🌱 Generando datos de prueba...")
    print("=" * 40)
    
    db = next(get_db())
    
    try:
        # Limpiar solo compras existentes (no usuarios para evitar foreign key issues)
        print("🧹 Limpiando compras existentes...")
        db.query(PurchaseHistory).delete()
        db.commit()
        
        # Crear usuarios (solo si no existen)
        print("👥 Creando usuarios...")
        users = []
        for i, profile in enumerate(USER_PROFILES):
            # Verificar si el usuario ya existe
            existing_user = db.query(User).filter(User.email == profile["email"]).first()
            if existing_user:
                users.append(existing_user)
                print(f"  Usuario {i+1}: {profile['email']} (ya existe)")
            else:
                user = User(
                    id=uuid4(),
                    email=profile["email"],
                    preferences=profile["preferences"]
                )
                users.append(user)
                db.add(user)
                print(f"  Usuario {i+1}: {profile['email']} (nuevo)")
        
        db.commit()
        print(f"✅ Creados {len(users)} usuarios")
        
        # Crear compras
        print("🛒 Generando compras...")
        total_purchases = 0
        
        for i, user in enumerate(users):
            purchases = generate_purchase_data(user.id, i)
            for purchase in purchases:
                db.add(purchase)
            total_purchases += len(purchases)
            print(f"  Usuario {i+1}: {len(purchases)} compras")
        
        db.commit()
        print(f"✅ Creadas {total_purchases} compras en total")
        
        # Mostrar resumen
        print("\n📊 Resumen de datos generados:")
        print(f"  Usuarios: {len(users)}")
        print(f"  Compras totales: {total_purchases}")
        print(f"  Promedio compras por usuario: {total_purchases / len(users):.1f}")
        
        # Mostrar algunos ejemplos de compras
        print("\n🛍️ Ejemplos de compras generadas:")
        sample_purchases = db.query(PurchaseHistory).limit(5).all()
        for i, purchase in enumerate(sample_purchases, 1):
            user = db.query(User).filter(User.id == purchase.user_id).first()
            print(f"  {i}. {user.email}: {purchase.store_name} - {purchase.total_amount:.2f}€ - {purchase.products[:3]}...")
        
        print("\n🎉 Datos de prueba generados exitosamente!")
        print("\nAhora puedes probar:")
        print("  python auto_preferences.py --action refresh_all")
        print("  python test_segment.py")
        
    except Exception as e:
        print(f"❌ Error generando datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(seed_test_data())
