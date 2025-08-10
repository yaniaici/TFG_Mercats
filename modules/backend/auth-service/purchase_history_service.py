#!/usr/bin/env python3
"""
Servicio para manejar el historial de compras de los usuarios
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
from models import PurchaseHistory, User
from schemas import PurchaseHistoryCreate, PurchaseHistorySummary
import structlog

logger = structlog.get_logger()

class PurchaseHistoryService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_purchase_record(self, purchase_data: PurchaseHistoryCreate) -> PurchaseHistory:
        """
        Crear un nuevo registro de compra en el historial del usuario
        """
        try:
            purchase_record = PurchaseHistory(
                user_id=purchase_data.user_id,
                ticket_id=purchase_data.ticket_id,
                purchase_date=purchase_data.purchase_date,
                store_name=purchase_data.store_name,
                total_amount=purchase_data.total_amount,
                products=purchase_data.products,
                num_products=purchase_data.num_products,
                ticket_type=purchase_data.ticket_type,
                is_market_store=purchase_data.is_market_store
            )
            
            self.db.add(purchase_record)
            self.db.commit()
            self.db.refresh(purchase_record)
            
            logger.info("Registro de compra creado", 
                       user_id=str(purchase_data.user_id),
                       ticket_id=str(purchase_data.ticket_id),
                       store_name=purchase_data.store_name,
                       total_amount=purchase_data.total_amount)
            
            return purchase_record
            
        except Exception as e:
            self.db.rollback()
            logger.error("Error creando registro de compra", 
                        error=str(e),
                        user_id=str(purchase_data.user_id),
                        ticket_id=str(purchase_data.ticket_id))
            raise
    
    def get_user_purchase_history(self, user_id: uuid.UUID, limit: int = 50, offset: int = 0) -> List[PurchaseHistory]:
        """
        Obtener el historial de compras de un usuario
        """
        try:
            purchases = self.db.query(PurchaseHistory)\
                .filter(PurchaseHistory.user_id == user_id)\
                .order_by(desc(PurchaseHistory.purchase_date))\
                .offset(offset)\
                .limit(limit)\
                .all()
            
            logger.info("Historial de compras obtenido", 
                       user_id=str(user_id),
                       count=len(purchases))
            
            return purchases
            
        except Exception as e:
            logger.error("Error obteniendo historial de compras", 
                        error=str(e),
                        user_id=str(user_id))
            raise
    
    def get_user_purchase_summary(self, user_id: uuid.UUID) -> PurchaseHistorySummary:
        """
        Obtener un resumen del historial de compras de un usuario
        """
        try:
            # Obtener estadísticas básicas
            stats = self.db.query(
                func.count(PurchaseHistory.id).label('total_purchases'),
                func.sum(PurchaseHistory.total_amount).label('total_spent'),
                func.avg(PurchaseHistory.total_amount).label('average_amount'),
                func.max(PurchaseHistory.purchase_date).label('last_purchase_date')
            ).filter(PurchaseHistory.user_id == user_id).first()
            
            if not stats or stats.total_purchases == 0:
                return PurchaseHistorySummary(
                    total_purchases=0,
                    total_spent=0.0,
                    average_purchase_amount=0.0
                )
            
            # Obtener tienda favorita
            favorite_store = self.db.query(
                PurchaseHistory.store_name,
                func.count(PurchaseHistory.id).label('visit_count')
            ).filter(PurchaseHistory.user_id == user_id)\
             .group_by(PurchaseHistory.store_name)\
             .order_by(desc('visit_count'))\
             .first()
            
            # Obtener productos más comprados
            most_purchased_products = self._get_most_purchased_products(user_id)
            
            summary = PurchaseHistorySummary(
                total_purchases=stats.total_purchases,
                total_spent=float(stats.total_spent or 0.0),
                favorite_store=favorite_store.store_name if favorite_store else None,
                most_purchased_products=most_purchased_products,
                last_purchase_date=stats.last_purchase_date,
                average_purchase_amount=float(stats.average_amount or 0.0)
            )
            
            logger.info("Resumen de compras obtenido", 
                       user_id=str(user_id),
                       total_purchases=summary.total_purchases,
                       total_spent=summary.total_spent)
            
            return summary
            
        except Exception as e:
            logger.error("Error obteniendo resumen de compras", 
                        error=str(e),
                        user_id=str(user_id))
            raise
    
    def _get_most_purchased_products(self, user_id: uuid.UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtener los productos más comprados por un usuario
        """
        try:
            # Obtener todas las compras del usuario
            purchases = self.db.query(PurchaseHistory.products)\
                .filter(PurchaseHistory.user_id == user_id)\
                .all()
            
            # Contar productos
            product_counts = {}
            for purchase in purchases:
                if purchase.products:
                    for product in purchase.products:
                        product_name = product.get('nombre', 'Producto desconocido')
                        if product_name in product_counts:
                            product_counts[product_name]['count'] += 1
                            product_counts[product_name]['total_spent'] += float(product.get('precio', 0))
                        else:
                            product_counts[product_name] = {
                                'name': product_name,
                                'count': 1,
                                'total_spent': float(product.get('precio', 0)),
                                'avg_price': float(product.get('precio', 0))
                            }
            
            # Ordenar por cantidad de compras
            sorted_products = sorted(
                product_counts.values(),
                key=lambda x: x['count'],
                reverse=True
            )[:limit]
            
            # Calcular precio promedio
            for product in sorted_products:
                product['avg_price'] = product['total_spent'] / product['count']
            
            return sorted_products
            
        except Exception as e:
            logger.error("Error obteniendo productos más comprados", 
                        error=str(e),
                        user_id=str(user_id))
            return []
    
    def get_purchase_by_ticket_id(self, ticket_id: uuid.UUID) -> Optional[PurchaseHistory]:
        """
        Obtener una compra específica por ID de ticket
        """
        try:
            purchase = self.db.query(PurchaseHistory)\
                .filter(PurchaseHistory.ticket_id == ticket_id)\
                .first()
            
            return purchase
            
        except Exception as e:
            logger.error("Error obteniendo compra por ticket_id", 
                        error=str(e),
                        ticket_id=str(ticket_id))
            return None
    
    def delete_purchase_record(self, purchase_id: uuid.UUID) -> bool:
        """
        Eliminar un registro de compra
        """
        try:
            purchase = self.db.query(PurchaseHistory)\
                .filter(PurchaseHistory.id == purchase_id)\
                .first()
            
            if not purchase:
                return False
            
            self.db.delete(purchase)
            self.db.commit()
            
            logger.info("Registro de compra eliminado", 
                       purchase_id=str(purchase_id))
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error("Error eliminando registro de compra", 
                        error=str(e),
                        purchase_id=str(purchase_id))
            return False
    
    def get_user_spending_by_period(self, user_id: uuid.UUID, days: int = 30) -> Dict[str, Any]:
        """
        Obtener el gasto del usuario por período
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            purchases = self.db.query(PurchaseHistory)\
                .filter(
                    PurchaseHistory.user_id == user_id,
                    PurchaseHistory.purchase_date >= start_date
                )\
                .order_by(PurchaseHistory.purchase_date)\
                .all()
            
            total_spent = sum(p.total_amount for p in purchases)
            num_purchases = len(purchases)
            
            return {
                'period_days': days,
                'total_spent': total_spent,
                'num_purchases': num_purchases,
                'average_per_purchase': total_spent / num_purchases if num_purchases > 0 else 0,
                'purchases': [
                    {
                        'date': p.purchase_date.isoformat(),
                        'store': p.store_name,
                        'amount': p.total_amount,
                        'products_count': p.num_products
                    }
                    for p in purchases
                ]
            }
            
        except Exception as e:
            logger.error("Error obteniendo gasto por período", 
                        error=str(e),
                        user_id=str(user_id),
                        days=days)
            return {
                'period_days': days,
                'total_spent': 0,
                'num_purchases': 0,
                'average_per_purchase': 0,
                'purchases': []
            } 