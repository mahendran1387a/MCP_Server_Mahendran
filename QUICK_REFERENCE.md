# Quick Reference Guide

## Architecture Overview

```
┌──────────────┐
│     USER     │  Asks: "What is 25 times 4?"
└──────┬───────┘
       │
       ▼
┌────────────────────────────────────────────────────────┐
│  LANGCHAIN + OLLAMA (The Brain)                       │
│                                                        │
│  1. Receives question                                 │
│  2. Thinks: "I need calculator tool"                  │
│  3. Requests: calculator(multiply, 25, 4)             │
│  4. Receives: 100                                     │
│  5. Responds: "The answer is 100"                     │
└────────┬───────────────────────────────────────────────┘
         │                          ▲
         │  Tool Request            │  Tool Result
         ▼                          │
┌────────────────────────────────────────────────────────┐
│  MCP SERVER (The Toolbox)                             │
│                                                        │
│  ┌──────────────┐         ┌──────────────┐           │
│  │ Calculator   │         │   Weather    │           │
│  │ • add        │         │ • get_weather│           │
│  │ • subtract   │         │              │           │
│  │ • multiply   │         │              │           │
│  │ • divide     │         │              │           │
│  └──────────────┘         └──────────────┘           │
└────────────────────────────────────────────────────────┘
```

## File Purposes

| File | Purpose | Key Functions |
|------|---------|---------------|
| `main.py` | User interface | `interactive_mode()`, `demo_mode()` |
| `langchain_mcp_client.py` | Orchestrator | `process_query()`, `initialize()` |
| `mcp_server.py` | Tool provider | `calculator_tool()`, `weather_tool()` |

## Data Flow Example

**Query:** "What is 25 times 4?"

```
Step 1: User Input
  → main.py receives: "What is 25 times 4?"

Step 2: Send to LLM
  → langchain_mcp_client.py
  → Ollama (llama3.2 model)
  → LLM Response: {"tool": "calculator", "arguments": {"operation": "multiply", "a": 25, "b": 4}}

Step 3: Parse Tool Call
  → Extracted: tool="calculator", operation="multiply", a=25, b=4

Step 4: Call MCP Tool
  → MCP Client calls MCP Server
  → calculator_tool(multiply, 25, 4)
  → Returns: "Result: 25 multiply 4 = 100"

Step 5: Send Result to LLM
  → LLM receives: "Tool returned: Result: 25 multiply 4 = 100"
  → LLM Response: "The result is 100."

Step 6: Display to User
  → User sees: "The result is 100."
```

## Key Code Snippets

### How the LLM Knows About Tools

```python
# System prompt tells LLM about available tools
system_prompt = """
You have access to:
- calculator: add, subtract, multiply, divide
- weather: get weather for a city

To use a tool, respond with JSON:
{"tool": "tool_name", "arguments": {...}}
"""
```

### How Tools Are Called

```python
# 1. LLM decides to use calculator
response = llm.invoke(query)  # Returns: {"tool": "calculator", ...}

# 2. Extract tool call
tool_call = extract_tool_call(response)

# 3. Call MCP server
result = await mcp_wrapper.call_tool(
    tool_call["tool"],        # "calculator"
    tool_call["arguments"]    # {"operation": "multiply", "a": 25, "b": 4}
)

# 4. Send result back to LLM
llm.invoke(f"Tool returned: {result}")
```

### How MCP Server Handles Requests

```python
# Server receives tool call
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "calculator":
        operation = arguments["operation"]  # "multiply"
        a = arguments["a"]                  # 25
        b = arguments["b"]                  # 4

        result = a * b if operation == "multiply" else ...
        return f"Result: {result}"
```

## Communication Protocol

### MCP Protocol (stdio)

```
Client Process          Server Process
     │                       │
     │  Start Server         │
     │──────────────────────>│
     │                       │
     │  list_tools()         │
     │──────────────────────>│
     │  [calculator, weather]│
     │<──────────────────────│
     │                       │
     │  call_tool(calc, ...) │
     │──────────────────────>│
     │  Result: 100          │
     │<──────────────────────│
     │                       │
```

All communication happens via:
- **stdin**: Client sends JSON to server
- **stdout**: Server sends JSON back to client

## Adding a New Tool

### Step 1: Define Tool in MCP Server

