from fastapi import FastAPI, Depends, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Set, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
import os
import structlog
import json
import asyncio

from database import get_db, Base, engine
from models import Segment, Campaign, CampaignSegment, Notification, User, PurchaseHistory
from schemas import (
    SegmentCreate, SegmentResponse,
    CampaignCreate, CampaignResponse,
    NotificationResponse, NotificationMarkSent,
    AIGeneratePayload
)
from auth_client import require_admin
from ai_client import generate_text


logger = structlog.get_logger()

# Crear tablas si no existen (solo para las del CRM)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CRM Service",
    description="MVP para segmentos, campañas y notificaciones",
    version="0.1.0"
)

# CORS para permitir preflight OPTIONS desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# FUNCIONES DE INFERENCIA DE PREFERENCIAS
# ----------------------------

async def infer_user_preferences_from_purchases(user_id: UUID, db: Session) -> Dict[str, Any]:
    """
    Infiere preferencias de usuario basándose en su historial de compras usando IA
    """
    try:
        # Obtener historial de compras del usuario
        purchases = db.query(PurchaseHistory).filter(
            PurchaseHistory.user_id == user_id
        ).order_by(PurchaseHistory.purchase_date.desc()).limit(20).all()
        
        if not purchases:
            return {}
        
        # Preparar datos para análisis de IA
        purchase_data = []
        for purchase in purchases:
            products_text = ""
            if purchase.products and isinstance(purchase.products, list):
                products_text = ", ".join([str(product) for product in purchase.products])
            
            purchase_data.append({
                "store": purchase.store_name,
                "total": float(purchase.total_amount),
                "products": products_text,
                "date": purchase.purchase_date.isoformat()
            })
        
        # Crear prompt para IA
        system_prompt = (
            "Eres un analista de comportamiento de compra. Analiza el historial de compras "
            "y extrae preferencias del usuario en formato JSON simple. Responde solo JSON válido "
            "con 2-4 preferencias clave. Ejemplos de preferencias: diet (vegetariano, vegano, etc.), "
            "organic (true/false), wine_preference (red, white, etc.), language (catalan, spanish, etc.), "
            "budget_level (low, medium, high), store_preference (mercadona, carrefour, etc.)."
        )
        
        prompt = f"""
        Analiza este historial de compras y extrae preferencias del usuario:
        
        {json.dumps(purchase_data, indent=2, default=str)}
        
        Responde solo con JSON válido de preferencias, ejemplo:
        {{"diet": "vegetariano", "organic": true, "budget_level": "medium"}}
        """
        
        # Generar preferencias con IA
        preferences_json = await generate_text(
            prompt=prompt,
            system=system_prompt,
            temperature=0.3,
            max_tokens=200
        )
        
        # Parsear JSON - limpiar markdown si existe
        preferences_json_clean = preferences_json.strip()
        if preferences_json_clean.startswith('```json'):
            preferences_json_clean = preferences_json_clean[7:]
        if preferences_json_clean.endswith('```'):
            preferences_json_clean = preferences_json_clean[:-3]
        preferences_json_clean = preferences_json_clean.strip()
        
        preferences = json.loads(preferences_json_clean)
        if isinstance(preferences, dict):
            return preferences
        
        return {}
        
    except Exception as e:
        logger.error("Error inferring user preferences", user_id=str(user_id), error=str(e))
        return {}

async def update_user_preferences_automatically(user_id: UUID, db: Session) -> Dict[str, Any]:
    """
    Actualiza automáticamente las preferencias de un usuario basándose en su historial
    """
    try:
        # Obtener usuario
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}
        
        # Inferir preferencias
        inferred_preferences = await infer_user_preferences_from_purchases(user_id, db)
        
        if inferred_preferences:
            # Actualizar preferencias del usuario
            user.preferences = inferred_preferences
            db.commit()
            db.refresh(user)
            
            logger.info("Updated user preferences automatically", 
                       user_id=str(user_id), 
                       preferences=inferred_preferences)
        
        return inferred_preferences
        
    except Exception as e:
        logger.error("Error updating user preferences", user_id=str(user_id), error=str(e))
        return {}

