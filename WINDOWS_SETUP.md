# Windows Setup Guide

## ⚡ Quick Start (Easiest Method)

### Step 1: Start Ollama
Open PowerShell and run:
```powershell
ollama serve
```
**Keep this window open!**

### Step 2: Start Web Server
Open a **NEW** PowerShell window and run:
```powershell
cd D:\MCP_Server_Mahendran
.\start_windows.bat
```

**OR** if you prefer PowerShell scripts:
```powershell
cd D:\MCP_Server_Mahendran
.\start_windows.ps1
```

### Step 3: Open Browser
Open your browser and go to:
```
http://localhost:5000
```

That's it! 🎉

---

## 📋 Prerequisites

Before running the server, make sure you have:

### 1. Python 3.10+
Check your version:
```powershell
python --version
```
Download from: https://www.python.org/downloads/

### 2. Ollama
Download and install from: https://ollama.com/download

After installation, verify:
```powershell
ollama --version
```

### 3. llama3.2 Model
Install the model:
```powershell
ollama pull llama3.2
```

Verify it's installed:
```powershell
ollama list
```

---

## 🔧 Manual Setup (If Scripts Don't Work)

### Step 1: Create Virtual Environment
```powershell
cd D:\MCP_Server_Mahendran
python -m venv venv
```

### Step 2: Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

**If you get an execution policy error:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Start Ollama (in a separate window)
```powershell
ollama serve
```

### Step 5: Start Web Server
```powershell
python web_server.py
```

### Step 6: Open Browser
```
http://localhost:5000
```

---

## 🐛 Troubleshooting

### Error: "Ollama is not running"

**Solution 0:** Run the diagnostic script (BEST OPTION)
```powershell
# Activate virtual environment first
.\venv\Scripts\Activate.ps1

# Run the diagnostic
python test_ollama.py
```

This will test:
- ✅ Ollama API connectivity
- ✅ llama3.2 model availability
- ✅ Ollama generation capability
- ✅ LangChain integration

The script will tell you exactly what's wrong and how to fix it!

**Solution 1:** Make sure Ollama is running
```powershell
# In one PowerShell window
ollama serve

# In another PowerShell window
curl http://localhost:11434/api/version
```

**Solution 2:** Check if port is in use
```powershell
netstat -ano | findstr :11434
```

If you see output, Ollama is running. If not, start it with `ollama serve`.

### Error: "llama3.2 not found"

Install the model:
```powershell
ollama pull llama3.2
```

Verify:
```powershell
ollama list
```

### Error: "Python not found"

Make sure Python is in your PATH:
1. Search for "Environment Variables" in Windows
2. Edit the PATH variable
3. Add Python installation directory (e.g., `C:\Python310\`)

### Error: "Port 5000 already in use"

Another application is using port 5000. Options:
1. Find and stop the other application
2. OR change the port in `web_server.py` (last line):
   ```python
   app.run(debug=True, host='0.0.0.0', port=5001)
   ```

### PowerShell Script Won't Run

If you get "execution policy" error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Or use the batch file instead:
```powershell
.\start_windows.bat
```

---

## 🎯 Features

Once running, you can:
- 🔢 **Calculator** - Perform arithmetic operations
- 🌤️ **Weather** - Get weather information
- 💰 **Gold Price** - Check live gold prices
- 📧 **Email** - Send emails
- 📚 **RAG** - Upload and search documents
- 💻 **Code Executor** - Run Python code
- 🌐 **Web Scraper** - Scrape websites
- 📁 **File Operations** - Read/write/list files
- 🎨 **Dark Mode** - Toggle between light and dark themes
- 📊 **Visualization** - View system architecture diagrams

---

## 🔥 Quick Test

After starting the server, try these quick actions:

1. Click "🔢 Calculate 25 × 4" - Should return 100
2. Click "🌤️ Weather in Paris" - Should return weather data
3. Toggle dark mode with the 🌙 button

---

## 📝 File Structure

```
D:\MCP_Server_Mahendran\
├── start_windows.ps1        ← PowerShell startup script
├── start_windows.bat        ← Batch startup script (double-click this!)
├── web_server.py            ← Main Flask server
├── langchain_mcp_client.py  ← LangChain + MCP client
├── mcp_server.py            ← MCP tool server
├── async_client_manager.py  ← Async client manager
├── rag_system.py            ← RAG system
├── requirements.txt         ← Python dependencies
├── templates/
│   └── index.html           ← Web UI
└── venv/                    ← Virtual environment (created automatically)
```

---

## 🌐 Accessing from Other Devices

To access from other devices on your network:

1. Find your Windows IP address:
   ```powershell
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., 192.168.1.100)

2. Make sure Windows Firewall allows port 5000:
   ```powershell
   netsh advfirewall firewall add rule name="Flask Server" dir=in action=allow protocol=TCP localport=5000
   ```

3. Access from other devices:
   ```
   http://192.168.1.100:5000
   ```

---

## 💡 Tips

1. **Keep Ollama Running**: Always have `ollama serve` running in a separate window
2. **Check Logs**: Watch the server console for detailed debug logs
3. **Refresh Browser**: If you get errors, refresh the browser page
4. **Dark Mode**: Your theme preference is saved in browser localStorage
5. **Document Upload**: Drag and drop files into the RAG upload zone

---

## 🆘 Still Having Issues?

If you're still experiencing problems:

1. Check the server console logs for detailed error messages
2. Visit `http://localhost:5000/api/test/ollama` to test Ollama connectivity
3. Make sure both PowerShell windows are open (one for Ollama, one for web server)
4. Try restarting both Ollama and the web server
5. Check the `DEBUG_README.md` file for advanced troubleshooting

---

## 📧 Support

For issues or questions:
- Check the logs in the PowerShell window
- Review `DEBUG_README.md` for detailed troubleshooting
- Ensure all prerequisites are installed and running

---

**Enjoy your AI assistant! 🚀**
