# How LangChain + Ollama + MCP Works

A comprehensive guide to understanding the architecture and flow of this integration.

---

## Table of Contents
1. [High-Level Architecture](#high-level-architecture)
2. [Components Explained](#components-explained)
3. [The Flow of a Query](#the-flow-of-a-query)
4. [Code Walkthrough](#code-walkthrough)
5. [Key Concepts](#key-concepts)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  USER                                                           │
│  "What is 25 times 4?"                                         │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  MAIN.PY (CLI Interface)                                       │
│  - Interactive or Demo mode                                    │
│  - Handles user input/output                                   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  LANGCHAIN_MCP_CLIENT.PY (Orchestrator)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  1. Receives query                                       │  │
│  │  2. Sends to Ollama LLM                                  │  │
│  │  3. Parses LLM response for tool calls                   │  │
│  │  4. Calls MCP tools if needed                            │  │
│  │  5. Sends tool results back to LLM                       │  │
│  │  6. Returns final answer to user                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────┐              ┌────────────────────┐      │
│  │  Ollama/LangChain│◄────────────►│  MCP Tool Wrapper  │      │
│  │                  │              │                    │      │
│  │  - llama3.2 model│              │  - list_tools()    │      │
│  │  - Generates     │              │  - call_tool()     │      │
│  │    responses     │              └─────────┬──────────┘      │
│  └──────────────────┘                        │                 │
└───────────────────────────────────────────────┼─────────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  MCP_SERVER.PY (Tool Provider)                                 │
│  ┌──────────────────────┐      ┌─────────────────────┐         │
│  │  Calculator Tool     │      │  Weather Tool       │         │
│  │  - add              │      │  - Get city weather │         │
│  │  - subtract         │      │  - Celsius/Fahrenheit│        │
│  │  - multiply         │      │  - Mock data        │         │
│  │  - divide           │      └─────────────────────┘         │
│  └──────────────────────┘                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Components Explained

### 1. **Ollama (Local LLM)**

**What it is:**
- A tool that runs Large Language Models (LLMs) locally on your computer
- Like ChatGPT, but running on YOUR machine instead of the cloud

**Why we use it:**
- Privacy: Your data never leaves your computer
- Free: No API costs
- Fast: No network latency

**In our code:**
```python
self.llm = ChatOllama(
    model=self.model_name,  # "llama3.2"
    temperature=0,          # Deterministic responses
)
```

**What it does:**
- Receives questions like "What is 25 times 4?"
- Understands it needs to use the calculator tool
- Generates responses in natural language

---

### 2. **LangChain**

**What it is:**
- A framework for building applications with LLMs
- Provides tools to connect LLMs with external functions/APIs

**Why we use it:**
- Easy integration with Ollama
- Handles message formatting
- Simplifies tool calling patterns

**In our code:**
```python
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage

response = self.llm.invoke(messages)  # LangChain handles the communication
```

---

### 3. **MCP (Model Context Protocol)**

**What it is:**
- A standardized protocol for LLMs to communicate with tools/services
- Think of it like a "USB standard" but for AI tools

**Why we use it:**
- Standard way to define tools
- Easy to add new tools
- Clear separation between LLM and tool logic

**Components:**
- **MCP Server** (`mcp_server.py`): Provides the tools
- **MCP Client** (in `langchain_mcp_client.py`): Uses the tools

**Tool Definition Example:**
```python
Tool(
    name="calculator",
    description="Perform basic arithmetic operations",
    inputSchema={
        "type": "object",
        "properties": {
            "operation": {"type": "string", "enum": ["add", "subtract", ...]},
            "a": {"type": "number"},
            "b": {"type": "number"}
        }
    }
)
```

---

## The Flow of a Query

Let's trace what happens when you ask: **"What is 25 times 4?"**

### Step 1: User Input → Main.py

```python
# main.py
query = input("\n💬 You: ")  # User types: "What is 25 times 4?"
await client.process_query(query)
```

### Step 2: Query → LangChain Client

```python
# langchain_mcp_client.py
async def process_query(self, query: str) -> str:
    # Build a message with system prompt and user query
    messages = [
        {"role": "system", "content": system_prompt},  # Describes available tools
        {"role": "user", "content": "What is 25 times 4?"}
    ]
```

### Step 3: Send to Ollama LLM

```python
# Ask the LLM what to do
response = self.llm.invoke(messages)
# LLM thinks: "I need to multiply 25 by 4, I should use the calculator tool"

# LLM Response:
# {"tool": "calculator", "arguments": {"operation": "multiply", "a": 25, "b": 4}}
```

**Why does the LLM know to use tools?**
- The system prompt tells it about available tools
- The LLM is trained to recognize when to use tools
- It formats the response as JSON when it needs a tool

### Step 4: Parse Tool Call

```python
# Extract the tool call from LLM response
tool_call = self._extract_tool_call(response_text)

# Extracted:
# {
#   "tool": "calculator",
#   "arguments": {"operation": "multiply", "a": 25, "b": 4}
# }
```

### Step 5: Call MCP Tool

```python
# Call the calculator tool via MCP
tool_result = await self.mcp_wrapper.call_tool(
    "calculator",
    {"operation": "multiply", "a": 25, "b": 4}
)

# MCP Server processes this:
# mcp_server.py → calculator_tool() → 25 * 4 = 100

# Tool Result: "Result: 25 multiply 4 = 100"
```

### Step 6: Send Result Back to LLM

```python
# Add tool result to conversation
messages.append({
    "role": "user",
    "content": "Tool 'calculator' returned: Result: 25 multiply 4 = 100"
})

# Ask LLM again to formulate a natural response
response = self.llm.invoke(messages)

# LLM Response: "The result of 25 multiplied by 4 is 100."
```

### Step 7: Return to User

```python
# Display the final answer
print(f"Final Answer: {response_text}")

# Output to user: "The result of 25 multiplied by 4 is 100."
```

---

## Code Walkthrough

### MCP Server (`mcp_server.py`)

**Purpose:** Provides tools that can be called by the LLM

```python
class MCPServer:
    def __init__(self):
        self.server = Server("langchain-ollama-mcp")
        self.setup_handlers()

    def setup_handlers(self):
        # Define what tools are available
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [Tool(name="calculator", ...), Tool(name="weather", ...)]

        # Handle tool execution
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any):
            if name == "calculator":
                return await self.calculator_tool(arguments)
            elif name == "weather":
                return await self.weather_tool(arguments)
```

**Calculator Tool Implementation:**
```python
async def calculator_tool(self, arguments: dict):
    operation = arguments.get("operation")  # "multiply"
    a = arguments.get("a")                  # 25
    b = arguments.get("b")                  # 4

    if operation == "multiply":
        result = a * b  # 100

    return [TextContent(type="text", text=f"Result: {a} {operation} {b} = {result}")]
```

### LangChain Client (`langchain_mcp_client.py`)

**Purpose:** Orchestrates communication between LLM and MCP tools

```python
class LangChainMCPClient:
    async def initialize(self):
        # 1. Connect to MCP server (stdio communication)
        self.stdio_context = stdio_client(server_params)
        self.read_stream, self.write_stream = await self.stdio_context.__aenter__()

        # 2. Create MCP session
        self.session = ClientSession(self.read_stream, self.write_stream)
        await self.session.__aenter__()
        await self.session.initialize()

        # 3. Wrap MCP tools
        self.mcp_wrapper = MCPToolWrapper(self.session)

        # 4. Initialize Ollama LLM
        self.llm = ChatOllama(model="llama3.2", temperature=0)
```

**Query Processing:**
```python
async def process_query(self, query: str):
    # Create system prompt with tool descriptions
    system_prompt = f"You have access to these tools: {tools_description}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]

    # Iterative loop: LLM → Tool → LLM → Answer
    while iteration < max_iterations:
        # Get LLM response
        response = self.llm.invoke(messages)

        # Check if LLM wants to use a tool
        tool_call = self._extract_tool_call(response.content)

        if tool_call:
            # Execute the tool
            result = await self.mcp_wrapper.call_tool(
                tool_call["tool"],
                tool_call["arguments"]
            )

            # Add result to conversation
            messages.append({"role": "user", "content": f"Tool returned: {result}"})
        else:
            # No tool needed, return the answer
            return response.content
```

### Main Application (`main.py`)

**Purpose:** User interface

```python
async def interactive_mode():
    client = LangChainMCPClient(model_name="llama3.2")
    await client.initialize()

    while True:
        query = input("\n💬 You: ")
        if query.lower() in ['quit', 'exit']:
            break

        await client.process_query(query)
```

---

## Key Concepts

### 1. **Async/Await**

**Why?** Because we're waiting for:
- Network I/O (talking to MCP server)
- LLM processing (Ollama generating responses)

```python
# Without async - blocks the entire program
result = wait_for_llm()  # Program freezes here

# With async - can do other things while waiting
result = await wait_for_llm()  # Can handle other tasks
```

### 2. **stdio (Standard Input/Output)**

The MCP server and client communicate via stdin/stdout:

```
Client                     Server
  |  --JSON Request-->      |
  |                         | (processes)
  |  <--JSON Response--     |
```

**Why stdio?**
- Simple: No network setup needed
- Secure: No ports to expose
- Universal: Works everywhere

### 3. **Context Managers (`async with` / `__aenter__`)**

Ensures proper cleanup:

```python
async with stdio_client(params) as (read, write):
    # Use the client
    pass
# Automatically cleaned up here

# Manual version (what we do):
context = stdio_client(params)
streams = await context.__aenter__()
try:
    # Use streams
finally:
    await context.__aexit__(None, None, None)  # Cleanup
```

### 4. **Tool Calling Pattern**

```
User Query
    ↓
LLM decides: "I need tool X with arguments Y"
    ↓
Tool X executes and returns result
    ↓
LLM receives result
    ↓
LLM formulates natural language response
    ↓
User sees answer
```

This is called **"Tool-Augmented Generation"** or **"Function Calling"**

### 5. **System Prompts**

We tell the LLM about available tools:

```python
system_prompt = """
You have access to these tools:
- calculator: Perform arithmetic (add, subtract, multiply, divide)
  Parameters: operation, a, b
- weather: Get weather for a city
  Parameters: city, units

When you need a tool, respond with:
{"tool": "tool_name", "arguments": {...}}
"""
```

This is how the LLM knows what tools exist and how to use them!

---

## Summary

**The Magic Formula:**

1. **User asks question**
2. **LLM understands the question** (via Ollama)
3. **LLM realizes it needs a tool** (because we told it about tools in system prompt)
4. **MCP Client calls the tool** (via standardized protocol)
5. **Tool executes and returns result** (MCP Server)
6. **LLM sees the result** (via conversation history)
7. **LLM generates natural language answer** (back to user)

**Key Technologies:**
- **Ollama**: Runs the LLM locally
- **LangChain**: Makes LLM integration easy
- **MCP**: Standardizes how tools are defined and called
- **Python asyncio**: Handles concurrent operations efficiently

**The Power:**
You can now easily add new tools (database queries, API calls, file operations, etc.) and the LLM will automatically know how to use them!

---

## Next Steps

1. **Add your own tool** - Try adding a "time" tool that returns current time
2. **Replace mock weather** - Integrate a real weather API
3. **Add more complex tools** - Database queries, web scraping, etc.
4. **Experiment with different models** - Try llama3.1, mistral, etc.

The beauty is: **Once you add a tool to the MCP server, the LLM automatically learns to use it!**
