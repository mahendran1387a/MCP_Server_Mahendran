// Tab 2: Animated Flowchart JavaScript - Updated for Current Architecture

const queries2 = {
    calculator: {
        question: "What is 25 × 4?",
        tool: "calculator",
        args: {operation: "multiply", a: 25, b: 4},
        result: "Result: 100",
        answer: "The result is 100."
    },
    rag: {
        question: "What documents do I have about Python?",
        tool: "rag_query",
        args: {query: "Python", n_results: 3},
        result: "Found 2 documents",
        answer: "Found 2 documents about Python."
    },
    combined: {
        question: "Calculate gold price + 5%?",
        tool: "calculator",
        args: {operation: "multiply", a: 2050, b: 1.05},
        result: "$2,152.50",
        answer: "New price: $2,152.50"
    }
};

let currentQuery2 = queries2.calculator;
let currentStep2 = 0;
let totalSteps2 = 14; // Browser->Web Server->AsyncManager->MCP Client->Ollama->MCP Server->Tools and back
let isPlaying = false;
let playbackSpeed = 1.0;
let playInterval = null;

const nodes = {
    browser: {x: 400, y: 50, label: "🌐 Browser", width: 130, height: 60},
    webServer: {x: 400, y: 170, label: "⚡ Web Server\n(Flask)", width: 140, height: 70},
    asyncManager: {x: 200, y: 310, label: "🔄 Async\nManager", width: 140, height: 70},
    mcpClient: {x: 600, y: 310, label: "🔌 MCP\nClient", width: 130, height: 70},
    ollama: {x: 200, y: 470, label: "🧠 Ollama\n(llama3.2)", width: 140, height: 70},
    mcpServer: {x: 600, y: 470, label: "🛠️ MCP\nServer", width: 130, height: 70},
    tools: {x: 600, y: 610, label: "⚙️ 8 Tools\n+ RAG API", width: 140, height: 70}
};

function getSteps2(query) {
    return [
        {
            from: "browser", to: "webServer",
            message: {from: "Browser", to: "Web Server", content: `POST /api/query\n"${query.question}"`},
            description: "Browser sends query to Flask server"
        },
        {
            from: "webServer", to: "asyncManager",
            message: {from: "Web Server", to: "AsyncClientManager", content: "Route query to MCP client"},
            description: "Web server routes to AsyncClientManager"
        },
        {
            from: "asyncManager", to: "mcpClient",
            message: {from: "AsyncClientManager", to: "MCP Client", content: `process_query("${query.question}")`},
            description: "Manager forwards to MCP client in background thread"
        },
        {
            from: "mcpClient", to: "ollama",
            message: {from: "MCP Client", to: "Ollama", content: `Query + System Prompt (8 tools)\n"${query.question}"`},
            description: "Send question to Ollama LLM with tool descriptions"
        },
        {
            from: "ollama", to: "mcpClient",
            message: {from: "Ollama", to: "MCP Client", content: `{"tool": "${query.tool}", "arguments": {...}}`},
            description: "Ollama decides to use a tool"
        },
        {
            from: "mcpClient", to: "mcpServer",
            message: {from: "MCP Client", to: "MCP Server", content: `call_tool("${query.tool}", ${JSON.stringify(query.args)})`},
            description: "Call MCP server to execute tool"
        },
        {
            from: "mcpServer", to: "tools",
            message: {from: "MCP Server", to: "Tools", content: `Execute: ${query.tool}\n${query.tool === 'rag_query' ? 'Via HTTP API → /api/rag/query' : 'Direct execution'}`},
            description: query.tool === 'rag_query' ?
                "RAG tool uses HTTP API (no DB locking!)" :
                "Execute tool directly"
        },
        {
            from: "tools", to: "mcpServer",
            message: {from: "Tools", to: "MCP Server", content: `Result: ${query.result}`},
            description: "Tool returns result"
        },
        {
            from: "mcpServer", to: "mcpClient",
            message: {from: "MCP Server", to: "MCP Client", content: `TextContent: "${query.result}"`},
            description: "MCP server returns result to client"
        },
        {
            from: "mcpClient", to: "ollama",
            message: {from: "MCP Client", to: "Ollama", content: `Tool returned: ${query.result}\nFormat final answer`},
            description: "Send tool result back to Ollama for formatting"
        },
        {
            from: "ollama", to: "mcpClient",
            message: {from: "Ollama", to: "MCP Client", content: `"${query.answer}"`},
            description: "Ollama generates natural language response"
        },
        {
            from: "mcpClient", to: "asyncManager",
            message: {from: "MCP Client", to: "AsyncClientManager", content: `Response: "${query.answer}"`},
            description: "Return response to manager"
        },
        {
            from: "asyncManager", to: "webServer",
            message: {from: "AsyncClientManager", to: "Web Server", content: `{"response": "${query.answer}"}`},
            description: "Manager returns to web server"
        },
        {
            from: "webServer", to: "browser",
            message: {from: "Web Server", to: "Browser", content: `JSON Response\n💬 AI: "${query.answer}"`},
            description: "Web server sends response to browser"
        }
    ];
}

