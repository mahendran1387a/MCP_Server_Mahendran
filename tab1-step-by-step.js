// Tab 1: Step-by-Step Flow JavaScript

const queries1 = {
    calculator: {
        question: "What is 25 × 4?",
        toolNeeded: "calculator",
        toolArgs: {operation: "multiply", a: 25, b: 4},
        toolResult: "Result: 25 multiply 4 = 100",
        finalAnswer: "The result of 25 multiplied by 4 is 100."
    },
    weather: {
        question: "What's the weather in Paris?",
        toolNeeded: "weather",
        toolArgs: {city: "Paris", units: "celsius"},
        toolResult: "Weather in Paris: 20°C, Sunny, Humidity: 65%, Wind: 15 km/h",
        finalAnswer: "The weather in Paris is 20°C and sunny with 65% humidity."
    },
    combined: {
        question: "Calculate 50 + 30, and also tell me the weather in Tokyo",
        toolNeeded: "calculator",
        toolArgs: {operation: "add", a: 50, b: 30},
        toolResult: "Result: 50 add 30 = 80",
        finalAnswer: "50 + 30 = 80. Weather in Tokyo is 18°C and cloudy."
    }
};

let currentQuery1 = queries1.calculator;
let currentStep1 = 0;
let totalSteps1 = 9;

function getSteps1(query) {
    return [
        {
            title: "1️⃣ User Input",
            component: "User",
            explanation: "The user types a question into the interactive CLI. The question is captured and sent to the LangChain client for processing.",
            data: `User Question: "${query.question}"`,
            code: `# main.py\nquery = input("💬 You: ")  # "${query.question}"\nawait client.process_query(query)`
        },
        {
            title: "2️⃣ LangChain Client Receives Query",
            component: "LangChain Client",
            explanation: "The LangChain client receives the query and prepares to send it to the Ollama LLM. It includes a system prompt that describes all available tools.",
            data: `Received: "${query.question}"\nPreparing context with tool descriptions...`,
            code: `# langchain_mcp_client.py\nasync def process_query(self, query: str):\n    messages = [\n        {"role": "system", "content": system_prompt},\n        {"role": "user", "content": "${query.question}"}\n    ]`
        },
        {
            title: "3️⃣ System Prompt with Tools",
            component: "LangChain Client",
            explanation: "A system prompt is created that tells the LLM about available tools (calculator and weather). This is how the LLM knows what tools it can use.",
            data: `System Prompt:\n"You have access to these tools:\n- calculator: add, subtract, multiply, divide\n- weather: get weather for a city\n\nTo use a tool, respond with JSON:\n{'tool': 'tool_name', 'arguments': {...}}"`,
            code: `# Tool descriptions are automatically fetched from MCP server\ntools = await self.mcp_wrapper.get_tools()\nsystem_prompt = self._format_tools_description(tools)`
        },
        {
            title: "4️⃣ Send to Ollama LLM",
            component: "Ollama",
            explanation: "The question and system prompt are sent to the Ollama LLM (llama3.2 model). The LLM analyzes the question and decides if it needs to use a tool.",
            data: `Sending to Ollama (llama3.2)...\nQuestion: "${query.question}"\nContext: [System prompt with tool descriptions]`,
            code: `# LangChain sends to Ollama\nresponse = self.llm.invoke(messages)\n# Ollama processes and decides action`
        },
        {
            title: "5️⃣ LLM Decides to Use Tool",
            component: "Ollama",
            explanation: `The LLM understands that to answer "${query.question}", it needs to use the ${query.toolNeeded} tool. It formats its response as JSON with the tool name and arguments.`,
            data: `LLM Response:\n{"tool": "${query.toolNeeded}", "arguments": ${JSON.stringify(query.toolArgs, null, 2)}}`,
            code: `# LLM response contains tool call\nresponse_text = response.content\n# Example: '{"tool": "${query.toolNeeded}", "arguments": {...}}'`
        },
        {
            title: "6️⃣ Parse and Call MCP Tool",
            component: "MCP Client",
            explanation: "The LangChain client extracts the tool call from the LLM's response, then calls the MCP server to execute the tool.",
            data: `Parsed Tool Call:\nTool: ${query.toolNeeded}\nArguments: ${JSON.stringify(query.toolArgs, null, 2)}\n\nCalling MCP Server...`,
            code: `# Extract tool call\ntool_call = self._extract_tool_call(response_text)\n\n# Call MCP tool\nresult = await self.mcp_wrapper.call_tool(\n    "${query.toolNeeded}",\n    ${JSON.stringify(query.toolArgs, null, 2)}\n)`
        },
        {
            title: "7️⃣ MCP Server Executes Tool",
            component: "MCP Server",
            explanation: `The MCP server receives the request and executes the ${query.toolNeeded} tool with the provided arguments. It performs the actual operation and returns the result.`,
            data: `Executing: ${query.toolNeeded}\nInput: ${JSON.stringify(query.toolArgs, null, 2)}\nOutput: "${query.toolResult}"`,
            code: `# mcp_server.py\nasync def ${query.toolNeeded}_tool(self, arguments):\n    ${query.toolNeeded === 'calculator' ?
                `operation = arguments["operation"]  # "${query.toolArgs.operation}"\n    a = arguments["a"]  # ${query.toolArgs.a}\n    b = arguments["b"]  # ${query.toolArgs.b}\n    result = a ${query.toolArgs.operation === 'multiply' ? '*' : '+'} b` :
                `city = arguments["city"]  # "${query.toolArgs.city}"\n    # Fetch weather data...\n    result = get_weather(city)`}\n    return [TextContent(text=f"${query.toolResult}")]`
        },
        {
            title: "8️⃣ Send Result to LLM",
            component: "Ollama",
            explanation: "The tool result is sent back to the LLM. The LLM now has the information it needs to formulate a natural language response for the user.",
            data: `Tool Result: "${query.toolResult}"\n\nAsking LLM to format natural response...`,
            code: `# Add tool result to conversation\nmessages.append({\n    "role": "user",\n    "content": "Tool returned: ${query.toolResult}"\n})\n\n# Ask LLM to formulate answer\nresponse = self.llm.invoke(messages)`
        },
        {
            title: "9️⃣ Final Answer to User",
            component: "User",
            explanation: "The LLM generates a natural language response based on the tool result. This final answer is displayed to the user in the CLI.",
            data: `Final Answer:\n"${query.finalAnswer}"`,
            code: `# Display to user\nprint(f"Final Answer: {response_text}")\n\n# Output shown in terminal:\n# "${query.finalAnswer}"`
        }
    ];
}

