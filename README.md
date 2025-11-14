# LangChain + Ollama + MCP Server with Web Interface

A powerful integration combining LangChain, Ollama, and a Model Control Plane (MCP) server with 8 intelligent tools, a beautiful web interface, and RAG (Retrieval-Augmented Generation) capabilities.

## ✨ Features

- **🌐 Modern Web Interface**: Beautiful responsive UI with real-time chat and file upload
- **🤖 LangChain Integration**: Leverages LangChain for building LLM applications
- **🦙 Ollama Support**: Uses local Ollama models (llama3.2) for privacy and control
- **🛠️ MCP Server**: Implements a Model Control Plane with **8 powerful tools**:
  - 🔢 **Calculator**: Perform arithmetic operations (add, subtract, multiply, divide)
  - 🌤️ **Weather**: Get weather information for any city (mock data for demo)
  - 💰 **Gold Price**: Get live market gold prices in multiple currencies (USD, EUR, GBP, INR)
  - 📧 **Email**: Send emails with subject and body to recipients (simulated)
  - 📚 **RAG Query**: Upload documents and query them with semantic search
  - 💻 **Code Execution**: Execute Python code safely with output capture
  - 🌐 **Web Scraping**: Extract text and links from web pages
  - 📁 **File Operations**: Read, write, list files and directories
