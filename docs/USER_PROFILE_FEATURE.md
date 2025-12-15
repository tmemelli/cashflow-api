# 🎯 User Profile Management - Feature Documentation

## Overview

This document details the User Profile Management feature implemented in version 1.1.0, which introduces smart timestamp separation for audit trails and self-service profile updates.

---

## 🧠 The Problem We Solved

### Initial Implementation (v1.0.0)
In the original version, the User model had only basic timestamps:
- `created_at` - Auto-generated on user creation
- `updated_at` - Auto-updated on ANY model change (using SQLAlchemy's `onupdate=func.now()`)

**Issue**: When a user logged in, we wanted to update `last_login_at`, but SQLAlchemy's `onupdate` would automatically trigger `updated_at` as well. This made it impossible to distinguish between:
- Profile updates (email, name changes)
- Authentication events (logins)

---

## ✅ The Solution

### Smart Timestamp Separation (v1.1.0)

We implemented three distinct timestamps with different update strategies:

| Timestamp | Purpose | Update Strategy | Triggered By |
|-----------|---------|----------------|--------------|
| `created_at` | Account creation | Auto (server_default) | User registration |
| `updated_at` | Profile modifications | Manual (CRUD layer) | Profile updates (PUT /me) |
| `last_login_at` | Login tracking | Direct SQL (db.execute) | Authentication (POST /login) |

---

## 🏗️ Technical Implementation

### 1. Model Changes (`app/models/user.py`)

**Before:**
```python
updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
```

**After:**
```python
updated_at = Column(DateTime(timezone=True), nullable=True)  # Manual update only
last_login_at = Column(DateTime(timezone=True), nullable=True)  # NEW
full_name = Column(String(150), nullable=False)  # NEW
```

### 2. CRUD Base Class (`app/crud/base.py`)

Added automatic `updated_at` handling in the update method:

```python
def update(self, db: Session, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
    # ... existing code ...
    
    # Update updated_at timestamp if model has this field
    if hasattr(db_obj, 'updated_at'):
        db_obj.updated_at = datetime.utcnow()
    
    db.add(db_obj)
    db.commit()
    # ...
```

### 3. Authentication Logic (`app/crud/crud_user.py`)

Login updates `last_login_at` without touching `updated_at`:

```python
def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
    user = self.get_by_email(db, email=email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    
    # Update last login timestamp using SQL directly
    # This avoids triggering the onupdate of updated_at field
    db.execute(
        update(User).where(User.id == user.id).values(last_login_at=datetime.utcnow())
    )
    db.commit()
    db.refresh(user)
    
    return user
```

**Key Point**: Using `db.execute()` with direct SQL bypasses SQLAlchemy's ORM tracking, preventing `onupdate` side effects.

### 4. New Endpoint (`app/api/v1/endpoints/auth.py`)

```python
@router.put("/me", response_model=User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Update current user profile."""
    user = crud_user.update(db, db_obj=current_user, obj_in=user_in)
    return user
```

**Key Point**: Uses token-based identification (no user ID in URL). The endpoint `/me` is RESTful standard used by GitHub, Twitter, Google APIs.

---

## 📊 Behavior Comparison

### Scenario 1: User Registration
```
Action: POST /api/v1/auth/register
Result:
  created_at: 2025-12-15T10:00:00  ✅
  updated_at: null                 ✅
  last_login_at: null              ✅
```

### Scenario 2: First Login
```
Action: POST /api/v1/auth/login
Result:
  created_at: 2025-12-15T10:00:00  (unchanged)
  updated_at: null                 ✅ NOT UPDATED
  last_login_at: 2025-12-15T10:05:00  ✅ UPDATED
```

### Scenario 3: Profile Update
```
Action: PUT /api/v1/auth/me (change full_name)
Result:
  created_at: 2025-12-15T10:00:00  (unchanged)
  updated_at: 2025-12-15T10:10:00  ✅ UPDATED
  last_login_at: 2025-12-15T10:05:00  (unchanged)
```

### Scenario 4: Second Login
```
Action: POST /api/v1/auth/login
Result:
  created_at: 2025-12-15T10:00:00  (unchanged)
  updated_at: 2025-12-15T10:10:00  ✅ NOT UPDATED
  last_login_at: 2025-12-15T10:15:00  ✅ UPDATED
```

---

## 🌍 Industry Standards

This pattern is used by major platforms:

| Platform | Pattern | Implementation |
|----------|---------|----------------|
| **GitHub** | Separate `updated_at` and `pushed_at` | Repository updates vs commit pushes |
| **Stripe** | Direct SQL for tracking fields | Payment logs don't update customer `updated_at` |
| **Shopify** | Event listeners for audit control | Only business logic triggers `updated_at` |
| **Twitter** | `last_activity_at` separate from profile | Tweets don't update profile timestamp |

---

## 🔍 Why This Matters for Recruiters

This implementation demonstrates:

1. **Deep ORM Understanding**
   - Knows when SQLAlchemy's automatic features cause problems
   - Understands the difference between ORM operations and direct SQL

2. **Production Experience**
   - Audit trails are critical in real-world systems
   - Compliance (GDPR, SOX) requires distinguishing user actions

3. **API Design Skills**
   - RESTful `/me` endpoint (industry standard)
   - Token-based self-identification (stateless, scalable)

4. **Problem-Solving Approach**
   - Identified side effect issue
   - Researched industry patterns
   - Implemented clean, maintainable solution

5. **Clean Code Principles**
   - Separation of concerns (login vs profile updates)
   - DRY (automated updated_at in base CRUD class)
   - Well-documented with clear docstrings

---

## 🧪 Testing the Feature

### Manual Testing Steps

1. **Register a user** (creates all timestamps)
2. **Login** (updates only last_login_at)
3. **Check /me** (verify updated_at still null)
4. **Update profile** (updates only updated_at)
5. **Check /me** (verify last_login_at unchanged)
6. **Login again** (updates only last_login_at)
7. **Check /me** (verify updated_at unchanged)

### Expected Results
- Each timestamp updates independently
- No side effects between operations
- Audit trail accurately reflects user actions

---

## 📚 References

- [SQLAlchemy ORM Events](https://docs.sqlalchemy.org/en/20/orm/events.html)
- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [RESTful API Design](https://restfulapi.net/)
- [Audit Trail Best Practices](https://www.imperva.com/learn/data-security/audit-trail/)

---

## 🚀 Future Enhancements

Potential improvements for v1.2.0:
- Add `profile_updated_by` field (for admin updates)
- Implement `last_activity_at` (any API interaction)
- Add `password_changed_at` for security tracking
- Create audit log table for all user actions