async def get_user_preferences_with_inference(user_id: UUID, db: Session) -> Dict[str, Any]:
    """
    Obtiene preferencias del usuario, inferiéndolas si no existen
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {}
    
    # Si no hay preferencias o están vacías, inferirlas
    if not user.preferences or user.preferences == {}:
        await update_user_preferences_automatically(user_id, db)
        db.refresh(user)
    
    return user.preferences or {}

# ----------------------------
# ENDPOINTS
# ----------------------------

@app.get("/")
def root():
    return {
        "service": "crm-service",
        "version": "0.1.0",
        "endpoints": {
            "segments": "/segments",
            "campaigns": "/campaigns",
            "notifications": "/notifications",
            "preferences": "/preferences",
        },
    }


@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now()}


# ----------------------------
# PREFERENCIAS DE USUARIO
# ----------------------------

@app.post("/preferences/infer/{user_id}")
async def infer_user_preferences_endpoint(
    user_id: UUID, 
    db: Session = Depends(get_db), 
    authorization: str | None = Header(default=None)
):
    """Inferir y actualizar preferencias de un usuario específico"""
    await require_admin(authorization.replace("Bearer ", "") if authorization else "")
    
    preferences = await update_user_preferences_automatically(user_id, db)
    return {"user_id": str(user_id), "preferences": preferences}

@app.get("/preferences/summary")
async def get_preferences_summary_endpoint(
    db: Session = Depends(get_db), 
    authorization: str | None = Header(default=None)
):
    """Obtener resumen de preferencias de todos los usuarios"""
    await require_admin(authorization.replace("Bearer ", "") if authorization else "")
    
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

@app.get("/preferences/{user_id}")
async def get_user_preferences_endpoint(
    user_id: UUID, 
    db: Session = Depends(get_db), 
    authorization: str | None = Header(default=None)
):
    """Obtener preferencias de un usuario (inferidas si no existen)"""
    await require_admin(authorization.replace("Bearer ", "") if authorization else "")
    
    preferences = await get_user_preferences_with_inference(user_id, db)
    return {"user_id": str(user_id), "preferences": preferences}

@app.post("/preferences/infer-all")
async def infer_all_users_preferences_endpoint(
    db: Session = Depends(get_db), 
    authorization: str | None = Header(default=None)
):
    """Inferir preferencias para todos los usuarios con historial de compras"""
    await require_admin(authorization.replace("Bearer ", "") if authorization else "")
    
    # Obtener usuarios con historial de compras
    users_with_purchases = db.query(PurchaseHistory.user_id).distinct().all()
    user_ids = [row[0] for row in users_with_purchases]
    
    results = []
    for user_id in user_ids:
        try:
            preferences = await update_user_preferences_automatically(user_id, db)
            results.append({
                "user_id": str(user_id),
                "preferences": preferences,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "user_id": str(user_id),
                "preferences": {},
                "status": "error",
                "error": str(e)
            })
    
    return {"processed_users": len(results), "results": results}

@app.post("/preferences/infer-new")
async def infer_new_users_preferences_endpoint(
    days_back: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db), 
    authorization: str | None = Header(default=None)
):
    """Inferir preferencias para usuarios con compras recientes"""
    await require_admin(authorization.replace("Bearer ", "") if authorization else "")
    
    from datetime import datetime, timedelta
    
    # Obtener usuarios con compras recientes
    threshold = datetime.utcnow() - timedelta(days=days_back)
    recent_users = db.query(PurchaseHistory.user_id).filter(
        PurchaseHistory.purchase_date >= threshold
    ).distinct().all()
    
    user_ids = [row[0] for row in recent_users]
    
    results = []
    for user_id in user_ids:
        try:
            # Verificar si el usuario ya tiene preferencias
            user = db.query(User).filter(User.id == user_id).first()
            if user and (not user.preferences or user.preferences == {}):
                preferences = await update_user_preferences_automatically(user_id, db)
                results.append({
                    "user_id": str(user_id),
                    "preferences": preferences,
                    "status": "updated" if preferences else "no_preferences_found"
                })
            else:
                results.append({
                    "user_id": str(user_id),
                    "preferences": user.preferences if user else {},
                    "status": "already_has_preferences"
                })
        except Exception as e:
            results.append({
                "user_id": str(user_id),
                "preferences": {},
                "status": "error",
                "error": str(e)
            })
    
    return {"processed_users": len(results), "days_back": days_back, "results": results}


# ----------------------------
# Segmentos
# ----------------------------

@app.post("/segments", response_model=SegmentResponse)
async def create_segment(payload: SegmentCreate, db: Session = Depends(get_db), authorization: str | None = Header(default=None)):
    await require_admin(authorization.replace("Bearer ", "") if authorization else "")

    # Mantener solo last_days, min_total_spent, min_num_purchases; ignorar tiendas
    filters = payload.filters or {}
    allowed_keys = {"last_days", "min_total_spent", "min_num_purchases"}
    base_filters = {k: v for k, v in filters.items() if k in allowed_keys}

    # Si llega prompt, invocar IA para derivar preferences_contains a partir del prompt
    if payload.prompt:
        try:
            system = (
                "Eres un generador de preferencias estandarizadas. Convierte descripciones "
                "a preferencias usando SIEMPRE estas claves exactas: diet, store_preference, "
                "language, organic, budget_level, product_category. "
                "Valores posibles: diet (vegetariano, vegano, omnivoro), "
                "store_preference (mercadona, carrefour, lidl, dia), "
                "language (catalan, spanish, english), "
                "organic (true, false), "
                "budget_level (low, medium, high), "
                "product_category (fruits, vegetables, dairy, meat, bread, beverages, snacks, organic, gourmet, baby). "
                "Responde solo JSON."
            )
            gen = await generate_text(
                prompt=(
                    f"Convierte a JSON estandarizado usando las claves exactas: {payload.prompt}. "
                    "Usa solo las claves y valores especificados arriba."
                ),
                system=system,
                temperature=0.2,
                max_tokens=120,
            )
            # Limpiar markdown si existe
            gen_clean = gen.strip()
            if gen_clean.startswith('```json'):
                gen_clean = gen_clean[7:]
            if gen_clean.endswith('```'):
                gen_clean = gen_clean[:-3]
            gen_clean = gen_clean.strip()
            
            prefs = json.loads(gen_clean)
            if isinstance(prefs, dict) and prefs:
                base_filters["preferences_contains"] = prefs
        except Exception:
            # Si falla la IA o el parseo, continuar con los filtros base
            pass

    segment = Segment(
        name=payload.name,
        description=payload.description,
        filters=base_filters,
        is_active=True,
    )
    db.add(segment)
    db.commit()
    db.refresh(segment)
    return segment


@app.get("/segments", response_model=List[SegmentResponse])
async def list_segments(db: Session = Depends(get_db), authorization: str | None = Header(default=None)):
    await require_admin(authorization.replace("Bearer ", "") if authorization else "")
    return db.query(Segment).order_by(Segment.created_at.desc()).all()


@app.get("/segments/{segment_id}", response_model=SegmentResponse)
async def get_segment(segment_id: UUID, db: Session = Depends(get_db), authorization: str | None = Header(default=None)):
    await require_admin(authorization.replace("Bearer ", "") if authorization else "")
    segment = db.query(Segment).filter(Segment.id == segment_id).first()
    if not segment:
        raise HTTPException(status_code=404, detail="Segmento no encontrado")
    return segment


async def query_user_ids_for_filters(db: Session, filters: dict) -> Set[UUID]:
    filters = filters or {}
    last_days = filters.get("last_days")
    min_total_spent = filters.get("min_total_spent")
    min_num_purchases = filters.get("min_num_purchases")
    # Ignoramos filtros por tienda para no sesgar la segmentación por establecimiento
    # stores_in = filters.get("stores_in") or []
    # is_market_store = filters.get("is_market_store")
    preferences_contains = filters.get("preferences_contains") or {}

    query = db.query(PurchaseHistory.user_id)

    if last_days:
        threshold = datetime.utcnow() - timedelta(days=int(last_days))
        query = query.filter(PurchaseHistory.purchase_date >= threshold)

    if min_total_spent is not None:
        # Subconsulta por usuario sum(total)
        from sqlalchemy import func
        totals = db.query(
            PurchaseHistory.user_id.label("user_id"),
            func.sum(PurchaseHistory.total_amount).label("total")
        )
        if last_days:
            totals = totals.filter(PurchaseHistory.purchase_date >= threshold)
        totals = totals.group_by(PurchaseHistory.user_id).subquery()
        query = db.query(totals.c.user_id).filter(totals.c.total >= min_total_spent)

    if min_num_purchases is not None:
        from sqlalchemy import func
        counts = db.query(
            PurchaseHistory.user_id.label("user_id"),
            func.count(PurchaseHistory.id).label("cnt")
        )
        if last_days:
            counts = counts.filter(PurchaseHistory.purchase_date >= threshold)
        counts = counts.group_by(PurchaseHistory.user_id).subquery()
        query = db.query(counts.c.user_id).filter(counts.c.cnt >= min_num_purchases)

    # Filtros por tienda deshabilitados (no tener en cuenta tiendas en los segmentos)

    user_ids = set([row[0] for row in query.distinct().all()])

    # Filtro por preferencias (JSON contains) - CON INFERENCIA AUTOMÁTICA
    if preferences_contains:
        pref_user_ids = set()
        
        # Obtener todos los usuarios que cumplen los filtros básicos
        candidate_users = user_ids if user_ids else set([row[0] for row in db.query(PurchaseHistory.user_id).distinct().all()])
        
        for user_id in candidate_users:
            try:
                # Obtener preferencias del usuario (inferidas si no existen)
                user_preferences = await get_user_preferences_with_inference(user_id, db)
                
                # Verificar si el usuario cumple con las preferencias requeridas
                matches_preferences = True
                for key, value in preferences_contains.items():
                    if key not in user_preferences or user_preferences[key] != value:
                        matches_preferences = False
                        break
                
                if matches_preferences:
                    pref_user_ids.add(user_id)
                    
            except Exception as e:
                logger.error("Error checking user preferences", user_id=str(user_id), error=str(e))
                continue
        
        # Intersectar con los usuarios que cumplen otros filtros
        user_ids = user_ids.intersection(pref_user_ids) if user_ids else pref_user_ids

    return user_ids


@app.post("/segments/{segment_id}/preview-users", response_model=List[str])
async def preview_segment_users(segment_id: UUID, limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db), authorization: str | None = Header(default=None)):
    await require_admin(authorization.replace("Bearer ", "") if authorization else "")
    segment = db.query(Segment).filter(Segment.id == segment_id).first()
    if not segment:
        raise HTTPException(status_code=404, detail="Segmento no encontrado")
    user_ids = list(await query_user_ids_for_filters(db, segment.filters))
    return [str(u) for u in user_ids[:limit]]


# ----------------------------
# Campañas
# ----------------------------

@app.post("/campaigns", response_model=CampaignResponse)
async def create_campaign(payload: CampaignCreate, db: Session = Depends(get_db), authorization: str | None = Header(default=None)):
    await require_admin(authorization.replace("Bearer ", "") if authorization else "")

    message = payload.message
    # Si no hay mensaje, intentar generarlo con IA a partir de preferencias de los segmentos
    if not message:
        try:
            prefs_list: list[dict] = []
            for seg_id in payload.segment_ids:
                seg = db.query(Segment).filter(Segment.id == seg_id).first()
                if seg and isinstance(seg.filters, dict) and seg.filters.get("preferences_contains"):
                    prefs_list.append(seg.filters["preferences_contains"])
            system = (
                "Eres un copywriter para un mercado local. Escribe un mensaje corto (máx 200 caracteres), "
                "cálido y claro, sin emojis, basado en preferencias sugeridas."
            )
            prompt = (
                f"Preferencias agregadas: {prefs_list}. Genera un copy promocional único con CTA suave."
            )
            message = await generate_text(prompt=prompt, system=system, temperature=0.6, max_tokens=120)
        except Exception:
            message = "Descubre nuestras ofertas especiales esta semana en el mercat!"

    campaign = Campaign(
        name=payload.name,
        description=payload.description,
        message=message,
        is_active=True,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    # Asociaciones con segmentos
    for seg_id in payload.segment_ids:
        db.add(CampaignSegment(campaign_id=campaign.id, segment_id=seg_id))
    db.commit()

    segment_ids = [cs.segment_id for cs in db.query(CampaignSegment).filter(CampaignSegment.campaign_id == campaign.id).all()]

    return CampaignResponse(
        id=campaign.id,
        name=campaign.name,
        description=campaign.description,
        message=campaign.message,
        is_active=campaign.is_active,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
        segment_ids=segment_ids,
    )


@app.get("/campaigns", response_model=List[CampaignResponse])
async def list_campaigns(db: Session = Depends(get_db), authorization: str | None = Header(default=None)):
    await require_admin(authorization.replace("Bearer ", "") if authorization else "")
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
    results: List[CampaignResponse] = []
    for c in campaigns:
        seg_ids = [cs.segment_id for cs in db.query(CampaignSegment).filter(CampaignSegment.campaign_id == c.id).all()]
        results.append(CampaignResponse(
            id=c.id,
            name=c.name,
            description=c.description,
            message=c.message,
            is_active=c.is_active,
            created_at=c.created_at,
            updated_at=c.updated_at,
            segment_ids=seg_ids,
        ))
    return results


@app.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: UUID, db: Session = Depends(get_db), authorization: str | None = Header(default=None)):
    await require_admin(authorization.replace("Bearer ", "") if authorization else "")
    c = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
    seg_ids = [cs.segment_id for cs in db.query(CampaignSegment).filter(CampaignSegment.campaign_id == c.id).all()]
    return CampaignResponse(
        id=c.id,
        name=c.name,
        description=c.description,
        message=c.message,
        is_active=c.is_active,
        created_at=c.created_at,
        updated_at=c.updated_at,
        segment_ids=seg_ids,
    )


@app.post("/campaigns/{campaign_id}/preview-users", response_model=List[str])
async def preview_campaign_users(campaign_id: UUID, limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db), authorization: str | None = Header(default=None)):
    await require_admin(authorization.replace("Bearer ", "") if authorization else "")
    c = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
    cs = db.query(CampaignSegment).filter(CampaignSegment.campaign_id == c.id).all()
    user_ids: Set[UUID] = set()
    for link in cs:
        segment = db.query(Segment).filter(Segment.id == link.segment_id).first()
        if segment:
            user_ids |= await query_user_ids_for_filters(db, segment.filters)
    return [str(u) for u in list(user_ids)[:limit]]


@app.post("/campaigns/{campaign_id}/dispatch", response_model=List[NotificationResponse])
async def dispatch_campaign(campaign_id: UUID, db: Session = Depends(get_db), authorization: str | None = Header(default=None)):
    await require_admin(authorization.replace("Bearer ", "") if authorization else "")
    c = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
    if not c.is_active:
        raise HTTPException(status_code=400, detail="Campaña inactiva")

    cs_links = db.query(CampaignSegment).filter(CampaignSegment.campaign_id == c.id).all()
    user_ids: Set[UUID] = set()
    for link in cs_links:
        segment = db.query(Segment).filter(Segment.id == link.segment_id).first()
        if segment and segment.is_active:
            user_ids |= await query_user_ids_for_filters(db, segment.filters)

    if not user_ids:
        return []

    notifications: List[Notification] = []
    for uid in user_ids:
        n = Notification(user_id=uid, campaign_id=c.id, message=c.message, status="queued")
        db.add(n)
        notifications.append(n)
    db.commit()
    for n in notifications:
        db.refresh(n)

    return [NotificationResponse.model_validate(n) for n in notifications]


@app.post("/campaigns/{campaign_id}/send-notifications")
async def send_campaign_notifications(
    campaign_id: UUID, 
    channel: str = Query("webpush", description="Canal de notificación (webpush, android, ios)"),
    db: Session = Depends(get_db), 
    authorization: str | None = Header(default=None)
):
    """
    Envía las notificaciones de una campaña a través del notification-sender
    """
    await require_admin(authorization.replace("Bearer ", "") if authorization else "")
    
    # Obtener campaña
    c = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
    if not c.is_active:
        raise HTTPException(status_code=400, detail="Campaña inactiva")

    # Obtener usuarios de la campaña
    cs_links = db.query(CampaignSegment).filter(CampaignSegment.campaign_id == c.id).all()
    user_ids: Set[UUID] = set()
    for link in cs_links:
        segment = db.query(Segment).filter(Segment.id == link.segment_id).first()
        if segment and segment.is_active:
            user_ids |= await query_user_ids_for_filters(db, segment.filters)

    if not user_ids:
        return {"message": "No hay usuarios para enviar notificaciones", "sent_count": 0}

    # Preparar notificaciones para el sender
    import httpx
    import os
    
    notification_sender_url = os.getenv("NOTIFICATION_SENDER_URL", "http://notification-sender:8007")
    
    notifications_to_send = []
    for user_id in user_ids:
        notifications_to_send.append({
            "user_id": str(user_id),
            "message": c.message,
            "title": c.name,
            "channel": channel,
            "data": {
                "campaign_id": str(campaign_id),
                "campaign_name": c.name
            }
        })
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{notification_sender_url}/send-batch",
                json={"requests": notifications_to_send},
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "message": "Notificaciones enviadas al notification-sender",
                    "campaign_id": str(campaign_id),
                    "total_users": len(user_ids),
                    "sender_response": result
                }
            else:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error del notification-sender: {response.text}"
                )
                
    except Exception as e:
        logger.warning("Notification sender not available, notifications queued only", error=str(e))
        return {
            "message": "Notification sender no disponible, notificaciones solo en cola",
            "campaign_id": str(campaign_id),
            "total_users": len(user_ids),
            "warning": "Las notificaciones se han creado en la base de datos pero no se han enviado"
        }


# ----------------------------
# Notificaciones
# ----------------------------

@app.get("/notifications", response_model=List[NotificationResponse])
async def list_notifications(status: str | None = None, db: Session = Depends(get_db), authorization: str | None = Header(default=None)):
    await require_admin(authorization.replace("Bearer ", "") if authorization else "")
    q = db.query(Notification).order_by(Notification.created_at.desc())
    if status:
        q = q.filter(Notification.status == status)
    return q.all()


@app.post("/notifications/{notification_id}/mark-sent", response_model=NotificationResponse)
async def mark_notification_sent(notification_id: UUID, payload: NotificationMarkSent, db: Session = Depends(get_db), authorization: str | None = Header(default=None)):
    await require_admin(authorization.replace("Bearer ", "") if authorization else "")
    n = db.query(Notification).filter(Notification.id == notification_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    n.status = "sent"
    n.meta = {**(n.meta or {}), **(payload.delivery_info or {})}
    db.commit()
    db.refresh(n)
    return n


# ----------------------------
# IA: generación de texto (via Ollama)
# ----------------------------

@app.post("/ai/generate")
async def ai_generate(payload: AIGeneratePayload, authorization: str | None = Header(default=None)):
    # Solo admin por ahora
    await require_admin(authorization.replace("Bearer ", "") if authorization else "")
    if not payload.prompt:
        raise HTTPException(status_code=400, detail="prompt requerido")
    try:
        text = await generate_text(
            prompt=payload.prompt, 
            system=payload.system, 
            temperature=payload.temperature, 
            max_tokens=payload.max_tokens
        )
        return {"text": text}
    except Exception as e:
        logger.error("ai_generate_error", error=str(e))
        raise HTTPException(status_code=500, detail="Error generando texto")

