# Debug Guide - Ollama Connection Issues

## Problem
Getting error: "❌ Ollama is not running" even though Ollama is running on Windows.

## Debug Features Added

### 1. Comprehensive Logging
The system now has DEBUG-level logging that shows every step of the initialization process.

### 2. Test Endpoint
A new endpoint `/api/test/ollama` to directly test Ollama connectivity.

## How to Debug

### Step 1: Test Ollama Directly

**In PowerShell (Windows):**
```powershell
# Check if Ollama is running
curl http://localhost:11434/api/version

# Check available models
ollama list
```

**Expected Output:**
```json
{"version":"0.x.x"}
```

### Step 2: Start the Web Server with Debug Logs

**In PowerShell:**
```powershell
cd D:\MCP_Server_Mahendran
.\venv\Scripts\Activate.ps1
python web_server.py
```

Watch the console output carefully. You'll see detailed logs like:
```
INFO - Starting initialization...
INFO - Creating MCP server parameters...
INFO - Starting MCP client stdio connection...
INFO - Initializing Ollama LLM with model: llama3.2
ERROR - Initialization failed: [actual error message]
```

### Step 3: Test Ollama Endpoint from Browser

Open your browser and go to:
```
http://localhost:5000/api/test/ollama
```

This will tell you if the web server can reach Ollama:
- ✅ Success: `{"status": "success", "message": "Ollama is running"}`
- ❌ Failure: Connection error details

## Common Issues and Solutions

### Issue 1: Ollama on Windows, Server on Linux/WSL
**Problem:** Different localhost addresses

**Solution:** Configure Ollama to listen on all interfaces:
```powershell
# In PowerShell
$env:OLLAMA_HOST = "0.0.0.0:11434"
ollama serve
```

Then find your Windows IP:
```powershell
ipconfig
# Look for IPv4 Address (e.g., 192.168.x.x)
```

Update `langchain_mcp_client.py`:
```python
self.llm = ChatOllama(
    model=self.model_name,
    temperature=0,
    base_url="http://192.168.x.x:11434"  # Use your Windows IP
)
```

### Issue 2: llama3.2 Model Not Installed
**Check:**
```powershell
ollama list
```

**Install if missing:**
```powershell
ollama pull llama3.2
```

### Issue 3: Port Blocked by Firewall
**Windows Firewall:**
```powershell
# Allow port 11434 through firewall
netsh advfirewall firewall add rule name="Ollama" dir=in action=allow protocol=TCP localport=11434
```

### Issue 4: Running Everything on Windows
**Simplest Solution:**

1. Make sure Ollama is running:
   ```powershell
   ollama serve
   ```

2. In a new PowerShell window:
   ```powershell
   cd D:\MCP_Server_Mahendran
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python web_server.py
   ```

3. Open browser: `http://localhost:5000`

## Reading Debug Logs

### Log Levels:
- **INFO**: Normal operation steps
- **ERROR**: Something went wrong
- **DEBUG**: Very detailed information

### Key Log Messages:

**Successful Init:**
```
INFO - Starting initialization...
INFO - MCP stdio connection established
INFO - ClientSession created
INFO - Session initialized
INFO - Ollama LLM initialized successfully
INFO - Found 8 tools: calculator, weather, gold_price, send_email, rag_query, code_execute, web_scrape, file_operations
```

**Connection Error:**
```
ERROR - Initialization failed: [Errno 111] Connection refused
Full traceback: ...
```

**Model Error:**
```
ERROR - Initialization failed: llama3.2 not found
```

## Quick Fix Checklist

- [ ] Ollama is running (`ollama serve` in PowerShell)
- [ ] Model is installed (`ollama list` shows llama3.2)
- [ ] Ollama responds to `curl http://localhost:11434/api/version`
- [ ] Web server is running (`python web_server.py`)
- [ ] Test endpoint works: `http://localhost:5000/api/test/ollama`
- [ ] Check firewall settings
- [ ] If on Windows, run everything on Windows (not WSL/Linux)

## Environment Detection

The system is currently:
- **Code Location:** `/home/user/MCP_Server_Mahendran` (Linux environment)
- **Ollama Location:** Windows (based on PowerShell commands)

This cross-platform setup requires special configuration!

## Next Steps

1. Check the server logs when you refresh the page
2. Look for the ERROR lines
3. Test the `/api/test/ollama` endpoint
4. Share the log output for further diagnosis

## Contact

If issue persists, provide:
1. Full server console output
2. Result from `/api/test/ollama`
3. Output from `ollama list` (PowerShell)
4. Your OS setup (Windows version, WSL, etc.)
