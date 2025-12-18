# 💰 CashFlow API

<div align="center">

🌍 **Language / Idioma**

[🇺🇸 English](./README.md) | 🇧🇷 **Português**

</div>

---

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.123.7-009688.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.44-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)

Uma API RESTful profissional para gerenciamento financeiro pessoal, construída com tecnologias Python modernas e melhores práticas.

**Autor:** Thiago Memelli  
**Primeiro Projeto de API Python** - Demonstrando arquitetura limpa, práticas de segurança e testes abrangentes.

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Tecnologias](#️-tecnologias)
- [Arquitetura](#️-arquitetura)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [Documentação da API](#-documentação-da-api)
- [Screenshots](#-screenshots)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Changelog](#-changelog)
- [Melhorias Futuras](#-melhorias-futuras)
- [Autor](#-autor)

---

## 🎯 Visão Geral

CashFlow API é um sistema completo de gerenciamento financeiro que permite aos usuários:
- Rastrear receitas e despesas com categorização detalhada
- Gerar relatórios financeiros abrangentes e estatísticas
- Analisar padrões de gastos por categoria
- Monitorar tendências financeiras mensais
- Manter autenticação segura de usuários com tokens JWT

Este projeto demonstra **código pronto para produção** com:
- ✅ Arquitetura Limpa (separação de responsabilidades)
- ✅ Princípios de design de API RESTful
- ✅ Validação abrangente de entrada
- ✅ Autenticação e autorização baseada em JWT
- ✅ Padrão de exclusão suave (preservação de dados)
- ✅ Documentação detalhada da API (OpenAPI/Swagger)
- ✅ Segurança de tipo com schemas Pydantic

---

## ✨ Funcionalidades

### 🔐 Autenticação e Segurança
- **Autenticação por Token JWT** - Acesso seguro a endpoints protegidos
- **Hash de Senha** - Criptografia Bcrypt para senhas de usuário
- **Expiração de Token** - Timeout de sessão configurável
- **Autorização de Usuário** - Controle de permissão em nível de endpoint

### 👤 Gerenciamento de Perfil de Usuário
- **Campo de Nome Completo** - Identificação de usuário obrigatória (1-150 caracteres)
- **Rastreamento de Status da Conta** - Flags is_active, is_superuser, is_deleted
- **Separação Inteligente de Timestamps** - Abordagem padrão da indústria para trilhas de auditoria:
  - `created_at` - Timestamp de criação da conta (gerado automaticamente no registro)
  - `updated_at` - Timestamp de modificação do perfil (atualizado apenas quando dados do usuário mudam)
  - `last_login_at` - Rastreamento de autenticação (atualizado apenas em login bem-sucedido)
- **Implementação de Timestamp** - Usa atualizações SQL diretas para prevenir efeitos colaterais indesejados:
  - Login atualiza `last_login_at` via `db.execute()` sem acionar `updated_at`
  - Atualizações de perfil modificam `updated_at` manualmente na camada CRUD
  - Demonstra compreensão do comportamento do ORM e melhores práticas de produção
- **Endpoint de Perfil Self-Service** - Usuários atualizam seus próprios dados via `/me` (identificação baseada em token)

### 📊 Gerenciamento Financeiro
- **Tipos de Transação Duplos** - Rastreamento de Receitas e Despesas
- **Sistema de Categorias** - Organize transações por categorias personalizadas ou padrão
- **Exclusão Suave** - Transações são marcadas como excluídas, não removidas permanentemente (trilha de auditoria)
- **Filtragem por Intervalo de Datas** - Consulte transações por períodos específicos

### 📈 Análises e Relatórios
- **Estatísticas Financeiras** - Cálculo em tempo real de totais, saldo e contagem de transações
- **Relatórios Resumidos** - Médias diárias para receitas, despesas e transações
- **Detalhamento por Categoria** - Análise de gastos/receitas por categoria com porcentagens
- **Tendências Mensais** - Dados financeiros históricos agrupados por mês
- **Análise de Tendências** - Opções de agregação diária, semanal ou mensal

### 🛡️ Integridade de Dados
- **Camada de Validação** - Schemas Pydantic garantem correção de dados
- **Segurança de Tipo** - Enums para tipos de transação e categoria
- **Restrições de Chave Estrangeira** - Integridade referencial no banco de dados
- **Timestamps Automáticos** - Rastreie tempos de criação e atualização

### 🤖 Assistente Financeiro Alimentado por IA (NOVO!)

A CashFlow API agora inclui um assistente de IA inteligente alimentado pelo GPT-4o-mini da OpenAI que entende seus dados financeiros e responde perguntas em linguagem natural.

**Recursos Principais:**
- **Consultas em Linguagem Natural** - Faça perguntas sobre suas finanças em português ou inglês simples
- **Análise Sensível ao Contexto** - A IA analisa seus dados de transação reais para fornecer respostas precisas
- **Histórico de Conversas** - Todos os chats são salvos com timestamps para referência futura
- **Recuperação Inteligente de Dados** - Busca automaticamente dados financeiros relevantes (categorias, transações, totais)
- **Limpeza de Markdown** - Limpador personalizado remove 95% da formatação de IA para saída de texto limpa

**Limpador de Markdown (95% de Cobertura):**
Nosso utilitário de processamento de texto personalizado garante que as respostas da IA sejam limpas e prontas para frontend:
- ✅ Remove `**negrito**`, `*itálico*`, `~~tachado~~`
- ✅ Remove `# cabeçalhos` e `> citações`
- ✅ Converte `- listas` em `• marcadores`
- ✅ Remove ` ```blocos de código``` ` e `` `código inline` ``
- ✅ Limpa `[links](url)` para texto simples
- ✅ Preserva quebras de linha (`\n\n`) para legibilidade
- ✅ Remove tags HTML e espaços em branco excessivos
- ✅ Saída é texto simples pronto para qualquer frontend

**Exemplos de Consultas:**
```
"Quanto gastei este mês?"
"Quais são minhas 3 principais categorias de despesas?"
"Mostre-me minha receita vs despesas"
"Analise meus gastos com comida"
"Qual é meu saldo atual?"
```

**Como Funciona:**
```
Pergunta do Usuário → Serviço de IA → API OpenAI
                         ↓
           Buscar Dados Financeiros do Usuário
                         ↓
           Gerar Resposta Contextual
                         ↓
           Aplicar Limpador de Markdown (95%)
                         ↓
           Salvar no Histórico de Chat
                         ↓
           Retornar Texto Limpo ao Usuário
```

**Implementação Técnica:**
- **Camada de Serviço**: `app/services/ai_service.py` - Orquestra interações de IA
- **Processamento de Texto**: `app/utils/markdown_cleaner.py` - 17 regras de limpeza
- **Modelo de Dados**: `app/models/chat.py` - Armazenamento de histórico de conversas
- **Endpoints**: 3 novas rotas em `app/api/v1/endpoints/ai_chat.py`

---

## 🛠️ Tecnologias

| Tecnologia | Versão | Propósito |
|------------|---------|-----------|
| **Python** | 3.11+ | Linguagem de programação principal |
| **FastAPI** | 0.123.7 | Framework web async moderno |
| **SQLAlchemy** | 2.0.44 | ORM para operações de banco de dados |
| **Pydantic** | 2.12.5 | Validação de dados e configurações |
| **JWT (python-jose)** | 3.5.0 | Autenticação baseada em token |
| **Bcrypt** | 4.0.1 | Hash de senha |
| **Uvicorn** | 0.38.0 | Servidor ASGI |
| **SQLite** | 3 | Banco de dados leve (desenvolvimento) |
| **OpenAI API** | 2.9.0 | Assistente de chat alimentado por IA |

### Por Que Essas Tecnologias?

- **FastAPI**: Documentação automática de API, alto desempenho, suporte async
- **SQLAlchemy**: ORM agnóstico de banco de dados, suporta migração PostgreSQL
- **Pydantic**: Verificação de tipo em tempo de execução, validação automática
- **JWT**: Autenticação stateless, escalável para sistemas distribuídos

---

## 🏗️ Arquitetura

### Padrão de Arquitetura Limpa

```
app/
├── api/                    # Camada de API (Controllers)
│   ├── deps.py             # Injeção de dependência
│   └── v1/
│       ├── api.py          # Agregação de rotas
│       └── endpoints/      # Manipuladores de rotas
├── core/                   # Configuração Principal
│   ├── config.py           # Gerenciamento de configurações
│   └── security.py         # Utilitários de autenticação
├── crud/                   # Camada de Acesso a Dados
│   ├── base.py             # Operações CRUD genéricas
│   └── crud_*.py           # Operações específicas do modelo
├── db/                     # Camada de Banco de Dados
│   ├── base.py             # Registro de modelos
│   └── session.py          # Conexão com BD
├── models/                 # Camada de Domínio (Modelos ORM)
│   ├── user.py
│   ├── category.py
│   ├── transaction.py
│   └── chat.py
├── services/               # Camada de Lógica de Negócios
│   ├── __init__.py
│   └── ai_service.py       # Integração e orquestração OpenAI
├── utils/                  # Funções Utilitárias
│   ├── __init__.py
│   └── markdown_cleaner.py # Limpeza de texto (95% cobertura)
└── schemas/                # Camada de Apresentação (DTOs)
    ├── user.py
    ├── category.py
    ├── transaction.py
    └── ai_chat.py
```

### Padrões de Design Utilizados

1. **Padrão Repository** - Camada CRUD abstrai operações de banco de dados
2. **Injeção de Dependência** - `Depends()` do FastAPI para dependências limpas
3. **Padrão DTO** - Schemas Pydantic separam contratos de API dos modelos
4. **Padrão de Exclusão Suave** - Flag `is_deleted` preserva trilha de auditoria
5. **Classe Base Genérica** - `CRUDBase` com TypeVars para reutilização de código

---

## 📦 Instalação

### Pré-requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- Ambiente virtual (recomendado)

### Configuração Passo a Passo

1. **Clone o repositório**
```bash
git clone https://github.com/tmemelli/cashflow-api.git
cd cashflow-api
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
```

3. **Ative o ambiente virtual**

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

4. **Instale as dependências**
```bash
pip install -r requirements.txt
```

5. **Configure as variáveis de ambiente**

Crie um arquivo `.env` no diretório raiz:
```env
# Configurações da Aplicação
PROJECT_NAME=CashFlow API
VERSION=1.0.0
API_V1_STR=/api/v1

# Configurações de Segurança
SECRET_KEY=sua-chave-secreta-aqui-mude-em-producao
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configurações de Banco de Dados
DATABASE_URL=sqlite:///./cashflow.db

# Configurações OpenAI (para Recurso de Chat IA)
OPENAI_API_KEY=sua-chave-api-openai-aqui-obtenha-em-platform.openai.com
OPENAI_MODEL=gpt-4o-mini
```

6. **Execute o servidor**
```bash
uvicorn app.main:app --reload
```

7. **Acesse a documentação**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 🚀 Uso

### Fluxo de Autenticação

1. **Registrar um novo usuário**
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "usuario@exemplo.com",
  "password": "senhaSegura123",
  "full_name": "Nome do Usuário"
}
```

2. **Fazer login e obter token JWT**
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=usuario@exemplo.com&password=senhaSegura123
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

3. **Usar token em requisições protegidas**
```http
GET /api/v1/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Gerenciar Categorias

**Criar categoria:**
```http
POST /api/v1/categories/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Alimentação",
  "type": "expense",
  "description": "Despesas relacionadas a alimentação"
}
```

### Criar Transações

**Adicionar despesa:**
```http
POST /api/v1/transactions/
Authorization: Bearer <token>
Content-Type: application/json

{
  "amount": 50.00,
  "description": "Almoço",
  "category_id": 1,
  "transaction_type": "expense",
  "date": "2025-12-18"
}
```

### Gerar Relatórios

**Obter estatísticas financeiras:**
```http
GET /api/v1/reports/statistics?start_date=2025-12-01&end_date=2025-12-31
Authorization: Bearer <token>
```

### Chat com IA (NOVO!)

**Fazer pergunta à IA:**
```http
POST /api/v1/ai/chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Quanto gastei com comida este mês?"
}
```

**Resposta:**
```json
{
  "reply": "Você gastou R$ 330,50 com comida este mês. Seu maior gasto foi R$ 150,50 no supermercado.",
  "data": {...},
  "sql_query": "..."
}
```

**Obter histórico de chat:**
```http
GET /api/v1/ai/history?limit=10
Authorization: Bearer <token>
```

**Deletar conversa específica:**
```http
DELETE /api/v1/ai/history/{chat_id}
Authorization: Bearer <token>
```

---

## 📚 Documentação da API

### 📚 Endpoints da API

#### 🔐 Autenticação (5 endpoints)
- `POST /api/v1/auth/register` - Criar nova conta de usuário
- `POST /api/v1/auth/login` - Autenticar e obter token JWT
- `POST /api/v1/auth/refresh` - Atualizar token expirado
- `GET /api/v1/auth/me` - Obter perfil do usuário atual
- `PUT /api/v1/auth/me` - Atualizar perfil do usuário

#### 📂 Categorias (5 endpoints)
- `POST /api/v1/categories` - Criar nova categoria
- `GET /api/v1/categories` - Listar todas as categorias (com paginação)
- `GET /api/v1/categories/{id}` - Obter categoria específica
- `PUT /api/v1/categories/{id}` - Atualizar categoria
- `DELETE /api/v1/categories/{id}` - Exclusão suave de categoria

#### 💸 Transações (6 endpoints)
- `POST /api/v1/transactions` - Criar nova transação (receita/despesa)
- `GET /api/v1/transactions` - Listar todas as transações (filtrável por data/categoria/tipo)
- `GET /api/v1/transactions/{id}` - Obter transação específica
- `PUT /api/v1/transactions/{id}` - Atualizar transação
- `DELETE /api/v1/transactions/{id}` - Exclusão suave de transação
- `GET /api/v1/transactions/summary` - Estatísticas rápidas

#### 📊 Relatórios (4 endpoints)
- `GET /api/v1/reports/statistics` - Estatísticas financeiras gerais
- `GET /api/v1/reports/by-category` - Detalhamento por categoria
- `GET /api/v1/reports/trends` - Tendências mensais/semanais
- `GET /api/v1/reports/summary` - Médias diárias

#### 🤖 Chat IA (3 endpoints - NOVO!)
- `POST /api/v1/ai/chat` - Perguntar à IA sobre suas finanças
- `GET /api/v1/ai/history` - Recuperar histórico de conversas (limite: 10-50)
- `DELETE /api/v1/ai/history/{id}` - Deletar conversa específica

**Total: 23 endpoints**

---

### Documentação Interativa

A API inclui documentação interativa completa acessível através de:

- **Swagger UI** (`/docs`): Interface interativa para testar endpoints
- **ReDoc** (`/redoc`): Documentação alternativa focada em legibilidade

**Recursos:**
- Testar todos os endpoints diretamente do navegador
- Exemplos de requisição/resposta
- Schemas de dados detalhados
- Documentação de autenticação
- Descrições de códigos de erro

---

## 📸 Screenshots

A pasta `docs/screenshots/` contém 26+ screenshots mostrando:

1-10: Operações CRUD de categorias
11-16: Gerenciamento de transações e relatórios
17-26: Recursos de gerenciamento de perfil de usuário
27+: Recursos de chat IA e limpeza de Markdown

Para ver todas as screenshots: [docs/screenshots/](./docs/screenshots/)

---

## 📁 Estrutura do Projeto

```
cashflow-api/
├── app/
│   ├── __init__.py
│   ├── main.py                      # Aplicação FastAPI
│   ├── api/
│   │   ├── deps.py                  # Injeção de dependência
│   │   └── v1/
│   │       ├── api.py               # Agregador de rotas
│   │       └── endpoints/
│   │           ├── auth.py          # Endpoints de autenticação
│   │           ├── categories.py    # Endpoints de categorias
│   │           ├── transactions.py  # Endpoints de transações
│   │           ├── reports.py       # Endpoints de relatórios
│   │           └── ai_chat.py       # Endpoints de chat IA (NOVO)
│   ├── core/
│   │   ├── config.py                # Configurações
│   │   └── security.py              # Utilitários JWT/Auth
│   ├── crud/
│   │   ├── base.py                  # Operações CRUD genéricas
│   │   ├── crud_user.py             # Operações de usuário
│   │   ├── crud_category.py         # Operações de categoria
│   │   └── crud_transaction.py      # Operações de transação
│   ├── db/
│   │   ├── base.py                  # Registro de modelos
│   │   └── session.py               # Configuração de BD
│   ├── models/
│   │   ├── user.py                  # Modelo de usuário
│   │   ├── category.py              # Modelo de categoria
│   │   ├── transaction.py           # Modelo de transação
│   │   └── chat.py                  # Modelo de chat IA (NOVO)
│   ├── services/
│   │   ├── __init__.py
│   │   └── ai_service.py            # Integração OpenAI (NOVO)
│   ├── utils/
│   │   ├── __init__.py
│   │   └── markdown_cleaner.py      # Limpeza de texto (NOVO)
│   └── schemas/
│       ├── user.py                  # Schemas de usuário
│       ├── category.py              # Schemas de categoria
│       ├── transaction.py           # Schemas de transação
│       └── ai_chat.py               # Schemas de chat IA (NOVO)
├── docs/
│   ├── screenshots/                 # Screenshots da API
│   └── CHANGELOG.md                 # Histórico de versões
├── migrations/                      # Migrações de banco de dados
├── .env                             # Variáveis de ambiente
├── .env.example                     # Modelo de variáveis de ambiente
├── .gitignore                       # Exclusões do Git
├── requirements.txt                 # Dependências Python
├── README.md                        # Documentação (Inglês)
└── README.pt-BR.md                  # Documentação (Português)
```

---

## 📝 Changelog

Para histórico detalhado de mudanças, consulte [CHANGELOG.md](./docs/CHANGELOG.md)

### Destaques da Versão Atual

**v1.2.0** (2025-12-18):
- 🤖 Adicionado recurso de Chat IA com integração OpenAI
- 🧹 Implementado Limpador de Markdown (95% de cobertura)
- 📊 3 novos endpoints para interação com IA
- 🏗️ Adicionadas camadas `services/` e `utils/`

**v1.1.0** (2025-12-15):
- 👤 Gerenciamento de perfil de usuário aprimorado
- ⏰ Sistema de timestamp inteligente
- 🔒 Endpoint de exclusão suave de conta

**v1.0.0** (2025-12-01):
- 🎉 Lançamento inicial com recursos principais

---

## 🔮 Melhorias Futuras

### Em Consideração

#### 🔐 Autenticação Avançada
- [ ] Login social OAuth2 (Google, GitHub)
- [ ] Autenticação de dois fatores (2FA)
- [ ] Autenticação por chave de API para integrações de terceiros
- [ ] Controle de acesso baseado em funções (RBAC) para sistemas multiusuário

#### 📊 Recursos Avançados
- [ ] **Gerenciamento de Orçamento** - Definir orçamentos mensais por categoria
- [ ] **Transações Recorrentes** - Automatizar contas/receitas mensais
- [ ] **Suporte Multi-moeda** - Rastrear despesas em diferentes moedas
- [ ] **Anexos de Arquivo** - Upload de recibos/faturas
- [ ] **Exportar Relatórios** - Geração de PDF/Excel
- [ ] **Notificações por Email** - Alertas de orçamento, resumos

#### 🗄️ Banco de Dados e Infraestrutura
- [ ] **Migração PostgreSQL** - Banco de dados pronto para produção
- [ ] **Seeding de Banco de Dados** - Implementar `init_db.py` com categorias padrão
- [ ] **Migrações Alembic** - Controle de versão de banco de dados
- [ ] **Cache Redis** - Melhorar desempenho de geração de relatórios
- [ ] **Suporte Docker** - Containerização para implantação fácil

#### 🧪 Testes e Qualidade
- [ ] **Testes Unitários** - Cobertura de código de 80%+ com pytest
- [ ] **Testes de Integração** - Teste completo de endpoints
- [ ] **Teste de Carga** - Benchmarks de desempenho com Locust
- [ ] **Pipeline CI/CD** - GitHub Actions para teste/implantação automatizados

#### 📱 Frontend e UX
- [ ] **Dashboard React** - Interface web interativa
- [ ] **App Mobile** - React Native ou Flutter
- [ ] **Gráficos e Visualizações** - Gráficos de tendências de gastos
- [ ] **Modo Escuro** - Suporte a tema de UI

#### 📖 Documentação
- [ ] **Coleção Postman** - Requisições de API pré-configuradas
- [ ] **Tutorial em Vídeo** - Guia de configuração e uso
- [ ] **Versionamento de API** - Suporte para endpoints v2, v3

#### ⚡ Performance
- [ ] **Otimização de Consultas** - Estratégia de indexação de banco de dados
- [ ] **Operações Assíncronas** - Implementação completa de async/await
- [ ] **Paginação** - Paginação baseada em cursor para grandes conjuntos de dados
- [ ] **API GraphQL** - Alternativa ao REST para consultas flexíveis

---

## 👨‍💻 Autor

**Thiago Memelli**

🎓 **Background**: Transicionando para Desenvolvimento Backend  
💼 **Procurando por**: Posições de Desenvolvedor Backend Python / Desenvolvedor de API  
📍 **Localização**: [Vitória, ES - Brasil (Aberto para Remoto)]  
📧 **Contato**: [tmemelli@gmail.com]  
🔗 **LinkedIn**: [linkedin.com/in/thiagomemelli](https://linkedin.com/in/thiagomemelli)  
🐙 **GitHub**: [github.com/tmemelli](https://github.com/tmemelli)

### Sobre Este Projeto

Este é meu **primeiro projeto de API Python**, construído do zero para demonstrar:

✅ **Princípios de Código Limpo** - Código legível, mantível e bem documentado  
✅ **Arquitetura de Software** - Separação de responsabilidades, princípios SOLID  
✅ **Design de API RESTful** - Práticas padrão da indústria  
✅ **Melhores Práticas de Segurança** - Auth JWT, hash de senha, validação de entrada  
✅ **Design de Banco de Dados** - Normalização, chaves estrangeiras, exclusões suaves  
✅ **Stack Python Moderno** - FastAPI, SQLAlchemy 2.0, Pydantic V2  
✅ **Documentação Profissional** - README abrangente, comentários inline  

**Por que construí isso:**  
Para demonstrar minha capacidade de entregar código de qualidade de produção e meu compromisso com o aprendizado de tecnologias backend modernas. Estou ativamente buscando oportunidades para contribuir com uma equipe de desenvolvimento e crescer como engenheiro de software profissional.

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja abaixo para detalhes:

```
Licença MIT

Copyright (c) 2025 Thiago Memelli

É concedida permissão, gratuitamente, a qualquer pessoa que obtenha uma cópia
deste software e arquivos de documentação associados (o "Software"), para lidar
com o Software sem restrição, incluindo, sem limitação, os direitos de usar,
copiar, modificar, mesclar, publicar, distribuir, sublicenciar e/ou vender
cópias do Software, e permitir que as pessoas a quem o Software é fornecido
o façam, sujeitas às seguintes condições:

O aviso de copyright acima e este aviso de permissão devem ser incluídos em todas
as cópias ou partes substanciais do Software.

O SOFTWARE É FORNECIDO "COMO ESTÁ", SEM GARANTIA DE QUALQUER TIPO, EXPRESSA OU
IMPLÍCITA, INCLUINDO, MAS NÃO SE LIMITANDO ÀS GARANTIAS DE COMERCIALIZAÇÃO,
ADEQUAÇÃO A UMA FINALIDADE ESPECÍFICA E NÃO VIOLAÇÃO. EM NENHUMA CIRCUNSTÂNCIA OS
AUTORES OU DETENTORES DOS DIREITOS AUTORAIS SERÃO RESPONSÁVEIS POR QUALQUER RECLAMAÇÃO,
DANOS OU OUTRA RESPONSABILIDADE, SEJA EM AÇÃO DE CONTRATO, DELITO OU DE OUTRA FORMA,
DECORRENTE DE, FORA DE OU EM CONEXÃO COM O SOFTWARE OU O USO OU OUTRAS NEGOCIAÇÕES NO
SOFTWARE.
```

---

## 🔮 Melhorias Futuras e Roadmap

Esta seção demonstra consciência de requisitos de nível de produção e considerações de escalabilidade.

### 🧪 Testes e Garantia de Qualidade
- [ ] **Testes Unitários** com pytest (meta: cobertura de 80%+)
- [ ] **Testes de Integração** para endpoints de API
- [ ] **Teste de Carga** com Locust/k6
- [ ] **Teste de Segurança** (validação OWASP Top 10)

### 🚀 DevOps e Infraestrutura
- [ ] **Docker/Docker Compose** para containerização
- [ ] **Pipeline CI/CD** (GitHub Actions/GitLab CI)
- [ ] **Migrações de Banco de Dados** com Alembic
- [ ] **Configuração Baseada em Ambiente** (dev/staging/prod)
- [ ] **Endpoints de Health Check** (/health, /ready)

### 📊 Observabilidade e Monitoramento
- [ ] **Logging Estruturado** (logs JSON com IDs de correlação)
- [ ] **Monitoramento de Desempenho de Aplicação** (APM)
- [ ] **Métricas e Dashboards** (Prometheus/Grafana)
- [ ] **Rastreamento de Erros** (integração Sentry)
- [ ] **Logs de Auditoria** para conformidade

### 🔒 Melhorias de Segurança
- [ ] **Rate Limiting** por usuário/IP (prevenir abuso de API)
- [ ] **Validação de Requisição** com schemas mais rigorosos
- [ ] **Configuração CORS** para produção
- [ ] **Gerenciamento de Chave de API** para auth serviço-a-serviço
- [ ] **Gerenciamento de Segredos** (AWS Secrets Manager/Vault)

### ⚡ Performance e Escalabilidade
- [ ] **Otimização de Pool de Conexão de Banco de Dados**
- [ ] **Cache Redis** para consultas frequentes
- [ ] **Padronização de Paginação** em todos os endpoints
- [ ] **Otimização de Consultas** com índices apropriados
- [ ] **Tarefas Assíncronas em Background** (Celery/Dramatiq)

### 🤖 Melhorias do Serviço de IA
- [ ] **Lógica de Retry** para falhas da API OpenAI
- [ ] **Mecanismos de Fallback** quando IA está indisponível
- [ ] **Monitoramento de Custo** para uso de OpenAI por usuário
- [ ] **Streaming de Resposta** para melhor UX
- [ ] **Cache de Contexto** para reduzir chamadas de API

### 📚 Documentação
- [ ] **Diagramas de Arquitetura** (Modelo C4/Draw.io)
- [ ] **Documentação de Estratégia de Versionamento de API**
- [ ] **Documentação de Schema de Banco de Dados** (diagramas ERD)
- [ ] **Guia de Implantação** para produção
- [ ] **Diretrizes de Contribuição** para código aberto

### 🌐 Recursos Adicionais
- [ ] **Suporte Multi-moeda**
- [ ] **Planejamento de Orçamento e Alertas**
- [ ] **Transações Recorrentes**
- [ ] **Exportação de Dados** (relatórios CSV/PDF)
- [ ] **Integração com App Mobile** (cliente REST)

---

> **Nota para Recrutadores:** Este roadmap demonstra minha compreensão de sistemas prontos para produção e requisitos de nível empresarial. Embora este seja um projeto de portfólio, estou totalmente ciente do que é necessário para escalar e manter software em ambientes de produção.

---

## 🙏 Agradecimentos

- **FastAPI** - Pelo excelente framework web async
- **SQLAlchemy** - Pelas poderosas capacidades de ORM
- **Pydantic** - Pela elegante validação de dados
- **Comunidade Python** - Pela extensa documentação e suporte

---

## 📞 Contato e Suporte

Se você é um recrutador ou gerente de contratação interessado nas minhas habilidades:

📧 **Email**: [tmemelli@gmail.com]  
💼 **LinkedIn**: [https://www.linkedin.com/in/thiagomemelli/]  
📱 **Telefone**: [+5527989030474]  
🌐 **Portfólio**: [https://thiagomemelli.com.br/]

**Estou disponível para:**
- Posições full-time de Desenvolvedor Backend
- Projetos de Desenvolvimento de API
- Consultoria Python/FastAPI
- Entrevistas técnicas

---

<div align="center">

### ⭐ Se você achou este projeto impressionante, por favor dê uma estrela!

**Feito com ❤️ por Thiago Memelli**

*Primeiro Projeto de API Python - Dezembro 2025*

</div>
