from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter(
    prefix="/packages",
    tags=["packages"]
)

@router.post("/", response_model=schemas.PacoteResponse, status_code=status.HTTP_201_CREATED)
def create_package(pacote: schemas.PacoteCreate, db: Session = Depends(get_db)):
    db_pacote = models.Pacote(**pacote.dict())
    db.add(db_pacote)
    db.commit()
    db.refresh(db_pacote)
    return db_pacote

@router.get("/", response_model=List[schemas.PacoteResponse])
def read_packages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    pacotes = db.query(models.Pacote).offset(skip).limit(limit).all()
    return pacotes

@router.get("/{package_id}", response_model=schemas.PacoteResponse)
def read_package(package_id: str, db: Session = Depends(get_db)):
    db_pacote = db.query(models.Pacote).filter(models.Pacote.id == package_id).first()
    if db_pacote is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pacote não encontrado"
        )
    return db_pacote

@router.put("/{package_id}", response_model=schemas.PacoteResponse)
def update_package(package_id: str, pacote: schemas.PacoteUpdate, db: Session = Depends(get_db)):
    db_pacote = db.query(models.Pacote).filter(models.Pacote.id == package_id).first()
    if db_pacote is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pacote não encontrado"
        )
    
    # Atualizar dados do pacote
    pacote_data = pacote.dict(exclude_unset=True)
    for key, value in pacote_data.items():
        setattr(db_pacote, key, value)
    
    db.commit()
    db.refresh(db_pacote)
    return db_pacote

@router.delete("/{package_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_package(package_id: str, db: Session = Depends(get_db)):
    db_pacote = db.query(models.Pacote).filter(models.Pacote.id == package_id).first()
    if db_pacote is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pacote não encontrado"
        )
    
    db.delete(db_pacote)
    db.commit()
    return None