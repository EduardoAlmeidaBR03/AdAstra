from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import mercadopago
import os
from app.database.database import get_db
from app.models import models
from app.schemas import schemas

# Configuração do MercadoPago
# Em produção, estas chaves devem ser armazenadas em variáveis de ambiente
MERCADO_PAGO_ACCESS_TOKEN = os.getenv("MERCADO_PAGO_ACCESS_TOKEN", "TEST-2915071579656535-051412-4a9844add009320a3f088ee8af1a03bc-574627484")
mp = mercadopago.SDK(MERCADO_PAGO_ACCESS_TOKEN)

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

# Rota para criar preferência de pagamento no MercadoPago
@router.post("/mercadopago/create_preference", status_code=status.HTTP_200_OK)
def criar_preferencia_mercadopago(
    booking_id: str, 
    db: Session = Depends(get_db)
):
    # Verificar se a reserva existe
    reserva = db.query(models.Reserva).filter(models.Reserva.id == booking_id).first()
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva não encontrada"
        )
    
    # Obter informações do pacote associado à reserva
    pacote = db.query(models.Pacote).filter(models.Pacote.id == reserva.package_id).first()
    if not pacote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pacote não encontrado"
        )
    
    # Criando a preferência de pagamento no MercadoPago
    preference_data = {
        "items": [
            {
                "title": f"Pacote Espacial: {pacote.nome}",
                "quantity": 1,
                "currency_id": "BRL",  # Pode ser alterado para outras moedas suportadas
                "unit_price": float(reserva.valor_total)
            }
        ],
        "back_urls": {
            "success": "http://localhost:8000/payments/success",
            "failure": "http://localhost:8000/payments/failure",
            "pending": "http://localhost:8000/payments/pending"
        },
        "external_reference": booking_id,
        "notification_url": "http://localhost:8000/webhook/mercadopago"
    }
    
    # Removido auto_return que causava erro
    
    try:
        preference_response = mp.preference().create(preference_data)
        
        # Verificar se a resposta da API foi bem-sucedida
        if "response" not in preference_response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro na comunicação com o MercadoPago: resposta inválida"
            )
        
        preference = preference_response["response"]
        
        # Verificar se as chaves necessárias estão presentes na resposta
        required_keys = ["id", "init_point", "sandbox_init_point"]
        missing_keys = [key for key in required_keys if key not in preference]
        if missing_keys:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Resposta incompleta do MercadoPago: campos ausentes: {', '.join(missing_keys)}"
            )
        
        # Retorna os links de pagamento e o ID da preferência
        return {
            "success": True,
            "preference_id": preference["id"],
            "init_point": preference["init_point"],
            "sandbox_init_point": preference["sandbox_init_point"]
        }
    except Exception as e:
        print(f"DEBUG - Erro ao criar preferência: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar pagamento com MercadoPago: {str(e)}"
        )

# Webhook para receber notificações do MercadoPago
@router.post("/webhook/mercadopago", status_code=status.HTTP_200_OK)
async def mercadopago_webhook(data: Dict[str, Any], db: Session = Depends(get_db)):
    try:
        if data["type"] == "payment":
            payment_id = data["data"]["id"]
            
            # Consultar informações do pagamento no MercadoPago
            payment_info = mp.payment().get(payment_id)
            
            # Verificar se a resposta tem o formato esperado
            if not isinstance(payment_info, dict):
                return {"status": "error", "message": "Resposta inválida do MercadoPago"}
            
            if "status" not in payment_info or payment_info["status"] != 200:
                return {"status": "error", "message": "Status da resposta do MercadoPago inválido"}
            
            if "response" not in payment_info:
                return {"status": "error", "message": "Resposta do MercadoPago não contém o campo 'response'"}
                
            payment_data = payment_info["response"]
            
            # Verificar campos obrigatórios no payment_data
            required_fields = ["external_reference", "status", "transaction_amount", "payment_method_id", "currency_id"]
            for field in required_fields:
                if field not in payment_data:
                    return {"status": "error", "message": f"Campo '{field}' ausente na resposta do MercadoPago"}
            
            external_reference = payment_data["external_reference"]  # booking_id
            payment_status = payment_data["status"]
                
            # Obter a reserva pelo external_reference
            reserva = db.query(models.Reserva).filter(models.Reserva.id == external_reference).first()
            if reserva:
                # Mapear status do MercadoPago para o status interno
                status_map = {
                    "approved": models.StatusPagamento.CONFIRMADO,
                    "pending": models.StatusPagamento.PENDENTE,
                    "rejected": models.StatusPagamento.RECUSADO
                }
                
                # Criar o registro de pagamento no banco de dados
                moeda = db.query(models.Moeda).filter(models.Moeda.codigo == payment_data["currency_id"]).first()
                if not moeda:
                    # Se a moeda não existir, use uma moeda padrão ou crie-a
                    moeda = db.query(models.Moeda).filter(models.Moeda.codigo == "BRL").first()
                
                pagamento = models.Pagamento(
                    booking_id=external_reference,
                    moeda_id=moeda.id,
                    valor=payment_data["transaction_amount"],
                    metodo=f"MercadoPago - {payment_data['payment_method_id']}",
                    status=status_map.get(payment_status, models.StatusPagamento.PENDENTE),
                    referencia_externa=str(payment_id)
                )
                
                db.add(pagamento)
                
                # Atualizar status da reserva se o pagamento for confirmado
                if payment_status == "approved":
                    reserva.status = models.StatusReserva.PAGO
                
                db.commit()
                
        return {"status": "success"}
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }