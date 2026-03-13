# Teste Técnico — Desenvolvedor Backend Python

## Sobre a vaga

Você fará parte de uma equipe que desenvolve uma plataforma SaaS multi-tenant para o setor financeiro/crédito. O backend é construído com **Python, FastAPI, SQLAlchemy, PostgreSQL** e roda em **AWS Lambda** com processamento assíncrono via **SQS**.

Este teste simula um cenário real do dia a dia do projeto.

---

## O Desafio

Construir uma **API de gerenciamento de propostas de crédito** com as seguintes características:

1. **Multi-tenancy** — isolamento de dados por tenant
2. **Autenticação JWT**
3. **Integração com banco externo** (mock fornecido)
4. **Processamento assíncrono** via fila de mensagens
5. **Recebimento de webhooks**

---

## Contexto de negócio

Uma empresa de crédito utiliza a plataforma para gerenciar propostas de empréstimo. O fluxo é:

```
1. Operador cadastra um CLIENTE
2. Operador solicita uma SIMULAÇÃO de crédito para o cliente
3. A simulação é enviada para o BANCO (API externa) de forma assíncrona
4. O banco processa e retorna o resultado via WEBHOOK
5. Se aprovado, o operador pode INCLUIR a proposta no banco
6. O banco processa a inclusão e retorna o status via WEBHOOK
7. O operador pode CONSULTAR o status atualizado da proposta
```

---

## Requisitos Técnicos

### 1. Estrutura do Projeto

Cada módulo da API deve seguir esta organização:

```
{modulo}/
├── endpoints.py    # Rotas FastAPI
├── service.py      # Lógica de negócio
├── repository.py   # Acesso a dados
└── dto.py          # Schemas Pydantic (entrada/saída)
```

### 2. Banco de Dados (PostgreSQL + SQLAlchemy + Alembic)

Modele **no mínimo** as seguintes tabelas:

#### tenants
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | PK |
| name | VARCHAR | Nome da empresa |
| document | VARCHAR | CNPJ |
| is_active | BOOLEAN | Ativo/inativo |
| created_at | TIMESTAMP | Data de criação |

#### users
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | PK |
| tenant_id | UUID | FK → tenants |
| name | VARCHAR | Nome completo |
| email | VARCHAR | Único por tenant |
| password_hash | VARCHAR | Senha hasheada |
| role | VARCHAR | admin / operator |
| is_active | BOOLEAN | Ativo/inativo |
| created_at | TIMESTAMP | Data de criação |

#### clients
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | PK |
| tenant_id | UUID | FK → tenants |
| name | VARCHAR | Nome completo |
| cpf | VARCHAR(11) | CPF (único por tenant) |
| birth_date | DATE | Data de nascimento |
| phone | VARCHAR | Telefone |
| created_at | TIMESTAMP | Data de criação |
| created_by | UUID | FK → users |

#### proposals
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | PK |
| tenant_id | UUID | FK → tenants |
| client_id | UUID | FK → clients |
| external_protocol | VARCHAR | Protocolo retornado pelo banco |
| type | VARCHAR | simulacao / proposta |
| amount | DECIMAL | Valor solicitado |
| installments | INTEGER | Número de parcelas |
| interest_rate | DECIMAL | Taxa de juros (retornada pelo banco) |
| installment_value | DECIMAL | Valor da parcela (retornado pelo banco) |
| status | VARCHAR | Ver tabela abaixo |
| bank_response | JSONB | Resposta completa do banco |
| created_at | TIMESTAMP | Data de criação |
| updated_at | TIMESTAMP | Última atualização |
| created_by | UUID | FK → users |

**Status possíveis da proposta:**
| Status | Descrição |
|--------|-----------|
| pending | Aguardando envio |
| processing | Enviada ao banco, aguardando resposta |
| simulated | Simulação concluída com sucesso |
| simulation_failed | Simulação falhou |
| submitted | Proposta incluída no banco |
| approved | Proposta aprovada |
| rejected | Proposta rejeitada |
| cancelled | Proposta cancelada |

**Todas as queries devem filtrar por `tenant_id`.** Um tenant nunca deve ver dados de outro.

### 3. Autenticação e Autorização

- Endpoint de **login** que recebe email + senha e retorna um JWT
- Middleware/dependency que valida o JWT e extrai `user_id` e `tenant_id`
- Todas as rotas protegidas devem receber o contexto do usuário autenticado
- Header `Authorization: Bearer {token}`

> Não é necessário implementar cadastro de usuário via API. Crie um **seed** (script ou migration) com ao menos 2 tenants e 2 usuários (um por tenant).

### 4. Endpoints da API

#### Clientes

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/clients` | Cadastrar cliente |
| GET | `/api/clients` | Listar clientes (com paginação) |
| GET | `/api/clients/{id}` | Buscar cliente por ID |
| PUT | `/api/clients/{id}` | Atualizar cliente |

#### Propostas

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/proposals/simulate` | Solicitar simulação de crédito |
| POST | `/api/proposals/{id}/submit` | Incluir proposta no banco |
| GET | `/api/proposals` | Listar propostas (com filtros e paginação) |
| GET | `/api/proposals/{id}` | Buscar proposta por ID |

#### Webhooks

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/webhooks/bank-callback` | Receber callback do banco |

### 5. Integração com o Banco Mock

Um **Mock Bank Server** é fornecido junto com este teste (ver seção "Infraestrutura"). Ele simula uma API bancária com os seguintes endpoints:

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/simular` | Envia simulação de crédito |
| POST | `/api/incluir` | Inclui proposta aprovada |
| GET | `/api/consultar/{protocolo}` | Consulta status de proposta |
| POST | `/api/cancelar/{protocolo}` | Cancela uma proposta |

