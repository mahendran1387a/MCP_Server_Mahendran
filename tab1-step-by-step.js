// Tab 1: Step-by-Step Flow JavaScript - Updated for Current Architecture

const queries1 = {
    calculator: {
        question: "What is 25 × 4?",
        toolNeeded: "calculator",
        toolArgs: {operation: "multiply", a: 25, b: 4},
        toolResult: "Result: 25 multiply 4 = 100",
        finalAnswer: "The result of 25 multiplied by 4 is 100."
    },
    rag: {
        question: "What documents do I have about Python?",
        toolNeeded: "rag_query",
        toolArgs: {query: "Python", n_results: 3},
        toolResult: "Found 2 relevant documents about Python programming and best practices",
        finalAnswer: "I found 2 documents in your knowledge base about Python, covering programming basics and best practices."
    },
    combined: {
        question: "Calculate the gold price change if it increases by 5%",
        toolNeeded: "calculator",
        toolArgs: {operation: "multiply", a: 2050, b: 1.05},
        toolResult: "Result: 2050 multiply 1.05 = 2152.5",
        finalAnswer: "If gold price increases by 5% from $2,050, it would be $2,152.50 per ounce."
    }
};

let currentQuery1 = queries1.calculator;
let currentStep1 = 0;
let totalSteps1 = 12;

function getSteps1(query) {
    return [
        {
            title: "1️⃣ Browser Opens Web Interface",
            component: "Browser",
            explanation: "User opens their browser and navigates to http://localhost:5000. The Flask web server serves the index.html page with the interactive chat interface.",
            data: `URL: http://localhost:5000\nLoading: index.html\nStatus: Connected`,
            code: `# web_server.py\n@app.route('/')\ndef index():\n    return render_template('index.html')`
        },
        {
            title: "2️⃣ Browser Initializes Session",
            component: "Browser",
            explanation: "The browser JavaScript automatically calls /api/initialize to set up a new MCP client session. This happens in the background when the page loads.",
            data: `POST /api/initialize\nCreating session...\nSession ID: d17186a5-be20-40aa...`,
            code: `// index.html JavaScript\nfetch('/api/initialize', {\n    method: 'POST'\n})\n.then(response => response.json())\n.then(data => {\n    console.log('Session initialized');\n});`
        },
        {
            title: "3️⃣ AsyncClientManager Creates Client",
            component: "AsyncClientManager",
            explanation: "The AsyncClientManager runs in a background thread with its own event loop. It creates and manages MCP client instances, keeping them alive across requests.",
            data: `Manager: AsyncClientManager\nBackground Thread: Running\nEvent Loop: Active\nCreating client for session...`,
            code: `# async_client_manager.py\nclass AsyncClientManager:\n    def initialize_client(self, session_id, model):\n        future = asyncio.run_coroutine_threadsafe(\n            self._create_client(session_id, model),\n            self.loop\n        )\n        future.result(timeout=30)`
        },
        {
            title: "4️⃣ MCP Client Connects to Server",
            component: "MCP Client",
            explanation: "The MCP client spawns the mcp_server.py as a subprocess and establishes communication via stdio (stdin/stdout). Note: MCP server does NOT open ChromaDB to avoid locking!",
            data: `Starting: python mcp_server.py\nStdio connection: Established\nMCP Session: Initialized\nChromaDB: NOT accessed (uses HTTP API)`,
            code: `# langchain_mcp_client.py\nserver_params = StdioServerParameters(\n    command="python",\n    args=["mcp_server.py"]\n)\nself.stdio_context = stdio_client(server_params)\nself.read_stream, self.write_stream = \\\n    await self.stdio_context.__aenter__()`
        },
        {
            title: "5️⃣ Initialize Ollama LLM",
            component: "Ollama",
            explanation: "The MCP client initializes ChatOllama with the llama3.2 model. Ollama must be running on localhost:11434 for this to work.",
            data: `Model: llama3.2\nTemperature: 0\nOllama URL: http://localhost:11434\nStatus: Connected`,
            code: `# langchain_mcp_client.py\nself.llm = ChatOllama(\n    model="llama3.2",\n    temperature=0,\n)\nlogger.info("Ollama LLM initialized")`
        },
        {
            title: "6️⃣ User Asks Question",
            component: "Browser",
            explanation: "User types their question in the chat interface and clicks Send. The browser sends a POST request to /api/query with the question.",
            data: `User Input: "${query.question}"\nPOST /api/query\nRequest: {"query": "${query.question}"}`,
            code: `// Browser sends query\nfetch('/api/query', {\n    method: 'POST',\n    headers: {'Content-Type': 'application/json'},\n    body: JSON.stringify({\n        query: "${query.question}"\n    })\n})`
        },
        {
            title: "7️⃣ Web Server Routes to Client",
            component: "Web Server",
            explanation: "The Flask web server receives the query and uses the AsyncClientManager to route it to the correct MCP client session in the background event loop.",
            data: `Session ID: d17186a5-be20-40aa...\nRouting to client...\nCalling: client_manager.query()`,
            code: `# web_server.py\n@app.route('/api/query', methods=['POST'])\ndef query():\n    session_id = session['session_id']\n    query_text = request.json['query']\n    \n    response = client_manager.query(\n        session_id, query_text\n    )\n    return jsonify(response)`
        },
        {
            title: "8️⃣ LLM Analyzes Question",
            component: "Ollama",
            explanation: "The question is sent to Ollama LLM along with a system prompt describing all 8 available tools: calculator, weather, gold_price, send_email, rag_query, code_execute, web_scrape, file_operations.",
            data: `System Prompt: Includes 8 tools\nUser Query: "${query.question}"\nLLM Processing...\nDecision: Use ${query.toolNeeded} tool`,
            code: `# LangChain sends to Ollama\nmessages = [\n    {"role": "system", "content": system_prompt},\n    {"role": "user", "content": "${query.question}"}\n]\nresponse = self.llm.invoke(messages)\n# LLM responds with tool call JSON`
        },
        {
            title: "9️⃣ Extract Tool Call",
            component: "MCP Client",
            explanation: `The LLM's response contains JSON specifying which tool to use. The client extracts this and prepares to call the ${query.toolNeeded} tool via the MCP server.`,
            data: `LLM Response:\n{"tool": "${query.toolNeeded}", "arguments": ${JSON.stringify(query.toolArgs, null, 2)}}\n\nParsing tool call...`,
            code: `# langchain_mcp_client.py\ntool_call = self._extract_tool_call(response_text)\ntool_name = tool_call["tool"]  # "${query.toolNeeded}"\narguments = tool_call["arguments"]`
        },
        {
            title: "🔟 MCP Server Executes Tool",
            component: "MCP Server",
            explanation: `The MCP server executes the ${query.toolNeeded} tool. ${query.toolNeeded === 'rag_query' ? 'For RAG queries, it uses HTTP API (localhost:5000/api/rag/query) to avoid database locking!' : 'The tool performs its specific operation.'}`,
            data: `Tool: ${query.toolNeeded}\nArguments: ${JSON.stringify(query.toolArgs, null, 2)}\n${query.toolNeeded === 'rag_query' ? 'Using: HTTP API to web server' : 'Executing: Direct operation'}\nResult: "${query.toolResult}"`,
            code: `# mcp_server.py\n${query.toolNeeded === 'rag_query' ?
                `# RAG queries use HTTP API\ndata = json.dumps({"query": query, "n_results": 3})\nreq = urllib.request.Request(\n    "http://localhost:5000/api/rag/query",\n    data=data\n)\nresult = urllib.request.urlopen(req)` :
                `# Direct tool execution\nresult = await self.${query.toolNeeded}_tool(arguments)`}`
        },
        {
            title: "1️⃣1️⃣ LLM Formats Final Answer",
            component: "Ollama",
            explanation: "The tool result is sent back to Ollama. The LLM uses this information to generate a natural, conversational response for the user.",
            data: `Tool Result: "${query.toolResult}"\n\nAsking LLM to formulate response...\nFinal Answer Ready!`,
            code: `# Add tool result to conversation\nmessages.append({\n    "role": "user",\n    "content": f"Tool returned: {tool_result}"\n})\n\n# Get final answer from LLM\nfinal_response = self.llm.invoke(messages)`
        },
        {
            title: "1️⃣2️⃣ Display Answer in Browser",
            component: "Browser",
            explanation: "The final answer travels back through the chain: MCP Client → AsyncClientManager → Web Server → Browser. The answer is displayed in the chat interface.",
            data: `Response received from server\nDisplaying in chat interface...\n\n💬 AI: "${query.finalAnswer}"`,
            code: `// Browser receives and displays\nfetch('/api/query', {...})\n  .then(response => response.json())\n  .then(data => {\n      displayMessage('AI', data.response);\n  });`
        }
    ];
}