// Initialize SVG flowchart
let svg, width, height;

function initFlowchart() {
    const container = document.getElementById('flowchart');
    width = container.parentElement.clientWidth;
    height = 700;

    // Clear existing
    container.innerHTML = '';

    svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', width);
    svg.setAttribute('height', height);
    svg.setAttribute('id', 'flowchart');
    container.appendChild(svg);

    // Draw edges first (so they appear behind nodes)
    drawEdges();

    // Draw nodes
    Object.entries(nodes).forEach(([id, node]) => {
        drawNode(id, node);
    });

    // Reset step
    currentStep2 = 0;
    updateMessages();
    updateProgress();
}

function drawNode(id, node) {
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.setAttribute('class', 'node');
    g.setAttribute('data-id', id);

    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('class', 'node-rect');
    rect.setAttribute('x', node.x - node.width/2);
    rect.setAttribute('y', node.y - node.height/2);
    rect.setAttribute('width', node.width);
    rect.setAttribute('height', node.height);

    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('class', 'node-text');
    text.setAttribute('x', node.x);
    text.setAttribute('y', node.y);

    // Handle multiline text
    const lines = node.label.split('\n');
    lines.forEach((line, i) => {
        const tspan = document.createElementNS('http://www.w3.org/2000/svg', 'tspan');
        tspan.setAttribute('x', node.x);
        tspan.setAttribute('dy', i === 0 ? '0' : '1.2em');
        tspan.textContent = line;
        text.appendChild(tspan);
    });

    g.appendChild(rect);
    g.appendChild(text);
    svg.appendChild(g);
}

function drawEdges() {
    const edges = [
        {from: 'browser', to: 'webServer'},
        {from: 'webServer', to: 'asyncManager'},
        {from: 'webServer', to: 'mcpClient'},
        {from: 'asyncManager', to: 'mcpClient'},
        {from: 'mcpClient', to: 'ollama'},
        {from: 'mcpClient', to: 'mcpServer'},
        {from: 'mcpServer', to: 'tools'}
    ];

    edges.forEach(edge => {
        const fromNode = nodes[edge.from];
        const toNode = nodes[edge.to];

        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('class', 'edge');
        path.setAttribute('data-from', edge.from);
        path.setAttribute('data-to', edge.to);

        // Simple straight line
        const d = `M ${fromNode.x} ${fromNode.y + fromNode.height/2} L ${toNode.x} ${toNode.y - toNode.height/2}`;
        path.setAttribute('d', d);
        path.setAttribute('stroke-dasharray', '10 5');

        svg.appendChild(path);
    });
}

