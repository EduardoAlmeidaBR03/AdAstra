from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"]
)

@router.post("/", response_model=schemas.ReservaResponse, status_code=status.HTTP_201_CREATED)
def create_booking(reserva: schemas.ReservaCreate, db: Session = Depends(get_db)):
    # Verificar se o cliente existe
    cliente = db.query(models.Cliente).filter(models.Cliente.id == reserva.cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Verificar se o pacote existe
    pacote = db.query(models.Pacote).filter(models.Pacote.id == reserva.package_id).first()
    if not pacote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pacote não encontrado"
        )
    
    # Verificar se o pacote está disponível
    if not pacote.disponibilidade:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pacote não está disponível"
        )
    
    # 1. Verificar se o cliente tem aprovação médica
    if cliente.status_medico != models.StatusMedico.APROVADO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cliente não possui aprovação médica para realizar viagens espaciais"
        )
    
    # 2. Verificar se o cliente completou as certificações necessárias
    if cliente.certificacao_status != models.CertificacaoStatus.CONCLUIDA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cliente não completou todas as certificações necessárias"
        )
    
    # 3. Calcular o valor da reserva considerando o imposto do país do cliente
    valor_original = float(pacote.preco)
    
    # Buscar regra fiscal para o país do cliente
    regra_fiscal = db.query(models.Imposto).filter(
        models.Imposto.pais_origem == cliente.pais,
        models.Imposto.pais_destino == "Espaço"
    ).first()
    
    # Se não existir regra específica, aplicar taxa padrão de 5%
    if not regra_fiscal:
        percentual_imposto = 5.0
    else:
        percentual_imposto = float(regra_fiscal.percentual)
    
    # Calcular valor do imposto e valor total
    valor_imposto = valor_original * (percentual_imposto / 100)
    valor_total = valor_original + valor_imposto
    
    # Criar a reserva com os valores calculados
    db_reserva = models.Reserva(
        cliente_id=reserva.cliente_id,
        package_id=reserva.package_id,
        valor_original=valor_original,
        valor_imposto=valor_imposto,
        valor_total=valor_total
    )
    
    db.add(db_reserva)
    db.commit()
    db.refresh(db_reserva)
    return db_reserva

@router.get("/", response_model=List[schemas.ReservaResponse])
def read_bookings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    reservas = db.query(models.Reserva).offset(skip).limit(limit).all()
    return reservas

@router.get("/{booking_id}", response_model=schemas.ReservaDetailResponse)
def read_booking(booking_id: str, db: Session = Depends(get_db)):
    db_reserva = db.query(models.Reserva).filter(models.Reserva.id == booking_id).first()
    if db_reserva is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva não encontrada"
        )
    return db_reserva

@router.put("/{booking_id}", response_model=schemas.ReservaResponse)
def update_booking(booking_id: str, reserva: schemas.ReservaUpdate, db: Session = Depends(get_db)):
    db_reserva = db.query(models.Reserva).filter(models.Reserva.id == booking_id).first()
    if db_reserva is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva não encontrada"
        )
    
    # Atualizar status da reserva
    reserva_data = reserva.dict(exclude_unset=True)
    for key, value in reserva_data.items():
        setattr(db_reserva, key, value)
    
    db.commit()
    db.refresh(db_reserva)
    return db_reserva

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(booking_id: str, db: Session = Depends(get_db)):
    db_reserva = db.query(models.Reserva).filter(models.Reserva.id == booking_id).first()
    if db_reserva is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva não encontrada"
        )
    
    # Cancelar a reserva em vez de excluí-la
    db_reserva.status = models.StatusReserva.CANCELADO
    db.commit()
    return None