# LangChain + Ollama + MCP Server

A powerful integration combining LangChain, Ollama, and a Model Control Plane (MCP) server with multiple intelligent tools.

## Features

- **LangChain Integration**: Leverages LangChain for building LLM applications
- **Ollama Support**: Uses local Ollama models for privacy and control
- **MCP Server**: Implements a Model Control Plane with **8 powerful tools**:
  - **Calculator**: Perform arithmetic operations (add, subtract, multiply, divide)
  - **Weather**: Get weather information for any city (mock data for demo)
  - **Gold Price**: Get live market gold prices in multiple currencies (USD, EUR, GBP, INR)
  - **Email**: Send emails with subject and body to recipients
  - **RAG (Retrieval-Augmented Generation)**: Upload documents and query them with semantic search
  - **Code Execution**: Execute Python code safely with output capture
  - **Web Scraping**: Extract text and links from web pages
  - **File Operations**: Read, write, list files and directories
- **Modern Web Interface**: Beautiful responsive UI with dark mode and toast notifications
- **Interactive CLI**: User-friendly command-line interface
- **Demo Mode**: Pre-configured examples to showcase capabilities
- **Interactive Visualizations**: Two-tab web interface showing step-by-step and animated flows
- **Document Intelligence**: RAG system with vector database for document search

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Main Application                     │
│                      (main.py)                          │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│            LangChain MCP Client                         │
│          (langchain_mcp_client.py)                      │
│                                                         │
│  ┌──────────────┐           ┌───────────────┐         │
│  │   LangChain  │◄─────────►│  MCP Wrapper  │         │
│  │   + Ollama   │           │               │         │
│  └──────────────┘           └───────┬───────┘         │
└────────────────────────────────────┼───────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────┐
│                   MCP Server                            │
│                (mcp_server.py)                          │
│                                                         │
│  ┌──────────┐  ┌────────┐  ┌─────────┐  ┌──────┐     │
│  │Calculator│  │Weather │  │GoldPrice│  │Email │     │
│  │   Tool   │  │  Tool  │  │  Tool   │  │ Tool │     │
│  └──────────┘  └────────┘  └─────────┘  └──────┘     │
│                                                         │
│  ┌──────────────────────────────────────────────┐     │
│  │          RAG Query Tool                       │     │
│  │      (Document Search & Retrieval)           │     │
│  └────────────────┬─────────────────────────────┘     │
└───────────────────┼───────────────────────────────────┘
                    │
                    ▼
         ┌────────────────────────┐
         │    RAG System          │
         │  (rag_system.py)       │
         │                        │
         │  • Document Upload     │
         │  • Text Extraction     │
         │  • Chunking            │
         │  • Vector Search       │
         └──────────┬─────────────┘
                    │
                    ▼
         ┌────────────────────────┐
         │     ChromaDB           │
         │  (Vector Database)     │
         └────────────────────────┘
```

## Prerequisites

1. **Python 3.9+**
2. **Ollama** installed and running
   - Install from: https://ollama.ai/
   - Pull a model: `ollama pull llama3.2`

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd MCP_Server_Mahendran
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Verify Ollama is running:
```bash
ollama list
```

## Usage

### Quick Start

Run the main application:
```bash
python main.py
```

Choose from:
1. **Interactive Mode**: Ask questions in real-time
2. **Demo Mode**: See pre-configured examples

### Interactive Mode

```bash
python main.py
# Select option 1

💬 You: What is 25 multiplied by 4?
# The assistant will use the calculator tool to compute the result

💬 You: What's the weather in Paris?
# The assistant will use the weather tool to fetch weather data

💬 You: Calculate 100 divided by 5
# Another calculation example
```

### Demo Mode

```bash
python main.py
# Select option 2
# Watch automated demonstrations of all features
```

### Direct Client Usage

You can also use the client directly in your own scripts:

```python
import asyncio
from langchain_mcp_client import LangChainMCPClient

