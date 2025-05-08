from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models import models
from app.schemas import schemas
from passlib.context import CryptContext

router = APIRouter(
    prefix="/clientes",
    tags=["clientes"]
)

# Configuração para hash de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

@router.post("/", response_model=schemas.ClienteResponse, status_code=status.HTTP_201_CREATED)
def create_cliente(cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    # Verificar se e-mail já existe
    db_cliente = db.query(models.Cliente).filter(models.Cliente.email == cliente.email).first()
    if db_cliente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Criar cliente com senha hash
    senha_hash = get_password_hash(cliente.senha)
    db_cliente = models.Cliente(
        nome=cliente.nome,
        email=cliente.email,
        senha_hash=senha_hash,
        data_nascimento=cliente.data_nascimento,
        documento_identidade=cliente.documento_identidade,
        telefone=cliente.telefone,
        pais=cliente.pais,
        endereco=cliente.endereco
    )
    
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@router.get("/", response_model=List[schemas.ClienteResponse])
def read_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    clientes = db.query(models.Cliente).offset(skip).limit(limit).all()
    return clientes

@router.get("/{cliente_id}", response_model=schemas.ClienteResponse)
def read_cliente(cliente_id: str, db: Session = Depends(get_db)):
    db_cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if db_cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    return db_cliente

@router.put("/{cliente_id}", response_model=schemas.ClienteResponse)
def update_cliente(cliente_id: str, cliente: schemas.ClienteUpdate, db: Session = Depends(get_db)):
    db_cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if db_cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Atualizar dados do cliente
    cliente_data = cliente.dict(exclude_unset=True)
    for key, value in cliente_data.items():
        setattr(db_cliente, key, value)
    
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cliente(cliente_id: str, db: Session = Depends(get_db)):
    db_cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if db_cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    db.delete(db_cliente)
    db.commit()
    return None