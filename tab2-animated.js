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
let totalSteps2 = getSteps2(queries2.calculator).length; // Dynamic based on query type
let isPlaying = false;
let playbackSpeed = 1.0;
let playInterval = null;

const nodes = {
    browser: {
        x: 400, y: 60,
        width: 600, height: 80,
        title: "🌐 Browser",
        subtitle: "(http://localhost:5000)",
        details: [],
        style: "primary"
    },
    webServer: {
        x: 400, y: 200,
        width: 600, height: 140,
        title: "⚡ Web Server (Flask)",
        subtitle: "(web_server.py)",
        details: [
            "• Serves web interface (templates/index.html)",
            "• Manages sessions and routing",
            "• Handles file uploads for RAG",
            "• Opens ChromaDB (SINGLE connection - avoids locking)"
        ],
        style: "primary"
    },
    asyncManager: {
        x: 400, y: 400,
        width: 600, height: 140,
        title: "🔄 AsyncClientManager",
        subtitle: "(async_client_manager.py)",
        details: [
            "• Background thread with persistent event loop",
            "• Manages MCP client lifecycle (create, query, cleanup)",
            "• Thread-safe async execution with run_coroutine_threadsafe()",
            "• Keeps clients alive across requests"
        ],
        style: "primary"
    },
    mcpClient: {
        x: 400, y: 570,
        width: 600, height: 100,
        title: "🔌 LangChain MCP Client",
        subtitle: "(langchain_mcp_client.py)",
        details: [
            "ChatOllama (llama3.2) ←→ MCP Wrapper (Tool Calls)"
        ],
        style: "primary"
    },
    mcpServer: {
        x: 400, y: 770,
        width: 600, height: 260,
        title: "🛠️ MCP Server",
        subtitle: "(mcp_server.py)",
        details: [
            "⚠️ IMPORTANT: Does NOT open ChromaDB directly (avoids locking)",
            "📚 RAG queries use HTTP API → http://localhost:5000/api/rag/query",
            "",
            "8 Tools:",
            "┌──────────┬──────────┬───────────┬────────────┐",
            "│Calculator│ Weather  │Gold Price │   Email    │",
            "├──────────┼──────────┼───────────┼────────────┤",
            "│RAG Query │   Code   │    Web    │    File    │",
            "│(HTTP API)│ Executor │  Scraper  │ Operations │",
            "└──────────┴──────────┴───────────┴────────────┘"
        ],
        style: "warning"
    },
    ragSystem: {
        x: 400, y: 1100,
        width: 600, height: 120,
        title: "📚 RAG System",
        subtitle: "(rag_system.py)",
        details: [
            "• Document upload and chunking",
            "• Vector embeddings with ChromaDB",
            "• Semantic search and relevance scoring",
            "• Accessed via web server (NO direct access from MCP server)"
        ],
        style: "success"
    },
    chromadb: {
        x: 400, y: 1270,
        width: 250, height: 80,
        title: "💾 ChromaDB",
        subtitle: "(Vector Database)",
        details: ["./rag_db/"],
        style: "database"
    }
};

function getSteps2(query) {
    const isRAGQuery = query.tool === 'rag_query';
    const steps = [
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
            from: "mcpClient", to: "mcpServer",
            message: {from: "MCP Client", to: "MCP Server", content: `Query: "${query.question}"\nOllama determines tool: ${query.tool}`},
            description: "MCP client sends query to server (Ollama inside client chooses tool)"
        },
        {
            from: "mcpServer", to: "mcpServer",
            message: {from: "MCP Server", to: "MCP Server", content: `Execute tool: ${query.tool}\nArgs: ${JSON.stringify(query.args)}`},
            description: isRAGQuery ? "RAG tool execution starts" : "Execute tool directly"
        }
    ];

    // Add RAG-specific steps
    if (isRAGQuery) {
        steps.push({
            from: "mcpServer", to: "ragSystem",
            message: {from: "MCP Server", to: "RAG System", content: `HTTP POST /api/rag/query\n{"query": "${query.args.query}", "n_results": ${query.args.n_results}}`},
            description: "RAG tool uses HTTP API (no database locking!)"
        });
        steps.push({
            from: "ragSystem", to: "chromadb",
            message: {from: "RAG System", to: "ChromaDB", content: `Vector search: "${query.args.query}"\nTop ${query.args.n_results} results`},
            description: "RAG system queries ChromaDB for semantic search"
        });
        steps.push({
            from: "chromadb", to: "ragSystem",
            message: {from: "ChromaDB", to: "RAG System", content: `${query.result}`},
            description: "ChromaDB returns relevant documents"
        });
        steps.push({
            from: "ragSystem", to: "mcpServer",
            message: {from: "RAG System", to: "MCP Server", content: `HTTP Response:\n${query.result}`},
            description: "RAG system returns results via HTTP"
        });
    }

    // Common return path
    steps.push({
        from: "mcpServer", to: "mcpClient",
        message: {from: "MCP Server", to: "MCP Client", content: `Tool result: ${query.result}`},
        description: "MCP server returns tool result to client"
    });
    steps.push({
        from: "mcpClient", to: "asyncManager",
        message: {from: "MCP Client", to: "AsyncClientManager", content: `Final answer: "${query.answer}"`},
        description: "Client formats response with Ollama and sends to manager"
    });
    steps.push({
        from: "asyncManager", to: "webServer",
        message: {from: "AsyncClientManager", to: "Web Server", content: `{"response": "${query.answer}"}`},
        description: "Manager returns to web server"
    });
    steps.push({
        from: "webServer", to: "browser",
        message: {from: "Web Server", to: "Browser", content: `JSON Response\n💬 AI: "${query.answer}"`},
        description: "Web server sends response to browser"
    });

    return steps;
}

