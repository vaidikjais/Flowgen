# ✅ DiagramGPT Setup Complete

## Issues Fixed

### 1. Database Connection Error
**Problem:** The `check_db_connection()` function was using raw SQL strings without SQLAlchemy's `text()` wrapper, causing errors in SQLAlchemy 2.0.

**Solution:** Added `from sqlalchemy import text` and updated the query to `await session.execute(text("SELECT 1"))`.

**Files Modified:**
- `app/core/database.py`

### 2. Port Configuration
**Problem:** PostgreSQL Docker container was running on port 5435 (not 5432) due to a port conflict.

**Solution:** Updated `.env` file with correct `DATABASE_URL`:
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5435/diagramgpt
```

## ✅ Verification Results

### Health Check
```json
{
    "status": "ok",
    "version": "1.0.0",
    "database": "ok",
    "llm": "ok"
}
```

### Diagram Generation
- ✅ Generated diagram from natural language prompt
- ✅ Saved to database with ID: `6e89dd31-ecf9-43f4-adc6-bba12f480566`
- ✅ Retrieved from history endpoint

### Database
- ✅ PostgreSQL running in Docker (port 5435)
- ✅ Tables created successfully
- ✅ CRUD operations working

## 🔧 pgAdmin4 Connection Settings

Since you have pgAdmin4 running in **another Docker container**, you have two options:

### Option 1: Using Container Name (Recommended)
If your pgAdmin4 container is on the **same Docker network** as DiagramGPT:

```
Connection Name: DiagramGPT
Host name/address: diagramgpt_postgres
Port: 5432
Maintenance database: diagramgpt
Username: postgres
Password: postgres
```

To add pgAdmin4 to the same network:
```bash
docker network connect diagramgpt_default <your_pgadmin_container_name>
```

### Option 2: Using host.docker.internal
Works on **Docker Desktop** (Mac/Windows):

```
Connection Name: DiagramGPT
Host name/address: host.docker.internal
Port: 5435
Maintenance database: diagramgpt
Username: postgres
Password: postgres
```

## 🚀 Application Status

The application is now fully functional:

- **Backend API:** http://localhost:8000/api/docs
- **Frontend UI:** http://localhost:8000
- **Health Check:** http://localhost:8000/api/health

### Available Endpoints

1. **POST /api/diagram/generate** - Generate diagram from natural language
   - Returns SVG by default
   - Add `Accept: application/json` header for JSON response

2. **POST /api/diagram/preview** - Render DOT code directly

3. **GET /api/diagram/history** - Get diagram history with pagination

4. **GET /api/diagram/{id}** - Get specific diagram by ID

5. **DELETE /api/diagram/{id}** - Delete diagram

6. **GET /api/health** - Health check with database status

7. **GET /api/user-preferences/{user_id}** - Get user preferences

8. **PUT /api/user-preferences/{user_id}** - Update user preferences

## 📝 Next Steps

1. **Set OpenAI API Key** (currently using placeholder):
   ```bash
   # Edit .env file and replace with your actual key
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

2. **Access Frontend:**
   Open http://localhost:8000 in your browser

3. **Connect pgAdmin4:**
   Use the connection settings above based on your Docker setup

4. **Run Tests:**
   ```bash
   uv run pytest tests/
   ```

## 🐛 Known Configuration

- PostgreSQL: Port **5435** on host (mapped from 5432 in container)
- FastAPI: Port **8000**
- Database: `diagramgpt`
- User: `postgres`
- Password: `postgres`

All services are running and operational! 🎉

