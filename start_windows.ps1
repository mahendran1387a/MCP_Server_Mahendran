# Windows Startup Script for LangChain + Ollama + MCP Web Server
# Run this in PowerShell on Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LangChain + Ollama + MCP Web Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if Ollama is running
Write-Host "Step 1: Checking Ollama..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/version" -UseBasicParsing -TimeoutSec 2
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Ollama is running!" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Ollama is not running!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please start Ollama in another PowerShell window:" -ForegroundColor Yellow
    Write-Host "  ollama serve" -ForegroundColor White
    Write-Host ""
    Write-Host "Then run this script again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 2: Check if llama3.2 model is installed
Write-Host ""
Write-Host "Step 2: Checking for llama3.2 model..." -ForegroundColor Yellow
$models = ollama list 2>&1 | Out-String
if ($models -match "llama3.2") {
    Write-Host "✅ llama3.2 model is installed!" -ForegroundColor Green
} else {
    Write-Host "❌ llama3.2 model not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Installing llama3.2..." -ForegroundColor Yellow
    ollama pull llama3.2
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ llama3.2 model installed successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to install llama3.2 model" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Step 3: Check if in correct directory
Write-Host ""
Write-Host "Step 3: Checking directory..." -ForegroundColor Yellow
if (-not (Test-Path "web_server.py")) {
    Write-Host "❌ web_server.py not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run this script from the MCP_Server_Mahendran directory:" -ForegroundColor Yellow
    Write-Host "  cd D:\MCP_Server_Mahendran" -ForegroundColor White
    Write-Host "  .\start_windows.ps1" -ForegroundColor White
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✅ In correct directory!" -ForegroundColor Green

# Step 4: Check/activate virtual environment
Write-Host ""
Write-Host "Step 4: Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "✅ Virtual environment found!" -ForegroundColor Green
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "⚠️  Virtual environment not found. Creating one..." -ForegroundColor Yellow
    python -m venv venv
    & "venv\Scripts\Activate.ps1"
    Write-Host "✅ Virtual environment created and activated!" -ForegroundColor Green
}

# Step 5: Install/check dependencies
Write-Host ""
Write-Host "Step 5: Checking dependencies..." -ForegroundColor Yellow
Write-Host "Installing/updating requirements..." -ForegroundColor Yellow
pip install -q -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Warning: Some dependencies may have failed to install" -ForegroundColor Yellow
}

# Step 6: Start the web server
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Web Server..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Web Interface will be available at:" -ForegroundColor Yellow
Write-Host "  http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
python web_server.py
