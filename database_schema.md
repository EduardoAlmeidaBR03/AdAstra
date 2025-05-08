# Documentação do Banco de Dados AdAstra

## Visão Geral

AdAstra é um sistema de gerenciamento para viagens espaciais que inclui reservas de pacotes, aprovações médicas, certificações, pagamentos e gestão de clientes. Este documento apresenta a estrutura do banco de dados e as relações entre suas entidades.

## Estrutura de Tabelas

### 1. Cliente (`clientes`)

Armazena informações dos clientes que desejam realizar viagens espaciais.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | String | Identificador único (UUID) |
| nome | String(255) | Nome completo do cliente |
| email | String(255) | Email do cliente (único) |
| senha_hash | String(255) | Hash da senha do cliente |
| data_nascimento | Date | Data de nascimento |
| documento_identidade | String(100) | Documento de identidade |
| telefone | String(20) | Telefone de contato |
| pais | String(100) | País de residência |
| endereco | Text | Endereço completo |
| status_medico | Enum | Status da aprovação médica (Pendente/Aprovado/Reprovado) |
| certificacao_status | Enum | Status da certificação (Pendente/Concluída) |
| data_cadastro | Timestamp | Data de cadastro no sistema |
| ultima_atualizacao | Timestamp | Data da última atualização |

### 2. Pacote (`packages`)

Representa os pacotes de viagens espaciais disponíveis.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | String | Identificador único (UUID) |
| nome | String(255) | Nome do pacote |
| descricao | Text | Descrição detalhada do pacote |
| tipo | Enum | Tipo do pacote (Suborbital/Estação Espacial) |
| preco | Decimal(10,2) | Preço base do pacote |
| disponibilidade | Boolean | Indica se o pacote está disponível |

### 3. Reserva (`bookings`)

Representa as reservas de pacotes espaciais feitas pelos clientes.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | String | Identificador único (UUID) |
| cliente_id | String | ID do cliente (chave estrangeira) |
| package_id | String | ID do pacote (chave estrangeira) |
| data_reserva | Timestamp | Data em que a reserva foi feita |
| status | Enum | Status da reserva (Reservado/Cancelado/Pago/Embarcado/Concluído) |
| valor_original | Decimal(10,2) | Valor original do pacote |
| valor_imposto | Decimal(10,2) | Valor do imposto aplicado |
| valor_total | Decimal(10,2) | Valor total (pacote + imposto) |
| assento | String(20) | Assento designado na viagem (opcional) |

### 4. AprovacaoMedica (`medical_clearance`)

Armazena os resultados das avaliações médicas dos clientes.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | String | Identificador único (UUID) |
| cliente_id | String | ID do cliente (chave estrangeira) |
| aprovado | Boolean | Indica se o cliente foi aprovado medicamente |
| detalhes | Text | Detalhes sobre a avaliação médica |
| data_verificacao | Timestamp | Data da avaliação médica |

### 5. Certificacao (`certifications`)

Rastreia as certificações necessárias para clientes participarem de viagens espaciais.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | String | Identificador único (UUID) |
| cliente_id | String | ID do cliente (chave estrangeira) |
| descricao | Text | Descrição da certificação |
| concluida | Boolean | Indica se a certificação foi concluída |
| data_certificacao | Timestamp | Data da certificação |

### 6. Moeda (`currencies`)

Armazena informações sobre moedas e taxas de câmbio.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | String | Identificador único (UUID) |
| nome | String(100) | Nome da moeda |
| codigo | String(10) | Código da moeda (único) |
| taxa_cambio | Decimal(10,6) | Taxa de câmbio em relação à moeda padrão |

### 7. Pagamento (`payments`)

Registra os pagamentos realizados para as reservas.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | String | Identificador único (UUID) |
| booking_id | String | ID da reserva (chave estrangeira) |
| valor | Decimal(10,2) | Valor do pagamento |
| moeda_id | String | ID da moeda utilizada (chave estrangeira) |
| status | Enum | Status do pagamento (Pendente/Confirmado/Falhou) |
| data_pagamento | Timestamp | Data do pagamento |

### 8. Imposto (`taxes`)

Define os impostos aplicados às viagens espaciais com base no país de origem e destino.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | String | Identificador único (UUID) |
| pais_origem | String(100) | País de origem |
| pais_destino | String(100) | País de destino |
| percentual | Decimal(5,2) | Percentual do imposto aplicado |
| descricao | Text | Descrição do imposto |

### 9. Viagem (`trips`)