**Detalhes do Mock Bank:**
- Processa requisições com delay simulado (2-5 segundos)
- Após processar, envia o resultado via **webhook** para sua API (POST no endpoint que você configurar)
- Pode retornar erros aleatórios (~10% das vezes) para testar resiliência
- A URL do webhook da sua API é configurada via variável de ambiente `WEBHOOK_CALLBACK_URL` no mock

#### Fluxo de simulação:
```
Sua API                          Mock Bank
   │                                │
   ├── POST /api/simular ──────────►│
   │   {cpf, amount, installments}  │
   │◄── 202 {protocol} ────────────┤
   │                                │ (processa em 2-5s)
   │◄── POST /webhooks/callback ────┤
   │   {protocol, status, rates}    │
   │                                │
```

#### Fluxo de inclusão:
```
Sua API                          Mock Bank
   │                                │
   ├── POST /api/incluir ──────────►│
   │   {protocol, client_data}      │
   │◄── 202 {protocol} ────────────┤
   │                                │ (processa em 2-5s)
   │◄── POST /webhooks/callback ────┤
   │   {protocol, status, details}  │
   │                                │
```

### 6. Processamento Assíncrono

A comunicação com o banco mock **não deve ser feita diretamente no endpoint**. Implemente um fluxo assíncrono:

```
Endpoint da API
    │
    ├── Valida dados
    ├── Cria proposta com status "pending"
    ├── Enfileira job na fila (SQS via LocalStack)
    └── Retorna 202 Accepted

Worker (consumidor da fila)
    │
    ├── Recebe mensagem da fila
    ├── Atualiza status para "processing"
    ├── Chama API do banco mock
    └── Em caso de erro, faz retry (a fila reenvia)
```

Utilize **SQS** via LocalStack (já configurado no docker-compose fornecido).

### 7. Recebimento de Webhook

O endpoint `POST /api/webhooks/bank-callback` recebe o callback do banco mock com o resultado:

```json
{
  "protocol": "MOCK-ABC123",
  "event": "simulation_completed",
  "status": "approved",
  "data": {
    "interest_rate": 1.99,
    "installment_value": 245.50,
    "total_amount": 5891.99,
    "approved_amount": 5000.00
  }
}
```

Ao receber:
1. Localizar a proposta pelo `external_protocol`
2. Atualizar o status e os dados retornados
3. Salvar a resposta completa no campo `bank_response`

---

## Infraestrutura Fornecida

Um `docker-compose.yml` é fornecido com:

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| `postgres` | 5432 | Banco de dados PostgreSQL 16 |
| `localstack` | 4566 | Simula AWS SQS localmente |
| `mock-bank` | 8001 | Mock Bank Server (API do banco simulado) |

Para subir:
```bash
docker-compose up -d
```

Sua API deve rodar na porta **8000**.

---

## O que esperamos na entrega

### Obrigatório
- [ ] Código fonte em repositório Git (GitHub, GitLab ou Bitbucket)
- [ ] `README.md` com instruções claras para rodar o projeto
- [ ] Migrations com Alembic funcionando
- [ ] Seed com dados iniciais (tenants + usuários)
- [ ] Todos os endpoints funcionando
- [ ] Fluxo assíncrono via fila (SQS/LocalStack)
- [ ] Webhook recebendo e processando callbacks
- [ ] Multi-tenancy funcionando (tenant A não vê dados do tenant B)
- [ ] Autenticação JWT
- [ ] Testes unitários (mínimo 5 testes cobrindo service/repository)

### Diferenciais (não obrigatórios)
- [ ] Testes de integração
- [ ] Dockerfile para a API do candidato
- [ ] Logs estruturados
- [ ] Documentação Swagger/OpenAPI customizada
- [ ] Tratamento de idempotência no webhook
- [ ] Rate limiting
- [ ] Validação de CPF

---

## Critérios de Avaliação

| Critério | Peso | O que avaliamos |
|----------|------|-----------------|
| **Arquitetura e organização** | 25% | Separação de responsabilidades, estrutura de pastas, modularidade |
| **Qualidade do código** | 25% | Legibilidade, naming, tipagem, tratamento de erros, boas práticas Python |
| **Multi-tenancy** | 15% | Isolamento correto, sem vazamento de dados entre tenants |
| **Fluxo assíncrono** | 15% | Integração com fila, worker funcionando, tratamento de falhas |
| **Banco de dados** | 10% | Modelagem, migrations, queries eficientes |
| **Testes** | 10% | Cobertura, qualidade dos testes, cenários relevantes |

---

## Regras

- Prazo: **4 dias corridos** a partir do recebimento
- Linguagem: **Python 3.11+**
- Framework: **FastAPI** (obrigatório)
- ORM: **SQLAlchemy 2.0+** (obrigatório)
- Migrations: **Alembic** (obrigatório)
- Você pode usar qualquer biblioteca adicional que julgar necessária
- O projeto deve rodar com `docker-compose up` + comando para iniciar sua API
- Em caso de dúvidas, documente suas decisões e premissas no README

---

## Como começar

```bash
# 1. Clone este repositório
git clone <url-do-repositorio>

# 2. Suba a infraestrutura
docker-compose up -d

# 3. Verifique se o mock bank está rodando
curl http://localhost:8001/health

# 4. Crie seu projeto na pasta raiz ou em uma pasta separada
# 5. Configure a conexão com PostgreSQL:
#    postgresql://postgres:postgres@localhost:5432/teste_tecnico

# 6. Desenvolva sua solução!
```

Boa sorte!
