from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models import models
from app.schemas import schemas
from datetime import datetime

router = APIRouter(
    prefix="/trips",
    tags=["trips"]
)

@router.post("/", response_model=schemas.ViagemResponse, status_code=status.HTTP_201_CREATED)
def create_trip(viagem: schemas.ViagemCreate, db: Session = Depends(get_db)):
    # Verificar se o pacote existe
    pacote = db.query(models.Pacote).filter(models.Pacote.id == viagem.pacote_id).first()
    if not pacote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pacote não encontrado"
        )
    
    # Verificar se a data de partida é futura
    if viagem.data_partida <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A data de partida deve ser no futuro"
        )
    
    # Verificar se a duração é válida (maior que zero)
    if viagem.duracao_horas <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A duração da viagem deve ser maior que zero"
        )
    
    # Criar a viagem
    db_viagem = models.Viagem(
        pacote_id=viagem.pacote_id,
        data_partida=viagem.data_partida,
        duracao_horas=viagem.duracao_horas,
        descricao=viagem.descricao,
        capacidade=viagem.capacidade
    )
    
    db.add(db_viagem)
    db.commit()
    db.refresh(db_viagem)
    return db_viagem

@router.get("/", response_model=List[schemas.ViagemResponse])
def read_trips(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    viagens = db.query(models.Viagem).offset(skip).limit(limit).all()
    return viagens

@router.get("/{trip_id}", response_model=schemas.ViagemDetailResponse)
def read_trip(trip_id: str, db: Session = Depends(get_db)):
    db_viagem = db.query(models.Viagem).filter(models.Viagem.id == trip_id).first()
    if db_viagem is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Viagem não encontrada"
        )
    return db_viagem

@router.put("/{trip_id}", response_model=schemas.ViagemResponse)
def update_trip(trip_id: str, viagem: schemas.ViagemUpdate, db: Session = Depends(get_db)):
    db_viagem = db.query(models.Viagem).filter(models.Viagem.id == trip_id).first()
    if db_viagem is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Viagem não encontrada"
        )
    
    # Não permitir alterações em viagens concluídas ou canceladas
    if db_viagem.status in [models.StatusViagem.CONCLUIDA, models.StatusViagem.CANCELADA]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível alterar uma viagem com status {db_viagem.status}"
        )
    
    # Atualizar os campos da viagem
    viagem_data = viagem.dict(exclude_unset=True)
    
    # Validar a data de partida se for fornecida
    if "data_partida" in viagem_data and viagem_data["data_partida"] <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A data de partida deve ser no futuro"
        )
    
    # Validar a duração se for fornecida
    if "duracao_horas" in viagem_data and viagem_data["duracao_horas"] <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A duração da viagem deve ser maior que zero"
        )
    
    # Validar a capacidade - não pode ser menor que o número atual de passageiros
    if "capacidade" in viagem_data and viagem_data["capacidade"] < len(db_viagem.reservas):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A nova capacidade não pode ser menor que o número atual de passageiros"
        )
    
    for key, value in viagem_data.items():
        setattr(db_viagem, key, value)
    
    db.commit()
    db.refresh(db_viagem)
    return db_viagem

@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_trip(trip_id: str, db: Session = Depends(get_db)):
    db_viagem = db.query(models.Viagem).filter(models.Viagem.id == trip_id).first()
    if db_viagem is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Viagem não encontrada"
        )
    
    # Não permitir cancelamento de viagens concluídas
    if db_viagem.status == models.StatusViagem.CONCLUIDA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível cancelar uma viagem já concluída"
        )
    
    # Verificar se a viagem já está em andamento
    if db_viagem.status == models.StatusViagem.EM_ANDAMENTO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível cancelar uma viagem em andamento"
        )
    
    # Cancelar a viagem em vez de excluí-la
    db_viagem.status = models.StatusViagem.CANCELADA
    db.commit()
    
    # Atualizar o status de todas as reservas associadas a esta viagem
    for reserva in db_viagem.reservas:
        reserva.status = models.StatusReserva.CANCELADO
        db.add(reserva)
    
    db.commit()
    return None

@router.put("/{trip_id}/start", response_model=schemas.ViagemResponse)
def start_trip(trip_id: str, db: Session = Depends(get_db)):
    db_viagem = db.query(models.Viagem).filter(models.Viagem.id == trip_id).first()
    if db_viagem is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Viagem não encontrada"
        )
    
    # Verificar se a viagem está agendada
    if db_viagem.status != models.StatusViagem.AGENDADA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível iniciar uma viagem com status {db_viagem.status}"
        )
    
    # Verificar se há pelo menos um passageiro na viagem
    if len(db_viagem.reservas) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível iniciar uma viagem sem passageiros"
        )
    
    # Atualizar status para EM_ANDAMENTO
    db_viagem.status = models.StatusViagem.EM_ANDAMENTO
    
    # Atualizar status das reservas para EMBARCADO
    for reserva in db_viagem.reservas:
        reserva.status = models.StatusReserva.EMBARCADO
        db.add(reserva)
    
    db.commit()
    db.refresh(db_viagem)
    return db_viagem

