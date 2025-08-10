from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from models import MarketStore
from schemas import MarketStoreCreate, MarketStoreUpdate
import uuid

class MarketStoreService:
    def __init__(self, db: Session):
        self.db = db

    def create_market_store(self, market_store: MarketStoreCreate) -> MarketStore:
        """Crear una nueva tienda del mercado"""
        db_market_store = MarketStore(
            id=uuid.uuid4(),
            name=market_store.name,
            description=market_store.description,
            is_active=True
        )
        self.db.add(db_market_store)
        self.db.commit()
        self.db.refresh(db_market_store)
        return db_market_store

    def get_market_store(self, market_store_id: uuid.UUID) -> Optional[MarketStore]:
        """Obtener una tienda del mercado por ID"""
        return self.db.query(MarketStore).filter(MarketStore.id == market_store_id).first()

    def get_market_store_by_name(self, name: str) -> Optional[MarketStore]:
        """Obtener una tienda del mercado por nombre"""
        return self.db.query(MarketStore).filter(
            and_(
                MarketStore.name.ilike(f"%{name}%"),
                MarketStore.is_active == True
            )
        ).first()

    def get_all_market_stores(self, skip: int = 0, limit: int = 100) -> List[MarketStore]:
        """Obtener todas las tiendas del mercado"""
        return self.db.query(MarketStore).filter(MarketStore.is_active == True).offset(skip).limit(limit).all()

    def update_market_store(self, market_store_id: uuid.UUID, market_store: MarketStoreUpdate) -> Optional[MarketStore]:
        """Actualizar una tienda del mercado"""
        db_market_store = self.get_market_store(market_store_id)
        if not db_market_store:
            return None

        update_data = market_store.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_market_store, field, value)

        self.db.commit()
        self.db.refresh(db_market_store)
        return db_market_store

    def delete_market_store(self, market_store_id: uuid.UUID) -> bool:
        """Eliminar una tienda del mercado (soft delete)"""
        db_market_store = self.get_market_store(market_store_id)
        if not db_market_store:
            return False

        db_market_store.is_active = False
        self.db.commit()
        return True

    def is_market_store(self, store_name: str) -> bool:
        """Verificar si una tienda es del mercado"""
        if not store_name:
            return False
        
        # Buscar coincidencias exactas o parciales
        market_store = self.db.query(MarketStore).filter(
            and_(
                MarketStore.name.ilike(f"%{store_name}%"),
                MarketStore.is_active == True
            )
        ).first()
        
        return market_store is not None

    def get_market_store_names(self) -> List[str]:
        """Obtener lista de nombres de tiendas del mercado"""
        stores = self.db.query(MarketStore.name).filter(MarketStore.is_active == True).all()
        return [store[0] for store in stores] 