- **🔄 AsyncIO Architecture**: Background event loop with AsyncClientManager for handling concurrent requests
- **📊 RAG System**: Vector database with ChromaDB for document intelligence
- **📈 Interactive Visualizations**: Step-by-step and animated flowcharts showing system architecture
- **🪟 Windows Support**: Dedicated startup scripts and setup guide for Windows users

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                          Browser                                  │
│                   (http://localhost:5000)                         │
└──────────────────────────┬───────────────────────────────────────┘
                           │ HTTP/JSON
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Web Server (Flask)                           │
│                      (web_server.py)                              │
│                                                                   │
│  • Serves web interface (templates/index.html)                   │
│  • Manages sessions and routing                                  │
│  • Handles file uploads for RAG                                  │
│  • Opens ChromaDB (SINGLE connection - avoids locking)           │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                  AsyncClientManager                               │
│              (async_client_manager.py)                            │
│                                                                   │
│  • Background thread with persistent event loop                  │
│  • Manages MCP client lifecycle (create, query, cleanup)         │
│  • Thread-safe async execution with run_coroutine_threadsafe()   │
│  • Keeps clients alive across requests                           │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│              LangChain MCP Client                                 │
│           (langchain_mcp_client.py)                               │
│                                                                   │
│  ┌──────────────────┐              ┌──────────────────┐         │
│  │  ChatOllama      │              │  MCP Wrapper     │         │
│  │  (llama3.2)      │◄────────────►│  (Tool Calls)    │         │
│  └──────────────────┘              └────────┬─────────┘         │
└───────────────────────────────────────────────┼──────────────────┘
                                                │ stdio (subprocess)
                                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                       MCP Server                                  │
│                    (mcp_server.py)                                │
│                                                                   │
│  ⚠️  IMPORTANT: Does NOT open ChromaDB directly (avoids locking) │
│  📚 RAG queries use HTTP API → http://localhost:5000/api/rag/query│
│                                                                   │
│  ┌────────────┐  ┌──────────┐  ┌───────────┐  ┌────────────┐   │
│  │ Calculator │  │ Weather  │  │ Gold Price│  │   Email    │   │
│  └────────────┘  └──────────┘  └───────────┘  └────────────┘   │
│                                                                   │
│  ┌────────────┐  ┌──────────┐  ┌───────────┐  ┌────────────┐   │
│  │ RAG Query  │  │   Code   │  │    Web    │  │    File    │   │
│  │ (HTTP API) │  │ Executor │  │  Scraper  │  │ Operations │   │
│  └────────────┘  └──────────┘  └───────────┘  └────────────┘   │
└──────────────────────────────────────────────────────────────────┘
                           │
                           │ HTTP (RAG queries only)
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                     RAG System                                    │
│                   (rag_system.py)                                 │
│                                                                   │
│  • Document upload and chunking                                  │
│  • Vector embeddings with ChromaDB                               │
│  • Semantic search and relevance scoring                         │
│  • Accessed via web server (NO direct access from MCP server)    │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
                  ┌────────────────────┐
                  │     ChromaDB       │
                  │  (Vector Database) │
                  │   ./rag_db/        │
                  └────────────────────┘
```

### 🔑 Key Architecture Decisions

1. **Database Locking Solution**: Only the web server opens ChromaDB. The MCP server queries RAG via HTTP API to avoid file locking conflicts.

2. **AsyncIO Architecture**: AsyncClientManager runs in a background thread with its own event loop, allowing Flask (synchronous) to work seamlessly with MCP clients (asynchronous).

3. **Session Management**: Each browser session gets its own MCP client instance, maintained throughout the session lifecycle.

## 📋 Prerequisites

1. **Python 3.9+** (tested with Python 3.13)
2. **Ollama** installed and running
   - Install from: https://ollama.ai/
   - Pull the llama3.2 model: `ollama pull llama3.2`
3. **Git** (for cloning the repository)

## 🚀 Quick Start

### For Windows Users (Recommended)

1. **Clone the repository:**
```powershell
git clone <repository-url>
cd MCP_Server_Mahendran
```

2. **Run the startup script:**
```powershell
.\start_windows.bat
```

The script will automatically:
- ✅ Check if Ollama is running
- ✅ Verify llama3.2 model is installed
- ✅ Create virtual environment if needed
- ✅ Install all dependencies
- ✅ Start the web server

3. **Open your browser:**
```
http://localhost:5000
```

**For detailed Windows setup, see [WINDOWS_SETUP.md](WINDOWS_SETUP.md)**

### For Linux/Mac Users

1. **Clone the repository:**
```bash
git clone <repository-url>
cd MCP_Server_Mahendran
```

2. **Create and activate virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Start Ollama (if not running):**
```bash
ollama serve
```

5. **In another terminal, pull the model:**
```bash
ollama pull llama3.2
```

6. **Start the web server:**
```bash
python web_server.py
```

7. **Open your browser:**
```
http://localhost:5000
```

## 🧪 Testing Ollama Connectivity

If you encounter "Ollama is not running" errors, use the diagnostic script:

```powershell
python test_ollama.py
```

This script tests:
- ✅ Ollama API endpoint accessibility
- ✅ llama3.2 model availability
- ✅ Ollama generation capability
- ✅ LangChain integration

The script provides detailed error messages and fix suggestions.

**For troubleshooting, see [DEBUG_README.md](DEBUG_README.md)**

## 📁 Project Structure

```
MCP_Server_Mahendran/
├── 🌐 Web Interface
│   ├── web_server.py                    # Flask web server (main entry point)
│   ├── templates/index.html             # Beautiful responsive web UI
│   ├── start_windows.bat                # Windows startup script (batch)
│   └── start_windows.ps1                # Windows startup script (PowerShell)
│
├── 🤖 Core System
│   ├── langchain_mcp_client.py          # LangChain + Ollama + MCP integration
│   ├── mcp_server.py                    # MCP server with 8 tools
│   ├── async_client_manager.py          # Background async client manager
│   └── rag_system.py                    # RAG system with ChromaDB
│
├── 🧪 Testing & Diagnostics
│   ├── test_ollama.py                   # Ollama connectivity diagnostic
│   ├── test_mcp_server.py               # MCP server tests
│   └── main.py                          # CLI interface (alternative to web)
│
├── 📚 Documentation
│   ├── README.md                        # This file
│   ├── WINDOWS_SETUP.md                 # Windows setup guide
│   ├── DEBUG_README.md                  # Debugging guide
│   ├── RAG_README.md                    # RAG system documentation
│   ├── WEB_FRONTEND_README.md           # Web interface documentation
│   ├── HOW_IT_WORKS.md                  # Technical deep dive
│   ├── QUICK_REFERENCE.md               # Quick reference guide
│   └── ADVANCED_FEATURES.md             # Advanced usage
│
├── 🎨 Visualizations
│   ├── visualization.html               # Interactive architecture visualization
│   ├── tab1-step-by-step.js             # Step-by-step flow (12 steps)
│   └── tab2-animated.js                 # Animated flowchart (14 steps)
│
├── 📦 Other
│   ├── requirements.txt                 # Python dependencies
│   ├── .gitignore                       # Git ignore rules
│   ├── uploads/                         # Temporary upload directory
│   └── rag_db/                          # ChromaDB vector database
```

## 🛠️ Tools Documentation

### 🔢 Calculator Tool

Performs basic arithmetic operations.

**Parameters:**
- `operation`: "add", "subtract", "multiply", or "divide"
- `a`: First number
- `b`: Second number

**Example Query:**
```
"What is 25 multiplied by 4?"
```

**Tool Call:**
```json
{
  "tool": "calculator",
  "arguments": {
    "operation": "multiply",
    "a": 25,
    "b": 4
  }
}
```

### 🌤️ Weather Tool

Gets weather information for a city (mock data for demonstration).

**Parameters:**
- `city`: City name (required)
- `units`: "celsius" or "fahrenheit" (default: "celsius")

**Example Query:**
```
"What's the weather in Paris?"
```

### 💰 Gold Price Tool

Gets live market gold prices in multiple currencies.

**Parameters:**
- `currency`: "USD", "EUR", "GBP", or "INR" (default: "USD")

**Example Query:**
```
"What's the current gold price in USD?"
```

### 📧 Email Tool

Send emails (simulated for demonstration).

**Parameters:**
- `to`: Recipient email address
- `subject`: Email subject line
- `body`: Email body content

**Example Query:**
```
"Send an email to user@example.com with subject 'Gold Alert' saying the price is $2,050"
```

### 📚 RAG Query Tool

Search uploaded documents using semantic similarity.

**Parameters:**
- `query`: The question or search query (required)
- `n_results`: Number of relevant documents (optional, default: 3)

**Example Query:**
```
"What do my documents say about Python programming?"
```

**Features:**
- Upload documents via web interface (TXT, PDF, DOC, DOCX, JSON, MD, CSV)
- Semantic search using vector embeddings
- Automatic document chunking
- ChromaDB vector database
- **Uses HTTP API to avoid database locking**

**For detailed RAG documentation, see [RAG_README.md](RAG_README.md)**

### 💻 Code Execution Tool

Execute Python code safely with output capture.

**Parameters:**
- `code`: Python code to execute

**Example Query:**
```
"Execute this Python code: print('Hello World')"
```

**Security:** Runs in restricted environment with limited builtins.

### 🌐 Web Scraping Tool

Extract text and links from web pages.

**Parameters:**
- `url`: The URL to scrape
- `extract_links`: Whether to extract links (optional, default: false)

**Example Query:**
```
"Scrape the text from https://example.com"
```

### 📁 File Operations Tool

Read, write, list files and directories.

**Parameters:**
- `operation`: "read", "write", "list", or "exists"
- `path`: File or directory path
- `content`: Content to write (only for write operation)

**Example Query:**
```
"Read the file at ./example.txt"
```

## 🌐 Web Interface

### Features

✅ **Interactive Chat**
- Real-time conversation with AI agent
- Beautiful gradient UI design
- Message history and timestamps
- Session persistence

✅ **RAG Document Upload**
- Drag-and-drop file upload
- Support for 7 file formats (TXT, PDF, DOC, DOCX, JSON, MD, CSV)
- Real-time upload status
- Database statistics display

✅ **Tool Integration**
- Quick action buttons for all 8 tools
- Tool sidebar with examples
- One-click query templates

✅ **Status Indicators**
- Connection status (Ollama, MCP Client)
- Toast notifications for important events
- Real-time feedback

### API Endpoints

```
POST   /api/initialize        - Initialize MCP client session
POST   /api/query             - Send query to AI agent
POST   /api/rag/upload        - Upload document to RAG system
POST   /api/rag/query         - Query RAG database (used by MCP server)
GET    /api/rag/stats         - Get RAG database statistics
GET    /api/rag/documents     - Get all documents in RAG
POST   /api/rag/clear         - Clear RAG database
GET    /api/test/ollama       - Test Ollama connectivity
GET    /api/tools             - Get available tools
```

**For detailed API documentation, see [WEB_FRONTEND_README.md](WEB_FRONTEND_README.md)**

## ⚙️ Configuration

### Changing the Ollama Model

Edit `langchain_mcp_client.py` (line 90):

```python
self.llm = ChatOllama(
    model="llama3.2",  # Change to your preferred model
    temperature=0,
)
```

Available models (install with `ollama pull <model>`):
- `llama3.2` (recommended, 3B parameters)
- `llama3.1` (8B parameters)
- `mistral` (7B parameters)
- `phi3` (3.8B parameters)

### Changing Web Server Port

Edit `web_server.py` (last line):

```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change port here
```

## 🐛 Troubleshooting

### ❌ "Ollama is not running" Error

**Solution:**
1. Run the diagnostic script: `python test_ollama.py`
2. Check if Ollama is running: `ollama serve`
3. Verify model is installed: `ollama list`
4. Pull model if needed: `ollama pull llama3.2`

**For detailed troubleshooting, see [DEBUG_README.md](DEBUG_README.md) and [WINDOWS_SETUP.md](WINDOWS_SETUP.md)**

### ❌ "Connection closed" Error

This error was caused by ChromaDB database locking. **It has been fixed!**

**Solution:** The MCP server now uses HTTP API for RAG queries instead of direct database access. No action needed.

### ❌ Port 5000 Already in Use

**Windows:**
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
lsof -i :5000
kill -9 <PID>
```

Or change the port in `web_server.py`.

### ❌ Import Errors

Make sure you're in the virtual environment:
```bash
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\Activate.ps1  # Windows PowerShell
```

Then reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

## 📚 Documentation

Comprehensive documentation is available:

- **[README.md](README.md)** - Main documentation (this file)
- **[WINDOWS_SETUP.md](WINDOWS_SETUP.md)** - Windows setup and troubleshooting
- **[DEBUG_README.md](DEBUG_README.md)** - Debugging and diagnostics guide
- **[RAG_README.md](RAG_README.md)** - Complete RAG system documentation
- **[WEB_FRONTEND_README.md](WEB_FRONTEND_README.md)** - Web interface guide
- **[HOW_IT_WORKS.md](HOW_IT_WORKS.md)** - Technical deep dive
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick command reference
- **[ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)** - Advanced usage patterns

## 🎨 Visualization

Open `visualization.html` in your browser to see:

**Tab 1 - Step-by-Step Flow (12 Steps):**
1. Browser Opens Web Interface
2. Browser Initializes Session
3. AsyncClientManager Creates Client
4. MCP Client Connects to Server (NO ChromaDB access)
5. Initialize Ollama LLM
6. User Asks Question
7. Web Server Routes to Client
8. LLM Analyzes Question (8 tools available)
9. Extract Tool Call
10. MCP Server Executes Tool (RAG uses HTTP API)
11. LLM Formats Final Answer
12. Display Answer in Browser

**Tab 2 - Animated Flowchart (14 Steps):**
- Interactive animated diagram
- Shows data packets flowing through system
- Playback controls with speed adjustment
- Message log panel

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `python test_ollama.py`
5. Submit a pull request

## 📝 License

MIT License - feel free to use this project for any purpose.

## 🙏 Acknowledgments

- [LangChain](https://python.langchain.com/) - Framework for LLM applications
- [Ollama](https://ollama.ai/) - Local LLM inference
- [MCP](https://modelcontextprotocol.io/) - Model Context Protocol
- [ChromaDB](https://www.trychroma.com/) - Vector database for RAG
- [Flask](https://flask.palletsprojects.com/) - Web framework for Python

## 💬 Support

For issues and questions:
- Run diagnostic: `python test_ollama.py`
- Check [DEBUG_README.md](DEBUG_README.md)
- Check [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for Windows-specific issues
- Open an issue on GitHub

---

**🚀 Made with ❤️ for the AI community**

**✨ Key Features:** Web Interface • 8 Tools • RAG System • AsyncIO • ChromaDB • No Database Locking
