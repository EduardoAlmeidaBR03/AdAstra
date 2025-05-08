from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter(
    prefix="/certifications",
    tags=["certifications"]
)

@router.get("/{cliente_id}", response_model=List[schemas.CertificacaoResponse])
def get_certifications(cliente_id: str, db: Session = Depends(get_db)):
    # Verificar se o cliente existe
    cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    certificacoes = db.query(models.Certificacao).filter(
        models.Certificacao.cliente_id == cliente_id
    ).all()
    return certificacoes

@router.post("/", response_model=schemas.CertificacaoResponse, status_code=status.HTTP_201_CREATED)
def create_certification(certificacao: schemas.CertificacaoCreate, db: Session = Depends(get_db)):
    # Verificar se o cliente existe
    cliente = db.query(models.Cliente).filter(models.Cliente.id == certificacao.cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Criar registro de certificação
    db_certificacao = models.Certificacao(**certificacao.dict())
    db.add(db_certificacao)
    
    # Verificar se todas as certificações estão concluídas
    if certificacao.concluida:
        todas_certificacoes = db.query(models.Certificacao).filter(
            models.Certificacao.cliente_id == certificacao.cliente_id
        ).all()
        
        todas_concluidas = all(cert.concluida for cert in todas_certificacoes)
        
        # Se todas as certificações estiverem concluídas, atualizar o status do cliente
        if todas_concluidas:
            cliente.certificacao_status = models.CertificacaoStatus.CONCLUIDA
    
    db.commit()
    db.refresh(db_certificacao)
    return db_certificacao

@router.put("/{certification_id}", response_model=schemas.CertificacaoResponse)
def update_certification(certification_id: str, certificacao: schemas.CertificacaoUpdate, db: Session = Depends(get_db)):
    db_certificacao = db.query(models.Certificacao).filter(models.Certificacao.id == certification_id).first()
    if db_certificacao is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificação não encontrada"
        )
    
    # Atualizar dados da certificação
    certificacao_data = certificacao.dict(exclude_unset=True)
    for key, value in certificacao_data.items():
        setattr(db_certificacao, key, value)
    
    # Verificar se todas as certificações estão concluídas
    if db_certificacao.concluida:
        cliente = db.query(models.Cliente).filter(models.Cliente.id == db_certificacao.cliente_id).first()
        todas_certificacoes = db.query(models.Certificacao).filter(
            models.Certificacao.cliente_id == db_certificacao.cliente_id
        ).all()
        
        todas_concluidas = all(cert.concluida for cert in todas_certificacoes)
        
        # Se todas as certificações estiverem concluídas, atualizar o status do cliente
        if todas_concluidas:
            cliente.certificacao_status = models.CertificacaoStatus.CONCLUIDA
    
    db.commit()
    db.refresh(db_certificacao)
    return db_certificacao

# Rota para simular integração com serviço externo de verificação de certificado
@router.post("/api/verifica-certificado", status_code=status.HTTP_200_OK)
def verifica_certificado(cliente_id: str, descricao: str, db: Session = Depends(get_db)):
    # Verificar se o cliente existe
    cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Simulação de verificação com serviço externo TrueProfile
    # Em uma aplicação real, isso seria uma chamada para uma API externa
    return {
        "success": True,
        "message": "Verificação de certificado processada com sucesso",
        "status": "Válido"
    }