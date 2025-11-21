# How to Run the MCP Server

## Quick Start Guide

### Prerequisites
1. **Python 3.9-3.12** (Python 3.13 has some compatibility issues)
2. **Ollama** installed and running
3. Virtual environment activated

### Step 1: Check Ollama is Running

```powershell
# Check Ollama service
ollama list

# Test Ollama
ollama run llama3.2 "Hello"
```

If Ollama is not running, start it:
```powershell
# Start Ollama service (usually starts automatically on Windows)
# If not, run the Ollama application from Start Menu
```

### Step 2: Install Dependencies

```powershell
# Make sure you're in the virtual environment
cd D:\MCP_Server_Mahendran
.\venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

### Step 3: Test the MCP Server

Before running the main application, test if the MCP server works:

```powershell
# Run the diagnostic script
python test_server_standalone.py
```

This will tell you if there are any issues with:
- Server imports
- RAG system initialization
- Server startup

### Step 4: Run the Application

**Option A: Command-Line Interface**
```powershell
python main.py
```

Choose option 1 for interactive mode or option 2 for demo mode.

**Option B: Web Interface** (Recommended)
```powershell
python web_server.py
```

Then open your browser to: **http://localhost:5000**

## Common Issues and Solutions

### Issue 1: "Connection closed" Error (MCP Server Won't Start)

**Symptoms:**
```
mcp.shared.exceptions.McpError: Connection closed
```

**Solution:**

This is usually caused by Python 3.13 compatibility issues. Try these fixes:

**Fix 1: Use Python 3.11 or 3.12**
```powershell
# Check your Python version
python --version

# If you have 3.13, install Python 3.11 or 3.12 from python.org
# Then recreate the virtual environment
python3.11 -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

**Fix 2: Run the Web Server Instead**
The web server has better compatibility:
```powershell
python web_server.py
```

**Fix 3: Use the Test Script**
Run the diagnostic to see what's failing:
```powershell
python test_server_standalone.py
```

### Issue 2: RAG System Errors

**Symptoms:**
```
Error initializing RAG system
```

**Solution:**
```powershell
# Reinstall ChromaDB
pip uninstall chromadb
pip install chromadb==1.3.4
```

### Issue 3: Ollama Connection Errors

**Symptoms:**
```
Failed to connect to Ollama
```

**Solution:**
```powershell
# 1. Check Ollama is running
ollama list

# 2. Test Ollama
curl http://localhost:11434/api/tags

# 3. Pull the model
ollama pull llama3.2

# 4. Restart Ollama service
# Close Ollama from system tray and restart it
```

### Issue 4: Import Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'X'
```

**Solution:**
```powershell
# Ensure virtual environment is activated
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue 5: Port Already in Use (Web Server)

**Symptoms:**
```
Address already in use: Port 5000
```

**Solution:**
```powershell
# Find what's using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or run on a different port by editing web_server.py
```

## Testing Individual Components

### Test 1: Test Ollama
```powershell
ollama run llama3.2 "What is 2+2?"
```

### Test 2: Test MCP Server Directly
```powershell
python mcp_server.py
# Press Ctrl+C after a few seconds. If no errors, it's working.
```

### Test 3: Test RAG System
```powershell
python -c "from rag_system import get_rag_system; rag = get_rag_system(); print('RAG OK')"
```

### Test 4: Test LangChain Client
```powershell
python langchain_mcp_client.py
```

## Recommended Setup

For the best experience:

1. **Use Python 3.11 or 3.12** (not 3.13)
2. **Use the Web Interface** (`python web_server.py`)
3. **Keep Ollama running** in the background
4. **Use a fresh virtual environment**

## Alternative: Simplified Startup

If you're having persistent issues, use this simplified approach:

```powershell
# 1. Ensure Ollama is running
ollama list

# 2. Start the web server (most stable option)
python web_server.py

# 3. Open browser to http://localhost:5000

# 4. Upload documents and ask questions through the web UI
```

## Getting Help

If issues persist:

1. Run the diagnostic: `python test_server_standalone.py`
2. Check Python version: `python --version`
3. Check installed packages: `pip list | Select-String "langchain|mcp|ollama"`
4. Review error logs carefully
5. Try the web interface instead of CLI

## Performance Tips

- First query is always slower (model loading)
- Web interface caches sessions for better performance
- RAG queries are faster after initial document indexing
- Use smaller models (llama3.2:1b) for faster responses

## Windows-Specific Notes

- Use PowerShell (not CMD)
- Ensure antivirus isn't blocking Python
- Run as Administrator if permission errors occur
- Check Windows Firewall if network errors occur
- Use absolute paths if relative paths fail
