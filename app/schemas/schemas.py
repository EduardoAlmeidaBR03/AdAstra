from pydantic import BaseModel, EmailStr, Field, validator
from datetime import date, datetime
from typing import Optional, List
from enum import Enum
from decimal import Decimal

# Enums
class StatusMedicoEnum(str, Enum):
    PENDENTE = "Pendente"
    APROVADO = "Aprovado"
    REPROVADO = "Reprovado"

class CertificacaoStatusEnum(str, Enum):
    PENDENTE = "Pendente"
    CONCLUIDA = "Concluída"

class TipoPacoteEnum(str, Enum):
    SUBORBITAL = "Suborbital"
    ESTACAO_ESPACIAL = "Estação Espacial"

class StatusReservaEnum(str, Enum):
    RESERVADO = "Reservado"
    CANCELADO = "Cancelado"
    PAGO = "Pago"
    EMBARCADO = "Embarcado"
    CONCLUIDO = "Concluído"

class StatusPagamentoEnum(str, Enum):
    PENDENTE = "Pendente"
    CONFIRMADO = "Confirmado"
    FALHOU = "Falhou"

class StatusViagemEnum(str, Enum):
    AGENDADA = "Agendada"
    EM_ANDAMENTO = "Em Andamento"
    CONCLUIDA = "Concluída"
    CANCELADA = "Cancelada"

class StatusEmbarqueEnum(str, Enum):
    PENDENTE = "Pendente"
    CONFIRMADO = "Confirmado"
    EMBARCADO = "Embarcado"
    NAO_COMPARECEU = "Não Compareceu"

# Schemas de Cliente
class ClienteBase(BaseModel):
    nome: str
    email: EmailStr
    data_nascimento: date
    documento_identidade: str
    telefone: str
    pais: str
    endereco: str

class ClienteCreate(ClienteBase):
    senha: str

class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    data_nascimento: Optional[date] = None
    documento_identidade: Optional[str] = None
    telefone: Optional[str] = None
    pais: Optional[str] = None
    endereco: Optional[str] = None
    status_medico: Optional[StatusMedicoEnum] = None
    certificacao_status: Optional[CertificacaoStatusEnum] = None

class ClienteResponse(ClienteBase):
    id: str
    status_medico: StatusMedicoEnum
    certificacao_status: CertificacaoStatusEnum
    data_cadastro: datetime
    ultima_atualizacao: datetime

    class Config:
        orm_mode = True

# Schemas de Pacote
class PacoteBase(BaseModel):
    nome: str
    descricao: str
    tipo: TipoPacoteEnum
    preco: Decimal
    disponibilidade: bool = True

class PacoteCreate(PacoteBase):
    pass

class PacoteUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    tipo: Optional[TipoPacoteEnum] = None
    preco: Optional[Decimal] = None
    disponibilidade: Optional[bool] = None

class PacoteResponse(PacoteBase):
    id: str

    class Config:
        orm_mode = True

# Schemas de Reserva
class ReservaBase(BaseModel):
    cliente_id: str
    package_id: str
    assento: Optional[str] = None

class ReservaCreate(ReservaBase):
    pass

class ReservaUpdate(BaseModel):
    status: Optional[StatusReservaEnum] = None
    assento: Optional[str] = None

class ReservaResponse(BaseModel):
    id: str
    cliente_id: str
    package_id: str
    data_reserva: datetime
    status: StatusReservaEnum
    valor_original: Decimal
    valor_imposto: Decimal
    valor_total: Decimal
    assento: Optional[str] = None

    class Config:
        orm_mode = True

class ReservaDetailResponse(ReservaResponse):
    cliente: "ClienteResponse"
    pacote: "PacoteResponse"
    pagamentos: List["PagamentoResponse"] = []
    viagens: List["ViagemResponse"] = []

    class Config:
        orm_mode = True

# Schemas de Aprovação Médica
class AprovacaoMedicaBase(BaseModel):
    cliente_id: str
    aprovado: bool
    detalhes: Optional[str] = None

class AprovacaoMedicaCreate(AprovacaoMedicaBase):
    pass

class AprovacaoMedicaUpdate(BaseModel):
    aprovado: Optional[bool] = None
    detalhes: Optional[str] = None