```python
# In mcp_server.py → list_tools()
Tool(
    name="my_new_tool",
    description="What this tool does",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "..."}
        }
    }
)
```

### Step 2: Implement Tool Logic

```python
# In mcp_server.py
async def my_new_tool(self, arguments: dict):
    param1 = arguments.get("param1")
    # Your logic here
    result = do_something(param1)
    return [TextContent(type="text", text=f"Result: {result}")]
```

### Step 3: Register Handler

```python
# In mcp_server.py → call_tool()
elif name == "my_new_tool":
    return await self.my_new_tool(arguments)
```

### Step 4: Done!

The LLM will automatically discover and use your new tool!

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: mcp` | MCP not installed | `pip install mcp` |
| `ConnectionRefusedError` | Ollama not running | `ollama serve` |
| `Model not found` | Model not downloaded | `ollama pull llama3.2` |
| `AttributeError: 'tuple' object...` | Old buggy code | `git pull` to get fix |

## Important Concepts

### 1. Why Async?
```python
# Synchronous (blocking)
result = call_tool()  # Wait... wait... wait...

# Asynchronous (non-blocking)
result = await call_tool()  # Do other stuff while waiting
```

### 2. Why MCP?
- **Standardization**: All tools follow same pattern
- **Discoverability**: LLM can ask "what tools exist?"
- **Modularity**: Add/remove tools without changing LLM code

### 3. Why LangChain?
- **Abstraction**: Don't worry about LLM API details
- **Compatibility**: Works with many LLM providers
- **Utilities**: Message formatting, conversation history, etc.

### 4. Why Ollama?
- **Privacy**: Everything runs locally
- **Free**: No API costs
- **Fast**: No network latency

## Common Patterns

### Pattern 1: Simple Tool Call
```
User: "What is 5 + 3?"
LLM: "I'll use calculator"
Tool: Returns "8"
LLM: "The answer is 8"
```

### Pattern 2: Multi-Step
```
User: "What is 5 + 3, and weather in Paris?"
LLM: "I need calculator and weather tools"
Tool 1: Returns "8"
Tool 2: Returns "20°C, Sunny"
LLM: "5 + 3 = 8. Paris is 20°C and sunny."
```

### Pattern 3: No Tool Needed
```
User: "What is the capital of France?"
LLM: "I know this, no tool needed"
LLM: "The capital of France is Paris"
```

## Extending the System

### Add a Real Weather API

```python
# In mcp_server.py
async def weather_tool(self, arguments: dict):
    city = arguments.get("city")

    # Replace mock data with real API
    import aiohttp
    async with aiohttp.ClientSession() as session:
        url = f"https://api.weather.com/v1/{city}"
        async with session.get(url) as response:
            data = await response.json()
            return [TextContent(type="text", text=f"Weather: {data}")]
```

### Add a Database Tool

```python
Tool(
    name="database_query",
    description="Query the database",
    inputSchema={
        "properties": {
            "query": {"type": "string"}
        }
    }
)

async def database_query_tool(self, arguments: dict):
    import sqlite3
    query = arguments.get("query")
    # Execute query safely
    results = execute_query(query)
    return [TextContent(type="text", text=str(results))]
```

## Testing

### Test MCP Server Only
```bash
python test_mcp_server.py
```

### Test Full Integration
```bash
python main.py
# Choose option 2 (Demo mode)
```

### Test Individual Components
```python
# Test LLM only
from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama3.2")
response = llm.invoke("Hello")
print(response.content)
```

## Performance Tips

1. **Use smaller models for simple tasks**: `llama3.2` vs `llama3.1:70b`
2. **Cache tool descriptions**: Don't regenerate system prompt every time
3. **Limit iterations**: Set `max_iterations` to prevent infinite loops
4. **Use temperature=0**: For deterministic tool calling

## Security Notes

⚠️ **Important**:
- Never pass user input directly to shell commands
- Validate all tool arguments
- Sanitize database queries
- Rate limit API calls
- Don't expose sensitive data in tool responses

## Resources

- **Ollama Docs**: https://ollama.ai/
- **LangChain Docs**: https://python.langchain.com/
- **MCP Spec**: https://modelcontextprotocol.io/
- **Project README**: README.md
- **Detailed Guide**: HOW_IT_WORKS.md
