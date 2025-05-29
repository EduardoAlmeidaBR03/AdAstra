from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models import models
from app.schemas import schemas
from sqlalchemy import desc

router = APIRouter(
    prefix="/medical_clearance",
    tags=["medical_clearance"]
)

@router.get("/{cliente_id}", response_model=List[schemas.AprovacaoMedicaResponse])
def get_medical_clearance(cliente_id: str, db: Session = Depends(get_db)):
    # Verificar se o cliente existe
    cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    aprovacoes = db.query(models.AprovacaoMedica).filter(
        models.AprovacaoMedica.cliente_id == cliente_id
    ).order_by(desc(models.AprovacaoMedica.data_verificacao)).all()
    return aprovacoes

@router.post("/", response_model=schemas.AprovacaoMedicaResponse, status_code=status.HTTP_201_CREATED)
def create_medical_clearance(aprovacao: schemas.AprovacaoMedicaCreate, db: Session = Depends(get_db)):
    # Verificar se o cliente existe
    cliente = db.query(models.Cliente).filter(models.Cliente.id == aprovacao.cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Criar registro de aprovação médica
    db_aprovacao = models.AprovacaoMedica(**aprovacao.dict())
    db.add(db_aprovacao)
    
    # Atualizar status médico do cliente com base na aprovação mais recente
    atualizar_status_medico(cliente, aprovacao.aprovado, db)
    
    db.commit()
    db.refresh(db_aprovacao)
    return db_aprovacao

@router.put("/{medical_clearance_id}", response_model=schemas.AprovacaoMedicaResponse)
def update_medical_clearance(
    medical_clearance_id: str, 
    aprovacao: schemas.AprovacaoMedicaUpdate, 
    db: Session = Depends(get_db)
):
    # Verificar se a aprovação médica existe
    db_aprovacao = db.query(models.AprovacaoMedica).filter(
        models.AprovacaoMedica.id == medical_clearance_id
    ).first()
    
    if not db_aprovacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aprovação médica não encontrada"
        )
    
    # Atualizar dados da aprovação médica
    aprovacao_data = aprovacao.dict(exclude_unset=True)
    for key, value in aprovacao_data.items():
        setattr(db_aprovacao, key, value)
    
    # Se o status de aprovação foi alterado, atualizar o status médico do cliente
    if "aprovado" in aprovacao_data:
        cliente = db.query(models.Cliente).filter(
            models.Cliente.id == db_aprovacao.cliente_id
        ).first()
        
        atualizar_status_medico(cliente, db_aprovacao.aprovado, db)
    
    db.commit()
    db.refresh(db_aprovacao)
    return db_aprovacao

# Função auxiliar para atualizar o status médico do cliente
def atualizar_status_medico(cliente, aprovado, db):
    if aprovado:
        cliente.status_medico = models.StatusMedico.APROVADO
    else:
        # Quando a aprovação médica é false, o status deve ser REPROVADO
        cliente.status_medico = models.StatusMedico.REPROVADO

# Nova rota para atualizar apenas o status de aprovação médica
@router.patch("/{medical_clearance_id}/status", response_model=schemas.AprovacaoMedicaResponse)
def update_medical_clearance_status(
    medical_clearance_id: str, 
    status: schemas.AprovacaoMedicaUpdate, 
    db: Session = Depends(get_db)
):
    """
    Atualiza apenas o status de aprovação médica.
    Esta rota é mais específica que a rota PUT e permite atualizar apenas o status.
    """
    # Verificar se a aprovação médica existe
    db_aprovacao = db.query(models.AprovacaoMedica).filter(
        models.AprovacaoMedica.id == medical_clearance_id
    ).first()
    
    if not db_aprovacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aprovação médica não encontrada"
        )
    
    # Verificar se o campo aprovado foi fornecido
    if status.aprovado is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O campo 'aprovado' é obrigatório"
        )
    
    # Atualizar apenas o status de aprovação
    db_aprovacao.aprovado = status.aprovado
    
    # Se o status de detalhes foi fornecido, atualizar também
    if status.detalhes is not None:
        db_aprovacao.detalhes = status.detalhes
    
    # Atualizar status médico do cliente
    cliente = db.query(models.Cliente).filter(
        models.Cliente.id == db_aprovacao.cliente_id
    ).first()
    
    atualizar_status_medico(cliente, db_aprovacao.aprovado, db)
    
    db.commit()
    db.refresh(db_aprovacao)
    return db_aprovacao

# Rota para simular integração com serviço externo de verificação médica
@router.post("/api/verifica-medico", status_code=status.HTTP_200_OK)
def verifica_medico(cliente_id: str, db: Session = Depends(get_db)):
    # Verificar se o cliente existe
    cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Simulação de verificação com serviço externo HealthVerity
    # Em uma aplicação real, isso seria uma chamada para uma API externa
    return {
        "success": True,
        "message": "Verificação médica processada com sucesso",
        "status": "Pendente"
    }