// Rest of the step-by-step visualization code
function updateVisualization1() {
    const viz = document.getElementById('visualization1');
    const steps = getSteps1(currentQuery1);
    const step = steps[currentStep1];

    viz.innerHTML = `
        <div class="component ${currentStep1 >= 0 ? 'active' : ''}">
            <h3>
                <div class="component-icon">${step.title.substring(0, 2)}</div>
                ${step.title}
            </h3>
            <p><strong>Component:</strong> ${step.component}</p>

            <div class="explanation ${currentStep1 >= 0 ? 'visible' : ''}">
                <h4>📖 What's Happening</h4>
                <p>${step.explanation}</p>
            </div>

            <div class="data-box ${currentStep1 >= 0 ? 'visible' : ''}">
                ${step.data.split('\n').map(line => `<div>${line}</div>`).join('')}
            </div>

            <div class="code-snippet ${currentStep1 >= 0 ? 'visible' : ''}">
${step.code}
            </div>
        </div>

        ${currentStep1 < totalSteps1 - 1 ? '<div class="arrow visible">⬇</div>' : ''}
    `;

    // Update progress
    const progress = ((currentStep1 + 1) / totalSteps1) * 100;
    document.getElementById('progressFill1').style.width = progress + '%';
    document.getElementById('currentStep1').textContent = currentStep1 + 1;
    document.getElementById('totalSteps1').textContent = totalSteps1;

    // Update button states
    document.getElementById('prevBtn1').disabled = currentStep1 === 0;
    document.getElementById('nextBtn1').disabled = currentStep1 === totalSteps1 - 1;
}

// Query selection
document.querySelectorAll('.query-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.query-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const queryType = btn.dataset.query;
        currentQuery1 = queries1[queryType];
        currentStep1 = 0;
        updateVisualization1();
    });
});

// Step controls
document.getElementById('nextBtn1').addEventListener('click', () => {
    if (currentStep1 < totalSteps1 - 1) {
        currentStep1++;
        updateVisualization1();
    }
});

document.getElementById('prevBtn1').addEventListener('click', () => {
    if (currentStep1 > 0) {
        currentStep1--;
        updateVisualization1();
    }
});

document.getElementById('resetBtn1').addEventListener('click', () => {
    currentStep1 = 0;
    updateVisualization1();
});

// Initialize
updateVisualization1();
