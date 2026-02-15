@echo off
REM AI Agent RAG System Startup Script for Windows

echo ╔════════════════════════════════════════════════════════════╗
echo ║   AI Agent RAG System - Environment Setup                  ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        exit /b 1
    )
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo ✓ Virtual environment activated
echo.

REM Check if requirements are installed
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        exit /b 1
    )
    echo ✓ Dependencies installed
) else (
    echo ✓ Dependencies already installed
)

echo.
REM Check .env file
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo ✓ .env file created
    echo.
    echo ⚠️  IMPORTANT: Edit .env file and add your OpenAI API key!
    echo   OPENAI_API_KEY=sk-your-key-here
) else (
    echo ✓ .env file exists
)

echo.
REM Create data directories
if not exist "data\uploads\" mkdir data\uploads
if not exist "data\vector_store\" mkdir data\vector_store
echo ✓ Data directories ready

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║   Setup Complete!                                          ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Next steps:
echo 1. Edit .env file and add your OpenAI API key
echo 2. Run tests: python tests/test_all.py
echo 3. Start server: python -m src.api.server
echo.
pause