let steps1 = getSteps1(currentQuery1);

function init1() {
    renderStep1();
    updateControls1();
}

function renderStep1() {
    const viz = document.getElementById('visualization1');
    const step = steps1[currentStep1];

    viz.innerHTML = `
        <div class="component active">
            <h3>
                <span class="component-icon">${step.title.substring(0, 2)}</span>
                ${step.title}
            </h3>

            <div class="explanation visible">
                <h4>📖 What's Happening?</h4>
                <p>${step.explanation}</p>
            </div>

            <div class="data-box visible">
                <div class="label">📊 Data:</div>
                <pre>${step.data}</pre>
            </div>

            <div class="code-snippet visible">
                <div class="label" style="color: #4CAF50; margin-bottom: 10px;">💻 Code:</div>
                <pre>${highlightCode1(step.code)}</pre>
            </div>
        </div>

        ${currentStep1 < totalSteps1 - 1 ? '<div class="arrow visible">⬇️</div>' : ''}
    `;

    updateProgress1();
}

function highlightCode1(code) {
    return code
        .replace(/(async|def|await|return|import|from|if|else)/g, '<span class="keyword">$1</span>')
        .replace(/(".*?")/g, '<span class="string">$1</span>')
        .replace(/(#.*)/g, '<span class="comment">$1</span>')
        .replace(/(\w+)\(/g, '<span class="function">$1</span>(');
}

function updateControls1() {
    document.getElementById('currentStep1').textContent = currentStep1 + 1;
    document.getElementById('totalSteps1').textContent = totalSteps1;
    document.getElementById('prevBtn1').disabled = currentStep1 === 0;
    document.getElementById('nextBtn1').disabled = currentStep1 === totalSteps1 - 1;
}

function updateProgress1() {
    const progress = ((currentStep1 + 1) / totalSteps1) * 100;
    document.getElementById('progressFill1').style.width = progress + '%';
}

// Event listeners for Tab 1
document.getElementById('nextBtn1').addEventListener('click', () => {
    if (currentStep1 < totalSteps1 - 1) {
        currentStep1++;
        renderStep1();
        updateControls1();
    }
});

document.getElementById('prevBtn1').addEventListener('click', () => {
    if (currentStep1 > 0) {
        currentStep1--;
        renderStep1();
        updateControls1();
    }
});

document.getElementById('resetBtn1').addEventListener('click', () => {
    currentStep1 = 0;
    renderStep1();
    updateControls1();
});

document.querySelectorAll('#step-by-step .query-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('#step-by-step .query-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const queryType = btn.dataset.query;
        currentQuery1 = queries1[queryType];
        steps1 = getSteps1(currentQuery1);
        currentStep1 = 0;
        renderStep1();
        updateControls1();
    });
});

// Keyboard navigation for Tab 1
document.addEventListener('keydown', (e) => {
    // Only handle if Tab 1 is active
    if (!document.getElementById('step-by-step').classList.contains('active')) return;

    if (e.key === 'ArrowRight' && currentStep1 < totalSteps1 - 1) {
        currentStep1++;
        renderStep1();
        updateControls1();
    } else if (e.key === 'ArrowLeft' && currentStep1 > 0) {
        currentStep1--;
        renderStep1();
        updateControls1();
    } else if (e.key === 'r' || e.key === 'R') {
        currentStep1 = 0;
        renderStep1();
        updateControls1();
    }
});

// Initialize Tab 1
init1();
