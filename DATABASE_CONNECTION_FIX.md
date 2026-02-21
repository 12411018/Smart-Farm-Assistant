# 🗄️ Database Connection Configuration

## Problem You're Facing

PostgreSQL user "meet" role is not permitted to log in.

**Error:**
```
FATAL: role "meet" is not permitted to log in
```

---

## ✅ Solution: Fix the PostgreSQL User

### On Windows (pgAdmin GUI)

1. **Open pgAdmin** (search in start menu)
2. **Navigate**: Servers → PostgreSQL 12 (or your version) → Login/Group Roles
3. **Right-click "meet"** → Properties
4. **Privileges tab:**
   - ✅ Check: "Can login?"
   - ✅ Check: "Superuser"
5. **Click Save**

**OR** in SQL (pgAdmin Query Tool):
```sql
ALTER ROLE meet WITH LOGIN;
ALTER ROLE meet WITH SUPERUSER;
```

---

## Alternative: Create New User (Recommended)

### If you don't want to fix "meet", create a new user:

**In pgAdmin Query Tool or Command Line:**
```sql
-- Create new user
CREATE ROLE smartfarm WITH LOGIN CREATEDB SUPERUSER;

-- Set password
ALTER ROLE smartfarm WITH PASSWORD 'SmartFarm123';

-- Create database owned by this user
CREATE DATABASE smart_farming OWNER smartfarm;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE smart_farming TO smartfarm;
```

**Update backend/.env:**
```ini
DATABASE_URL=postgresql+psycopg2://smartfarm:SmartFarm123@localhost:5432/smart_irrigation
```

---

## Option 3: Use Existing Admin User (postgres)

Most PostgreSQL installations have a `postgres` admin user:

**Update backend/.env:**
```ini
DATABASE_URL=postgresql+psycopg2://postgres:your_admin_password@localhost:5432/smart_irrigation
```

Replace `your_admin_password` with the password you set during PostgreSQL installation.

---

## Option 4: Skip PostgreSQL (Use SQLite)

If PostgreSQL is too complicated, use SQLite for development:

**Update backend/.env:**
```ini
DATABASE_URL=sqlite:///./smart_farming.db
```

This stores everything locally in a `.db` file (no server needed).

---

## Verify Your Connection

After fixing, test the connection:

### Command Line Test:
```bash
psql -U smartfarm -d smart_irrigation
# Or
psql -U postgres -d smart_irrigation  
# Or 
psql -U meet -d smart_irrigation
```

If it connects, you'll see:
```
smart_irrigation=>
```

Type `\q` to quit.

### Python Test:
```python
import psycopg2

try:
    conn = psycopg2.connect(
        "dbname=smart_irrigation user=smartfarm password=SmartFarm123 host=localhost"
    )
    print("✅ Connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
```

---

## After Fixing: Initialize Database

Once connection works:

```bash
cd backend
venv\Scripts\python init_db.py
```

Expected output:
```
✅ PostgreSQL engine created with connection pooling
✓ Database connection successful!
✓ All tables created/verified!
✅ DATABASE SETUP COMPLETE!
```

---

## Complete Working .env

Once you have working credentials:

```ini
# PostgreSQL Connection (choose one option)
DATABASE_URL=postgresql+psycopg2://smartfarm:SmartFarm123@localhost:5432/smart_irrigation

# OR PostgreSQL with postgres admin
# DATABASE_URL=postgresql+psycopg2://postgres:your_password@localhost:5432/smart_irrigation

# OR SQLite (no PostgreSQL needed)
# DATABASE_URL=sqlite:///./smart_farming.db

# JWT Secret (keep secure in production!)
SECRET_KEY=your-super-secret-key-change-in-production-value-12345

# Ollama
OLLAMA_ENDPOINT=http://localhost:11434/api/generate
OLLAMA_MODEL=mistral:latest

# Debug mode (set to False in production)
DEBUG=False
```

---

## Which Option is Easiest?

| Option | Difficulty | Speed | Best For |
|--------|-----------|-------|----------|
| Fix "meet" user | Easy | Fast | If user exists |
| Create new user | Easy | Fast | Clean setup |
| Use postgres | Medium | Fast | Works first time |
| Use SQLite | Easy | Very Fast | Testing without DB server |

---

## 🚀 Next Steps

1. **Choose one option above** and apply it
2. **Test the connection** with one of the test methods
3. **Run initialization**:
   ```bash
   cd backend && venv\Scripts\python init_db.py
   ```
4. **Start servers**:
   ```bash
   # Terminal 1
   cd backend && venv\Scripts\python -m uvicorn main:app --reload
   
   # Terminal 2  
   npm run dev
   ```
5. **Open** http://localhost:5173 and test sign up/sign in

---

## 📋 Troubleshooting

**"FATAL: unknown user"**
→ User doesn't exist. Use the `postgres` user instead.

**"FATAL: password authentication failed"**  
→ Wrong password. Check if password is correct.

**"could not connect to server"**
→ PostgreSQL not running. Start it:
- Windows: Start → Services → PostgreSQL → right-click → Start
- Mac: `brew services start postgresql`
- Linux: `sudo systemctl start postgresql`

**"database does not exist"**
→ Create database first:
```sql
CREATE DATABASE smart_irrigation;
```

---

## Tell me:

To help faster, provide:
1. Which PostgreSQL version? (`SELECT version();`)
2. Which user can you access? (postgres? meet? other?)
3. What password did you set for that user?

Then I can give exact commands for your setup! 🎯