async def main():
    client = LangChainMCPClient(model_name="llama3.2")

    try:
        await client.initialize()
        result = await client.process_query("What is 15 + 27?")
        print(result)
    finally:
        await client.cleanup()

asyncio.run(main())
```

## Project Structure

```
MCP_Server_Mahendran/
├── main.py                       # Main CLI application
├── langchain_mcp_client.py       # LangChain + Ollama + MCP integration
├── mcp_server.py                 # MCP server with 5 tools
├── rag_system.py                 # RAG system with ChromaDB
├── web_server.py                 # Flask web server
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
├── README.md                     # This file
├── RAG_README.md                 # Detailed RAG documentation
├── WEB_FRONTEND_README.md        # Web interface documentation
├── templates/
│   └── index.html                # Web frontend with RAG interface
├── visualization.html            # Interactive flow visualization
├── uploads/                      # Temporary upload directory
└── rag_db/                       # ChromaDB vector database
```

## MCP Tools

### Calculator Tool

Performs basic arithmetic operations.

**Parameters:**
- `operation`: "add", "subtract", "multiply", or "divide"
- `a`: First number
- `b`: Second number

**Example:**
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

### Weather Tool

Gets weather information for a city (mock data for demonstration).

**Parameters:**
- `city`: City name (required)
- `units`: "celsius" or "fahrenheit" (default: "celsius")

**Example:**
```json
{
  "tool": "weather",
  "arguments": {
    "city": "Paris",
    "units": "celsius"
  }
}
```

### Gold Price Tool

Gets live market gold prices in multiple currencies.

**Parameters:**
- `currency`: "USD", "EUR", "GBP", or "INR" (default: "USD")

**Example:**
```json
{
  "tool": "gold_price",
  "arguments": {
    "currency": "USD"
  }
}
```

**Sample Output:**
```
💰 Live Gold Price
────────────────────────────────
Price: USD 2,050.25 per troy ounce
24h Change: +0.75% (+USD 15.23)
Currency: USD
Updated: 2025-11-14 10:30:00

Market Status: 🟢 Open
```

### Email Tool

Send emails with subject and body to recipients (simulated for demo).

**Parameters:**
- `to`: Recipient email address (required)
- `subject`: Email subject line (required)
- `body`: Email body content (required)

**Example:**
```json
{
  "tool": "send_email",
  "arguments": {
    "to": "user@example.com",
    "subject": "Gold Price Alert",
    "body": "Current gold price is $2,050 per ounce"
  }
}
```

**Sample Output:**
```
📧 Email Sent Successfully!
────────────────────────────────
To: user@example.com
Subject: Gold Price Alert
Sent: 2025-11-14 10:30:00

Message Preview:
Current gold price is $2,050 per ounce

Status: ✅ Delivered
```

### RAG (Retrieval-Augmented Generation) Tool

Search uploaded documents using semantic similarity and natural language queries.

**Parameters:**
- `query`: The question or search query (required)
- `n_results`: Number of relevant documents to retrieve (optional, default: 3)

**Example:**
```json
{
  "tool": "rag_query",
  "arguments": {
    "query": "What does the document say about AI?",
    "n_results": 3
  }
}
```

**Sample Output:**
```
📚 RAG Query Results
────────────────────────────────
Query: What does the document say about AI?
Found: 3 relevant document(s)

Result #1 (Relevance: High)
────────────────────────────────
Artificial Intelligence (AI) is the simulation of human
intelligence processes by machines, especially computer systems...