// Initialize SVG flowchart
let svg, width, height;

function initFlowchart() {
    const container = document.getElementById('flowchart');
    width = container.parentElement.clientWidth;
    height = 1400; // Increased height for detailed diagram

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

    // Main rectangle with style-based coloring
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('class', `node-rect node-${node.style}`);
    rect.setAttribute('x', node.x - node.width/2);
    rect.setAttribute('y', node.y - node.height/2);
    rect.setAttribute('width', node.width);
    rect.setAttribute('height', node.height);
    rect.setAttribute('rx', 10);

    g.appendChild(rect);

    let currentY = node.y - node.height/2 + 25;

    // Title (bold, larger)
    const title = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    title.setAttribute('class', 'node-title');
    title.setAttribute('x', node.x);
    title.setAttribute('y', currentY);
    title.setAttribute('text-anchor', 'middle');
    title.setAttribute('font-weight', 'bold');
    title.setAttribute('font-size', '16px');
    title.textContent = node.title;
    g.appendChild(title);
    currentY += 20;

    // Subtitle (smaller, gray)
    if (node.subtitle) {
        const subtitle = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        subtitle.setAttribute('class', 'node-subtitle');
        subtitle.setAttribute('x', node.x);
        subtitle.setAttribute('y', currentY);
        subtitle.setAttribute('text-anchor', 'middle');
        subtitle.setAttribute('font-size', '12px');
        subtitle.setAttribute('fill', '#666');
        subtitle.textContent = node.subtitle;
        g.appendChild(subtitle);
        currentY += 20;
    }

    // Details (left-aligned, smaller font)
    if (node.details && node.details.length > 0) {
        currentY += 5;
        node.details.forEach(detail => {
            const detailText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            detailText.setAttribute('class', 'node-detail');
            detailText.setAttribute('x', node.x - node.width/2 + 15);
            detailText.setAttribute('y', currentY);
            detailText.setAttribute('text-anchor', 'start');
            detailText.setAttribute('font-size', '11px');
            detailText.setAttribute('font-family', 'monospace');

            // Special styling for warnings
            if (detail.startsWith('⚠️')) {
                detailText.setAttribute('fill', '#ff5722');
                detailText.setAttribute('font-weight', 'bold');
            } else if (detail.startsWith('📚')) {
                detailText.setAttribute('fill', '#2196F3');
                detailText.setAttribute('font-weight', 'bold');
            } else {
                detailText.setAttribute('fill', '#333');
            }

            detailText.textContent = detail;
            g.appendChild(detailText);
            currentY += 15;
        });
    }

    svg.appendChild(g);
}

