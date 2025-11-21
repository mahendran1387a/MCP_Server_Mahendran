# Quick Start - Get Running in 2 Minutes

## The Problem You're Facing

You're seeing this error:
```
mcp.shared.exceptions.McpError: Connection closed
```

This is a **Python 3.13 compatibility issue** with the MCP server subprocess communication.

## The Solution - Use the Web Interface

The web interface works better and is more stable. Here's how:

### 1. Make Sure Ollama is Running ✅

You already verified this works:
```powershell
ollama run llama3.2 "Say hello"
# Output: Hello!
```

### 2. Run the Web Server

```powershell
python web_server.py
```

### 3. Open Your Browser

Go to: **http://localhost:5000**

That's it! The web interface bypasses the subprocess issues.

## What You Can Do

Once the web interface is open:

1. **Chat with AI** - Type questions in the chat
2. **Upload Documents** - Use RAG to search your documents
3. **Use Tools** - Calculator, Weather, Gold Price, Email, etc.
4. **View Stats** - See how many documents are indexed

## Example Queries to Try

- "What is 25 * 48?"
- "What's the weather in London?"
- "What is the current gold price in USD?"
- "Calculate 100 / 5 and tell me the result"

## If Web Server Also Fails

If you see errors with the web server:

### Option 1: Check Python Version
```powershell
python --version
```

If it says **3.13**, that's the problem. Install **Python 3.11 or 3.12** instead.

### Option 2: Run Diagnostic
```powershell
python test_server_standalone.py
```

This will tell you exactly what's wrong.

### Option 3: Try Without MCP Server

The web server can work with just Ollama directly. Edit `web_server.py` if needed.

## Why This Happens

- Python 3.13 has changes to `asyncio` that break some subprocess communication
- The MCP SDK is still catching up with Python 3.13
- Windows has different subprocess handling than Linux/Mac
- The web server is more robust and handles these issues better

## Recommended Long-Term Fix

1. **Install Python 3.11 or 3.12**
   - Download from: https://www.python.org/downloads/
   - Choose version 3.11.x or 3.12.x

2. **Recreate Virtual Environment**
   ```powershell
   # Remove old venv
   Remove-Item -Recurse -Force venv

   # Create new with Python 3.11/3.12
   python3.11 -m venv venv

   # Activate
   .\venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Run Again**
   ```powershell
   python main.py
   # This should now work!
   ```

## Quick Reference

| Command | Purpose |
|---------|---------|
| `ollama list` | Check Ollama models |
| `python web_server.py` | Start web interface |
| `python main.py` | Start CLI (needs Python <3.13) |
| `python test_server_standalone.py` | Run diagnostics |
| `python --version` | Check Python version |

## Still Stuck?

1. Make sure Ollama is running: `ollama list`
2. Make sure you're in venv: You should see `(venv)` in prompt
3. Try web server first: `python web_server.py`
4. Check Python version: Should be 3.9-3.12, not 3.13

## Success Indicators

When it works, you'll see:

**Web Server:**
```
✓ RAG system initialized with X documents
Running on http://127.0.0.1:5000
```

**CLI Mode:**
```
✓ Initialized LangChain with Ollama model: llama3.2
✓ Connected to MCP server
✓ Available tools: calculator, weather, gold_price, ...

Ready! Ask me anything.
```

If you see these messages, you're good to go! 🎉
