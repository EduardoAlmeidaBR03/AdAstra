from sqlalchemy import Column, String, Integer, Float, Boolean, Date, DateTime, Enum, Text, ForeignKey, DECIMAL, Table
from sqlalchemy.dialects.sqlite import DATETIME as TIMESTAMP
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime, date, timedelta
from app.database.database import Base

class StatusMedico(str, enum.Enum):
    PENDENTE = "Pendente"
    APROVADO = "Aprovado"
    REPROVADO = "Reprovado"

class CertificacaoStatus(str, enum.Enum):
    PENDENTE = "Pendente"
    CONCLUIDA = "Concluída"

class TipoPacote(str, enum.Enum):
    SUBORBITAL = "Suborbital"
    ESTACAO_ESPACIAL = "Estação Espacial"

class StatusReserva(str, enum.Enum):
    RESERVADO = "Reservado"
    CANCELADO = "Cancelado"
    PAGO = "Pago"
    EMBARCADO = "Embarcado"
    CONCLUIDO = "Concluído"

class StatusPagamento(str, enum.Enum):
    PENDENTE = "Pendente"
    CONFIRMADO = "Confirmado"
    FALHOU = "Falhou"

class StatusViagem(str, enum.Enum):
    AGENDADA = "Agendada"
    EM_ANDAMENTO = "Em Andamento"
    CONCLUIDA = "Concluída"
    CANCELADA = "Cancelada"

# Tabela de associação entre viagens e reservas
viagem_reserva = Table(
    'trip_bookings',
    Base.metadata,
    Column('viagem_id', String, ForeignKey('trips.id'), primary_key=True),
    Column('reserva_id', String, ForeignKey('bookings.id'), primary_key=True),
    Column('assento', String(20), nullable=True),
    Column('data_associacao', TIMESTAMP, default=datetime.utcnow)
)

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    documento_identidade = Column(String(100), nullable=False)
    telefone = Column(String(20), nullable=False)
    pais = Column(String(100), nullable=False)
    endereco = Column(Text, nullable=False)
    status_medico = Column(Enum(StatusMedico), default=StatusMedico.PENDENTE)
    certificacao_status = Column(Enum(CertificacaoStatus), default=CertificacaoStatus.PENDENTE)
    data_cadastro = Column(TIMESTAMP, default=datetime.utcnow)
    ultima_atualizacao = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    reservas = relationship("Reserva", back_populates="cliente")
    certificacoes = relationship("Certificacao", back_populates="cliente")
    aprovacoes_medicas = relationship("AprovacaoMedica", back_populates="cliente")

class Pacote(Base):
    __tablename__ = "packages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=False)
    tipo = Column(Enum(TipoPacote), nullable=False)
    preco = Column(DECIMAL(10, 2), nullable=False)
    disponibilidade = Column(Boolean, default=True)

    # Relacionamentos
    reservas = relationship("Reserva", back_populates="pacote")
    viagens = relationship("Viagem", back_populates="pacote")

class Reserva(Base):
    __tablename__ = "bookings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cliente_id = Column(String, ForeignKey("clientes.id"), nullable=False)
    package_id = Column(String, ForeignKey("packages.id"), nullable=False)
    data_reserva = Column(TIMESTAMP, default=datetime.utcnow)
    status = Column(Enum(StatusReserva), default=StatusReserva.RESERVADO)
    valor_original = Column(DECIMAL(10, 2), nullable=False)  # Valor original do pacote
    valor_imposto = Column(DECIMAL(10, 2), nullable=False)  # Valor do imposto
    valor_total = Column(DECIMAL(10, 2), nullable=False)  # Valor total (pacote + imposto)
    assento = Column(String(20), nullable=True)  # Assento designado na viagem 

    # Relacionamentos
    cliente = relationship("Cliente", back_populates="reservas")
    pacote = relationship("Pacote", back_populates="reservas")
    pagamentos = relationship("Pagamento", back_populates="reserva")
    viagens = relationship("Viagem", secondary=viagem_reserva, back_populates="reservas")

class AprovacaoMedica(Base):
    __tablename__ = "medical_clearance"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cliente_id = Column(String, ForeignKey("clientes.id"), nullable=False)
    aprovado = Column(Boolean, default=False)
    detalhes = Column(Text, nullable=True)
    data_verificacao = Column(TIMESTAMP, default=datetime.utcnow)

    # Relacionamentos
    cliente = relationship("Cliente", back_populates="aprovacoes_medicas")

class Certificacao(Base):
    __tablename__ = "certifications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cliente_id = Column(String, ForeignKey("clientes.id"), nullable=False)
    descricao = Column(Text, nullable=False)
    concluida = Column(Boolean, default=False)
    data_certificacao = Column(TIMESTAMP, default=datetime.utcnow)

    # Relacionamentos
    cliente = relationship("Cliente", back_populates="certificacoes")

class Moeda(Base):
    __tablename__ = "currencies"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(100), nullable=False)
    codigo = Column(String(10), nullable=False, unique=True)
    taxa_cambio = Column(DECIMAL(10, 6), nullable=False)

    # Relacionamentos
    pagamentos = relationship("Pagamento", back_populates="moeda")

class Pagamento(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_id = Column(String, ForeignKey("bookings.id"), nullable=False)
    valor = Column(DECIMAL(10, 2), nullable=False)
    moeda_id = Column(String, ForeignKey("currencies.id"), nullable=False)
    status = Column(Enum(StatusPagamento), default=StatusPagamento.PENDENTE)
    data_pagamento = Column(TIMESTAMP, default=datetime.utcnow)

    # Relacionamentos
    reserva = relationship("Reserva", back_populates="pagamentos")
    moeda = relationship("Moeda", back_populates="pagamentos")

class Imposto(Base):
    __tablename__ = "taxes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pais_origem = Column(String(100), nullable=False)
    pais_destino = Column(String(100), nullable=False)
    percentual = Column(DECIMAL(5, 2), nullable=False)
    descricao = Column(Text, nullable=True)

class Viagem(Base):
    __tablename__ = "trips"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pacote_id = Column(String, ForeignKey("packages.id"), nullable=False)  # Adicionando referência ao pacote
    data_partida = Column(DateTime, nullable=False)
    duracao_horas = Column(Integer, nullable=False)
    descricao = Column(Text, nullable=True)
    status = Column(Enum(StatusViagem), default=StatusViagem.AGENDADA)
    capacidade = Column(Integer, default=1)  # Número máximo de passageiros
    data_criacao = Column(TIMESTAMP, default=datetime.utcnow)
    data_atualizacao = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    pacote = relationship("Pacote", back_populates="viagens")
    reservas = relationship("Reserva", secondary=viagem_reserva, back_populates="viagens")

    @property
    def data_retorno(self):
        """Calcula a data estimada de retorno com base na duração da viagem"""
        return self.data_partida + timedelta(hours=self.duracao_horas)
    
    @property
    def numero_passageiros(self):
        """Retorna o número atual de passageiros (reservas)"""
        return len(self.reservas)
    
    @property
    def vagas_disponiveis(self):
        """Retorna o número de vagas disponíveis"""
        return max(0, self.capacidade - self.numero_passageiros)