function animateStep(step) {
    // Clear all active states
    document.querySelectorAll('.node').forEach(n => n.classList.remove('active', 'pulsing'));
    document.querySelectorAll('.edge').forEach(e => e.classList.remove('active'));
    document.querySelectorAll('.message').forEach(m => m.classList.remove('active'));

    if (step < 0 || step >= totalSteps2) return;

    const steps = getSteps2(currentQuery2);
    const currentStepData = steps[step];

    // Activate from node
    const fromNode = document.querySelector(`.node[data-id="${currentStepData.from}"]`);
    if (fromNode) fromNode.classList.add('active', 'pulsing');

    // Activate to node
    const toNode = document.querySelector(`.node[data-id="${currentStepData.to}"]`);
    if (toNode) toNode.classList.add('active');

    // Activate edge
    const edge = document.querySelector(`.edge[data-from="${currentStepData.from}"][data-to="${currentStepData.to}"]`);
    if (edge) edge.classList.add('active');

    // Activate message
    const messageEl = document.querySelector(`.message[data-step="${step}"]`);
    if (messageEl) messageEl.classList.add('active');

    updateProgress();
}

function updateMessages() {
    const messageLog = document.getElementById('messageLog');
    const steps = getSteps2(currentQuery2);

    messageLog.innerHTML = steps.map((step, i) => `
        <div class="message ${i === currentStep2 ? 'active' : ''}" data-step="${i}">
            <div class="timestamp">Step ${i + 1}/${steps.length}</div>
            <div class="from-to">${step.message.from} → ${step.message.to}</div>
            <div class="content">${step.message.content}</div>
        </div>
    `).join('');
}

function updateProgress() {
    const progress = ((currentStep2 + 1) / totalSteps2) * 100;
    document.getElementById('progressFill2').style.width = progress + '%';
    document.getElementById('currentStep2').textContent = currentStep2 + 1;
    document.getElementById('totalSteps2').textContent = totalSteps2;

    document.getElementById('prevBtn2').disabled = currentStep2 === 0;
    document.getElementById('nextBtn2').disabled = currentStep2 === totalSteps2 - 1;
}

// Query selection
document.querySelectorAll('.query-option').forEach(opt => {
    opt.addEventListener('click', () => {
        document.querySelectorAll('.query-option').forEach(o => o.classList.remove('selected'));
        opt.classList.add('selected');

        const queryType = opt.dataset.query;
        currentQuery2 = queries2[queryType];
        currentStep2 = 0;
        totalSteps2 = getSteps2(currentQuery2).length;
        updateMessages();
        animateStep(currentStep2);
    });
});

// Playback controls
document.getElementById('playBtn').addEventListener('click', () => {
    isPlaying = true;
    document.getElementById('playBtn').style.display = 'none';
    document.getElementById('pauseBtn').style.display = 'block';

    playInterval = setInterval(() => {
        if (currentStep2 < totalSteps2 - 1) {
            currentStep2++;
            animateStep(currentStep2);
        } else {
            // Stop at end
            isPlaying = false;
            document.getElementById('playBtn').style.display = 'block';
            document.getElementById('pauseBtn').style.display = 'none';
            clearInterval(playInterval);
        }
    }, 2000 / playbackSpeed);
});

document.getElementById('pauseBtn').addEventListener('click', () => {
    isPlaying = false;
    document.getElementById('playBtn').style.display = 'block';
    document.getElementById('pauseBtn').style.display = 'none';
    clearInterval(playInterval);
});

document.getElementById('nextBtn2').addEventListener('click', () => {
    if (currentStep2 < totalSteps2 - 1) {
        currentStep2++;
        animateStep(currentStep2);
    }
});

document.getElementById('prevBtn2').addEventListener('click', () => {
    if (currentStep2 > 0) {
        currentStep2--;
        animateStep(currentStep2);
    }
});

document.getElementById('resetBtn2').addEventListener('click', () => {
    currentStep2 = 0;
    animateStep(currentStep2);
});

// Speed control
document.getElementById('speedSlider').addEventListener('input', (e) => {
    playbackSpeed = parseFloat(e.target.value);
    document.getElementById('speedValue').textContent = playbackSpeed.toFixed(1);
});

// Initialize on load
setTimeout(() => {
    if (document.querySelector('.tab-content.active')?.id === 'animated') {
        initFlowchart();
        animateStep(currentStep2);
    }
}, 100);
