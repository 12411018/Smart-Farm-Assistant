# Quick Database Setup

## Your Current Situation

PostgreSQL user "meet" doesn't have login permissions. Here are three solutions:

---

## ✅ SOLUTION 1: Use Your Existing PostgreSQL User

If you have PostgreSQL with another user, update `backend/.env`:

```ini
DATABASE_URL=postgresql+psycopg2://YOUR_USERNAME:YOUR_PASSWORD@localhost:5432/YOUR_DATABASE
```

Replace:
- `YOUR_USERNAME` → your PostgreSQL username
- `YOUR_PASSWORD` → your password  
- `YOUR_DATABASE` → your database name

Then run:
```bash
cd backend && venv\Scripts\python init_db.py
```

---

## ✅ SOLUTION 2: Create New PostgreSQL User (Windows)

1. **Open pgAdmin** (installed with PostgreSQL)
2. **Right-click "Login/Group Roles"** → Create → Login/Group Role
3. **Fill in:**
   - Name: `farmuser`
   - Password: `SecurePass123`
   - Role tab: Check ✓ "Can login", ✓ "Superuser"
4. **Right-click Databases** → Create → Database
   - Name: `smart_farming`
   - Owner: `farmuser`
5. **Update backend/.env:**
   ```ini
   DATABASE_URL=postgresql+psycopg2://farmuser:SecurePass123@localhost:5432/smart_farming
   ```
6. **Run:**
   ```bash
   cd backend && venv\Scripts\python init_db.py
   ```

---

## ✅ SOLUTION 3: Use SQLite (Quick Development)

If you don't have PostgreSQL set up yet:

**Update `backend/.env`:**
```ini
DATABASE_URL=sqlite:///./smart_farming.db
```

**Run:**
```bash
cd backend && venv\Scripts\python init_db.py
```

This creates a local `smart_farming.db` file with all tables.

---

## 🚀 After Setup: Start Servers

### Terminal 1 - Backend:
```bash
cd backend
venv\Scripts\python -m uvicorn main:app --reload
```

### Terminal 2 - Frontend:
```bash
npm run dev
```

### Open Browser:
```
http://localhost:5173
```

---

## 🧪 Test Authentication

1. Click **"Sign In"** button (top right)
2. Click **"Sign Up"** tab
3. Register:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `MyPassword123` (uppercase + digits required)
4. Click **"Create Account"**
5. You're logged in! 🎉

---

## 📊 What Gets Created

All 6 tables with your data:

```
Database
├── users (authentication)
├── crop_plans (your crops)
├── crop_stages (growth phases)
├── irrigation_schedule (planned watering)
├── irrigation_logs (executed watering)
└── weather_logs (weather history)
```

---

## Need Help?

**PostgreSQL Connection Issues?**
- Check: `psql -U postgres -d smart_irrigation`
- Or: Use SQLite option above

**Which Should I Use?**
- `SQLite` → Quick testing
- `PostgreSQL` → Production / Multiple users / Complex queries

**PostgreSQL Not Installed?**
- Windows: https://www.postgresql.org/download/windows/
- Mac: `brew install postgresql`
- Linux: `sudo apt install postgresql`

---

## Tell Me

Provide your PostgreSQL details and I'll update the .env file for you:
- Username?
- Password?
- Host? (usually localhost)
- Database name?
