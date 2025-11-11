# Quick Start Guide 🚀

Get up and running in 5 minutes!

## Prerequisites

1. **Python 3.11+**
2. **PostgreSQL** - Database for storing diagrams and caching
   ```bash
   # macOS
   brew install postgresql@15
   brew services start postgresql@15
   
   # Ubuntu/Debian
   sudo apt-get install postgresql-15
   
   # Windows: Download from https://www.postgresql.org/download/
   ```

3. **Graphviz** - For rendering diagrams
   ```bash
   # macOS
   brew install graphviz
   
   # Ubuntu/Debian
   sudo apt-get install graphviz
   
   # Windows: Download from https://graphviz.org/download/
   ```

4. **OpenAI API Key** - Get from [platform.openai.com](https://platform.openai.com/api-keys)

## Quick Start with Docker (Recommended)

```bash
# 1. Clone and navigate to project
cd diagramGPT

# 2. Set your API key in .env file
echo "OPENAI_API_KEY=sk-your-api-key-here" > .env

# 3. Start everything (PostgreSQL + App)
docker-compose up -d

# 4. Run database migrations
docker-compose exec diagram-gpt alembic upgrade head

# 5. (Optional) Seed sample data
docker-compose exec diagram-gpt python scripts/seed_data.py
```

## Quick Start (Unix/macOS) - Local Development

```bash
# 1. Create database
createdb diagramgpt

# 2. Set environment variables
export OPENAI_API_KEY="sk-your-api-key-here"
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/diagramgpt"

# 3. Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Run migrations
alembic upgrade head

# 5. (Optional) Seed sample data
python scripts/seed_data.py

# 6. Start server
uvicorn app.main:app --reload
```

## Quick Start (Windows) - Local Development

```cmd
# 1. Create database using pgAdmin or psql

# 2. Set environment variables
set OPENAI_API_KEY=sk-your-api-key-here
set DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/diagramgpt

# 3. Install dependencies
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 4. Run migrations
alembic upgrade head

# 5. (Optional) Seed sample data
python scripts\seed_data.py

# 6. Start server
uvicorn app.main:app --reload
```

## Manual Start

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY="sk-your-api-key-here"

# Run server
uvicorn app.main:app --reload
```

## Access the App

- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## Environment Variables

Create a `.env` file in the project root with these variables:

```bash
# Required
OPENAI_API_KEY=your-api-key-here
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/diagramgpt

# Optional (with defaults)
OPENAI_MODEL=gpt-4
PORT=8000
LOG_LEVEL=INFO
ENABLE_CACHE=true
CACHE_RETENTION_DAYS=30
```

## Database Management

```bash
# Create a new migration after model changes
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Seed sample data
python scripts/seed_data.py

# Cleanup old diagrams
python scripts/cleanup_old_diagrams.py
```

## Test the API

```bash
curl -X POST http://localhost:8000/api/diagram/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Draw a simple flowchart with start, process, and end nodes","format":"svg"}' \
  --output test.svg
```

## Example Prompts to Try

1. "Draw a flowchart for user login with validation"
2. "Create a network diagram with router, firewall, and servers"
3. "Show a class diagram for an e-commerce system"
4. "Design a state machine for a traffic light"

## New Features in v2.0 (Clean Architecture)

- ✅ **PostgreSQL Database**: Persistent storage for diagram history
- ✅ **Smart Caching**: Reduces redundant LLM calls
- ✅ **User Preferences**: Save default format and layout settings
- ✅ **Generation Logs**: Track API usage and performance
- ✅ **Clean Architecture**: Separated layers (Controller/Service/Repository)
- ✅ **Comprehensive Logging**: Structured logging with request tracking
- ✅ **Database Migrations**: Alembic for schema management
- ✅ **Enhanced Testing**: Unit and integration test suites

## API Endpoints

- `POST /api/diagram/generate` - Generate diagram from prompt
- `POST /api/diagram/preview` - Preview DOT code
- `GET /api/diagram/history` - Get diagram history
- `GET /api/diagram/{id}` - Get specific diagram
- `DELETE /api/diagram/{id}` - Delete diagram
- `GET /api/preferences` - Get user preferences
- `PUT /api/preferences` - Update user preferences
- `GET /health` - Simple health check
- `GET /api/health` - Detailed health check

## Troubleshooting

**"Database connection error"** → Ensure PostgreSQL is running and DATABASE_URL is correct

**"Graphviz not found"** → Install Graphviz system package (see Prerequisites)

**"OpenAI API error"** → Check your API key is set correctly

**"Port 8000 in use"** → Change port: `export PORT=8001`

**"Migration errors"** → Run `alembic upgrade head` to apply migrations

---

For detailed documentation, see:
- [README.md](README.md) - Complete project documentation
- [docs/architecture/clean-architecture.md](docs/architecture/clean-architecture.md) - Architecture overview

