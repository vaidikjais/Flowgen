# Flowgen 🎨

**AI-Powered Diagram Generator**

Generate beautiful diagrams and Work Breakdown Structures from natural language using AI. Simple, fast, and production-ready.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## ✨ Features

### 🎯 Three Diagram Types

- **Flowcharts & Diagrams** - Network topologies, flowcharts, class diagrams, state machines (via Graphviz)
- **Work Breakdown Structures (WBS)** - Project hierarchies, task breakdowns, organizational charts (via PlantUML)
- **Gantt Charts** - Project timelines, task schedules, milestone tracking (via Mermaid)

### 🚀 Powerful Capabilities

- **Natural Language Input** - Describe in plain English, get professional diagrams
- **Multiple Output Formats** - SVG (vector) and PNG (raster)
- **Multiple Layout Engines** - 6 Graphviz engines for optimal diagram layout
- **REST API** - Clean, documented endpoints with interactive Swagger UI
- **Modern Web Interface** - Beautiful, responsive frontend with tabbed interface
- **Multi-LLM Support** - OpenAI, NVIDIA NIM, or Google Gemini
- **Type-Safe** - Full type hints and Pydantic validation
- **Production Ready** - Comprehensive error handling, logging, and monitoring

## 📋 Quick Start

### Prerequisites

**Required:**

1. **Python 3.11+**
2. **Graphviz** (system package)
3. **LLM API Key** (OpenAI, NVIDIA NIM, or Google Gemini)

**Install Graphviz:**

```bash
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz libgraphviz-dev

# Windows
# Download from https://graphviz.org/download/
# Add to PATH and verify: dot -V
```

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd Flowgen

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
# LLM Provider (choose one: openai, nvidia, or gemini)
LLM_PROVIDER=nvidia

# === OpenAI Configuration ===
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4

# === NVIDIA NIM Configuration ===
NVIDIA_API_KEY=nvapi-your-key-here
NVIDIA_MODEL=qwen/qwen3-next-80b-a3b-instruct
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1

# === Google Gemini Configuration ===
GOOGLE_API_KEY=your-gemini-key-here
GEMINI_MODEL=gemini-pro

# === Server Configuration (Optional) ===
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
DEBUG=false

# === Limits (Optional) ===
MAX_PROMPT_LENGTH=2000
MAX_DOT_LENGTH=50000
MAX_PLANTUML_LENGTH=50000
MAX_TOKENS=1024

# === PlantUML Server (Optional) ===
PLANTUML_SERVER_URL=https://www.plantuml.com/plantuml

# === CORS (Optional) ===
CORS_ORIGINS=http://localhost:8000,http://localhost:3000,http://127.0.0.1:8000
```

### Run the Application

```bash
# Start the server
python -m app.main

# Or with uvicorn for development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Access the application:**

- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🎨 Using the Web Interface

### 1. Generate Diagrams (Graphviz)

Click the **"📊 Diagram"** tab and try:

```
Draw a flowchart for user authentication with login, validation,
and error handling
```

```
Create a network diagram with router, firewall, web servers,
and database cluster
```

**Supports:** Flowcharts, network diagrams, class diagrams, state machines, organizational charts, and more.

### 2. Generate WBS (PlantUML)

Click the **"📋 WBS"** tab and try:

```
Create a WBS for building a mobile app with planning, design,
development, testing, and deployment phases
```

```
Create a WBS for an e-commerce platform with user management,
product catalog, shopping cart, and payment processing
```

**Supports:** Project hierarchies, work breakdowns, task decomposition, organizational structures.

### 3. Generate Gantt Charts (Mermaid)

Click the **"📅 Gantt"** tab and try:

```
Create a project timeline for a web application development with
planning phase in January, development in February-March,
testing in April, and deployment in May
```

```
Create a Gantt chart for a marketing campaign with research,
content creation, social media rollout, and performance analysis
```

**Supports:** Project timelines, task scheduling, dependencies, milestones, critical paths.

## 📚 API Reference

### Diagram Endpoints

#### Generate Diagram from Natural Language

```bash
POST /api/diagram/generate
```

**Request:**

```json
{
  "prompt": "Draw a flowchart for order processing",
  "format": "svg",
  "layout": "dot"
}
```

**Parameters:**

- `prompt` (string, required) - Natural language description
- `format` (string) - "svg" or "png" (default: "svg")
- `layout` (string) - "dot", "neato", "fdp", "sfdp", "twopi", "circo" (default: "dot")

**Response:** Image bytes (SVG/PNG) or JSON with base64 image

**Example:**

```bash
curl -X POST http://localhost:8000/api/diagram/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a login flowchart with validation",
    "format": "svg"
  }' \
  --output diagram.svg
```

