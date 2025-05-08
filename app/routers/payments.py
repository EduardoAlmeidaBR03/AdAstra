from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter(
    prefix="/payments",
    tags=["payments"]
)

@router.get("/", response_model=List[schemas.PagamentoResponse])
def read_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    pagamentos = db.query(models.Pagamento).offset(skip).limit(limit).all()
    return pagamentos

@router.get("/{payment_id}", response_model=schemas.PagamentoResponse)
def read_payment(payment_id: str, db: Session = Depends(get_db)):
    db_pagamento = db.query(models.Pagamento).filter(models.Pagamento.id == payment_id).first()
    if db_pagamento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pagamento não encontrado"
        )
    return db_pagamento

@router.post("/", response_model=schemas.PagamentoResponse, status_code=status.HTTP_201_CREATED)
def create_payment(pagamento: schemas.PagamentoCreate, db: Session = Depends(get_db)):
    # Verificar se a reserva existe
    reserva = db.query(models.Reserva).filter(models.Reserva.id == pagamento.booking_id).first()
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva não encontrada"
        )
    
    # Verificar se a moeda existe
    moeda = db.query(models.Moeda).filter(models.Moeda.id == pagamento.moeda_id).first()
    if not moeda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Moeda não encontrada"
        )
    
    db_pagamento = models.Pagamento(**pagamento.dict())
    db.add(db_pagamento)
    
    # Atualizar status da reserva para "Pago" quando um pagamento for confirmado
    if db_pagamento.status == models.StatusPagamento.CONFIRMADO:
        reserva.status = models.StatusReserva.PAGO
    
    db.commit()
    db.refresh(db_pagamento)
    return db_pagamento

@router.put("/{payment_id}", response_model=schemas.PagamentoResponse)
def update_payment(payment_id: str, pagamento: schemas.PagamentoUpdate, db: Session = Depends(get_db)):
    db_pagamento = db.query(models.Pagamento).filter(models.Pagamento.id == payment_id).first()
    if db_pagamento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pagamento não encontrado"
        )
    
    # Atualizar status do pagamento
    pagamento_data = pagamento.dict(exclude_unset=True)
    for key, value in pagamento_data.items():
        setattr(db_pagamento, key, value)
    
    # Se pagamento for confirmado, atualizar status da reserva
    if pagamento.status == models.StatusPagamento.CONFIRMADO:
        reserva = db.query(models.Reserva).filter(models.Reserva.id == db_pagamento.booking_id).first()
        reserva.status = models.StatusReserva.PAGO
    
    db.commit()
    db.refresh(db_pagamento)
    return db_pagamento

# Rota para simular integração com serviço externo de pagamento
@router.post("/api/pagamento", status_code=status.HTTP_200_OK)
def processar_pagamento(booking_id: str, valor: float, moeda_codigo: str, db: Session = Depends(get_db)):
    # Verificar se a reserva existe
    reserva = db.query(models.Reserva).filter(models.Reserva.id == booking_id).first()
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva não encontrada"
        )
    
    # Verificar se a moeda existe
    moeda = db.query(models.Moeda).filter(models.Moeda.codigo == moeda_codigo).first()
    if not moeda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Moeda não encontrada"
        )
    
    # Simulação de processamento com serviço externo Stripe/Coinbase
    # Em uma aplicação real, isso seria uma chamada para uma API externa
    return {
        "success": True,
        "message": "Pagamento processado com sucesso",
        "transaction_id": "pay_" + booking_id[:8],
        "status": "Confirmado"
    }