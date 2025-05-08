# AdAstra - Sistema de Reservas Espaciais

## Sobre o Projeto

AdAstra é um sistema de reservas para viagens espaciais, desenvolvido com FastAPI e SQLAlchemy. A plataforma permite que os clientes se registrem, passem por verificação médica, obtenham certificações necessárias e reservem pacotes espaciais.

## Estrutura do Banco de Dados

### Tabelas e Relacionamentos

#### 1. Cliente (`clientes`)
- Armazena informações dos clientes
- **Campos principais**: id, nome, email, senha_hash, documento_identidade, país, status_médico, etc.
- **Relacionamentos**:
  - Um cliente pode ter várias reservas (`Reserva`)
  - Um cliente pode ter várias certificações (`Certificacao`)
  - Um cliente pode ter várias aprovações médicas (`AprovacaoMedica`)

#### 2. Pacote (`packages`)
- Contém informações sobre os pacotes de viagem espacial disponíveis
- **Campos principais**: id, nome, descrição, tipo (Suborbital/Estação Espacial), preço, disponibilidade
- **Relacionamentos**:
  - Um pacote pode ter várias reservas (`Reserva`)

#### 3. Reserva (`bookings`)
- Registra as reservas feitas pelos clientes
- **Campos principais**: id, cliente_id, package_id, data_reserva, status, valor_original, valor_imposto, valor_total
- **Relacionamentos**:
  - Cada reserva pertence a um cliente (`Cliente`)
  - Cada reserva está associada a um pacote (`Pacote`)
  - Uma reserva pode ter vários pagamentos (`Pagamento`)

#### 4. AprovacaoMedica (`medical_clearance`)
- Registra as verificações médicas dos clientes
- **Campos principais**: id, cliente_id, aprovado, detalhes, data_verificacao
- **Relacionamentos**:
  - Cada aprovação médica pertence a um cliente (`Cliente`)

#### 5. Certificacao (`certifications`)
- Registra as certificações obtidas pelos clientes
- **Campos principais**: id, cliente_id, descricao, concluida, data_certificacao
- **Relacionamentos**:
  - Cada certificação pertence a um cliente (`Cliente`)

#### 6. Moeda (`currencies`)
- Armazena as moedas disponíveis para pagamento
- **Campos principais**: id, nome, codigo, taxa_cambio
- **Relacionamentos**:
  - Uma moeda pode ser usada em vários pagamentos (`Pagamento`)

#### 7. Pagamento (`payments`)
- Registra os pagamentos das reservas
- **Campos principais**: id, booking_id, valor, moeda_id, status, data_pagamento
- **Relacionamentos**:
  - Cada pagamento está associado a uma reserva (`Reserva`)
  - Cada pagamento utiliza uma moeda (`Moeda`)

#### 8. Imposto (`taxes`)
- Define as taxas aplicadas de acordo com o país de origem
- **Campos principais**: id, pais_origem, pais_destino, percentual, descricao

### Diagrama de Relacionamento

```
Cliente 1:N Reserva N:1 Pacote
Cliente 1:N AprovacaoMedica
Cliente 1:N Certificacao
Reserva 1:N Pagamento N:1 Moeda
```

## Enums (Tipos Enumerados)

1. **StatusMedico**: Pendente, Aprovado, Reprovado
2. **CertificacaoStatus**: Pendente, Concluída
3. **TipoPacote**: Suborbital, Estação Espacial
4. **StatusReserva**: Reservado, Cancelado, Pago
5. **StatusPagamento**: Pendente, Confirmado, Falhou

## Funcionalidades da Aplicação

### 1. Gerenciamento de Clientes
- Cadastro de novos clientes
- Atualização de dados cadastrais
- Consulta de status médico e certificações

### 2. Aprovação Médica
- Registro e atualização de aprovações médicas
- Verificação de aptidão para viagens espaciais

### 3. Certificações
- Registro de treinamentos e certificações necessárias
- Atualização de status de conclusão

### 4. Pacotes de Viagem
- Catálogo de pacotes disponíveis
- Informações sobre tipos, preços e disponibilidade

### 5. Reservas
- Criação de reservas para pacotes
- Cálculo automático de impostos baseado no país de origem
- Atualização de status (reservado, cancelado, pago)

### 6. Pagamentos
- Processamento de pagamentos em diferentes moedas
- Conversão automática baseada na taxa de câmbio
- Acompanhamento do status de pagamento

## Rotas da API

A API está organizada nos seguintes endpoints:

- **/clientes** - Gerenciamento de clientes
- **/packages** - Gerenciamento de pacotes de viagem
- **/bookings** - Gerenciamento de reservas
- **/medical_clearance** - Gerenciamento de aprovações médicas
- **/certifications** - Gerenciamento de certificações
- **/currencies** - Gerenciamento de moedas
- **/payments** - Gerenciamento de pagamentos
- **/taxes** - Gerenciamento de impostos

## Como Executar a Aplicação

### Pré-requisitos

- Python 3.8+
- Pip (gerenciador de pacotes do Python)

### Passos para Execução

1. **Clone o repositório**
   ```bash
   git clone [URL_DO_REPOSITÓRIO]
   cd AdAstra
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure o ambiente**
   - Crie um arquivo `.env` se necessário, baseado no `.env.example` (caso exista)

4. **Execute o script para popular o banco de dados**
   ```bash
   python seed_database.py
   ```
   - Este script criará todas as tabelas necessárias e populará o banco com dados iniciais:
     - Clientes de exemplo
     - Pacotes de viagem
     - Moedas e taxas de câmbio
     - Impostos por país
     - Aprovações médicas e certificações
     - Reservas e pagamentos de exemplo

5. **Inicie a aplicação**
   ```bash
   uvicorn main:app --reload
   ```

6. **Acesse a documentação da API**
   - Abra o navegador e acesse: `http://localhost:8000/docs`
   - A documentação interativa Swagger estará disponível

## Exemplos de Uso

### Consultar Pacotes Disponíveis
```bash
curl -X GET "http://localhost:8000/packages" -H "accept: application/json"
```

### Criar um Novo Cliente
```bash
curl -X POST "http://localhost:8000/clientes" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Ana Silva",
    "email": "ana.silva@exemplo.com",
    "senha": "senha123",
    "data_nascimento": "1990-05-15",
    "documento_identidade": "AB123456",
    "telefone": "+55 11 98765-4321",
    "pais": "Brasil",
    "endereco": "Av. Paulista, 1000, São Paulo, SP"
  }'
```

### Fazer uma Reserva
```bash
curl -X POST "http://localhost:8000/bookings" \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_id": "ID_DO_CLIENTE",
    "package_id": "ID_DO_PACOTE"
  }'
```

## Contribuição

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adicionando nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request