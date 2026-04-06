# 🔧 Database Initialization Fix - User Management

## Issue
When trying to use the user creation endpoint (`/create`), you got this error:
```
sqlite3.OperationalError: no such table: users
```

## Root Cause
The database tables for user management (users, diagnoses, feedbacks, etc.) defined in `models.py` were not being initialized when the server started.

The application had two separate database systems:
1. **SQLModel tables** (disease files, predictions, knowledge base) - initialized by `create_db_and_tables()`
2. **SQLAlchemy tables** (users, diagnoses, etc.) - needed to be initialized by `init_db()`

## Solution Applied
Updated `main.py` lifespan function to call **both** database initialization functions:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()  # Initialize SQLModel tables
    init_db()              # Initialize SQLAlchemy tables (ADDED)
    print("Database initialized on startup")
    yield
    # Shutdown
    print("Application shutting down")
```

## What Changed
**File**: `c:\Elastic_architects\Backend\farmer_backend\main.py`

**Added import**:
```python
from dbhandler import get_db, init_db  # Added init_db
```

**Updated lifespan**:
- Added `init_db()` call to create SQLAlchemy tables

## Tables Now Created

### SQLModel Tables (for disease management)
- `diseasefilesmodel` - Disease file records
- `diseasepredictionmodel` - Prediction results
- `knowledgebasemodel` - Knowledge base entries

### SQLAlchemy Tables (for user management)
- `users` - User accounts
- `diagnosis_records` - Diagnosis history
- `admin_feedbacks` - Admin feedback

## Testing the Fix

### 1. Verify Database Initialization
```bash
python -c "from dbhandler import init_db; init_db(); print('OK')"
```

Expected output:
```
Database tables created successfully!
```

### 2. Test User Creation Endpoint

Start server:
```bash
python run_server.py
```

In another terminal, test user creation:
```bash
python test_user_endpoints.py
```

Or use curl:
```bash
curl -X POST http://localhost:8000/create \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Password123!",
    "firstname": "Test",
    "lastname": "User",
    "created_by": "admin",
    "user_role": "farmer"
  }'
```

Expected response:
```json
{
  "message": "User created"
}
```

### 3. Test Login Endpoint
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Password123!"
  }'
```

Expected response with token in header:
```json
{
  "message": "Login successful",
  "username": "testuser",
  "role": "farmer"
}
```

## Files Involved

1. **main.py** - Updated lifespan function
2. **dbhandler.py** - Contains `init_db()` function
3. **models.py** - Defines all SQLAlchemy table models
4. **repository/user_repository.py** - Implements user operations

## Database Files

The application uses two SQLite database files:

1. **farmer_backend.db** - SQLModel tables (disease management)
2. **plant_disease.db** - SQLAlchemy tables (user management)

Both are automatically created in the application root directory on first run.

## Endpoints Now Available

### User Management
- `POST /create` - Create new user
- `POST /login` - Login user (returns token)
- `GET /current_user` - Get current user info
- `GET /users` - Get all users (admin only)
- `DELETE /delete/{username}` - Delete user
- `POST /unlock/{username}` - Unlock user
- `POST /changepwd` - Change password

### Disease Management (existing)
- All `/api/disease-files/*` endpoints
- All `/api/disease-predictions/*` endpoints
- All `/api/knowledge-base/*` endpoints

## Troubleshooting

### Still getting "no such table" error?
1. Delete both database files:
   ```bash
   rm farmer_backend.db plant_disease.db
   ```
2. Restart server:
   ```bash
   python run_server.py
   ```

### Port already in use?
```bash
python -m uvicorn main:app --port 8001
```

### Import errors?
```bash
pip install --upgrade -r requirements.txt
```

## What's Next?

The backend now has both:
1. **Disease management system** - 40+ endpoints for tracking crops and predictions
2. **User management system** - 7 endpoints for user authentication and management

You can now:
- Create user accounts
- Login and get authentication tokens
- Track disease files with authenticated users
- Manage predictions and knowledge base

---

**Status**: ✅ Database initialization fixed and working
**Date**: November 27, 2025
**Fix Type**: Database initialization issue
