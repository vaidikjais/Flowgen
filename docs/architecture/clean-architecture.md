# DiagramGPT Clean Architecture

## Overview

DiagramGPT follows Clean Architecture principles with clear separation of concerns across multiple layers. This document explains the architecture, design decisions, and how different components interact.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                      │
│                   (FastAPI Controllers)                     │
│  - diagram_controller.py                                    │
│  - user_preference_controller.py                            │
│  - health_controller.py                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    Business Logic Layer                     │
│                      (Services)                             │
│  - diagram_service.py (orchestration)                       │
│  - llm_service.py                                           │
│  - render_service.py                                        │
│  - cache_service.py                                         │
│  - user_preference_service.py                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Data Access Layer                         │
│                     (Repositories)                          │
│  - diagram_repository.py                                    │
│  - user_preference_repository.py                            │
│  - generation_log_repository.py                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Database Layer                            │
│                  (SQLModel/PostgreSQL)                      │
│  - diagram_model.py                                         │
│  - user_preference_model.py                                 │
│  - generation_log_model.py                                  │
└─────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### 1. Controllers (Presentation Layer)

**Location:** `app/controller/`

**Responsibility:** Handle HTTP requests and responses

- Request validation (via Pydantic schemas)
- Dependency injection
- HTTP status codes and error handling
- Response formatting
- **NO business logic** - delegate to services

**Example:**
```python
@router.post("/api/diagram/generate")
async def generate_diagram(
    request_data: GenerateDiagramRequest,
    service: DiagramService = Depends(get_diagram_service)
):
    image_bytes, dot_code, diagram_id = await service.generate_diagram(...)
    return Response(content=image_bytes, media_type="image/svg+xml")
```

### 2. Services (Business Logic Layer)

**Location:** `app/services/`

**Responsibility:** Implement core business logic and orchestration

- Business rule enforcement
- Transaction orchestration
- Coordination between multiple repositories
- External service integration (OpenAI, Graphviz)
- Error handling and logging
- **NO database queries** - delegate to repositories

**Key Services:**

- **DiagramService**: Main orchestrator for diagram generation workflow
- **LLMService**: Handles OpenAI API calls with retry logic
- **RenderService**: Graphviz rendering with validation
- **CacheService**: Manages diagram caching logic
- **UserPreferenceService**: User settings management

### 3. Repositories (Data Access Layer)

**Location:** `app/repository/`

**Responsibility:** Abstract database operations

- Raw database queries (SELECT, INSERT, UPDATE, DELETE)
- SQLAlchemy/SQLModel operations
- Query optimization
- **NO business logic** - pure data access

**Example:**
```python
async def find_by_prompt_hash(self, prompt_hash: str) -> Optional[Diagram]:
    statement = select(Diagram).where(Diagram.prompt_hash == prompt_hash)
    result = await self.db.execute(statement)
    return result.scalars().first()
```

### 4. Models (Database Schema Layer)

**Location:** `app/models/`

**Responsibility:** Define database table schemas

- SQLModel entities (ORM + Pydantic combined)
- Field definitions with types and constraints
- Relationships between tables
- Indexes for query optimization

### 5. Schemas (Validation Layer)

**Location:** `app/schemas/`

**Responsibility:** Request/response validation and serialization

- API request validation
- Response serialization
- Data transformation between layers
- Type safety

## Cross-Cutting Concerns

### Middleware

**Location:** `app/middleware/`

- **RequestIDMiddleware**: Adds unique ID to each request for tracking
- **ErrorHandlerMiddleware**: Global exception handling
- **CORSMiddleware**: Cross-origin resource sharing

### Utilities

**Location:** `app/utils/`

- **logger.py**: Structured logging with request context
- **hash_utils.py**: Prompt hashing for cache lookups

### Configuration

**Location:** `app/core/`

- **config.py**: Pydantic Settings v2 for type-safe configuration
- **database.py**: Async SQLModel engine and session management
- **exceptions.py**: Custom exception classes

## Data Flow: Diagram Generation

```
1. HTTP Request
   ↓
2. Controller (diagram_controller.py)
   - Validates request via Pydantic schema
   - Injects DiagramService dependency
   ↓
3. DiagramService (diagram_service.py)
   - Checks cache via CacheService
   - If not cached:
     a) Calls LLMService to generate DOT code
     b) Calls RenderService to create image
     c) Saves to database via DiagramRepository
     d) Logs metrics via GenerationLogRepository
   ↓
4. Repository Layer
   - Executes database queries
   - Returns entities
   ↓
5. Service Layer
   - Returns results to controller
   ↓
6. Controller
   - Formats HTTP response
   - Returns image or JSON
```

## Caching Strategy

DiagramGPT implements a smart caching system to reduce redundant LLM calls:

1. **Prompt Hashing**: SHA-256 hash of (prompt + format + layout)
2. **Cache Lookup**: Check database for existing diagram with same hash
3. **Cache Hit**: Return cached diagram (re-render or use stored image)
4. **Cache Miss**: Generate new diagram via LLM, save to cache

## Database Schema

### Diagrams Table
- Stores generated diagrams with DOT code and metadata
- Indexed on `prompt_hash` for fast cache lookups
- Indexed on `created_at` for history queries

### User Preferences Table
- Stores per-user settings (default format, layout, theme)
- Unique constraint on `user_id`

### Generation Logs Table
- Tracks LLM API usage for analytics
- Records token usage, latency, success/failure
- Indexed on `created_at` for time-series queries

## Error Handling

Layered error handling approach:

1. **Controller Level**: HTTP exceptions (400, 404, 500)
2. **Service Level**: Business logic exceptions (LLMError, RenderError)
3. **Repository Level**: Database exceptions (connection, constraint violations)
4. **Global Handler**: ErrorHandlerMiddleware catches all uncaught exceptions

## Testing Strategy

### Unit Tests (`tests/unit/`)
- Test individual components in isolation
- Mock external dependencies
- Focus on business logic correctness

### Integration Tests (`tests/integration/`)
- Test API endpoints end-to-end
- Use test database
- Verify HTTP responses and side effects

## Best Practices Implemented

1. **Dependency Injection**: All dependencies injected via FastAPI's Depends()
2. **Async All The Way**: Fully async/await for I/O operations
3. **Type Safety**: Comprehensive type hints throughout
4. **Logging**: Structured logging with request context
5. **Configuration**: Environment-based config with validation
6. **Separation of Concerns**: Each layer has single responsibility
7. **Testability**: Easy to test with dependency injection
8. **Documentation**: Comprehensive docstrings on all public APIs

## Future Enhancements

- Add rate limiting middleware
- Implement Redis cache layer for hot data
- Add authentication/authorization
- Implement event sourcing for audit trail
- Add WebSocket support for real-time previews
- Implement horizontal scaling with load balancer