Representa as viagens espaciais realizadas para determinado pacote.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | String | Identificador único (UUID) |
| pacote_id | String | ID do pacote (chave estrangeira) |
| data_partida | DateTime | Data e hora de partida da viagem |
| duracao_horas | Integer | Duração da viagem em horas |
| descricao | Text | Descrição detalhada da viagem (opcional) |
| status | Enum | Status da viagem (Agendada/Em Andamento/Concluída/Cancelada) |
| capacidade | Integer | Número máximo de passageiros |
| data_criacao | Timestamp | Data de criação do registro |
| data_atualizacao | Timestamp | Data da última atualização |

### 10. Associação Viagem-Reserva (`trip_bookings`)

Tabela de associação que conecta viagens a reservas, permitindo múltiplos passageiros por viagem.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| viagem_id | String | ID da viagem (chave primária, chave estrangeira) |
| reserva_id | String | ID da reserva (chave primária, chave estrangeira) |
| assento | String(20) | Assento designado para o passageiro (opcional) |
| data_associacao | Timestamp | Data em que a reserva foi associada à viagem |

## Diagrama de Relacionamentos

```
+-------------+     1:N      +--------------+     N:1     +------------+
|   Cliente   |------------->|   Reserva    |<------------|   Pacote   |
+-------------+              +--------------+             +------------+
      |                             |  ^                        |
      |                             |  |                        |
      | 1:N                         | N:M                       | 1:N
      |                             |  |                        |
      v                             v  |                        v
+----------------+           +---------------+             +------------+
| AprovacaoMedica|           |    Viagem     |             |  Imposto   |
+----------------+           +---------------+             +------------+
      ^                             |
      |                             |
      | 1:N                         | N:1
      |                             |
+----------------+           +---------------+
|  Certificacao  |           |   Pagamento   |<------------ +------------+
+----------------+           +---------------+      N:1     |   Moeda    |
                                                            +------------+
```

## Relações entre as Tabelas

1. **Cliente**:
   - Um cliente pode ter múltiplas reservas (1:N)
   - Um cliente pode ter múltiplas certificações (1:N)
   - Um cliente pode ter múltiplas aprovações médicas (1:N)

2. **Pacote**:
   - Um pacote pode estar em múltiplas reservas (1:N)
   - Um pacote pode ter múltiplas viagens (1:N)

3. **Reserva**:
   - Uma reserva pertence a um único cliente (N:1)
   - Uma reserva está associada a um único pacote (N:1)
   - Uma reserva pode ter múltiplos pagamentos (1:N)
   - Uma reserva pode participar de múltiplas viagens (N:M)

4. **Viagem**:
   - Uma viagem está associada a um único pacote (N:1)
   - Uma viagem pode ter múltiplas reservas associadas (N:M)

5. **Moeda**:
   - Uma moeda pode ser usada em múltiplos pagamentos (1:N)

6. **Pagamento**:
   - Um pagamento está associado a uma única reserva (N:1)
   - Um pagamento usa uma única moeda (N:1)

## Fluxo do Sistema

```
+-------------------+     +----------------+     +------------------+
| Cliente se        |---->| Realiza exames |---->| Obtém aprovação  |
| cadastra          |     | médicos        |     | médica           |
+-------------------+     +----------------+     +------------------+
          |                                               |
          v                                               v
+-------------------+     +----------------+     +------------------+
| Completa          |---->| Seleciona um   |---->| Cria uma         |
| certificações     |     | pacote         |     | reserva          |
+-------------------+     +----------------+     +------------------+
                                                          |
                                                          v
                                               +------------------+
                                               | Realiza          |
                                               | pagamento        |
                                               +------------------+
                                                          |
                                                          v
                                               +------------------+
                                               | Reserva          |
                                               | confirmada (PAGO)|
                                               +------------------+
                                                          |
                                                          v
                                               +------------------+     +------------------+
                                               | Associação com   |---->| Embarque na      |
                                               | uma viagem       |     | viagem           |
                                               +------------------+     +------------------+
                                                                                |
                                                                                v
                                                                       +------------------+
                                                                       | Viagem concluída |
                                                                       +------------------+
```

## Enumerações do Sistema

### StatusMedico
- PENDENTE
- APROVADO
- REPROVADO

### CertificacaoStatus
- PENDENTE
- CONCLUIDA

### TipoPacote
- SUBORBITAL
- ESTACAO_ESPACIAL

### StatusReserva
- RESERVADO
- CANCELADO
- PAGO
- EMBARCADO
- CONCLUIDO

### StatusPagamento
- PENDENTE
- CONFIRMADO
- FALHOU

### StatusViagem
- AGENDADA
- EM_ANDAMENTO
- CONCLUIDA
- CANCELADA