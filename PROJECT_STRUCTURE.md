# Project Structure

```
diagram-gpt-fastapi/
│
├── 📱 Core Application
│   ├── app/
│   │   ├── __init__.py           # Package initialization
│   │   ├── main.py               # FastAPI app + REST endpoints
│   │   ├── llm_client.py         # OpenAI LLM wrapper with retry logic
│   │   ├── diagram_renderer.py   # Graphviz rendering functions
│   │   ├── schemas.py            # Pydantic request/response models
│   │   └── config.py             # Environment configuration
│   │
│   ├── frontend/
│   │   └── index.html            # Beautiful web UI for diagram generation
│   │
│   └── tests/
│       └── test_render.py        # Unit tests for rendering
│
├── 📝 Documentation
│   ├── README.md                 # Comprehensive documentation
│   ├── QUICK_START.md            # 3-minute setup guide
│   └── PROJECT_STRUCTURE.md      # This file
│
├── 🐳 Docker & Deployment
│   ├── Dockerfile                # Production Docker image
│   ├── docker-compose.yml        # Docker Compose configuration
│   └── .dockerignore             # Docker build exclusions
│
├── 🛠️ Development Tools
│   ├── requirements.txt          # Python dependencies (pinned versions)
│   ├── .gitignore                # Git exclusions
│   ├── run.sh                    # Quick start script (Unix/macOS)
│   └── run.bat                   # Quick start script (Windows)
│
└── 📚 Examples
    └── examples/
        └── example_client.py     # Python client usage examples
```

## File Descriptions

### Core Application (`app/`)

#### `main.py` (FastAPI Application)
- 🎯 **Purpose**: Main FastAPI application with REST endpoints
- 🔌 **Endpoints**:
  - `POST /api/diagram/generate` - Generate from natural language
  - `POST /api/diagram/preview` - Render from DOT code
  - `GET /api/health` - Health check
- ✨ **Features**:
  - CORS middleware configured
  - Global exception handling
  - Async endpoint support
  - Static file serving (frontend)
  - Comprehensive error responses

#### `llm_client.py` (LLM Wrapper)
- 🎯 **Purpose**: OpenAI API wrapper for DOT generation
- ✨ **Features**:
  - Structured system prompt for DOT generation
  - Automatic retry with exponential backoff
  - Response sanitization (strips markdown)
  - Fallback mock implementation
  - Support for both openai library and requests

#### `diagram_renderer.py` (Graphviz Renderer)
- 🎯 **Purpose**: Render DOT code to images
- ✨ **Features**:
  - SVG and PNG output
  - Multiple layout engines (dot, neato, fdp, sfdp, twopi, circo)
  - Input validation
  - Timeout handling
  - Detailed error messages

#### `schemas.py` (Data Models)
- 🎯 **Purpose**: Pydantic models for validation
- 📦 **Models**:
  - `GenerateDiagramRequest`
  - `PreviewDiagramRequest`
  - `DiagramResponse`
  - `HealthResponse`
  - `ErrorResponse`

#### `config.py` (Configuration)
- 🎯 **Purpose**: Environment variable management
- ⚙️ **Settings**:
  - OpenAI API configuration
  - Server settings (host, port)
  - Security limits (max lengths, tokens)
  - CORS origins
  - Logging configuration

### Frontend (`frontend/`)

#### `index.html` (Web UI)
- 🎯 **Purpose**: Beautiful, responsive web interface
- ✨ **Features**:
  - Modern gradient design
  - Real-time diagram preview
  - Format selection (SVG/PNG)
  - Layout engine selector
  - Example prompt buttons
  - Error/success messaging
  - Responsive design (mobile-friendly)

### Tests (`tests/`)

#### `test_render.py` (Unit Tests)
- 🎯 **Purpose**: Test diagram rendering functionality
- ✅ **Coverage**:
  - DOT syntax validation
  - SVG/PNG rendering
  - Multiple layout engines
  - Error handling
  - MIME type helpers

### Documentation

#### `README.md`
- 📖 Complete project documentation
- 🚀 Installation instructions
- 🔧 Configuration guide
- 📚 API documentation with examples
- 🐳 Docker deployment guide
- 🔒 Production considerations

#### `QUICK_START.md`
- ⚡ 3-minute setup guide
- 🎯 Essential commands only
- 🧪 Quick test examples

### Docker Files

#### `Dockerfile`
- 🐳 Multi-stage build for optimization
- 🔒 Non-root user for security
- 🏥 Health check configured
- 📦 Installs Graphviz system package

#### `docker-compose.yml`
- 🚀 One-command deployment
- ⚙️ Environment configuration
- 🔄 Auto-restart policy
- 🏥 Health monitoring

### Scripts

#### `run.sh` / `run.bat`
- 🎯 **Purpose**: One-command startup
- ✨ **Features**:
  - Auto-creates virtual environment
  - Installs dependencies if needed
  - Checks for Graphviz installation
  - Validates OpenAI API key
  - Starts server with reload

### Examples

#### `example_client.py`
- 🎯 **Purpose**: Python client library example
- 📝 **Demonstrates**:
  - API client class
  - Generate diagram from prompt
  - Preview from DOT code
  - Get JSON response with metadata
  - Save images to files
  - Error handling

## Key Features by File

| Feature | File |
|---------|------|
| REST API Endpoints | `app/main.py` |
| OpenAI Integration | `app/llm_client.py` |
| Graphviz Rendering | `app/diagram_renderer.py` |
| Input Validation | `app/schemas.py` |
| Configuration | `app/config.py` |
| Web Interface | `frontend/index.html` |
| Unit Tests | `tests/test_render.py` |
| Docker Build | `Dockerfile` |
| Quick Deploy | `docker-compose.yml` |
| Easy Startup | `run.sh`, `run.bat` |
| Client Examples | `examples/example_client.py` |

## Technology Stack

- **Backend**: FastAPI 0.109.0
- **Server**: Uvicorn with asyncio
- **LLM**: OpenAI API (GPT-4/3.5)
- **Rendering**: Graphviz (Python wrapper + system binary)
- **Validation**: Pydantic 2.5.3
- **Testing**: pytest
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Containerization**: Docker

## Lines of Code

- **Backend**: ~800 lines (well-commented)
- **Frontend**: ~500 lines (HTML + CSS + JS)
- **Tests**: ~200 lines
- **Documentation**: ~1000 lines
- **Total**: ~2500 lines

## Next Steps

1. ✅ Set your `OPENAI_API_KEY`
2. ✅ Install Graphviz
3. ✅ Run `./run.sh` (or `run.bat` on Windows)
4. 🎨 Open http://localhost:8000
5. 🚀 Generate your first diagram!

---

**Built with ❤️ using FastAPI and Graphviz**

