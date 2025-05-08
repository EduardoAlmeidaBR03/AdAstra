from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter(
    prefix="/taxes",
    tags=["taxes"]
)

@router.get("/", response_model=List[schemas.ImpostoResponse])
def read_taxes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    impostos = db.query(models.Imposto).offset(skip).limit(limit).all()
    return impostos

@router.post("/", response_model=schemas.ImpostoResponse, status_code=status.HTTP_201_CREATED)
def create_tax(imposto: schemas.ImpostoCreate, db: Session = Depends(get_db)):
    # Verificar se já existe regra fiscal para esta combinação de países
    db_imposto = db.query(models.Imposto).filter(
        models.Imposto.pais_origem == imposto.pais_origem,
        models.Imposto.pais_destino == imposto.pais_destino
    ).first()
    
    if db_imposto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Regra fiscal já existe para esta combinação de países"
        )
    
    db_imposto = models.Imposto(**imposto.dict())
    db.add(db_imposto)
    db.commit()
    db.refresh(db_imposto)
    return db_imposto

# Rota para simular integração com serviço externo de impostos
@router.post("/api/imposto", status_code=status.HTTP_200_OK)
def calcular_imposto(pais_origem: str, pais_destino: str, valor: float, db: Session = Depends(get_db)):
    # Buscar regra fiscal
    regra_fiscal = db.query(models.Imposto).filter(
        models.Imposto.pais_origem == pais_origem,
        models.Imposto.pais_destino == pais_destino
    ).first()
    
    if not regra_fiscal:
        # Usar regra padrão se não existir específica
        percentual = 5.0  # 5% padrão
    else:
        percentual = float(regra_fiscal.percentual)
    
    # Calcular imposto
    valor_imposto = valor * (percentual / 100)
    
    # Simulação de cálculo com serviço externo TaxJar/AvaTax
    # Em uma aplicação real, isso seria uma chamada para uma API externa
    return {
        "success": True,
        "message": "Cálculo de imposto realizado com sucesso",
        "origem": pais_origem,
        "destino": pais_destino,
        "percentual": percentual,
        "valor_base": valor,
        "valor_imposto": valor_imposto,
        "valor_total": valor + valor_imposto
    }