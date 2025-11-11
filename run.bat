@echo off
REM Quick start script for diagram-gpt-fastapi (Windows)

echo 🚀 Starting diagram-gpt-fastapi...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo 📥 Installing dependencies...
    pip install -r requirements.txt
)

REM Check if Graphviz is installed
where dot >nul 2>nul
if errorlevel 1 (
    echo ⚠️  WARNING: Graphviz not found!
    echo    Please install Graphviz from: https://graphviz.org/download/
    echo.
)

REM Check if OpenAI API key is set
if "%OPENAI_API_KEY%"=="" (
    echo ⚠️  WARNING: OPENAI_API_KEY not set!
    echo    The app will use fallback mock implementation.
    echo    Set it with: set OPENAI_API_KEY=sk-your-key
    echo.
)

REM Start the server
echo 🌐 Starting server on http://localhost:8000
echo 📚 API docs: http://localhost:8000/docs
echo 🎨 Web UI: http://localhost:8000
echo.
echo Press Ctrl+C to stop
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

