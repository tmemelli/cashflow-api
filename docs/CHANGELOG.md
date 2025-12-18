# 📝 Changelog - CashFlow API

All notable changes to this project will be documented in this file.

## [1.2.0] - 2025-12-18

### ✨ Added - AI-Powered Financial Assistant

#### 🤖 AI Chat Feature
- **Natural Language Queries** - Ask questions about finances in plain language
- **OpenAI Integration** - Powered by GPT-4o-mini for intelligent responses
- **Context-Aware Analysis** - AI analyzes user's actual transaction data
- **Conversation History** - All chats saved with timestamps for future reference
- **3 New Endpoints**:
  - `POST /api/v1/ai/chat` - Ask AI about your finances
  - `GET /api/v1/ai/history` - Retrieve conversation history (limit: 10-50)
  - `DELETE /api/v1/ai/history/{id}` - Delete specific conversation

#### 🧹 Markdown Cleaner Utility (95% Coverage)
- **Text Formatting Removal** - Removes bold (`**text**`), italic (`*text*`), headers (`# text`)
- **List Conversion** - Converts `- item` to `• item` for better readability
- **Code Block Removal** - Cleans ` ```code blocks``` ` and `` `inline code` ``
- **Link Cleaning** - Converts `[text](url)` to plain text
- **Line Break Preservation** - Maintains `\n\n` for paragraph structure
- **HTML Tag Removal** - Strips all HTML tags for security
- **Whitespace Normalization** - Removes excess spaces and blank lines
- **17 Cleaning Rules** - Comprehensive text processing pipeline

#### Technical Implementation
- **New Layer: `services/`** - Business logic separation
  - Created `AIService` class for OpenAI orchestration
  - Handles data fetching, prompt building, response processing
  
- **New Layer: `utils/`** - Shared utility functions
  - Created `MarkdownCleaner` class with 17 text cleaning rules
  - Static methods for easy reusability
  
- **New Model: `Chat`** - Conversation history persistence
  - Stores user questions and AI responses
  - Tracks timestamps and relationship to users
  
- **New Schema: `ai_chat.py`** - Request/response validation
  - `ChatRequest` - Validates user input
  - `ChatResponse` - Structured AI response with optional data
  - `ChatHistory` - Conversation list with metadata

#### Database Changes
- Added `chats` table for AI conversation history
- Foreign key relationship: `chats.user_id → users.id`
- Automatic timestamps: `created_at`
- Schema: question (Text), response (Text), SQL query tracking

#### Dependencies
- **Added**: `openai==2.9.0` - OpenAI API client library

#### Documentation
- Updated README.md with AI Chat section
- Updated README.md with Markdown Cleaner documentation  
- Added architecture diagram showing `services/` and `utils/` layers
- Added AI Chat usage examples in API documentation
- Updated technology stack table with OpenAI API
- Updated total endpoints: 20 → 23

#### Error Handling
- Transaction rollback on AI service failures
- Graceful error messages for OpenAI API issues
- Database connection timeout handling (SQLite locking prevention)

### 🎯 Why These Changes?

These improvements demonstrate:
- **AI Integration Skills** - Working with external APIs (OpenAI)
- **Text Processing** - Custom utility for data cleaning (95% coverage)
- **Service Architecture** - Proper separation of business logic
- **Production Readiness** - Error handling, database locking solutions
- **Clean Code** - Utilities, services, and comprehensive documentation

---

## [1.1.0] - 2025-12-15

### ✨ Added - User Profile Management

#### New Features
- **Full Name Field** - Required user identification (1-150 characters)
- **Smart Timestamp Separation** - Industry-standard audit trail implementation
- **Self-Service Profile Endpoint** - PUT `/api/v1/auth/me` for users to update their own data

#### Technical Improvements
- **Smart Timestamp System**:
  - `created_at` - Account creation timestamp (auto-generated on registration)
  - `updated_at` - Profile modification timestamp (manual update via CRUD)
  - `last_login_at` - Authentication tracking (direct SQL update)
  
- **ORM Side Effect Prevention**:
  - Removed `onupdate=func.now()` from `updated_at` field
  - Login updates `last_login_at` via `db.execute()` without triggering `updated_at`
  - Profile updates modify `updated_at` manually in CRUD base class

#### Database Changes
- Added `full_name` column to users table (String 150, not null)
- Added `is_deleted` column for soft delete pattern (Boolean, default False)
- Added `last_login_at` column for login tracking (DateTime, nullable)
- Modified `updated_at` to manual update only (removed auto onupdate)

#### API Changes
- **POST /api/v1/auth/register** - Now requires `full_name` field
- **PUT /api/v1/auth/me** - New endpoint for profile updates (NEW)
- **DELETE /api/v1/auth/me** - New endpoint for soft delete account - IRREVERSIBLE (NEW)
- **GET /api/v1/auth/me** - Now returns `full_name`, `last_login_at`, `updated_at`, `is_deleted`
- **All protected endpoints** - Now reject requests from deleted users (HTTP 410 Gone)

#### Code Architecture
- Updated `CRUDBase.update()` to automatically set `updated_at` timestamp
- Updated `CRUDUser.authenticate()` to use direct SQL for `last_login_at`
- Added app startup event to auto-create database tables
- Improved model and schema docstrings

#### Documentation
- Updated README.md with User Profile Management section
- Updated README.pt-BR.md with Portuguese documentation
- Added new screenshots (17-26) showing new features
- Total endpoints: 18 → 20 (Auth: 3 → 5)

### 📸 New Screenshots
- `17-register-with-fullname.png` - Registration with full_name field (required)
- `18-login-get-token.png` - Login process returning JWT token
- `19-auth-me-initial-timestamps.png` - Initial user data with timestamps
- `20-update-profile-put-me.png` - Profile update endpoint in action
- `21-auth-me-after-profile-update.png` - Shows updated_at populated
- `22-second-login.png` - Second login for timestamp comparison
- `23-auth-me-after-second-login.png` - Shows last_login_at updated

### 🎯 Why These Changes?

These improvements demonstrate:
- **Production-grade understanding** of ORM behavior and side effect prevention
- **Industry-standard patterns** for audit trails (used by GitHub, Google, Stripe)
- **RESTful API design** with token-based self-identification (`/me` endpoint)
- **Separation of concerns** between authentication tracking and profile updates
- **Clean code principles** with proper documentation and type safety

---

## [1.0.0] - 2025-12-01

### Initial Release

#### Features
- JWT-based authentication system
- Income and expense tracking
- Category management
- Financial reports and statistics
- Soft delete pattern
- Comprehensive API documentation (Swagger/ReDoc)
- Clean architecture with CRUD layer
- Type-safe schemas with Pydantic
- 18 RESTful endpoints

#### Tech Stack
- Python 3.11+
- FastAPI 0.123.7
- SQLAlchemy 2.0.44
- Pydantic 2.12.5
- JWT (python-jose)
- Bcrypt password hashing