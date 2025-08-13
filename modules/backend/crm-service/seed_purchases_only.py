#!/usr/bin/env python3
"""
Script para generar solo compras de prueba para usuarios existentes
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

def generate_purchase_data(user_id, user_index):
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
    
    pattern = patterns[user_index % 4]  # Usar módulo para distribuir patrones
    
    purchases = []
    num_purchases = random.randint(8, 15)  # 8-15 compras por usuario
    
    for i in range(num_purchases):
        # Fecha aleatoria en los últimos 60 días
        days_ago = random.randint(0, 60)
        purchase_date = datetime.utcnow() - timedelta(days=days_ago)
        
        # Seleccionar categorías según el patrón
        categories = pattern["categories"].copy()
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
            ticket_id=uuid4(),  # Generar un ticket_id único
            store_name=store,
            total_amount=total_amount,
            products=products,
            purchase_date=purchase_date,
            num_products=len(products),
            ticket_type="test",
            is_market_store=True
        )
        
        purchases.append(purchase)
    
    return purchases

async def seed_purchases_only():
    """Genera solo compras para usuarios existentes"""
    
    print("🛒 Generando compras de prueba...")
    print("=" * 40)
    
    db = next(get_db())
    
    try:
        # Limpiar compras existentes
        print("🧹 Limpiando compras existentes...")
        db.query(PurchaseHistory).delete()
        db.commit()
        
        # Obtener usuarios existentes
        users = db.query(User).all()
        print(f"👥 Usuarios encontrados: {len(users)}")
        
        if len(users) == 0:
            print("❌ No hay usuarios en el sistema. Crea usuarios primero.")
            return
        
        # Crear compras para cada usuario
        print("🛒 Generando compras...")
        total_purchases = 0
        
        for i, user in enumerate(users):
            purchases = generate_purchase_data(user.id, i)
            for purchase in purchases:
                db.add(purchase)
            total_purchases += len(purchases)
            print(f"  Usuario {i+1} ({user.email}): {len(purchases)} compras")
        
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
        
        print("\n🎉 Compras de prueba generadas exitosamente!")
        print("\nAhora puedes probar:")
        print("  python auto_preferences.py --action refresh_all")
        print("  python test_segment.py")
        
    except Exception as e:
        print(f"❌ Error generando compras: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(seed_purchases_only())