function drawEdges() {
    // Collect all unique edges from all possible query types
    const allEdges = new Map();

    // Add edges from all query types to ensure complete coverage
    Object.values(queries2).forEach(query => {
        const steps = getSteps2(query);
        steps.forEach(step => {
            const key = `${step.from}-${step.to}`;
            if (!allEdges.has(key)) {
                allEdges.set(key, {from: step.from, to: step.to});
            }
        });
    });

    // Static edges for visual structure
    const staticEdges = [
        {from: 'browser', to: 'webServer'},
        {from: 'webServer', to: 'asyncManager'},
        {from: 'asyncManager', to: 'mcpClient'},
        {from: 'mcpClient', to: 'mcpServer'},
        {from: 'mcpServer', to: 'ragSystem', style: 'http'},
        {from: 'ragSystem', to: 'chromadb'}
    ];

    staticEdges.forEach(edge => {
        const key = `${edge.from}-${edge.to}`;
        if (!allEdges.has(key)) {
            allEdges.set(key, edge);
        } else if (edge.style) {
            allEdges.get(key).style = edge.style;
        }
    });

    // Add arrowhead marker definition first
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
    marker.setAttribute('id', 'arrowhead');
    marker.setAttribute('markerWidth', '10');
    marker.setAttribute('markerHeight', '10');
    marker.setAttribute('refX', '9');
    marker.setAttribute('refY', '3');
    marker.setAttribute('orient', 'auto');

    const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    polygon.setAttribute('points', '0 0, 10 3, 0 6');
    polygon.setAttribute('fill', '#999');

    marker.appendChild(polygon);
    defs.appendChild(marker);
    svg.insertBefore(defs, svg.firstChild);

    // Draw all edges
    allEdges.forEach(edge => {
        const fromNode = nodes[edge.from];
        const toNode = nodes[edge.to];

        if (!fromNode || !toNode) return;

        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('class', 'edge');
        path.setAttribute('data-from', edge.from);
        path.setAttribute('data-to', edge.to);

        let d;

        // Handle self-loop (same node)
        if (edge.from === edge.to) {
            // Draw a loop on the right side of the node
            const centerX = fromNode.x + fromNode.width/2;
            const centerY = fromNode.y;
            const loopSize = 40;
            d = `M ${centerX} ${centerY - 20}
                 C ${centerX + loopSize} ${centerY - 40},
                   ${centerX + loopSize} ${centerY + 40},
                   ${centerX} ${centerY + 20}`;
        } else {
            // Calculate arrow path for normal edges
            const startY = fromNode.y + fromNode.height/2;
            const endY = toNode.y - toNode.height/2;
            const midY = (startY + endY) / 2;

            // For return paths (going up), offset to the side to avoid overlap
            if (startY > endY) {
                const offset = 30;
                d = `M ${fromNode.x + offset} ${startY}
                     L ${fromNode.x + offset} ${midY}
                     L ${toNode.x + offset} ${midY}
                     L ${toNode.x + offset} ${endY}`;
            } else {
                d = `M ${fromNode.x} ${startY}
                     L ${fromNode.x} ${midY}
                     L ${toNode.x} ${midY}
                     L ${toNode.x} ${endY}`;
            }
        }

        path.setAttribute('d', d);
        path.setAttribute('stroke-dasharray', '5 3');
        path.setAttribute('marker-end', 'url(#arrowhead)');

        // Special styling for HTTP edge
        if (edge.style === 'http') {
            path.setAttribute('stroke', '#2196F3');
            path.setAttribute('stroke-width', '3');
        }

        svg.appendChild(path);

        // Add label for special edges
        if (edge.style === 'http' && edge.from !== edge.to) {
            const fromNode = nodes[edge.from];
            const toNode = nodes[edge.to];
            const startY = fromNode.y + fromNode.height/2;
            const endY = toNode.y - toNode.height/2;
            const midY = (startY + endY) / 2;

            const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            label.setAttribute('x', toNode.x + 40);
            label.setAttribute('y', midY);
            label.setAttribute('font-size', '11px');
            label.setAttribute('fill', '#2196F3');
            label.setAttribute('font-weight', 'bold');
            label.textContent = 'HTTP (RAG only)';
            svg.appendChild(label);
        }
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

    // Activate to node (don't duplicate if self-loop)
    if (currentStepData.from !== currentStepData.to) {
        const toNode = document.querySelector(`.node[data-id="${currentStepData.to}"]`);
        if (toNode) toNode.classList.add('active');
    }

    // Activate edge
    const edge = document.querySelector(`.edge[data-from="${currentStepData.from}"][data-to="${currentStepData.to}"]`);
    if (edge) {
        edge.classList.add('active');
    } else {
        // Edge might not be found, log for debugging
        console.log(`Edge not found: ${currentStepData.from} -> ${currentStepData.to}`);
    }

    // Activate message and scroll into view
    const messageEl = document.querySelector(`.message[data-step="${step}"]`);
    if (messageEl) {
        messageEl.classList.add('active');
        // Smooth scroll the message into view
        messageEl.scrollIntoView({behavior: 'smooth', block: 'nearest'});
    }

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
