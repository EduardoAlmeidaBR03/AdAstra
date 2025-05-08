from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter(
    prefix="/passengers",
    tags=["passengers"]
)

@router.post("/", response_model=schemas.PassageiroResponse, status_code=status.HTTP_201_CREATED)
def create_passenger(passageiro: schemas.PassageiroCreate, db: Session = Depends(get_db)):
    # Verificar se a viagem existe
    viagem = db.query(models.Viagem).filter(models.Viagem.id == passageiro.viagem_id).first()
    if not viagem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Viagem não encontrada"
        )
    
    # Verificar se o cliente existe
    cliente = db.query(models.Cliente).filter(models.Cliente.id == passageiro.cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Verificar se a viagem não está cancelada ou concluída
    if viagem.status in [models.StatusViagem.CANCELADA, models.StatusViagem.CONCLUIDA]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível adicionar passageiros a uma viagem com status {viagem.status}"
        )
    
    # Verificar se o cliente já está registrado nesta viagem
    passageiro_existente = db.query(models.Passageiro).filter(
        models.Passageiro.viagem_id == passageiro.viagem_id,
        models.Passageiro.cliente_id == passageiro.cliente_id
    ).first()
    
    if passageiro_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este cliente já está registrado como passageiro nesta viagem"
        )
    
    # Verificar se há vagas disponíveis na viagem
    if viagem.vagas_disponiveis <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não há vagas disponíveis para esta viagem"
        )
    
    # Verificar se o cliente tem aprovação médica
    if cliente.status_medico != models.StatusMedico.APROVADO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cliente não possui aprovação médica para realizar viagens espaciais"
        )
    
    # Verificar se o cliente completou as certificações necessárias
    if cliente.certificacao_status != models.CertificacaoStatus.CONCLUIDA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cliente não completou todas as certificações necessárias"
        )
    
    # Criar o passageiro
    db_passageiro = models.Passageiro(
        viagem_id=passageiro.viagem_id,
        cliente_id=passageiro.cliente_id,
        assento=passageiro.assento,
        observacoes=passageiro.observacoes
    )
    
    db.add(db_passageiro)
    db.commit()
    db.refresh(db_passageiro)
    return db_passageiro

@router.get("/", response_model=List[schemas.PassageiroResponse])
def read_passengers(
    skip: int = 0, 
    limit: int = 100, 
    viagem_id: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Passageiro)
    
    # Filtrar por viagem se o parâmetro for fornecido
    if viagem_id:
        query = query.filter(models.Passageiro.viagem_id == viagem_id)
    
    passageiros = query.offset(skip).limit(limit).all()
    return passageiros

@router.get("/{passenger_id}", response_model=schemas.PassageiroDetailResponse)
def read_passenger(passenger_id: str, db: Session = Depends(get_db)):
    db_passageiro = db.query(models.Passageiro).filter(models.Passageiro.id == passenger_id).first()
    if db_passageiro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passageiro não encontrado"
        )
    return db_passageiro

@router.put("/{passenger_id}", response_model=schemas.PassageiroResponse)
def update_passenger(passenger_id: str, passageiro: schemas.PassageiroUpdate, db: Session = Depends(get_db)):
    db_passageiro = db.query(models.Passageiro).filter(models.Passageiro.id == passenger_id).first()
    if db_passageiro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passageiro não encontrado"
        )
    
    # Verificar se a viagem permite alterações
    viagem = db.query(models.Viagem).filter(models.Viagem.id == db_passageiro.viagem_id).first()
    if viagem.status in [models.StatusViagem.CONCLUIDA, models.StatusViagem.CANCELADA]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível atualizar passageiros de uma viagem com status {viagem.status}"
        )
    
    # Atualizar os campos do passageiro
    passageiro_data = passageiro.dict(exclude_unset=True)
    for key, value in passageiro_data.items():
        setattr(db_passageiro, key, value)
    
    db.commit()
    db.refresh(db_passageiro)
    return db_passageiro

@router.delete("/{passenger_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_passenger(passenger_id: str, db: Session = Depends(get_db)):
    db_passageiro = db.query(models.Passageiro).filter(models.Passageiro.id == passenger_id).first()
    if db_passageiro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passageiro não encontrado"
        )
    
    # Verificar se a viagem permite remoção de passageiros
    viagem = db.query(models.Viagem).filter(models.Viagem.id == db_passageiro.viagem_id).first()
    if viagem.status in [models.StatusViagem.CONCLUIDA, models.StatusViagem.CANCELADA, models.StatusViagem.EM_ANDAMENTO]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível remover passageiros de uma viagem com status {viagem.status}"
        )
    
    db.delete(db_passageiro)
    db.commit()
    return None