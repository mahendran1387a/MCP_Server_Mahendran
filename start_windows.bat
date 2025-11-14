@echo off
REM Windows Batch Script for LangChain + Ollama + MCP Web Server
REM Double-click this file to start the server

echo ========================================
echo LangChain + Ollama + MCP Web Server
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "web_server.py" (
    echo ERROR: web_server.py not found!
    echo.
    echo Please run this script from the MCP_Server_Mahendran directory
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

echo.
echo ========================================
echo Starting Web Server...
echo ========================================
echo.
echo Web Interface: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python web_server.py

pause