@router.put("/{trip_id}/complete", response_model=schemas.ViagemResponse)
def complete_trip(trip_id: str, db: Session = Depends(get_db)):
    db_viagem = db.query(models.Viagem).filter(models.Viagem.id == trip_id).first()
    if db_viagem is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Viagem não encontrada"
        )
    
    # Verificar se a viagem está em andamento
    if db_viagem.status != models.StatusViagem.EM_ANDAMENTO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível concluir uma viagem com status {db_viagem.status}"
        )
    
    # Atualizar status para CONCLUIDA
    db_viagem.status = models.StatusViagem.CONCLUIDA
    
    # Atualizar status das reservas para CONCLUIDO
    for reserva in db_viagem.reservas:
        reserva.status = models.StatusReserva.CONCLUIDO
        db.add(reserva)
        
    db.commit()
    db.refresh(db_viagem)
    return db_viagem

@router.post("/{trip_id}/bookings", response_model=schemas.ViagemReservaResponse)
def add_booking_to_trip(trip_id: str, booking_data: schemas.ViagemReservaCreate, db: Session = Depends(get_db)):
    """Adiciona uma reserva existente a uma viagem"""
    
    # Verificar se a viagem existe
    viagem = db.query(models.Viagem).filter(models.Viagem.id == trip_id).first()
    if not viagem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Viagem não encontrada"
        )
    
    # Verificar se a reserva existe
    reserva = db.query(models.Reserva).filter(models.Reserva.id == booking_data.reserva_id).first()
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva não encontrada"
        )
    
    # Verificar se a viagem permite adicionar reservas
    if viagem.status != models.StatusViagem.AGENDADA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Só é possível adicionar reservas a viagens com status AGENDADA, atual: {viagem.status}"
        )
    
    # Verificar se a reserva está paga
    if reserva.status != models.StatusReserva.PAGO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Só é possível adicionar reservas com status PAGO à viagem"
        )
    
    # Verificar se o pacote da reserva é o mesmo da viagem
    if reserva.package_id != viagem.pacote_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O pacote da reserva deve ser o mesmo da viagem"
        )
    
    # Verificar se a reserva já está associada a esta viagem
    if reserva in viagem.reservas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta reserva já está associada a esta viagem"
        )
    
    # Verificar se há vagas disponíveis
    if viagem.vagas_disponiveis <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não há vagas disponíveis nesta viagem"
        )
    
    # Verificar se o cliente tem aprovação médica e certificações
    cliente = reserva.cliente
    if cliente.status_medico != models.StatusMedico.APROVADO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O cliente não possui aprovação médica para viagens espaciais"
        )
    
    if cliente.certificacao_status != models.CertificacaoStatus.CONCLUIDA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O cliente não completou todas as certificações necessárias"
        )
    
    # Adicionar a reserva à viagem na tabela de associação
    statement = models.viagem_reserva.insert().values(
        viagem_id=trip_id,
        reserva_id=booking_data.reserva_id,
        assento=booking_data.assento,
        data_associacao=datetime.utcnow()
    )
    
    db.execute(statement)
    db.commit()
    
    # Atualizar o assento na reserva também
    if booking_data.assento:
        reserva.assento = booking_data.assento
        db.add(reserva)
        db.commit()
    
    # Retornar os dados da associação
    return {
        "viagem_id": trip_id,
        "reserva_id": booking_data.reserva_id,
        "assento": booking_data.assento,
        "data_associacao": datetime.utcnow()
    }

@router.delete("/{trip_id}/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_booking_from_trip(trip_id: str, booking_id: str, db: Session = Depends(get_db)):
    """Remove uma reserva de uma viagem"""
    
    # Verificar se a viagem existe
    viagem = db.query(models.Viagem).filter(models.Viagem.id == trip_id).first()
    if not viagem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Viagem não encontrada"
        )
    
    # Verificar se a reserva existe
    reserva = db.query(models.Reserva).filter(models.Reserva.id == booking_id).first()
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva não encontrada"
        )
    
    # Verificar se a viagem permite remover reservas
    if viagem.status != models.StatusViagem.AGENDADA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Só é possível remover reservas de viagens com status AGENDADA, atual: {viagem.status}"
        )
    
    # Verificar se a reserva está associada a esta viagem
    if reserva not in viagem.reservas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta reserva não está associada a esta viagem"
        )
    
    # Remover a reserva da viagem na tabela de associação
    statement = models.viagem_reserva.delete().where(
        (models.viagem_reserva.c.viagem_id == trip_id) & 
        (models.viagem_reserva.c.reserva_id == booking_id)
    )
    
    db.execute(statement)
    db.commit()
    
    return None