#### Preview DOT Code

```bash
POST /api/diagram/preview
```

**Request:**

```json
{
  "dot": "digraph { A -> B -> C; }",
  "format": "svg",
  "layout": "dot"
}
```

### WBS Endpoints

#### Generate WBS from Natural Language

```bash
POST /api/wbs/generate
```

**Request:**

```json
{
  "prompt": "Create a WBS for software development project",
  "format": "svg"
}
```

**Parameters:**

- `prompt` (string, required) - Natural language description
- `format` (string) - "svg" or "png" (default: "svg")

**Response:** Image bytes (SVG/PNG) or JSON with base64 image

**Example:**

```bash
curl -X POST http://localhost:8000/api/wbs/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a WBS for website redesign project",
    "format": "svg"
  }' \
  --output wbs.svg
```

#### Preview PlantUML Code

```bash
POST /api/wbs/preview
```

**Request:**

```json
{
  "plantuml_code": "@startwbs\n* Project\n** Phase 1\n@endwbs",
  "format": "svg"
}
```

### Gantt Chart Endpoints

#### Generate Gantt Chart from Natural Language

```bash
POST /api/gantt/generate
```

**Request:**

```json
{
  "prompt": "Create a project timeline for web app development",
  "format": "svg"
}
```

**Parameters:**

- `prompt` (string, required) - Natural language description
- `format` (string) - "svg" or "png" (default: "svg")

**Response:** Image bytes (SVG/PNG) or JSON with base64 image

**Example:**

```bash
curl -X POST http://localhost:8000/api/gantt/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Project timeline with planning, development, and testing phases",
    "format": "svg"
  }' \
  --output gantt.svg
```

#### Preview Mermaid Gantt Code

```bash
POST /api/gantt/preview
```

**Request:**

```json
{
  "mermaid_code": "gantt\n    title Project\n    dateFormat YYYY-MM-DD\n    section Phase\n    Task :2025-01-01, 3d",
  "format": "svg"
}
```

### Health Check

```bash
GET /health
```

**Response:**

```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

## 🏗️ Project Structure

```
Flowgen/
├── app/
│   ├── controller/          # API endpoints
│   │   ├── diagram_controller.py
│   │   ├── wbs_controller.py
│   │   ├── gantt_controller.py
│   │   └── health_controller.py
│   ├── services/            # Business logic
│   │   ├── diagram_service.py
│   │   ├── wbs_service.py
│   │   ├── gantt_service.py
│   │   ├── llm_service.py
│   │   ├── render_service.py (Graphviz)
│   │   ├── plantuml_service.py (PlantUML)
│   │   └── mermaid_service.py (Mermaid)
│   ├── schemas/             # Pydantic models
│   │   ├── diagram_schema.py
│   │   ├── wbs_schema.py
│   │   ├── gantt_schema.py
│   │   └── common_schema.py
│   ├── middleware/          # Request/response middleware
│   ├── core/                # Configuration & exceptions
│   ├── utils/               # Logging utilities
│   └── main.py              # FastAPI application
├── frontend/
│   └── index.html           # Web interface
├── tests/
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project metadata
├── GANTT_INTEGRATION.md    # Gantt integration guide
└── README.md               # This file
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/unit/test_render_service.py -v
```

## 🔐 Environment Variables

| Variable              | Description                                   | Default                             | Required        |
| --------------------- | --------------------------------------------- | ----------------------------------- | --------------- |
| `LLM_PROVIDER`        | LLM provider: `openai`, `nvidia`, or `gemini` | `openai`                            | ✅              |
| `OPENAI_API_KEY`      | OpenAI API key                                | -                                   | If using OpenAI |
| `OPENAI_MODEL`        | OpenAI model name                             | `gpt-4`                             | If using OpenAI |
| `NVIDIA_API_KEY`      | NVIDIA NIM API key                            | -                                   | If using NVIDIA |
| `NVIDIA_MODEL`        | NVIDIA model name                             | `qwen/qwen3-next-80b-a3b-instruct`  | If using NVIDIA |
| `GOOGLE_API_KEY`      | Google Gemini API key                         | -                                   | If using Gemini |
| `GEMINI_MODEL`        | Gemini model name                             | `gemini-pro`                        | If using Gemini |
| `HOST`                | Server host                                   | `0.0.0.0`                           | ❌              |
| `PORT`                | Server port                                   | `8000`                              | ❌              |
| `LOG_LEVEL`           | Logging level                                 | `INFO`                              | ❌              |
| `MAX_PROMPT_LENGTH`   | Max prompt characters                         | `2000`                              | ❌              |
| `MAX_DOT_LENGTH`      | Max DOT code characters                       | `50000`                             | ❌              |
| `MAX_PLANTUML_LENGTH` | Max PlantUML code characters                  | `50000`                             | ❌              |
| `MAX_TOKENS`          | Max LLM tokens                                | `1024`                              | ❌              |
| `PLANTUML_SERVER_URL` | PlantUML server URL                           | `https://www.plantuml.com/plantuml` | ❌              |
| `CORS_ORIGINS`        | Allowed CORS origins (comma-separated)        | `http://localhost:8000,...`         | ❌              |

