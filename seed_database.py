import sys
import os
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# Adicionar o diretório raiz ao path para importar os módulos da aplicação
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import SessionLocal, engine, Base
from app.models.models import (
    Cliente, Pacote, Reserva, AprovacaoMedica, Certificacao, 
    Moeda, Pagamento, Imposto, Viagem, StatusMedico, CertificacaoStatus,
    TipoPacote, StatusReserva, StatusPagamento, StatusViagem, viagem_reserva
)

# Configuração para hash de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def seed_database():
    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)
    
    # Criar uma sessão
    db = SessionLocal()
    
    try:
        # Limpar tabelas existentes (opcional - remova essas linhas se quiser manter dados existentes)
        db.execute(viagem_reserva.delete())
        db.query(Viagem).delete()
        db.query(Pagamento).delete()
        db.query(Reserva).delete()
        db.query(AprovacaoMedica).delete()
        db.query(Certificacao).delete()
        db.query(Cliente).delete()
        db.query(Pacote).delete()
        db.query(Moeda).delete()
        db.query(Imposto).delete()
        db.commit()
        
        # Criar moedas
        moedas = [
            Moeda(
                id=str(uuid.uuid4()),
                nome="Dólar Americano",
                codigo="USD",
                taxa_cambio=Decimal("1.0")
            ),
            Moeda(
                id=str(uuid.uuid4()),
                nome="Euro",
                codigo="EUR",
                taxa_cambio=Decimal("1.07")
            ),
            Moeda(
                id=str(uuid.uuid4()),
                nome="Bitcoin",
                codigo="BTC",
                taxa_cambio=Decimal("68750.0")
            ),
            Moeda(
                id=str(uuid.uuid4()),
                nome="Real Brasileiro",
                codigo="BRL",
                taxa_cambio=Decimal("0.18")
            )
        ]
        
        for moeda in moedas:
            db.add(moeda)
        
        db.commit()
        
        # IMPORTANTE: Criar impostos primeiro, pois serão referenciados nas reservas
        impostos = [
            Imposto(
                id=str(uuid.uuid4()),
                pais_origem="Brasil",
                pais_destino="Espaço",
                percentual=Decimal("8.50"),
                descricao="Imposto de serviços espaciais - Brasil"
            ),
            Imposto(
                id=str(uuid.uuid4()),
                pais_origem="Estados Unidos",
                pais_destino="Espaço",
                percentual=Decimal("6.25"),
                descricao="Space Services Tax - EUA"
            ),
            Imposto(
                id=str(uuid.uuid4()),
                pais_origem="União Europeia",
                pais_destino="Espaço",
                percentual=Decimal("7.00"),
                descricao="EU Space Travel VAT"
            )
        ]
        
        for imposto in impostos:
            db.add(imposto)
        
        db.commit()
        
        # Criar clientes de exemplo
        clientes = [
            Cliente(
                id=str(uuid.uuid4()),
                nome="João Silva",
                email="joao.silva@example.com",
                senha_hash=get_password_hash("password123"),
                data_nascimento=date(1985, 5, 15),
                documento_identidade="AB123456",
                telefone="+55 11 99999-8888",
                pais="Brasil",
                endereco="Av. Paulista, 1000, São Paulo, SP",
                status_medico=StatusMedico.PENDENTE,
                certificacao_status=CertificacaoStatus.PENDENTE,
                data_cadastro=datetime.now(),
                ultima_atualizacao=datetime.now()
            ),
            Cliente(
                id=str(uuid.uuid4()),
                nome="Maria Souza",
                email="maria.souza@example.com",
                senha_hash=get_password_hash("senha456"),
                data_nascimento=date(1990, 7, 20),
                documento_identidade="CD789012",
                telefone="+55 21 98888-7777",
                pais="Brasil",
                endereco="Rua Copacabana, 500, Rio de Janeiro, RJ",
                status_medico=StatusMedico.APROVADO,
                certificacao_status=CertificacaoStatus.CONCLUIDA,
                data_cadastro=datetime.now() - timedelta(days=30),
                ultima_atualizacao=datetime.now() - timedelta(days=5)
            ),
            Cliente(
                id=str(uuid.uuid4()),
                nome="John Doe",
                email="john.doe@example.com",
                senha_hash=get_password_hash("pass789"),
                data_nascimento=date(1978, 3, 10),
                documento_identidade="P12345678",
                telefone="+1 555-123-4567",
                pais="Estados Unidos",
                endereco="123 Main St, New York, NY",
                status_medico=StatusMedico.APROVADO,  # Alterado para APROVADO para permitir reservas
                certificacao_status=CertificacaoStatus.CONCLUIDA,  # Alterado para CONCLUÍDA para permitir reservas
                data_cadastro=datetime.now() - timedelta(days=60),
                ultima_atualizacao=datetime.now() - timedelta(days=15)
            )
        ]
        
        for cliente in clientes:
            db.add(cliente)
        
        db.commit()
        
        # Criar pacotes de viagem
        pacotes = [
            Pacote(
                id=str(uuid.uuid4()),
                nome="Experiência Suborbital",
                descricao="Uma experiência única de voo suborbital, onde você ultrapassará a linha de Kármán e experimentará a microgravidade por aproximadamente 5 minutos.",
                tipo=TipoPacote.SUBORBITAL,
                preco=Decimal("250000.00"),
                disponibilidade=True
            ),
            Pacote(
                id=str(uuid.uuid4()),
                nome="Órbita Terrestre",
                descricao="Viaje em órbita ao redor da Terra durante 3 dias, observando o planeta azul de uma perspectiva única.",
                tipo=TipoPacote.SUBORBITAL,
                preco=Decimal("500000.00"),
                disponibilidade=True
            ),
            Pacote(
                id=str(uuid.uuid4()),
                nome="Estadia na Estação Espacial",
                descricao="Passe 7 dias na Estação Espacial Internacional, realizando experimentos científicos e desfrutando da vista privilegiada.",
                tipo=TipoPacote.ESTACAO_ESPACIAL,
                preco=Decimal("35000000.00"),
                disponibilidade=True
            ),
            Pacote(
                id=str(uuid.uuid4()),
                nome="Missão Lunar",
                descricao="Visite a lua em uma missão de 14 dias, incluindo caminhada lunar e coleta de amostras.",
                tipo=TipoPacote.ESTACAO_ESPACIAL,
                preco=Decimal("150000000.00"),
                disponibilidade=False
            )
        ]
        
        for pacote in pacotes:
            db.add(pacote)
        
        db.commit()
        
        # Criar aprovações médicas - para garantir que os clientes possam fazer reservas
        aprovacoes_medicas = [
            AprovacaoMedica(
                id=str(uuid.uuid4()),
                cliente_id=clientes[0].id,
                aprovado=False,
                detalhes="Pendente de exames complementares",
                data_verificacao=datetime.now() - timedelta(days=10)
            ),
            AprovacaoMedica(
                id=str(uuid.uuid4()),
                cliente_id=clientes[1].id,
                aprovado=True,
                detalhes="Todos os exames em conformidade",
                data_verificacao=datetime.now() - timedelta(days=25)
            ),
            AprovacaoMedica(
                id=str(uuid.uuid4()),
                cliente_id=clientes[2].id,
                aprovado=True,  # Alterado para true
                detalhes="Todos os exames em conformidade",
                data_verificacao=datetime.now() - timedelta(days=40)
            )
        ]
        
        for aprovacao in aprovacoes_medicas:
            db.add(aprovacao)
        
        db.commit()
        
        # Criar certificações
        certificacoes = [
            Certificacao(
                id=str(uuid.uuid4()),
                cliente_id=clientes[0].id,
                descricao="Treinamento básico de voo espacial",
                concluida=False,
                data_certificacao=datetime.now() - timedelta(days=5)
            ),
            Certificacao(
                id=str(uuid.uuid4()),
                cliente_id=clientes[1].id,
                descricao="Treinamento completo de astronauta",
                concluida=True,
                data_certificacao=datetime.now() - timedelta(days=20)
            ),
            Certificacao(
                id=str(uuid.uuid4()),
                cliente_id=clientes[1].id,
                descricao="Curso avançado de sobrevivência espacial",
                concluida=True,
                data_certificacao=datetime.now() - timedelta(days=15)
            ),
            Certificacao(
                id=str(uuid.uuid4()),
                cliente_id=clientes[2].id,
                descricao="Treinamento básico de voo espacial",
                concluida=True,
                data_certificacao=datetime.now() - timedelta(days=35)
            ),
            Certificacao(
                id=str(uuid.uuid4()),
                cliente_id=clientes[2].id,
                descricao="Curso avançado de sobrevivência espacial",
                concluida=True,
                data_certificacao=datetime.now() - timedelta(days=30)
            )
        ]
        
        for certificacao in certificacoes:
            db.add(certificacao)
        
        db.commit()
        
        # Criar reservas
        # Agora buscamos os impostos diretamente do banco de dados
        imposto_brasil = db.query(Imposto).filter(
            Imposto.pais_origem == "Brasil",
            Imposto.pais_destino == "Espaço"
        ).first()
        
        imposto_eua = db.query(Imposto).filter(
            Imposto.pais_origem == "Estados Unidos",
            Imposto.pais_destino == "Espaço"
        ).first()
        
        # Reserva 1 - Cliente 1 (Maria) com Pacote 0 (Experiência Suborbital)
        valor_original_1 = float(pacotes[0].preco)
        percentual_1 = float(imposto_brasil.percentual)
        valor_imposto_1 = valor_original_1 * (percentual_1 / 100)
        valor_total_1 = valor_original_1 + valor_imposto_1
        
        # Reserva 2 - Cliente 1 (Maria) com Pacote 2 (Estação Espacial)
        valor_original_2 = float(pacotes[2].preco)
        percentual_2 = float(imposto_brasil.percentual)
        valor_imposto_2 = valor_original_2 * (percentual_2 / 100)
        valor_total_2 = valor_original_2 + valor_imposto_2
        
        # Reserva 3 - Cliente 2 (John) com Pacote 2 (Estação Espacial) - mesmo pacote para testar múltiplas reservas
        valor_original_3 = float(pacotes[2].preco)
        percentual_3 = float(imposto_eua.percentual)
        valor_imposto_3 = valor_original_3 * (percentual_3 / 100)
        valor_total_3 = valor_original_3 + valor_imposto_3
        
        # Reserva 4 - Cliente 2 (John) com Pacote 1 (Órbita Terrestre)
        valor_original_4 = float(pacotes[1].preco)
        percentual_4 = float(imposto_eua.percentual)
        valor_imposto_4 = valor_original_4 * (percentual_4 / 100)
        valor_total_4 = valor_original_4 + valor_imposto_4
        
        reservas = [
            Reserva(
                id=str(uuid.uuid4()),
                cliente_id=clientes[1].id,  # Maria (tem aprovação médica e certificações)
                package_id=pacotes[0].id,
                data_reserva=datetime.now() - timedelta(days=15),
                status=StatusReserva.RESERVADO,
                valor_original=valor_original_1,
                valor_imposto=valor_imposto_1,
                valor_total=valor_total_1,
                assento=None  # Será definido quando associado a uma viagem
            ),
            Reserva(
                id=str(uuid.uuid4()),
                cliente_id=clientes[1].id,  # Maria (tem aprovação médica e certificações)
                package_id=pacotes[2].id,
                data_reserva=datetime.now() - timedelta(days=45),
                status=StatusReserva.PAGO,
                valor_original=valor_original_2,
                valor_imposto=valor_imposto_2,
                valor_total=valor_total_2,
                assento=None
            ),
            Reserva(
                id=str(uuid.uuid4()),
                cliente_id=clientes[2].id,  # John (tem aprovação médica e certificações)
                package_id=pacotes[2].id,  # Mesmo pacote da Maria para testar múltiplas reservas em uma viagem
                data_reserva=datetime.now() - timedelta(days=40),
                status=StatusReserva.PAGO,
                valor_original=valor_original_3,
                valor_imposto=valor_imposto_3,
                valor_total=valor_total_3,
                assento=None
            ),
            Reserva(
                id=str(uuid.uuid4()),
                cliente_id=clientes[2].id,  # John (tem aprovação médica e certificações)
                package_id=pacotes[1].id,
                data_reserva=datetime.now() - timedelta(days=60),
                status=StatusReserva.CANCELADO,
                valor_original=valor_original_4,
                valor_imposto=valor_imposto_4,
                valor_total=valor_total_4,
                assento=None
            )
        ]
        
        for reserva in reservas:
            db.add(reserva)
        
        db.commit()
        
        # Criar pagamentos
        pagamentos = [
            Pagamento(
                id=str(uuid.uuid4()),
                booking_id=reservas[0].id,
                valor=Decimal(valor_total_1),
                moeda_id=moedas[0].id,  # USD
                status=StatusPagamento.PENDENTE,
                data_pagamento=datetime.now() - timedelta(days=14)
            ),
            Pagamento(
                id=str(uuid.uuid4()),
                booking_id=reservas[1].id,
                valor=Decimal(valor_total_2),
                moeda_id=moedas[0].id,  # USD
                status=StatusPagamento.CONFIRMADO,
                data_pagamento=datetime.now() - timedelta(days=40)
            ),
            Pagamento(
                id=str(uuid.uuid4()),
                booking_id=reservas[2].id,
                valor=Decimal(valor_total_3),
                moeda_id=moedas[1].id,  # EUR
                status=StatusPagamento.CONFIRMADO,  # John também tem pagamento confirmado
                data_pagamento=datetime.now() - timedelta(days=35)
            ),
            Pagamento(
                id=str(uuid.uuid4()),
                booking_id=reservas[3].id,
                valor=Decimal(valor_total_4),
                moeda_id=moedas[1].id,  # EUR
                status=StatusPagamento.FALHOU,
                data_pagamento=datetime.now() - timedelta(days=58)
            )
        ]
        
        for pagamento in pagamentos:
            db.add(pagamento)
        
        db.commit()
        
        # Criar viagens para os pacotes
        viagens = [
            Viagem(
                id=str(uuid.uuid4()),
                pacote_id=pacotes[2].id,  # Viagem para o pacote Estação Espacial
                data_partida=datetime.now() + timedelta(days=30),  # Viagem no futuro
                duracao_horas=72,  # 3 dias na estação espacial
                descricao="Visita à Estação Espacial Internacional com atividades científicas e observação da Terra",
                status=StatusViagem.AGENDADA,
                capacidade=5,  # Capacidade para 5 passageiros
                data_criacao=datetime.now() - timedelta(days=38),
                data_atualizacao=datetime.now() - timedelta(days=38)
            ),
            Viagem(
                id=str(uuid.uuid4()),
                pacote_id=pacotes[2].id,  # Viagem para o pacote Estação Espacial
                data_partida=datetime.now() + timedelta(days=180),  # Viagem mais distante no futuro
                duracao_horas=120,  # 5 dias
                descricao="Retorno à Estação Espacial Internacional para experimentos avançados",
                status=StatusViagem.AGENDADA,
                capacidade=3,  # Capacidade para 3 passageiros
                data_criacao=datetime.now() - timedelta(days=30),
                data_atualizacao=datetime.now() - timedelta(days=30)
            )
        ]
        
        # Adicionando uma viagem com status EM_ANDAMENTO
        viagem_em_andamento = Viagem(
            id=str(uuid.uuid4()),
            pacote_id=pacotes[2].id,  # Viagem para o pacote Estação Espacial
            data_partida=datetime.now() - timedelta(days=2),  # Iniciou há 2 dias
            duracao_horas=168,  # 7 dias
            descricao="Missão de pesquisa na Estação Espacial com experimentos de cristalização",
            status=StatusViagem.EM_ANDAMENTO,
            capacidade=4,  # Capacidade para 4 passageiros
            data_criacao=datetime.now() - timedelta(days=60),
            data_atualizacao=datetime.now() - timedelta(days=2)  # Atualizado quando começou
        )
        viagens.append(viagem_em_andamento)
        
        # Adicionando uma viagem com status CONCLUIDA
        viagem_concluida = Viagem(
            id=str(uuid.uuid4()),
            pacote_id=pacotes[2].id,  # Viagem para o pacote Estação Espacial
            data_partida=datetime.now() - timedelta(days=90),
            duracao_horas=48,  # 2 dias
            descricao="Voo de treinamento e adaptação às condições de microgravidade",
            status=StatusViagem.CONCLUIDA,
            capacidade=2,  # Capacidade para 2 passageiros
            data_criacao=datetime.now() - timedelta(days=120),
            data_atualizacao=datetime.now() - timedelta(days=88)  # Atualizado quando concluiu
        )
        viagens.append(viagem_concluida)
        
        # Adicionando uma viagem com status CANCELADA
        viagem_cancelada = Viagem(
            id=str(uuid.uuid4()),
            pacote_id=pacotes[2].id,  # Viagem para o pacote Estação Espacial
            data_partida=datetime.now() - timedelta(days=15),
            duracao_horas=96,  # 4 dias
            descricao="Missão de teste de equipamentos na órbita terrestre baixa",
            status=StatusViagem.CANCELADA,
            capacidade=3,  # Capacidade para 3 passageiros
            data_criacao=datetime.now() - timedelta(days=45),
            data_atualizacao=datetime.now() - timedelta(days=20)  # Atualizado quando cancelou
        )
        viagens.append(viagem_cancelada)
        
        for viagem in viagens:
            db.add(viagem)
        
        db.commit()
        
        # Associar reservas às viagens (viagem_reserva)
        # Para a primeira viagem agendada, associar as reservas pagas de Maria e John
        db.execute(viagem_reserva.insert().values(
            viagem_id=viagens[0].id,
            reserva_id=reservas[1].id,  # Reserva da Maria (pacote Estação Espacial)
            assento="A1",
            data_associacao=datetime.now() - timedelta(days=30)
        ))
        
        db.execute(viagem_reserva.insert().values(
            viagem_id=viagens[0].id,
            reserva_id=reservas[2].id,  # Reserva do John (pacote Estação Espacial)
            assento="A2",
            data_associacao=datetime.now() - timedelta(days=28)
        ))
        
        # Para a viagem em andamento, associar a reserva da Maria
        db.execute(viagem_reserva.insert().values(
            viagem_id=viagem_em_andamento.id,
            reserva_id=reservas[1].id,  # Reserva da Maria
            assento="B1",
            data_associacao=datetime.now() - timedelta(days=10)
        ))
        
        # Atualizando a reserva para EMBARCADO já que a viagem está em andamento
        reservas[1].status = StatusReserva.EMBARCADO
        db.add(reservas[1])
        
        # Para a viagem concluída, associar a reserva da Maria
        db.execute(viagem_reserva.insert().values(
            viagem_id=viagem_concluida.id,
            reserva_id=reservas[1].id,  # Usando a mesma reserva da Maria para demonstração
            assento="C1",
            data_associacao=datetime.now() - timedelta(days=100)
        ))
        
        db.commit()
        
        print("Banco de dados populado com sucesso!")
        
    except Exception as e:
        db.rollback()
        print(f"Erro ao popular o banco de dados: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()