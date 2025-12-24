# 💰 CashFlow API

<div align="center">

🌍 **Language / Idioma**

[🇺🇸 English](./README.md) | 🇧🇷 **Português**

</div>

---

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.123.7-009688.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.44-red.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-2.9.0-412991.svg)
![Tests](https://img.shields.io/badge/Tests-67%20Passing-success.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)

Uma API RESTful **pronta para produção** para gerenciamento de finanças pessoais com **insights alimentados por IA**, construída com tecnologias Python modernas e melhores práticas.

**Autor:** Thiago Memelli  
**Tipo de Projeto:** API Backend Full-Stack com Integração de IA  
**Cobertura de Testes:** 67 testes abrangentes em 5 suítes de testes

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Principais Recursos](#-principais-recursos)
- [Tecnologias](#-tecnologias)
- [Arquitetura](#-arquitetura)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [Documentação da API](#-documentação-da-api)
- [Testes](#-testes)
- [Capturas de Tela](#-capturas-de-tela)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Changelog](#-changelog)
- [Melhorias Futuras](#-melhorias-futuras)
- [Autor](#-autor)

---

## 🎯 Visão Geral

CashFlow API é um **sistema completo de gerenciamento financeiro** que permite aos usuários:

✅ Rastrear receitas e despesas com categorização detalhada  
✅ Gerar relatórios financeiros abrangentes e análises  
✅ **Fazer perguntas sobre finanças em linguagem natural para IA** (NOVO!)  
✅ Analisar padrões de gastos por categoria  
✅ Monitorar tendências financeiras mensais e semanais  
✅ Manter autenticação segura de usuários com tokens JWT  

### Por Que Este Projeto Se Destaca

Esta não é apenas uma API CRUD. Ela demonstra **engenharia pronta para produção**:

- 🏗️ **Arquitetura Limpa** - Separação em camadas (API → CRUD → Models → DB)
- 🔒 **Segurança em Primeiro Lugar** - Auth JWT, hash bcrypt, validação de entrada
- 🤖 **Integração com IA** - OpenAI GPT-4o-mini para insights financeiros
- 🧪 **Testes Abrangentes** - 67 testes com integração real de API
- 📚 **Documentação Profissional** - OpenAPI/Swagger, comentários inline
- 🛡️ **Integridade de Dados** - Soft deletes, chaves estrangeiras, type safety
- 📊 **Análises Avançadas** - 4 tipos de relatório com análise de tendências

---

## ✨ Principais Recursos

### 🔐 Autenticação & Segurança
- **Autenticação por Token JWT** - Sistema de auth stateless e escalável
- **Hash de Senha** - Criptografia Bcrypt (padrão da indústria)
- **Expiração de Token** - Timeout de sessão configurável (padrão: 4 horas)
- **Esquemas de Auth Duplos** - OAuth2 Password Flow + HTTP Bearer
- **Autorização de Usuário** - Controle de permissão por endpoint

### 👤 Gerenciamento de Perfil de Usuário
- **Campo Nome Completo** - Identificação obrigatória do usuário (1-150 caracteres)
- **Rastreamento de Status da Conta** - Flags `is_active`, `is_superuser`, `is_deleted`
- **Arquitetura Inteligente de Timestamps**:
  - `created_at` - Criação da conta (gerado automaticamente no registro)
  - `updated_at` - Alterações no perfil (atualização manual na camada CRUD)
  - `last_login_at` - Eventos de autenticação (atualização SQL direta para evitar efeitos colaterais do ORM)
- **API Self-Service** - Usuários atualizam seus próprios dados via endpoint `/me`

### 💰 Gerenciamento Financeiro
- **Tipos de Transação Duplos** - Rastreamento de Receitas e Despesas
- **Sistema de Categorias** - Organize transações com categorias personalizadas
- **Padrão Soft Delete** - Preservação de trilha de auditoria (transações marcadas como deletadas, não removidas)
- **Filtro por Período** - Consulte transações por períodos específicos
- **Estatísticas em Tempo Real** - Cálculo instantâneo de totais, saldo, contagem de transações

### 📈 Análises & Relatórios (4 Tipos de Relatório)

#### 1. **Relatório Resumo** (`GET /api/v1/reports/summary`)
Visão geral financeira com médias diárias:
- Total de receitas, despesas, saldo
- Contagem de transações
- Média diária de receita/despesa
- Valor médio por transação

#### 2. **Detalhamento por Categoria** (`GET /api/v1/reports/by-category`)
Análise de gastos por categoria:
- Valor total por categoria
- Distribuição percentual
- Contagem de transações por categoria
- Rastreamento de transações sem categoria

#### 3. **Histórico Mensal** (`GET /api/v1/reports/monthly`)
Dados históricos agrupados por mês:
- Agregação por ano/mês
- Comparação de receitas vs despesas
- Cálculo de saldo mensal
- Período de retrospectiva configurável

#### 4. **Análise de Tendências** (`GET /api/v1/reports/trends`)
Padrões financeiros ao longo do tempo:
- Agregação diária (últimos 30 dias)
- Agregação semanal (últimas 12 semanas)
- Agregação mensal (últimos 12 meses)
- Datas de início/fim do período incluídas

### 🤖 Assistente Financeiro com IA

**A joia da coroa desta API** - Um assistente inteligente que entende suas finanças.

#### O Que o Torna Especial?

✅ **Consultas em Linguagem Natural** - Nenhum conhecimento SQL necessário  
✅ **Análise com Contexto** - IA analisa SEUS dados reais de transações  
✅ **Histórico de Conversas** - Todas as conversas salvas com timestamps  
✅ **Limpeza de Markdown** - Utilitário personalizado remove 95% da formatação de IA  
✅ **Recuperação de Erros** - Tratamento elegante de falhas de API  

#### Implementação Técnica

```
┌─────────────┐
│Pergunta User│
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│ Camada de Serviço IA │
│ • Buscar dados user  │
│ • Construir contexto │
│ • Chamar API OpenAI  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Limpador de Markdown │
│ • Remover ** bold ** │
│ • Remover ### headers│
│ • Limpar ``` code ```│
│ • Converter - listas │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Salvar no Histórico  │
│ • Pergunta           │
│ • Resposta Limpa     │
│ • Consulta SQL       │
│ • Sucesso/Erro       │
└──────────────────────┘
```

#### Exemplos de Consultas

```
"Quanto eu gastei este mês?"
"Quais são minhas 3 principais categorias de despesa?"
"Mostre minhas receitas vs despesas"
"Analise meus gastos com alimentação"
"Qual é meu saldo atual?"
"Estou gastando demais com transporte?"
```

#### Limpador de Markdown (95% de Cobertura)

Nosso processador de texto personalizado garante que respostas da IA estejam prontas para o frontend:

| Regra | Entrada | Saída |
|-------|---------|-------|
| Negrito | `**texto**` | `texto` |
| Itálico | `*texto*` | `texto` |
| Cabeçalhos | `### Título` | `Título` |
| Listas | `- item` | `• item` |
| Código | `` `código` `` | `código` |
| Links | `[texto](url)` | `texto` |

**Localização:** `app/utils/markdown_cleaner.py`  
**Cobertura:** 16 regras regex, 95%+ remoção de markdown  
**Saída:** Texto puro adequado para qualquer frontend  

### 🛡️ Integridade & Qualidade de Dados

- **Validação Pydantic** - Verificação de tipos em runtime em todas as entradas
- **Enums para Constantes** - Tipos de transação, tipos de categoria
- **Restrições de Chave Estrangeira** - Integridade referencial garantida
- **Timestamps Automáticos** - Geração de timestamp do lado do servidor
- **Padrão Soft Delete** - Trilha de auditoria para compliance

---

## 🛠️ Tecnologias

### Stack Principal

| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| **Python** | 3.14+ | Linguagem de programação principal |
| **FastAPI** | 0.123.7 | Framework web assíncrono moderno |
| **SQLAlchemy** | 2.0.44 | ORM para operações de banco de dados |
| **Pydantic** | 2.12.5 | Validação de dados e configurações |
| **JWT (python-jose)** | 3.5.0 | Autenticação baseada em token |
| **Bcrypt (passlib)** | 1.7.4 | Hash de senhas |
| **Uvicorn** | 0.38.0 | Servidor ASGI |
| **SQLite** | 3 | Banco de dados leve (dev) |

### IA & Recursos Avançados

| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| **OpenAI API** | 2.9.0 | Assistente de chat com IA |
| **GPT-4o-mini** | Mais recente | Modelo LLM custo-efetivo |

### Testes & Qualidade

| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| **pytest** | 9.0.2 | Framework de testes |
| **pytest-cov** | 7.0.0 | Relatório de cobertura |
| **httpx** | 0.28.1 | Cliente HTTP para TestClient |

### Por Que Essas Tecnologias?

#### FastAPI
- ✅ Geração automática de documentação OpenAPI
- ✅ Alta performance (comparável ao Node.js)
- ✅ Suporte nativo a async/await
- ✅ Injeção de dependência built-in
- ✅ Type safety com Pydantic

#### SQLAlchemy 2.0
- ✅ Agnóstico de banco de dados (fácil migração para PostgreSQL)
- ✅ Suporte moderno a async
- ✅ Query builder poderoso
- ✅ Arquitetura amigável para migrações

#### Pydantic V2
- ✅ Validação de tipos em runtime
- ✅ Serialização JSON automática
- ✅ Gerenciamento de configurações
- ✅ 5-50x mais rápido que V1

#### Autenticação JWT
- ✅ Stateless (sem armazenamento de sessão do lado do servidor)
- ✅ Escalável para sistemas distribuídos
- ✅ Segurança padrão da indústria
- ✅ Compatibilidade cross-platform

---

## 🏗️ Arquitetura

### Padrão de Arquitetura Limpa

Este projeto segue princípios de **Arquitetura Limpa** com separação clara de responsabilidades:

```
app/
├── api/                    # 🌐 Camada API (Interface HTTP)
│   ├── deps.py             # Injeção de dependência
│   └── v1/
│       ├── api.py          # Agregação de routers
│       └── endpoints/      # Handlers de rotas
│           ├── auth.py           # Autenticação (login, register, me)
│           ├── categories.py     # CRUD de Categorias + soft delete
│           ├── transactions.py   # CRUD de Transações + estatísticas
│           ├── reports.py        # 4 tipos de relatório
│           └── ai_chat.py        # Assistente IA (NOVO!)
│
├── core/                   # ⚙️ Configuração Central
│   ├── config.py           # Configurações (Pydantic Settings)
│   └── security.py         # Utilitários JWT (criar/verificar tokens)
│
├── crud/                   # 💾 Camada de Acesso a Dados
│   ├── base.py             # Operações CRUD genéricas
│   ├── crud_user.py        # Operações de usuário
│   ├── crud_category.py    # Operações de categoria
│   └── crud_transaction.py # Operações de transação + estatísticas
│
├── db/                     # 🗄️ Camada de Banco de Dados
│   ├── base.py             # Registro de models
│   ├── session.py          # Factory de conexão DB
│   └── init_db.py          # Seed de categorias padrão
│
├── models/                 # 🧩 Camada de Domínio (Models ORM)
│   ├── user.py             # Model de usuário (auth)
│   ├── category.py         # Model de categoria (soft delete)
│   ├── transaction.py      # Model de transação (soft delete)
│   └── chat.py             # Model de histórico de chat (NOVO!)
│
├── schemas/                # 📋 Objetos de Transferência de Dados
│   ├── user.py             # DTOs de usuário (create, update, response)
│   ├── category.py         # DTOs de categoria
│   ├── transaction.py      # DTOs de transação
│   └── ai_chat.py          # DTOs de chat IA (NOVO!)
│
├── services/               # 🧠 Camada de Lógica de Negócio
│   └── ai_service.py       # Orquestração de IA (NOVO!)
│
└── utils/                  # 🛠️ Utilitários
    └── markdown_cleaner.py # Processamento de texto (NOVO!)
```

### Camadas da Arquitetura Explicadas

#### 1. **Camada API** (`app/api/`)
- **Responsabilidade:** Tratamento de requisição/resposta HTTP
- **Padrão:** Injeção de dependência para banco de dados e auth de usuário
- **Validação:** Schemas Pydantic garantem integridade de dados
- **Documentação:** OpenAPI auto-gerada a partir de type hints

#### 2. **Camada CRUD** (`app/crud/`)
- **Responsabilidade:** Abstração de operações de banco de dados
- **Padrão:** Padrão Repository com classe base
- **Benefícios:** Queries reutilizáveis, testável sem camada HTTP
- **Exemplo:** `crud_transaction.get_statistics()` usado por relatórios

#### 3. **Camada de Serviço** (`app/services/`)
- **Responsabilidade:** Lógica de negócio complexa
- **Padrão:** Objetos de serviço para orquestração
- **Exemplo:** Serviço IA busca dados → chama OpenAI → salva histórico

#### 4. **Camada de Model** (`app/models/`)
- **Responsabilidade:** Definição de schema do banco de dados
- **Padrão:** Models ORM SQLAlchemy
- **Recursos:** Relacionamentos, timestamps, soft deletes

#### 5. **Camada de Schema** (`app/schemas/`)
- **Responsabilidade:** Validação e serialização de dados
- **Padrão:** Models Pydantic
- **Benefícios:** Type safety, validação automática, serialização JSON

### Exemplo de Fluxo de Dados: Criando uma Transação

```
1. HTTP POST /api/v1/transactions
   ↓
2. Camada API (endpoints/transactions.py)
   - Valida token → obtém current_user
   - Valida corpo da requisição via Pydantic
   ↓
3. Camada CRUD (crud/crud_transaction.py)
   - Cria instância do model Transaction
   - Adiciona à sessão do banco de dados
   ↓
4. Banco de dados faz commit da transação
   ↓
5. Schema serializa a resposta
   ↓
6. API retorna JSON para o cliente
```

---

## 🚀 Instalação

### Pré-requisitos

- **Python 3.11+** (Testado em 3.14)
- **pip** (Gerenciador de pacotes Python)
- **SQLite** (Incluído com Python)
- **Chave API OpenAI** (Para recursos de IA - obtenha em [platform.openai.com](https://platform.openai.com/api-keys))

### Passo 1: Clonar o Repositório

```bash
git clone https://github.com/yourusername/cashflow-api.git
cd cashflow-api
```

### Passo 2: Criar Ambiente Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Passo 3: Instalar Dependências

```bash
# Dependências de produção
pip install -r requirements.txt

# Dependências de desenvolvimento (para testes)
pip install -r requirements-dev.txt
```

### Passo 4: Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar arquivo .env com suas configurações
```

**Configuração Obrigatória:**

```env
# Segurança (ALTERE ISSO!)
SECRET_KEY=sua-chave-super-secreta-min-32-chars

# OpenAI (Obrigatório para recursos de IA)
OPENAI_API_KEY=sk-sua-chave-api-openai-aqui
OPENAI_MODEL=gpt-4o-mini

# Expiração do token (opcional, padrão: 240 minutos = 4 horas)
ACCESS_TOKEN_EXPIRE_MINUTES=240
```

### Passo 5: Executar a Aplicação

```bash
uvicorn app.main:app --reload
```

A API estará disponível em:
- **Base da API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Passo 6: Verificar Instalação

Abra seu navegador e acesse http://localhost:8000/docs

Você deverá ver a **Swagger UI** com todos os endpoints documentados.

---

## 📖 Uso

### Guia de Início Rápido

#### 1. Registrar um Novo Usuário

**Endpoint:** `POST /api/v1/auth/register`

```json
{
  "email": "usuario@exemplo.com",
  "password": "senha_segura",
  "full_name": "João Silva"
}
```

**Resposta:**
```json
{
  "id": 1,
  "email": "usuario@exemplo.com",
  "full_name": "João Silva",
  "is_active": true,
  "created_at": "2025-12-24T10:00:00Z"
}
```

#### 2. Login

**Endpoint:** `POST /api/v1/auth/login`

```form-data
username: usuario@exemplo.com
password: senha_segura
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 3. Autenticar no Swagger

1. Clique no botão **"Authorize"** (ícone 🔒)
2. Cole seu token no campo de valor
3. Clique em **"Authorize"**
4. Todos os endpoints estão agora acessíveis!

#### 4. Criar Sua Primeira Categoria

**Endpoint:** `POST /api/v1/categories/`

```json
{
  "name": "Alimentação",
  "type": "expense"
}
```

#### 5. Criar Sua Primeira Transação

**Endpoint:** `POST /api/v1/transactions/`

```json
{
  "type": "expense",
  "amount": 50.00,
  "description": "Almoço no restaurante",
  "date_transaction": "2025-12-24",
  "category_id": 1
}
```

#### 6. Perguntar à IA Sobre Suas Finanças

**Endpoint:** `POST /api/v1/ai/chat`

```json
{
  "message": "Quanto gastei com alimentação?"
}
```

**Resposta:**
```json
{
  "reply": "Você gastou R$50,00 com alimentação. Isso inclui 1 transação de almoço em um restaurante.",
  "data": {
    "total_income": 0.00,
    "total_expense": 50.00,
    "balance": -50.00,
    "transaction_count": 1,
    "categories": [
      {"name": "Alimentação", "type": "expense", "total": 50.00}
    ]
  },
  "sql_query": "Múltiplas consultas de agregação executadas..."
}
```

---

## 📚 Documentação da API

### Visão Geral dos Endpoints

#### 🔐 Autenticação (`/api/v1/auth`)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/register` | Criar nova conta de usuário | ❌ |
| POST | `/login` | Login e obter token JWT | ❌ |
| GET | `/me` | Obter perfil do usuário atual | ✅ |
| PUT | `/me` | Atualizar perfil do usuário | ✅ |
| DELETE | `/me` | Soft delete da conta | ✅ |

#### 📂 Categorias (`/api/v1/categories`)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/` | Criar nova categoria | ✅ |
| GET | `/` | Listar todas as categorias | ✅ |
| GET | `/{id}` | Obter categoria por ID | ✅ |
| PUT | `/{id}` | Atualizar categoria | ✅ |
| DELETE | `/{id}` | Soft delete da categoria | ✅ |
| POST | `/{id}/restore` | Restaurar categoria deletada | ✅ |

#### 💰 Transações (`/api/v1/transactions`)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/` | Criar transação | ✅ |
| GET | `/` | Listar transações (paginado) | ✅ |
| GET | `/{id}` | Obter transação por ID | ✅ |
| PUT | `/{id}` | Atualizar transação | ✅ |
| DELETE | `/{id}` | Soft delete da transação | ✅ |
| POST | `/{id}/restore` | Restaurar transação deletada | ✅ |
| GET | `/statistics` | Obter estatísticas financeiras | ✅ |

#### 📊 Relatórios (`/api/v1/reports`)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/summary` | Resumo financeiro geral | ✅ |
| GET | `/by-category` | Detalhamento por categoria | ✅ |
| GET | `/monthly` | Dados históricos mensais | ✅ |
| GET | `/trends` | Análise de tendências (diário/semanal/mensal) | ✅ |

#### 🤖 Chat IA (`/api/v1/ai`)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/chat` | Perguntar à IA sobre finanças | ✅ |
| GET | `/history` | Obter histórico de conversas | ✅ |
| DELETE | `/history/{id}` | Deletar chat específico | ✅ |

### Autenticação

Todos os endpoints protegidos requerem um token JWT no header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Documentação Interativa

Visite http://localhost:8000/docs para **documentação interativa da API** com:
- ✅ Funcionalidade Try-it-out
- ✅ Exemplos de request/response
- ✅ Definições de schemas
- ✅ Testes de autenticação

---

## 🧪 Testes

### Visão Geral da Suíte de Testes

Este projeto inclui **cobertura de testes abrangente** com **67 testes passando** em **5 módulos de teste**:

| Módulo | Testes | Área de Foco | Integração |
|--------|--------|--------------|------------|
| `test_auth.py` | 12 | Registro de usuário, login, perfil | ✅ Banco de Dados |
| `test_categories.py` | 13 | Operações CRUD, soft delete | ✅ Banco de Dados |
| `test_transactions.py` | 18 | CRUD, estatísticas, filtragem | ✅ Banco de Dados |
| `test_reports.py` | 8 | 4 tipos de relatório, cálculos | ✅ Banco de Dados |
| `test_ai_chat.py` | 16 | **Integração IA (API REAL)** | ✅✅ OpenAI + DB |

**Total:** 67 testes passando
**Cobertura:** Testes de integração End-to-End
**Chamadas de API:** Integração real com API OpenAI (não mockada)

### Executando Testes

#### Executar Todos os Testes

```bash
pytest -v
```

#### Executar Suíte de Teste Específica

```bash
pytest tests/test_auth.py -v
pytest tests/test_transactions.py -v
pytest tests/test_ai_chat.py -v -s  # -s mostra print statements
```

#### Executar com Relatório de Cobertura

```bash
pytest --cov=app --cov-report=html
```

Abra `htmlcov/index.html` para visualizar relatório detalhado de cobertura.

### Destaques dos Testes

#### 1. **Testes de Integração IA Real** (`test_ai_chat.py`)

Diferente da maioria dos projetos que mockam OpenAI, testamos **integração real de API**:

```python
def test_chat_with_real_financial_data():
    """
    Caso de Teste: IA Analisa Dados Financeiros Reais do Usuário.
    
    ⚠️ CHAMADA DE API REAL - Consome ~200 tokens (~$0.002)
    """
    # Cria transações reais
    create_transaction(headers, "income", 5000, today)
    create_transaction(headers, "expense", 1500, today)
    
    # Chama API OpenAI real
    response = client.post("/api/v1/ai/chat", headers=headers, json={
        "message": "Qual é meu saldo atual?"
    })
    
    # Valida resposta da IA com dados reais
    assert float(response.json()["data"]["balance"]) == 3500.00
```

**Custo por execução completa de testes:** ~$0.02 USD (~2000 tokens)

#### 2. **Precisão Matemática** (`test_reports.py`)

Testes validam cálculos financeiros exatos:

```python
def test_summary_calculations():
    """Valida totais, saldo e médias diárias."""
    # Dia 1: +3000, Dia 2: -1000, Dia 3: -500
    # Esperado: receita=3000, despesa=1500, saldo=1500
    # Média diária receita: 3000/3 = 1000
    # Média diária despesa: 1500/3 = 500
```

#### 3. **Isolamento de Segurança** (Todas as suítes de teste)

Cada suíte de testes valida isolamento de dados do usuário:

```python
def test_user_isolation():
    """Usuário A não pode ver dados do Usuário B."""
    create_transaction(headers_a, "income", 99999, today)
    
    # Usuário B consulta seus dados
    response = client.get("/api/v1/transactions", headers=headers_b)
    
    # Deve ver 0 transações, não os dados do Usuário A
    assert len(response.json()["transactions"]) == 0
```

### Arquitetura de Testes

Testes seguem o padrão **Pirâmide de Testes**:

```
        /\
       /  \
      / E2E\     ← 16 testes IA (Integração OpenAI real)
     /______\
    /        \
   /Integration\  ← 53 testes de endpoint (Integração com BD)
  /____________\
       Base
```

**Benefícios:**
- ✅ Detectar bugs cedo (validação a nível unitário)
- ✅ Validar comportamento real (testes de integração)
- ✅ Garantir prontidão para produção (E2E com APIs reais)

---

## 📸 Capturas de Tela

O diretório `docs/screenshots/` contém **53 capturas de tela detalhadas** documentando:

### 1. Servidor & Documentação (3 capturas de tela)
- Confirmação do servidor rodando
- Visão geral da Swagger UI (partes 1-3)

### 2. Fluxo de Autenticação (14 capturas de tela)
- Request/response de registro de usuário
- Request/response de login
- Autorização no Swagger
- Recuperação de perfil (`GET /me`)
- Fluxo de atualização de perfil
- Deleção de conta (soft delete)
- Acesso negado após deleção (410 Gone)

### 3. Gerenciamento de Categorias (12 capturas de tela)
- Criar categoria de receita
- Criar categoria de despesa
- Obter categoria por ID
- Atualizar categoria
- Listar todas as categorias
- Deletar categoria (soft delete)
- Restaurar categoria deletada

### 4. Gerenciamento de Transações (12 capturas de tela)
- Criar transação de despesa
- Criar transação de receita
- Listar todas as transações
- Obter transação por ID
- Atualizar transação
- Deletar transação
- Estatísticas financeiras
- Restaurar transação deletada

### 5. Relatórios Financeiros (5 capturas de tela)
- Relatório de resumo financeiro
- Detalhamento de receitas por categoria
- Detalhamento de despesas por categoria
- Histórico financeiro mensal
- Tendências financeiras ao longo do tempo

### 6. Assistente de Chat IA (7 capturas de tela)
- Chat com IA (request/response)
- Obter histórico de conversas
- Deletar chat específico
- Histórico após deleção

**Para visualizar capturas de tela:**
```
open docs/screenshots/
```

---

## 📁 Estrutura do Projeto

```
cashflow-api/
│
├── app/                              # Código fonte da aplicação
│   ├── api/                          # Camada API
│   │   ├── deps.py                   # Dependências (DB, auth)
│   │   └── v1/
│   │       ├── api.py                # Agregação de routers
│   │       └── endpoints/            # Handlers de rotas
│   │           ├── auth.py           # Autenticação (login, register, me)
│   │           ├── categories.py     # CRUD de Categorias + soft delete
│   │           ├── transactions.py   # CRUD de Transações + estatísticas
│   │           ├── reports.py        # 4 tipos de relatório
│   │           └── ai_chat.py        # Assistente IA (NOVO!)
│   │
│   ├── core/                         # Configuração central
│   │   ├── config.py                 # Configurações (Pydantic)
│   │   └── security.py               # Utilitários JWT
│   │
│   ├── crud/                         # Camada de acesso a dados
│   │   ├── base.py                   # Classe base CRUD genérica
│   │   ├── crud_user.py              # Operações de banco de dados de usuário
│   │   ├── crud_category.py          # Operações de banco de dados de categoria
│   │   └── crud_transaction.py       # Operações de banco de dados de transação
│   │
│   ├── db/                           # Camada de banco de dados
│   │   ├── base.py                   # Registro de models
│   │   ├── session.py                # Conexão DB
│   │   └── init_db.py                # Utilitários de seeding
│   │
│   ├── models/                       # Models ORM
│   │   ├── user.py                   # Model de banco de dados de usuário
│   │   ├── category.py               # Model de banco de dados de categoria
│   │   ├── transaction.py            # Model de banco de dados de transação
│   │   └── chat.py                   # Model de histórico de chat IA
│   │
│   ├── schemas/                      # DTOs Pydantic
│   │   ├── user.py                   # Schemas de validação de usuário
│   │   ├── category.py               # Schemas de validação de categoria
│   │   ├── transaction.py            # Schemas de validação de transação
│   │   └── ai_chat.py                # Schemas de validação de chat IA
│   │
│   ├── services/                     # Lógica de negócio
│   │   └── ai_service.py             # Integração OpenAI
│   │
│   ├── utils/                        # Utilitários
│   │   └── markdown_cleaner.py       # Processamento de texto
│   │
│   └── main.py                       # Ponto de entrada da aplicação
│
├── tests/                            # Suítes de teste (67 testes)
│   ├── conftest.py                   # Configuração Pytest
│   ├── test_pyramid.png              # Diagrama visual de estratégia de testes
│   ├── test_auth.py                  # 12 testes
│   ├── test_categories.py            # 13 testes
│   ├── test_transactions.py          # 18 testes
│   ├── test_reports.py               # 8 testes
│   └── test_ai_chat.py               # 16 testes (OpenAI REAL)
│
├── docs/                             # Documentação
│   ├── screenshots/                  # 53 capturas de tela da API + resultados de testes
│   ├── CHANGELOG.md                  # Histórico de versões
│   ├── test_report.html              # Relatório interativo de cobertura de testes
│   ├── test_execution.log            # Logs brutos de execução de testes (Auditoria)
│   └── USER_PROFILE_FEATURE.md       # Documentação de feature
│
├── migrations/                       # Migrações de banco de dados
│   ├── 001_add_soft_delete_to_categories.py
│   └── 002_add_deleted_at_to_transactions.py
│
├── logs/                             # Logs da aplicação
│
├── .env.example                      # Template de ambiente
├── .gitignore                        # Regras de ignore do Git
├── requirements.txt                  # Dependências de produção
├── requirements-dev.txt              # Dependências de desenvolvimento
├── README.md                         # Este arquivo (EN)
└── README.pt-BR.md                   # README em Português
```

---

## 📝 Changelog

Veja [CHANGELOG.md](./docs/CHANGELOG.md) para histórico detalhado de versões.

### Versão Mais Recente: 1.0.0 (Dezembro 2025)

**Principais Funcionalidades:**
- ✅ CRUD completo para usuários, categorias, transações
- ✅ Autenticação JWT com esquemas duplos
- ✅ 4 tipos de relatórios abrangentes
- ✅ Assistente financeiro com IA (integração OpenAI)
- ✅ Utilitário de limpeza de Markdown (95% de cobertura)
- ✅ Padrão soft delete para preservação de dados
- ✅ 67 testes passando com integração real de API
- ✅ Documentação OpenAPI/Swagger
- ✅ 53 capturas de tela detalhadas

---

## 🚀 Melhorias Futuras & Roadmap

Esta seção demonstra consciência de **requisitos de nível de produção** e **considerações de escalabilidade**.

### 🧪 Testes & Garantia de Qualidade
- [x] **Testes Unitários** - 67 testes passando ✅
- [x] **Testes de Integração** - Chamadas de API reais ✅
- [ ] **Relatório de Cobertura de Código** - Meta: 90%+
- [ ] **Testes de Carga** com Locust/k6
- [ ] **Testes de Segurança** (validação OWASP Top 10)

Qualidade de código é garantida através de uma suíte de testes abrangente cobrindo Auth, CRUD, Relatórios e integração de IA.

**Prova Visual (Relatório HTML):**
![Resultados de Testes](./docs/screenshots/test-coverage-results.png)

**Logs de Auditoria:**
Para verificação técnica, logs de execução completos estão disponíveis:
- [📄 Ver Log de Execução Bruto](./docs/test_execution.log)
- [📊 Ver Relatório HTML Interativo](./docs/test_report.html)

> **Relatório Gerado:** 2025-12-24
> **Status:** 100% Passando (67/67 testes)
> **Engine:** pytest 9.0.2

### 🚀 DevOps & Infraestrutura
- [x] **Docker** support (Dockerfile adicionado)
- [ ] **Docker Compose** orquestração
- [ ] **Pipeline CI/CD** (GitHub Actions)
- [ ] **Migrações Alembic** (substituir sistema customizado)
- [ ] **Configuração Baseada em Ambiente** (dev/staging/prod)
- [ ] **Endpoints de Health Check** (`/health`, `/ready`)
- [ ] **Migração PostgreSQL** (banco de dados de produção)

### 📊 Observabilidade & Monitoramento
- [ ] **Logging Estruturado** (logs JSON com correlation IDs)
- [ ] **Application Performance Monitoring** (APM)
- [ ] **Métricas & Dashboards** (Prometheus/Grafana)
- [ ] **Rastreamento de Erros** (integração Sentry)
- [ ] **Logs de Auditoria** para compliance

### 🔒 Melhorias de Segurança
- [ ] **Controle de Acesso Baseado em Papéis (RBAC)** - Ativar lógica `is_superuser` para dashboard Admin
- [ ] **Rate Limiting** por usuário/IP (prevenir abuso)
- [ ] **Validação de Request** com schemas mais rigorosos
- [ ] **Configuração CORS** para produção
- [ ] **Gerenciamento de API Key** para auth de serviço
- [ ] **Gerenciamento de Secrets** (AWS Secrets Manager/Vault)
- [ ] **Autenticação de Dois Fatores** (2FA)

### ⚡ Performance & Escalabilidade
- [ ] **Connection Pooling de Banco de Dados** otimização
- [ ] **Cache Redis** para queries frequentes
- [ ] **Padronização de Paginação** em todos os endpoints
- [ ] **Otimização de Queries** com índices adequados
- [ ] **Tarefas em Background Assíncronas** (Celery/Dramatiq)

### 🤖 Melhorias do Serviço de IA
- [ ] **Lógica de Retry** para falhas da API OpenAI
- [ ] **Mecanismos de Fallback** quando IA indisponível
- [ ] **Monitoramento de Custo** para uso de OpenAI por usuário
- [ ] **Streaming de Resposta** para melhor UX
- [ ] **Cache de Contexto** para reduzir chamadas de API
- [ ] **Otimização de Prompt Engineering**

### 📚 Documentação
- [ ] **Diagramas de Arquitetura** (Modelo C4/Draw.io)
- [ ] **Documentação de Estratégia de Versionamento de API**
- [ ] **Documentação de Schema do Banco de Dados** (diagramas ERD)
- [ ] **Guia de Deploy** para produção
- [ ] **Diretrizes de Contribuição** para open source
- [ ] **Coleção Postman** para testes de API

### 🌐 Funcionalidades Adicionais
- [ ] **Suporte Multi-moeda** (USD, EUR, BRL, etc.)
- [ ] **Planejamento de Orçamento & Alertas**
- [ ] **Transações Recorrentes**
- [ ] **Exportação de Dados** (relatórios CSV/PDF)
- [ ] **Integração com App Mobile** (cliente REST)
- [ ] **Seeding de Categorias Padrão** na primeira execução
- [ ] **Notificações por Email** para alertas
- [ ] **Suporte a Webhook** para integrações

---

> **Nota para Recrutadores:** Este roadmap demonstra meu entendimento de sistemas prontos para produção e requisitos de nível enterprise. Embora este seja um projeto de portfólio, estou plenamente ciente do que é necessário para escalar e manter software em ambientes de produção.

---

## 👨‍💻 Autor

**Thiago Memelli**

🎓 **Background**: Analista de Sistemas & Desenvolvedor Experiente (12+ anos)
💼 **Foco**: Desenvolvimento Backend Python, Arquitetura de API, Ciência de Dados
💼 **Objetivo Atual**: Posições de Python Backend Developer / API Developer  
📍 **Localização**: Vitória, ES - Brasil (Aberto a Remoto)  
📧 **Email**: tmemelli@gmail.com  
🔗 **LinkedIn**: [linkedin.com/in/thiagomemelli](https://linkedin.com/in/thiagomemelli)  
🐙 **GitHub**: [github.com/tmemelli](https://github.com/tmemelli)  
🌐 **Portfolio**: [thiagomemelli.com.br](https://thiagomemelli.com.br)  
📱 **Telefone**: +55 27 98903-0474

### Sobre Este Projeto

Este é meu **primeiro projeto de API Python**, construído do zero para demonstrar:

✅ **Princípios de Clean Code** - Legível, manutenível, bem documentado  
✅ **Arquitetura de Software** - Separação em camadas, princípios SOLID  
✅ **Design de API RESTful** - Práticas padrão da indústria  
✅ **Melhores Práticas de Segurança** - Auth JWT, bcrypt, validação  
✅ **Design de Banco de Dados** - Normalização, chaves estrangeiras, soft deletes  
✅ **Stack Python Moderno** - FastAPI, SQLAlchemy 2.0, Pydantic V2  
✅ **Integração com IA** - OpenAI GPT-4o-mini com processamento de texto customizado  
✅ **Excelência em Testes** - 67 testes incluindo integração real de API  
✅ **Documentação Profissional** - README abrangente, OpenAPI  

### Por Que Eu Construí Isso

Para demonstrar minha capacidade de:
- 🎯 Entregar **código de qualidade de produção**
- 🧠 Integrar **tecnologias modernas de IA**
- 🔧 Construir **sistemas backend escaláveis**
- 📚 Escrever **documentação técnica clara**
- 🧪 Implementar **testes abrangentes**

**Estou ativamente buscando oportunidades** para contribuir com um time de desenvolvimento e crescer como engenheiro de software profissional.

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT.

```
MIT License

Copyright (c) 2025 Thiago Memelli

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Agradecimentos

- **FastAPI** - Pelo excelente framework web assíncrono
- **SQLAlchemy** - Pelas poderosas capacidades de ORM
- **Pydantic** - Pela elegante validação de dados
- **OpenAI** - Pela tecnologia de IA acessível
- **Comunidade Python** - Pela documentação extensa e suporte

---

## 📞 Contato & Suporte

Se você é um **recrutador** ou **hiring manager** interessado em minhas habilidades:

📧 **Email**: [tmemelli@gmail.com](mailto:tmemelli@gmail.com)  
💼 **LinkedIn**: [https://www.linkedin.com/in/thiagomemelli/](https://www.linkedin.com/in/thiagomemelli/)  
📱 **Telefone**: [+55 27 98903-0474](tel:+5527989030474)  
🌐 **Portfolio**: [https://thiagomemelli.com.br/](https://thiagomemelli.com.br/)

**Estou disponível para:**
- Posições de Backend Developer em tempo integral
- Projetos de Desenvolvimento de API
- Consultoria Python/FastAPI
- Entrevistas técnicas
- Oportunidades freelance

---

<div align="center">

### ⭐ Se você achou este projeto impressionante, por favor dê uma estrela!

**Feito com ❤️ e ☕ por Thiago Memelli**

*Primeiro Projeto de API Python - Dezembro 2025*

</div>
