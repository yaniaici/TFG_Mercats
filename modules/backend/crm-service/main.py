from fastapi import FastAPI, Depends, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Set, Optional
from uuid import UUID
from datetime import datetime, timedelta
import os
import structlog

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

@app.get("/")
def root():
    return {
        "service": "crm-service",
        "version": "0.1.0",
        "endpoints": {
            "segments": "/segments",
            "campaigns": "/campaigns",
            "notifications": "/notifications",
        },
    }


@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now()}


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
                "Eres un asistente que mapea una descripción en lenguaje natural a pares clave-valor "
                "simples de preferencias de usuario (JSON plano). Responde solo JSON."
            )
            gen = await generate_text(
                prompt=(
                    "Convierte a JSON llano de preferencias (clave:valor) el siguiente criterio de "
                    f"segmentación para usuarios de mercado: {payload.prompt}. Limita a 1-3 pares "
                    "sencillos, valores tipo string/boolean/number."
                ),
                system=system,
                temperature=0.2,
                max_tokens=120,
            )
            import json
            prefs = json.loads(gen)
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


def query_user_ids_for_filters(db: Session, filters: dict) -> Set[UUID]:
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

    # Filtro por preferencias (JSON contains)
    if preferences_contains:
        pref_query = db.query(User.id)
        for key, value in preferences_contains.items():
            from sqlalchemy import cast
            # Para Postgres JSONB @> requiere construcción; aquí aproximamos con texto
            pref_query = pref_query.filter(User.preferences[key].astext == str(value))
        pref_user_ids = set([row[0] for row in pref_query.all()])
        user_ids = user_ids.intersection(pref_user_ids) if user_ids else pref_user_ids

    return user_ids


@app.post("/segments/{segment_id}/preview-users", response_model=List[str])
async def preview_segment_users(segment_id: UUID, limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db), authorization: str | None = Header(default=None)):
    await require_admin(authorization.replace("Bearer ", "") if authorization else "")
    segment = db.query(Segment).filter(Segment.id == segment_id).first()
    if not segment:
        raise HTTPException(status_code=404, detail="Segmento no encontrado")
    user_ids = list(query_user_ids_for_filters(db, segment.filters))
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
            user_ids |= query_user_ids_for_filters(db, segment.filters)
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
            user_ids |= query_user_ids_for_filters(db, segment.filters)

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