class AprovacaoMedicaResponse(AprovacaoMedicaBase):
    id: str
    data_verificacao: datetime

    class Config:
        orm_mode = True

# Schemas de Certificação
class CertificacaoBase(BaseModel):
    cliente_id: str
    descricao: str
    concluida: bool = False

class CertificacaoCreate(CertificacaoBase):
    pass

class CertificacaoUpdate(BaseModel):
    descricao: Optional[str] = None
    concluida: Optional[bool] = None

class CertificacaoResponse(CertificacaoBase):
    id: str
    data_certificacao: datetime

    class Config:
        orm_mode = True

# Schemas de Moeda
class MoedaBase(BaseModel):
    nome: str
    codigo: str
    taxa_cambio: Decimal

class MoedaCreate(MoedaBase):
    pass

class MoedaUpdate(BaseModel):
    nome: Optional[str] = None
    codigo: Optional[str] = None
    taxa_cambio: Optional[Decimal] = None

class MoedaResponse(MoedaBase):
    id: str

    class Config:
        orm_mode = True

# Schemas de Pagamento
class PagamentoBase(BaseModel):
    booking_id: str
    valor: Decimal
    moeda_id: str

class PagamentoCreate(PagamentoBase):
    pass

class PagamentoUpdate(BaseModel):
    status: Optional[StatusPagamentoEnum] = None

class PagamentoResponse(PagamentoBase):
    id: str
    status: StatusPagamentoEnum
    data_pagamento: datetime

    class Config:
        orm_mode = True

# Schemas de Imposto
class ImpostoBase(BaseModel):
    pais_origem: str
    pais_destino: str
    percentual: Decimal
    descricao: Optional[str] = None

class ImpostoCreate(ImpostoBase):
    pass

class ImpostoResponse(ImpostoBase):
    id: str

    class Config:
        orm_mode = True

# Schemas de Viagem
class ViagemBase(BaseModel):
    pacote_id: str
    data_partida: datetime
    duracao_horas: int
    descricao: Optional[str] = None
    capacidade: int = 1

class ViagemCreate(ViagemBase):
    pass

class ViagemUpdate(BaseModel):
    data_partida: Optional[datetime] = None
    duracao_horas: Optional[int] = None
    descricao: Optional[str] = None
    capacidade: Optional[int] = None
    status: Optional[StatusViagemEnum] = None

class ViagemResponse(BaseModel):
    id: str
    pacote_id: str
    data_partida: datetime
    duracao_horas: int
    descricao: Optional[str] = None
    capacidade: int
    status: StatusViagemEnum
    data_criacao: datetime
    data_atualizacao: datetime
    numero_passageiros: int
    vagas_disponiveis: int
    data_retorno: datetime

    class Config:
        orm_mode = True

class ViagemDetailResponse(ViagemResponse):
    pacote: "PacoteResponse"
    reservas: List[ReservaResponse] = []

    class Config:
        orm_mode = True

# Schema da relação Viagem-Reserva
class ViagemReservaCreate(BaseModel):
    reserva_id: str
    assento: Optional[str] = None

class ViagemReservaResponse(BaseModel):
    viagem_id: str
    reserva_id: str
    assento: Optional[str] = None
    data_associacao: datetime

    class Config:
        orm_mode = True

# Schemas de Passageiro
class PassageiroBase(BaseModel):
    viagem_id: str
    cliente_id: str
    assento: Optional[str] = None
    observacoes: Optional[str] = None

class PassageiroCreate(PassageiroBase):
    pass

class PassageiroUpdate(BaseModel):
    assento: Optional[str] = None
    status_embarque: Optional[StatusEmbarqueEnum] = None
    observacoes: Optional[str] = None

class PassageiroResponse(BaseModel):
    id: str
    viagem_id: str
    cliente_id: str
    assento: Optional[str] = None
    status_embarque: StatusEmbarqueEnum
    observacoes: Optional[str] = None
    data_criacao: datetime
    data_atualizacao: datetime

    class Config:
        orm_mode = True

class PassageiroDetailResponse(PassageiroResponse):
    cliente: ClienteResponse
    viagem: ViagemResponse

    class Config:
        orm_mode = True