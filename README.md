# diagram-gpt-fastapi 🎨

A production-ready FastAPI application that generates beautiful diagrams from natural language descriptions using OpenAI's LLM and Graphviz.

## 🌟 Features

- **Natural Language to Diagrams**: Describe what you want in plain English, get a professional diagram
- **Multiple Output Formats**: SVG (vector) and PNG (raster) support
- **Multiple Layout Engines**: Choose from dot, neato, fdp, sfdp, twopi, and circo
- **REST API**: Clean, well-documented endpoints
- **Modern Web UI**: Beautiful, responsive frontend included
- **Docker Ready**: Production-ready containerization
- **Type Safe**: Full type hints and Pydantic validation
- **Error Handling**: Comprehensive error handling and validation

## 📋 Prerequisites

### System Requirements

1. **Python 3.11+**
2. **Graphviz** (system binaries required)

### Install Graphviz

#### macOS
```bash
brew install graphviz
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install graphviz libgraphviz-dev
```

#### Windows
Download and install from [Graphviz Downloads](https://graphviz.org/download/)

After installation, ensure `dot` is in your PATH:
```bash
dot -V  # Should print Graphviz version
```

### OpenAI API Key

Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone repository
cd diagram-gpt-fastapi

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file or export environment variables:

```bash
# Required
export OPENAI_API_KEY="sk-your-api-key-here"

# Optional (with defaults)
export OPENAI_MODEL="gpt-4"                    # or gpt-3.5-turbo
export HOST="0.0.0.0"
export PORT="8000"
export MAX_PROMPT_LENGTH="2000"
export MAX_DOT_LENGTH="50000"
export MAX_TOKENS="1024"
export LOG_LEVEL="INFO"
```

### 3. Run the Application

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
python -m app.main
```

Visit [http://localhost:8000](http://localhost:8000) to use the web interface!

## 🐳 Docker Deployment

### Build and Run

```bash
# Build image
docker build -t diagram-gpt-fastapi .

# Run container
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY="sk-your-api-key-here" \
  -e OPENAI_MODEL="gpt-4" \
  --name diagram-gpt \
  diagram-gpt-fastapi
```

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  diagram-gpt:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_MODEL=gpt-4
      - LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with:
```bash
docker-compose up -d
```

## 📚 API Documentation

### Endpoints

#### 1. Generate Diagram from Prompt

**POST** `/api/diagram/generate`

Generate a diagram from natural language description.

**Request Body:**
```json
{
  "prompt": "Draw a flowchart for user signup with validation and error handling",
  "format": "svg",
  "layout": "dot"
}
```

**Parameters:**
- `prompt` (string, required): Natural language description of the diagram
- `format` (string, optional): Output format - "svg" or "png" (default: "svg")
- `layout` (string, optional): Graphviz engine - "dot", "neato", "fdp", "sfdp", "twopi", "circo" (default: "dot")

**Response:**
- Default: Image with appropriate `Content-Type` (image/svg+xml or image/png)
- With `Accept: application/json` header:
```json
{
  "diagram_dot": "digraph {...}",
  "image_base64": "PD94bWwgdmVyc2lvbj0...",
  "format": "svg"
}
```

**Example cURL:**
```bash
# Get SVG directly
curl -X POST http://localhost:8000/api/diagram/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Draw a flowchart for user login with username/password validation",
    "format": "svg"
  }' \
  --output diagram.svg

# Get PNG
curl -X POST http://localhost:8000/api/diagram/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a network diagram with router, firewall, and servers",
    "format": "png"
  }' \
  --output diagram.png

# Get JSON response
curl -X POST http://localhost:8000/api/diagram/generate \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "prompt": "Show a class diagram for e-commerce system",
    "format": "svg"
  }'
```

#### 2. Preview Diagram from DOT Code

**POST** `/api/diagram/preview`

Render a diagram from Graphviz DOT code directly (no LLM call).

**Request Body:**
```json
{
  "dot": "digraph { A -> B; B -> C; }",
  "format": "svg",
  "layout": "dot"
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:8000/api/diagram/preview \
  -H "Content-Type: application/json" \
  -d '{
    "dot": "digraph test { rankdir=LR; A -> B -> C; }",
    "format": "svg"
  }' \
  --output preview.svg
