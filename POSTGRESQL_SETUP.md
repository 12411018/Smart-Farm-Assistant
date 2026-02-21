# PostgreSQL Database Setup Guide

## Quick Setup Instructions

### Option 1: Use Your PostgreSQL Connection String Directly

If you already have a PostgreSQL database running, update the `.env` file in the `backend` folder:

```
# backend/.env
DATABASE_URL=postgresql+psycopg2://YOUR_USERNAME:YOUR_PASSWORD@YOUR_HOST:5432/YOUR_DATABASE
SECRET_KEY=your-super-secret-key-change-in-production
```

Replace with your actual values:
- `YOUR_USERNAME` - PostgreSQL username
- `YOUR_PASSWORD` - PostgreSQL password
- `YOUR_HOST` - Database host (localhost, IP, or cloud host)
- `YOUR_DATABASE` - Database name (e.g., smart_irrigation)

### Option 2: Create PostgreSQL User and Database (Linux/Mac)

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create user
CREATE USER meet WITH PASSWORD 'meet';

# Create database
CREATE DATABASE smart_irrigation OWNER meet;

# Grant permissions
ALTER USER meet WITH CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE smart_irrigation TO meet;

# Exit PostgreSQL
\q
```

### Option 3: Create PostgreSQL User and Database (Windows)

1. Open pgAdmin (comes with PostgreSQL)
2. Right-click "Servers" → "Create" → "Server"
3. Name it "Local" and connect
4. Right-click "Databases" → "Create" → "Database"
   - Name: `smart_irrigation`
5. Right-click "Login/Group Roles" → "Create" → "Login/Group Role"
   - Name: `meet`
   - Password: `meet`
   - Privileges tab: Check "Can login?" and "Superuser"

### Option 4: Using Cloud PostgreSQL (AWS RDS, Heroku, etc.)

Your cloud provider will give you a connection string like:
```
postgresql+psycopg2://user:password@hostname.region.rds.amazonaws.com:5432/dbname
```

Add this to `.env`:
```
DATABASE_URL=postgresql+psycopg2://user:password@hostname.region.rds.amazonaws.com:5432/dbname
```

### Option 5: Fall Back to SQLite (Development Only)

If PostgreSQL is not available, the system will automatically use SQLite:
```
# backend/.env
DATABASE_URL=sqlite:///./smart_farming.db
```

## Verify Connection

After setting up PostgreSQL and updating `.env`, run:

```bash
cd backend
venv\Scripts\python init_db.py
```

You should see:
```
✅ PostgreSQL engine created with connection pooling
✓ Database connection successful!
✓ All tables created/verified!
✅ DATABASE SETUP COMPLETE!
```

## Tables Created

The system will automatically create these tables:

1. **users** - User authentication and profiles
2. **crop_plans** - Master crop planning records
3. **crop_stages** - Growth stages for each crop
4. **irrigation_schedule** - Planned irrigation events
5. **irrigation_logs** - Executed irrigation records
6. **weather_logs** - Historical weather data

## Troubleshooting

### Connection refused
- Ensure PostgreSQL server is running
- Check host and port are correct
- Verify firewall allows connection

### Authentication failed
- Verify username and password
- Check user has login permissions
- Ensure database exists

### Database does not exist
- Create database manually (see Option 2 or 3)
- Or use SQLite fallback

## Next Steps

1. Start the backend:
   ```bash
   cd backend
   venv\Scripts\python -m uvicorn main:app --reload
   ```

2. Start the frontend:
   ```bash
   npm run dev
   ```

3. Access the app at: http://localhost:5173