## 💡 Example Prompts

### Diagrams (Graphviz)

**Flowcharts:**

- "Draw a flowchart for user registration with email verification"
- "Create a decision tree for customer support ticket routing"

**Network Diagrams:**

- "Show a cloud architecture with load balancer, app servers, and Redis cache"
- "Design a microservices topology with API gateway and message queue"

**Class Diagrams:**

- "Create a class diagram for a blogging platform with User, Post, and Comment"
- "Design an e-commerce system with Product, Order, and Payment classes"

**State Machines:**

- "Draw a state machine for order lifecycle from cart to delivered"
- "Show payment states with approval and rejection flows"

### WBS (PlantUML)

**Software Projects:**

- "Create a WBS for developing a SaaS application with MVP and scaling phases"
- "Break down a mobile app project with iOS and Android development"

**Business Projects:**

- "Create a WBS for launching a marketing campaign across multiple channels"
- "Design a product launch breakdown with market research, development, and go-to-market"

**Research Projects:**

- "Create a WBS for a PhD research project with literature review, experiments, and thesis"
- "Break down a data science project with data collection, analysis, and visualization"

### Gantt Charts (Mermaid)

**Software Projects:**

- "Create a timeline for building a web app with 2 weeks planning, 6 weeks development, 2 weeks testing"
- "Schedule a mobile app release with parallel iOS and Android development tracks"

**Marketing Campaigns:**

- "Create a 3-month campaign timeline with research, content creation, launch, and analysis phases"
- "Schedule a product launch with pre-launch activities, launch day, and post-launch monitoring"

**Event Planning:**

- "Create a timeline for organizing a conference with 6 months of planning and preparation"
- "Schedule a wedding with venue booking, vendor selection, and final preparations"

## 🐛 Troubleshooting

### Graphviz Not Found

**Error:** `ExecutableNotFound: failed to execute 'dot'`

**Solution:** Install Graphviz system package and ensure it's in your PATH

### PlantUML Connection Failed

**Error:** `Failed to connect to PlantUML server`

**Solution:**

- Check your internet connection
- Verify PlantUML server is accessible: https://www.plantuml.com/plantuml
- Try changing `PLANTUML_SERVER_URL` in .env
- Check firewall/proxy settings

### LLM API Errors

**Error:** `Failed to generate code`

**Solution:**

- Verify API key is correct and active
- Check you have API credits/access
- Ensure `LLM_PROVIDER` matches your API key (openai/nvidia/gemini)
- Verify model name is valid for your provider
- Check provider service status

### Port Already in Use

**Error:** `Address already in use`

**Solution:**

```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Change port in .env
PORT=8080
```

## 🚀 Production Deployment

### Security Best Practices

1. **Never commit API keys** - Use environment variables or secrets management
2. **Enable authentication** - Add API keys or OAuth for production
3. **Configure CORS** - Restrict `CORS_ORIGINS` to your domains
4. **Rate limiting** - Implement request rate limits
5. **Input validation** - Already included via Pydantic

### Performance Optimization

1. **Caching** - Cache frequent prompts/diagrams with Redis
2. **Load balancing** - Run multiple instances behind nginx/HAProxy
3. **Resource limits** - Set memory/CPU limits for rendering
4. **Monitoring** - Add Prometheus metrics and health checks

### Monitoring & Logging

1. **Structured logging** - Configure JSON logging format
2. **Error tracking** - Integrate Sentry or similar
3. **Metrics** - Track response times, success rates, LLM token usage
4. **Health checks** - Use `/health` endpoint for uptime monitoring

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Additional diagram types (sequence diagrams, ER diagrams)
- More LLM providers (Anthropic Claude, Azure OpenAI)
- Diagram editing and refinement
- Template library
- Batch generation
- Export to additional formats (PDF, DOC)
- Caching layer
- Database persistence

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Graphviz](https://graphviz.org/) - Graph visualization software
- [PlantUML](https://plantuml.com/) - UML diagram tool
- [LangChain](https://python.langchain.com/) - LLM framework
- OpenAI, NVIDIA, Google - LLM providers

---

**Built with ❤️ by developers, for developers**

For questions or issues, please check the [API documentation](http://localhost:8000/docs) or create an issue on GitHub.