Metadata: ai_guide.pdf | Length: 450 chars
────────────────────────────────
💡 Tip: You can use this information to answer your question!
```

**Features:**
- Upload documents via web interface (TXT, PDF, DOC, DOCX, JSON, MD, CSV)
- Semantic search using vector embeddings
- Automatic document chunking for better retrieval
- Relevance scoring and ranking
- ChromaDB vector database for efficient search

**For detailed RAG documentation, see [RAG_README.md](RAG_README.md)**

## Configuration

### Changing the Ollama Model

Edit the model name in `main.py` or `langchain_mcp_client.py`:

```python
client = LangChainMCPClient(model_name="llama3.2")  # Change to your preferred model
```

Available models (install with `ollama pull <model>`):
- llama3.2
- llama3.1
- mistral
- phi3
- And more...

### Adding Custom Tools

To add new tools to the MCP server:

1. Add the tool definition in `mcp_server.py` in the `list_tools()` method
2. Implement the tool logic as a new method
3. Add the tool handler in the `call_tool()` method

Example:

```python
# In list_tools()
Tool(
    name="my_custom_tool",
    description="Description of what it does",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param1"]
    }
)

# Implement the tool
async def my_custom_tool(self, arguments: dict) -> list[TextContent]:
    param1 = arguments.get("param1")
    # Your logic here
    return [TextContent(type="text", text=f"Result: {param1}")]

# In call_tool()
elif name == "my_custom_tool":
    return await self.my_custom_tool(arguments)
```

## Web Interface

### Starting the Web Server

Launch the beautiful web interface with RAG support:

```bash
python web_server.py
```

Then open your browser to: **http://localhost:5000**

### Web Interface Features

✅ **Interactive Chat**
- Real-time conversation with AI agent
- Beautiful gradient UI design
- Message history and timestamps

✅ **RAG Document Upload**
- Drag-and-drop file upload
- Support for 7 file formats (TXT, PDF, DOC, DOCX, JSON, MD, CSV)
- Real-time upload status
- Database statistics display

✅ **Tool Integration**
- Quick action buttons for all 5 tools
- Tool sidebar with examples
- One-click query templates

✅ **Session Management**
- Persistent conversations
- Clear conversation history
- Per-session state management

**For detailed web interface documentation, see [WEB_FRONTEND_README.md](WEB_FRONTEND_README.md)**

## Documentation

This project includes comprehensive documentation:

- **[README.md](README.md)** (this file) - Main project documentation
- **[RAG_README.md](RAG_README.md)** - Complete RAG system guide
  - Document upload and management
  - Query examples and best practices
  - API documentation
  - Troubleshooting guide
  - Advanced usage patterns
- **[WEB_FRONTEND_README.md](WEB_FRONTEND_README.md)** - Web interface guide
  - Quick start instructions
  - API endpoints
  - Customization options
  - Deployment guide

## Troubleshooting

### Ollama Connection Issues

If you get connection errors:
1. Make sure Ollama is running: `ollama serve`
2. Check if the model is installed: `ollama list`
3. Pull the model if needed: `ollama pull llama3.2`

### MCP Server Not Starting

1. Check if port is already in use
2. Verify Python version is 3.9+
3. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

### Import Errors

Make sure you're in the virtual environment:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### RAG Issues

**No documents found:**
1. Check if documents were uploaded: Click "🔄 Refresh Stats"
2. Verify file format is supported
3. Check server logs for processing errors

**Upload fails:**
1. Ensure file is under 16MB
2. Check file extension is supported
3. Verify disk space for `./rag_db` directory

**Low relevance results:**
1. Rephrase query using document terminology
2. Upload more relevant documents
3. Try requesting more results (n_results=5)

**For detailed RAG troubleshooting, see [RAG_README.md](RAG_README.md)**

## Development

### Running Tests

```bash
# Add your tests here
pytest tests/
```

### Code Style

Format code with black:
```bash
pip install black
black *.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use this project for any purpose.

## Acknowledgments

- [LangChain](https://python.langchain.com/) - Framework for LLM applications
- [Ollama](https://ollama.ai/) - Local LLM inference
- [MCP](https://modelcontextprotocol.io/) - Model Context Protocol
- [ChromaDB](https://www.trychroma.com/) - Vector database for RAG
- [Flask](https://flask.palletsprojects.com/) - Web framework for Python

## Support

For issues and questions:
- Open an issue on GitHub
- Check the troubleshooting section above
- Review Ollama documentation: https://github.com/ollama/ollama

---

**Made with ❤️ for the AI community**