```

#### 3. Health Check

**GET** `/api/health`

Check if the service is running.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

**Example cURL:**
```bash
curl http://localhost:8000/api/health
```

### Interactive API Documentation

Once the server is running, visit:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🧪 Testing

```bash
# Install test dependencies (included in requirements.txt)
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run specific test file
pytest tests/test_render.py -v
```

## 🏗️ Project Structure

```
diagram-gpt-fastapi/
├── app/
│   ├── main.py              # FastAPI application and endpoints
│   ├── llm_client.py        # OpenAI LLM wrapper
│   ├── diagram_renderer.py  # Graphviz rendering functions
│   ├── schemas.py           # Pydantic models
│   └── config.py            # Configuration management
├── frontend/
│   └── index.html           # Web UI
├── tests/
│   └── test_render.py       # Unit tests
├── Dockerfile               # Docker configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔒 Production Considerations

### Security

1. **API Key Management**: Never commit API keys. Use environment variables or secrets management.
2. **Rate Limiting**: Implement rate limiting (e.g., using slowapi or nginx)
3. **Input Validation**: Already implemented with Pydantic; consider additional sanitization
4. **CORS**: Configure `CORS_ORIGINS` appropriately for your domain
5. **Authentication**: Add API key auth or OAuth for production use

### Performance

1. **Caching**: Cache frequent prompts using Redis/Memcached
2. **Task Queue**: Use Celery/RQ for async diagram generation
3. **Resource Limits**: Set timeouts and memory limits for Graphviz rendering
4. **Connection Pooling**: Use connection pools for database (if adding persistence)

### Monitoring

1. **Logging**: Configure structured logging (JSON format)
2. **Metrics**: Add Prometheus metrics for monitoring
3. **Tracing**: Implement distributed tracing (OpenTelemetry)
4. **Error Tracking**: Use Sentry or similar for error reporting

### Scalability

1. **Horizontal Scaling**: Run multiple instances behind a load balancer
2. **Database**: Add PostgreSQL/MongoDB for storing generated diagrams
3. **CDN**: Serve static frontend assets via CDN
4. **API Gateway**: Use Kong/Traefik for advanced routing and auth

## 🛠️ Development

### Code Style

```bash
# Format code
black app/ tests/

# Lint
flake8 app/ tests/

# Type checking
mypy app/
```

### Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | None |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4` |
| `OPENAI_BASE_URL` | OpenAI API base URL | `https://api.openai.com/v1` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `MAX_PROMPT_LENGTH` | Max characters in prompt | `2000` |
| `MAX_DOT_LENGTH` | Max characters in DOT code | `50000` |
| `MAX_TOKENS` | Max LLM response tokens | `1024` |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:8000,...` |
| `LOG_LEVEL` | Logging level | `INFO` |

## 📝 Example Prompts

Try these prompts to get started:

1. **Flowcharts**:
   - "Draw a flowchart for user authentication with login, validation, and error handling"
   - "Create a process flow for order fulfillment with inventory check and payment"

2. **Network Diagrams**:
   - "Show a network topology with router, firewall, web server, and database"
   - "Design a microservices architecture with API gateway, services, and database"

3. **Class Diagrams**:
   - "Create a class diagram for a blog system with User, Post, and Comment classes"
   - "Design an e-commerce class structure with Product, Order, and Customer"

4. **State Machines**:
   - "Draw a state machine for a traffic light system"
   - "Show order states from pending to delivered with transitions"

5. **Organizational Charts**:
   - "Create an org chart for a tech company with CEO, CTO, and engineering teams"
   - "Design a project team structure with PM, developers, and designers"

## 🐛 Troubleshooting

### Graphviz Not Found

**Error**: `ExecutableNotFound: failed to execute 'dot'`

**Solution**: Install Graphviz system package (see Prerequisites section)

### OpenAI API Errors

**Error**: `Failed to generate DOT code`

**Solution**: 
- Check your API key is valid
- Ensure you have API credits
- Check OpenAI service status

### Port Already in Use

**Error**: `Address already in use`

**Solution**: Change the PORT environment variable or kill the process using port 8000

### CORS Errors

**Error**: `Access-Control-Allow-Origin` errors in browser

**Solution**: Add your frontend domain to `CORS_ORIGINS` environment variable

## 📄 License

This project is provided as-is for educational and development purposes.

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Add authentication/authorization
- [ ] Implement caching layer
- [ ] Add diagram export to PDF
- [ ] Support for other LLM providers (Anthropic, Azure OpenAI)
- [ ] Diagram editing capabilities
- [ ] Template library
- [ ] Batch diagram generation
- [ ] Webhook support for async generation

## 📧 Support

For issues and questions, please check:
1. This README
2. API documentation at `/docs`
3. Test files for usage examples

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Graphviz](https://graphviz.org/) - Graph visualization software
- [OpenAI](https://openai.com/) - LLM provider
- [Python Graphviz](https://graphviz.readthedocs.io/) - Python wrapper

---

Built with ❤️ using FastAPI and Graphviz

