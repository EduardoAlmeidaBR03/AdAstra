from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter(
    prefix="/currencies",
    tags=["currencies"]
)

@router.get("/", response_model=List[schemas.MoedaResponse])
def read_currencies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    moedas = db.query(models.Moeda).offset(skip).limit(limit).all()
    return moedas

@router.post("/", response_model=schemas.MoedaResponse, status_code=status.HTTP_201_CREATED)
def create_currency(moeda: schemas.MoedaCreate, db: Session = Depends(get_db)):
    # Verificar se o código da moeda já existe
    db_moeda = db.query(models.Moeda).filter(models.Moeda.codigo == moeda.codigo).first()
    if db_moeda:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código da moeda já existe"
        )
    
    db_moeda = models.Moeda(**moeda.dict())
    db.add(db_moeda)
    db.commit()
    db.refresh(db_moeda)
    return db_moeda

@router.put("/{currency_id}", response_model=schemas.MoedaResponse)
def update_currency(currency_id: str, moeda: schemas.MoedaUpdate, db: Session = Depends(get_db)):
    db_moeda = db.query(models.Moeda).filter(models.Moeda.id == currency_id).first()
    if db_moeda is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Moeda não encontrada"
        )
    
    # Atualizar dados da moeda
    moeda_data = moeda.dict(exclude_unset=True)
    
    # Verificar se o código já existe, caso esteja sendo atualizado
    if "codigo" in moeda_data and moeda_data["codigo"] != db_moeda.codigo:
        codigo_existente = db.query(models.Moeda).filter(models.Moeda.codigo == moeda_data["codigo"]).first()
        if codigo_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Código da moeda já existe"
            )
    
    for key, value in moeda_data.items():
        setattr(db_moeda, key, value)
    
    db.commit()
    db.refresh(db_moeda)
    return db_moeda