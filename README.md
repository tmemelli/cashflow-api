# 💰 CashFlow API

<div align="center">

🌍 **Language / Idioma**

🇺🇸 **English** | [🇧🇷 Português](./README.pt-BR.md)

</div>

---

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.123.7-009688.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.44-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)

A professional RESTful API for personal financial management, built with modern Python technologies and best practices.

**Author:** Thiago Memelli  
**First Python API Project** - Demonstrating clean architecture, security best practices, and comprehensive testing.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Technologies](#-technologies)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Screenshots](#-screenshots)
- [Project Structure](#-project-structure)
- [Changelog](#-changelog)
- [Future Improvements](#-future-improvements)
- [Author](#-author)

---

## 🎯 Overview

CashFlow API is a complete financial management system that allows users to:
- Track income and expenses with detailed categorization
- Generate comprehensive financial reports and statistics
- Analyze spending patterns by category
- Monitor monthly financial trends
- Maintain secure user authentication with JWT tokens

This project demonstrates **production-ready code** with:
- ✅ Clean Architecture (separation of concerns)
- ✅ RESTful API design principles
- ✅ Comprehensive input validation
- ✅ JWT-based authentication & authorization
- ✅ Soft delete pattern (data preservation)
- ✅ Detailed API documentation (OpenAPI/Swagger)
- ✅ Type safety with Pydantic schemas

---

## ✨ Features

### 🔐 Authentication & Security
- **JWT Token Authentication** - Secure access to protected endpoints
- **Password Hashing** - Bcrypt encryption for user passwords
- **Token Expiration** - Configurable session timeout
- **User Authorization** - Endpoint-level permission control

### � User Profile Management
- **Full Name Field** - Required user identification (1-150 characters)
- **Account Status Tracking** - is_active, is_superuser, is_deleted flags
- **Smart Timestamp Separation** - Industry-standard approach to audit trails:
  - `created_at` - Account creation timestamp (auto-generated on registration)
  - `updated_at` - Profile modification timestamp (updated only when user data changes)
  - `last_login_at` - Authentication tracking (updated only on successful login)
- **Timestamp Implementation** - Uses direct SQL updates to prevent unintended side effects:
  - Login updates `last_login_at` via `db.execute()` without triggering `updated_at`
  - Profile updates modify `updated_at` manually in CRUD layer
  - Demonstrates understanding of ORM behavior and production best practices
- **Self-Service Profile Endpoint** - Users update their own data via `/me` (token-based identification)

### �📊 Financial Management
- **Dual Transaction Types** - Income and Expense tracking
- **Category System** - Organize transactions by custom or default categories
- **Soft Delete** - Transactions are marked as deleted, not permanently removed (audit trail)
- **Date Range Filtering** - Query transactions by specific time periods

### 📈 Analytics & Reports
- **Financial Statistics** - Real-time calculation of totals, balance, and transaction count
- **Summary Reports** - Daily averages for income, expenses, and transactions
- **Category Breakdown** - Spending/income analysis by category with percentages
- **Monthly Trends** - Historical financial data grouped by month
- **Trend Analysis** - Daily, weekly, or monthly aggregation options

### 🛡️ Data Integrity
- **Validation Layer** - Pydantic schemas ensure data correctness
- **Type Safety** - Enums for transaction and category types
- **Foreign Key Constraints** - Referential integrity in database
- **Automatic Timestamps** - Track creation and update times

### 🤖 AI-Powered Financial Assistant (NEW!)

CashFlow API now includes an intelligent AI assistant powered by OpenAI's GPT-4o-mini that understands your financial data and answers questions in natural language.

**Key Features:**
- **Natural Language Queries** - Ask questions about your finances in plain English/Portuguese
- **Context-Aware Analysis** - AI analyzes your actual transaction data to provide accurate answers
- **Conversation History** - All chats are saved with timestamps for future reference
- **Smart Data Retrieval** - Automatically fetches relevant financial data (categories, transactions, totals)
- **Markdown Cleaning** - Custom cleaner removes 95% of AI formatting for clean text output

**Markdown Cleaner (95% Coverage):**
Our custom text processing utility ensures AI responses are clean and frontend-ready:
- ✅ Removes `**bold**`, `*italic*`, `~~strikethrough~~`
- ✅ Removes `# headers` and `> blockquotes`
- ✅ Converts `- lists` to `• bullet points`
- ✅ Removes ` ```code blocks``` ` and `` `inline code` ``
- ✅ Cleans `[links](url)` to plain text
- ✅ Preserves line breaks (`\n\n`) for readability
- ✅ Removes HTML tags and excess whitespace
- ✅ Output is plain text ready for any frontend

**Example Queries:**
```
"How much did I spend this month?"
"What are my top 3 expense categories?"
"Show me my income vs expenses"
"Analyze my spending on food"
"What's my current balance?"
```

**How It Works:**
```
User Question → AI Service → OpenAI API
                    ↓
          Fetch User's Financial Data
                    ↓
          Generate Contextual Response
                    ↓
          Apply Markdown Cleaner (95%)
                    ↓
          Save to Chat History
                    ↓
          Return Clean Text to User
```

**Technical Implementation:**
- **Service Layer**: `app/services/ai_service.py` - Orchestrates AI interactions
- **Text Processing**: `app/utils/markdown_cleaner.py` - 17 cleaning rules
- **Data Model**: `app/models/chat.py` - Conversation history storage
- **Endpoints**: 3 new routes in `app/api/v1/endpoints/ai_chat.py`

---

## 🛠️ Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Core programming language |
| **FastAPI** | 0.123.7 | Modern async web framework |
| **SQLAlchemy** | 2.0.44 | ORM for database operations |
| **Pydantic** | 2.12.5 | Data validation and settings |
| **JWT (python-jose)** | 3.5.0 | Token-based authentication |
| **Bcrypt** | 4.0.1 | Password hashing |
| **Uvicorn** | 0.38.0 | ASGI server |
| **SQLite** | 3 | Lightweight database (development) |
| **OpenAI API** | 2.9.0 | AI-powered chat assistant |

### Why These Technologies?

- **FastAPI**: Automatic API documentation, high performance, async support
- **SQLAlchemy**: Database agnostic ORM, supports PostgreSQL migration
- **Pydantic**: Runtime type checking, automatic validation
- **JWT**: Stateless authentication, scalable for distributed systems

---

## 🏗️ Architecture

### Clean Architecture Pattern

```
app/
├── api/                    # API Layer (Controllers)
│   ├── deps.py             # Dependency injection
│   └── v1/
│       ├── api.py          # Router aggregation
│       └── endpoints/      # Route handlers
├── core/                   # Core Configuration
│   ├── config.py           # Settings management
│   └── security.py         # Auth utilities
├── crud/                   # Data Access Layer
│   ├── base.py             # Generic CRUD operations
│   └── crud_*.py           # Model-specific operations
├── db/                     # Database Layer
│   ├── base.py             # Model registration
│   └── session.py          # DB connection
├── models/                 # Domain Layer (ORM Models)
│   ├── user.py
│   ├── category.py
│   └── transaction.py
├── services/               # Business Logic Layer
│   ├── __init__.py
│   └── ai_service.py       # OpenAI integration & orchestration
├── utils/                  # Utility Functions
│   ├── __init__.py
│   └── markdown_cleaner.py # Text cleaning (95% coverage)
└── schemas/                # Presentation Layer (DTOs)
    ├── user.py
    ├── category.py
    └── transaction.py
```

### Design Patterns Used

1. **Repository Pattern** - CRUD layer abstracts database operations
2. **Dependency Injection** - FastAPI's `Depends()` for clean dependencies
3. **DTO Pattern** - Pydantic schemas separate API contracts from models
4. **Soft Delete Pattern** - `is_deleted` flag preserves audit trail
5. **Generic Base Class** - `CRUDBase` with TypeVars for code reuse

---

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step-by-Step Setup

1. **Clone the repository**
```bash
git clone https://github.com/tmemelli/cashflow-api.git
cd cashflow-api
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Configure environment variables**

Create a `.env` file in the root directory:
```env
# Application Settings
PROJECT_NAME=CashFlow API
VERSION=1.0.0
API_V1_STR=/api/v1

# Security Settings
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Settings
DATABASE_URL=sqlite:///./cashflow.db
```

⚠️ **Important**: Generate a secure SECRET_KEY for production:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

6. **Initialize the database**
```bash
python create_db.py
```

7. **Run the server**
```bash
uvicorn app.main:app --reload
```

8. **Access the API**
- API: http://localhost:8000
- Interactive Docs (Swagger): http://localhost:8000/docs
- Alternative Docs (ReDoc): http://localhost:8000/redoc

---

## 🚀 Usage

### Quick Start Guide

#### 1️⃣ Register a User
```bash
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

#### 2️⃣ Login
```bash
POST /api/v1/auth/login
{
  "username": "user@example.com",
  "password": "securepassword123"
}
```
Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 3️⃣ Use the Token

Add to request headers:
```
Authorization: Bearer <your-access-token>
```

Or use the "Authorize" button in Swagger UI.

#### 4️⃣ Create a Category
```bash
POST /api/v1/categories/
{
  "name": "Salary",
  "type": "income"
}
```

#### 5️⃣ Create a Transaction
```bash
POST /api/v1/transactions/
{
  "type": "income",
  "amount": 5000.00,
  "description": "Monthly salary",
  "date": "2025-12-01",
  "category_id": 1
}
```

#### 6️⃣ View Statistics
```bash
GET /api/v1/transactions/statistics
```

#### 7️⃣ Update Your Profile
```bash
PUT /api/v1/auth/me
{
  "full_name": "Thiago Memelli Updated",
  "email": "newemail@example.com"
}
```

**Note:** This updates `updated_at` timestamp but NOT `last_login_at` (smart timestamp separation).

### 🤖 AI-Powered Financial Assistant (NEW!)

CashFlow API now includes an intelligent AI assistant powered by OpenAI's GPT-4o-mini that understands your financial data and answers questions in natural language.

**Key Features:**
- **Natural Language Queries** - Ask questions about your finances in plain English/Portuguese
- **Context-Aware Analysis** - AI analyzes your actual transaction data to provide accurate answers
- **Conversation History** - All chats are saved with timestamps for future reference
- **Smart Data Retrieval** - Automatically fetches relevant financial data (categories, transactions, totals)
- **Markdown Cleaning** - Custom cleaner removes 95% of AI formatting for clean text output

**Markdown Cleaner (95% Coverage):**
Our custom text processing utility ensures AI responses are clean and frontend-ready:
- ✅ Removes `**bold**`, `*italic*`, `~~strikethrough~~`
- ✅ Removes `# headers` and `> blockquotes`
- ✅ Converts `- lists` to `• bullet points`
- ✅ Removes ` ```code blocks``` ` and `` `inline code` ``
- ✅ Cleans `[links](url)` to plain text
- ✅ Preserves line breaks (`\n\n`) for readability
- ✅ Removes HTML tags and excess whitespace
- ✅ Output is plain text ready for any frontend

**Example Queries:**
```
"How much did I spend this month?"
"What are my top 3 expense categories?"
"Show me my income vs expenses"
"Analyze my spending on food"
"What's my current balance?"
```
---

### 📚 API Endpoints

#### 🔐 Authentication (5 endpoints)
- `POST /api/v1/auth/register` - Create new user account
- `POST /api/v1/auth/login` - Authenticate and get JWT token
- `POST /api/v1/auth/refresh` - Refresh expired token
- `GET /api/v1/auth/me` - Get current user profile
- `PUT /api/v1/auth/me` - Update user profile

#### 📂 Categories (5 endpoints)
- `POST /api/v1/categories` - Create new category
- `GET /api/v1/categories` - List all categories (with pagination)
- `GET /api/v1/categories/{id}` - Get specific category
- `PUT /api/v1/categories/{id}` - Update category
- `DELETE /api/v1/categories/{id}` - Soft delete category

#### 💸 Transactions (6 endpoints)
- `POST /api/v1/transactions` - Create new transaction (income/expense)
- `GET /api/v1/transactions` - List all transactions (filterable by date/category/type)
- `GET /api/v1/transactions/{id}` - Get specific transaction
- `PUT /api/v1/transactions/{id}` - Update transaction
- `DELETE /api/v1/transactions/{id}` - Soft delete transaction
- `GET /api/v1/transactions/summary` - Quick statistics

#### 📊 Reports (4 endpoints)
- `GET /api/v1/reports/statistics` - Overall financial statistics
- `GET /api/v1/reports/by-category` - Breakdown by category
- `GET /api/v1/reports/trends` - Monthly/weekly trends
- `GET /api/v1/reports/summary` - Daily averages

#### 🤖 AI Chat (3 endpoints - NEW!)
- `POST /api/v1/ai/chat` - Ask AI about your finances
- `GET /api/v1/ai/history` - Retrieve conversation history (limit: 10-50)
- `DELETE /api/v1/ai/history/{id}` - Delete specific conversation

**Total: 23 endpoints**

### 📖 Detailed Examples

#### Get Transactions with Filters
```bash
GET /api/v1/transactions/?start_date=2025-01-01&end_date=2025-01-31&transaction_type=expense
```

#### Get Category Breakdown
```bash
GET /api/v1/reports/by-category?start_date=2025-01-01&transaction_type=expense
```

Response:
```json
{
  "period": {
    "start_date": "2025-01-01",
    "end_date": "2025-01-31"
  },
  "by_category": [
    {
      "category_id": 1,
      "category_name": "Food",
      "category_type": "expense",
      "total_amount": "850.50",
      "transaction_count": 12,
      "percentage": 24.3
    }
  ],
  "total": "3500.50"
}
```

### 🤖 Example: AI Chat Query

**Request:**
```http
POST /api/v1/ai/chat
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "message": "How much did I spend on food this month?"
}
```

**Response:**
```json
{
  "reply": "You spent $330.50 on food this month. Your largest expense was $150.50 at the supermarket. This represents 33% of your total monthly expenses.",
  "data": {
    "total_spent": 330.50,
    "category": "Food & Drinks",
    "transaction_count": 12
  },
  "sql_query": "SELECT SUM(amount) FROM transactions WHERE category_id=... AND date>=..."
}
```

**Get Chat History:**
```http
GET /api/v1/ai/history?limit=10
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
[
  {
    "id": 1,
    "question": "How much did I spend on food this month?",
    "response": "You spent $330.50 on food this month...",
    "created_at": "2025-12-18T10:30:00Z"
  }
]
```
---

## 📸 Screenshots

### Server Running
![Server Running](docs/screenshots/01-servidor-rodando.png)

### Swagger UI - API Documentation
![Swagger Home](docs/screenshots/02-swagger-home-parte1.png)

### User Registration
![Register](docs/screenshots/03-auth-register.png)

### JWT Token Login
![Login](docs/screenshots/04-auth-login.png)

### Categories Management
![Categories](docs/screenshots/09-categories-list.png)

### Transaction List
![Transactions](docs/screenshots/12-transactions-list.png)

### Financial Statistics
![Statistics](docs/screenshots/13-statistics.png)

### Reports - Summary
![Summary Report](docs/screenshots/14-reports-summary.png)

### Reports - By Category
![Category Report](docs/screenshots/15-reports-by-category.png)

### Database Structure
![Database](docs/screenshots/16-database-tables.png)

---

## 📂 Project Structure

```
cashflow-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py             # Shared dependencies (auth, db)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py          # Router aggregation
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── auth.py     # Authentication endpoints
│   │           ├── categories.py
│   │           ├── transactions.py
│   │           └── reports.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Settings management
│   │   └── security.py         # JWT & password utilities
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── base.py             # Generic CRUD with TypeVars
│   │   ├── crud_user.py
│   │   ├── crud_category.py
│   │   └── crud_transaction.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py             # Model imports for SQLAlchemy
│   │   ├── session.py          # Database engine & session
│   │   └── init_db.py          # DB initialization (future use)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User ORM model
│   │   ├── category.py         # Category ORM model
│   │   └── transaction.py      # Transaction ORM model
│   └── schemas/
│       ├── __init__.py
│       ├── user.py             # User Pydantic schemas
│       ├── category.py         # Category Pydantic schemas
│       └── transaction.py      # Transaction Pydantic schemas
├── docs/
│   ├── CHANGELOG.md            # Version history and updates
│   ├── USER_PROFILE_FEATURE.md # Detailed feature documentation
│   └── screenshots/            # API testing screenshots
├── tests/                      # Unit & integration tests (future)
├── .env                        # Environment variables
├── .env.example                # Example environment file
├── .gitignore
├── create_db.py                # Database initialization script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

### Key Files Explained

- **`main.py`**: FastAPI app initialization, CORS, OpenAPI config
- **`deps.py`**: Dependency injection (DB session, current user)
- **`base.py` (crud)**: Generic CRUD operations using Python generics
- **`security.py`**: JWT encoding/decoding, password hashing
- **`config.py`**: Pydantic Settings for environment variables
- **`base.py` (db)**: Central import point for all models (Alembic support)

---

## � Changelog

### Version 1.1.0 (December 15, 2025)

**✨ New Features:**
- User Profile Management with smart timestamp separation
- PUT `/api/v1/auth/me` endpoint for self-service profile updates
- Full name field added to user registration

**🔧 Technical Improvements:**
- Implemented industry-standard audit trail pattern
- Direct SQL updates to prevent ORM side effects
- Manual timestamp control in CRUD layer

**📚 Documentation:**
- Comprehensive changelog ([docs/CHANGELOG.md](docs/CHANGELOG.md))
- Feature deep-dive guide ([docs/USER_PROFILE_FEATURE.md](docs/USER_PROFILE_FEATURE.md))
- New screenshots showing timestamp behavior (17-23)

**For full details**, see [CHANGELOG.md](docs/CHANGELOG.md)

---

## �🚧 Future Improvements

### Planned Features

#### 🔒 Enhanced Security
- [ ] Rate limiting to prevent brute force attacks
- [ ] OAuth2 social login (Google, GitHub)
- [ ] Two-factor authentication (2FA)
- [ ] API key authentication for third-party integrations
- [ ] Role-based access control (RBAC) for multi-user systems

#### 📊 Advanced Features
- [ ] **Budget Management** - Set monthly budgets per category
- [ ] **Recurring Transactions** - Automate monthly bills/income
- [ ] **Multi-currency Support** - Track expenses in different currencies
- [ ] **File Attachments** - Upload receipts/invoices
- [ ] **Export Reports** - PDF/Excel generation
- [ ] **Email Notifications** - Budget alerts, summaries

#### 🗄️ Database & Infrastructure
- [ ] **PostgreSQL Migration** - Production-ready database
- [ ] **Database Seeding** - Implement `init_db.py` with default categories:
  ```python
  # Default Income Categories
  - Salary, Freelance, Investments, Gifts, Bonus
  
  # Default Expense Categories  
  - Food, Transport, Housing, Health, Entertainment, Education, Utilities
  ```
- [ ] **Alembic Migrations** - Database version control
- [ ] **Redis Caching** - Improve report generation performance
- [ ] **Docker Support** - Containerization for easy deployment

#### 🧪 Testing & Quality
- [ ] **Unit Tests** - 80%+ code coverage with pytest
- [ ] **Integration Tests** - Full endpoint testing
- [ ] **Load Testing** - Performance benchmarks with Locust
- [ ] **CI/CD Pipeline** - GitHub Actions for automated testing/deployment

#### 📱 Frontend & UX
- [ ] **React Dashboard** - Interactive web interface
- [ ] **Mobile App** - React Native or Flutter
- [ ] **Charts & Visualizations** - Spending trends graphs
- [ ] **Dark Mode** - UI theme support

#### 📖 Documentation
- [ ] **Postman Collection** - Pre-configured API requests
- [ ] **Video Tutorial** - Setup and usage guide
- [ ] **API Versioning** - Support for v2, v3 endpoints

#### ⚡ Performance
- [ ] **Query Optimization** - Database indexing strategy
- [ ] **Async Operations** - Full async/await implementation
- [ ] **Pagination** - Cursor-based pagination for large datasets
- [ ] **GraphQL API** - Alternative to REST for flexible queries

### Partially Implemented

#### ✅ Database Initialization (`init_db.py`)
Currently contains scaffolding code for:
- Creating default system categories
- Seeding initial admin user
- Populating test data

**Status**: Documented but commented out (ready for implementation)

**Why not implemented yet**: SQLAlchemy auto-creates tables on first request. For MVP, manual category creation via API is sufficient. Production deployment will implement this feature.

---

## 👨‍💻 Author

**Thiago Memelli**

🎓 **Background**: Transitioning to Backend Development  
💼 **Looking for**: Python Backend Developer / API Developer positions  
📍 **Location**: [Vitória, ES - Brazil (Open to Remote)]  
📧 **Contact**: [tmemelli@gmail.com]  
🔗 **LinkedIn**: [linkedin.com/in/thiagomemelli](https://linkedin.com/in/thiagomemelli)  
🐙 **GitHub**: [github.com/tmemelli](https://github.com/tmemelli)

### About This Project

This is my **first Python API project**, built from scratch to demonstrate:

✅ **Clean Code Principles** - Readable, maintainable, well-documented code  
✅ **Software Architecture** - Separation of concerns, SOLID principles  
✅ **RESTful API Design** - Industry-standard practices  
✅ **Security Best Practices** - JWT auth, password hashing, input validation  
✅ **Database Design** - Normalization, foreign keys, soft deletes  
✅ **Modern Python Stack** - FastAPI, SQLAlchemy 2.0, Pydantic V2  
✅ **Professional Documentation** - Comprehensive README, inline comments  

**Why I built this:**  
To showcase my ability to deliver production-quality code and my commitment to learning modern backend technologies. I'm actively seeking opportunities to contribute to a development team and grow as a professional software engineer.

---

## 📄 License

This project is licensed under the MIT License - see below for details:

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

## � Future Improvements & Roadmap

This section demonstrates awareness of production-grade requirements and scalability considerations.

### 🧪 Testing & Quality Assurance
- [ ] **Unit Tests** with pytest (target: 80%+ coverage)
- [ ] **Integration Tests** for API endpoints
- [ ] **Load Testing** with Locust/k6
- [ ] **Security Testing** (OWASP Top 10 validation)

### 🚀 DevOps & Infrastructure
- [ ] **Docker/Docker Compose** for containerization
- [ ] **CI/CD Pipeline** (GitHub Actions/GitLab CI)
- [ ] **Database Migrations** with Alembic (currently using custom system)
- [ ] **Environment-based Configuration** (dev/staging/prod)
- [ ] **Health Check Endpoints** (/health, /ready)

### 📊 Observability & Monitoring
- [ ] **Structured Logging** (JSON logs with correlation IDs)
- [ ] **Application Performance Monitoring** (APM)
- [ ] **Metrics & Dashboards** (Prometheus/Grafana)
- [ ] **Error Tracking** (Sentry integration)
- [ ] **Audit Logs** for compliance

### 🔒 Security Enhancements
- [ ] **Rate Limiting** per user/IP (prevent API abuse)
- [ ] **Request Validation** with stricter schemas
- [ ] **CORS Configuration** for production
- [ ] **API Key Management** for service-to-service auth
- [ ] **Secrets Management** (AWS Secrets Manager/Vault)

### ⚡ Performance & Scalability
- [ ] **Database Connection Pooling** optimization
- [ ] **Redis Caching** for frequent queries
- [ ] **Pagination** standardization across all endpoints
- [ ] **Query Optimization** with proper indexes
- [ ] **Async Background Tasks** (Celery/Dramatiq)

### 🤖 AI Service Improvements
- [ ] **Retry Logic** for OpenAI API failures
- [ ] **Fallback Mechanisms** when AI is unavailable
- [ ] **Cost Monitoring** for OpenAI usage per user
- [ ] **Response Streaming** for better UX
- [ ] **Context Caching** to reduce API calls

### 📚 Documentation
- [ ] **Architecture Diagrams** (C4 Model/Draw.io)
- [ ] **API Versioning Strategy** documentation
- [ ] **Database Schema Documentation** (ERD diagrams)
- [ ] **Deployment Guide** for production
- [ ] **Contributing Guidelines** for open source

### 🌐 Additional Features
- [ ] **Multi-currency Support**
- [ ] **Budget Planning & Alerts**
- [ ] **Recurring Transactions**
- [ ] **Data Export** (CSV/PDF reports)
- [ ] **Mobile App Integration** (REST client)

---

> **Note for Recruiters:** This roadmap demonstrates my understanding of production-ready systems and enterprise-level requirements. While this is a portfolio project, I'm fully aware of what it takes to scale and maintain software in production environments.

---

## �🙏 Acknowledgments

- **FastAPI** - For the excellent async web framework
- **SQLAlchemy** - For the powerful ORM capabilities
- **Pydantic** - For elegant data validation
- **Python Community** - For extensive documentation and support

---

## 📞 Contact & Support

If you're a recruiter or hiring manager interested in my skills:

📧 **Email**: [tmemelli@gmail.com]  
💼 **LinkedIn**: [https://www.linkedin.com/in/thiagomemelli/]  
📱 **Phone**: [+5527989030474]  
🌐 **Portfolio**: [https://thiagomemelli.com.br/]

**I'm available for:**
- Full-time Backend Developer positions
- API Development projects
- Python/FastAPI consulting
- Technical interviews

---

<div align="center">

### ⭐ If you found this project impressive, please star it!

**Made with ❤️ by Thiago Memelli**

*First Python API Project - December 2025*

</div>
