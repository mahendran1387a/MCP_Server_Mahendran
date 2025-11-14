// Tab 2: Animated Flowchart JavaScript

const queries2 = {
    calculator: {
        question: "What is 25 × 4?",
        tool: "calculator",
        args: {operation: "multiply", a: 25, b: 4},
        result: "Result: 100",
        answer: "The result is 100."
    },
    weather: {
        question: "What's the weather in Paris?",
        tool: "weather",
        args: {city: "Paris", units: "celsius"},
        result: "20°C, Sunny",
        answer: "Paris is 20°C and sunny."
    },
    combined: {
        question: "Calculate 50 + 30, and weather?",
        tool: "calculator",
        args: {operation: "add", a: 50, b: 30},
        result: "80, Tokyo: 18°C",
        answer: "50+30=80. Tokyo is 18°C."
    }
};

let currentQuery2 = queries2.calculator;
let currentStep2 = 0;
let totalSteps2 = 12;
let isPlaying = false;
let playbackSpeed = 1.0;
let playInterval = null;

const nodes = {
    user: {x: 400, y: 50, label: "👤 User", width: 120, height: 60},
    langchain: {x: 400, y: 180, label: "🔗 LangChain\nClient", width: 140, height: 70},
    ollama: {x: 200, y: 350, label: "🧠 Ollama\nLLM", width: 130, height: 70},
    mcpClient: {x: 600, y: 350, label: "🔌 MCP\nClient", width: 130, height: 70},
    mcpServer: {x: 600, y: 520, label: "🛠️ MCP\nServer", width: 130, height: 70},
    tools: {x: 600, y: 650, label: "⚙️ Tools", width: 120, height: 60}
};

function getSteps2(query) {
    return [
        {
            from: "user", to: "langchain",
            message: {from: "User", to: "LangChain Client", content: query.question},
            description: "User submits query"
        },
        {
            from: "langchain", to: "langchain",
            message: {from: "LangChain", to: "Self", content: "Preparing system prompt with tool descriptions..."},
            description: "Prepare context"
        },
        {
            from: "langchain", to: "ollama",
            message: {from: "LangChain", to: "Ollama", content: `System: You have calculator and weather tools\nUser: ${query.question}`},
            description: "Send to LLM"
        },
        {
            from: "ollama", to: "ollama",
            message: {from: "Ollama", to: "Self", content: "Analyzing query... Need to use tool!"},
            description: "LLM reasoning"
        },
        {
            from: "ollama", to: "langchain",
            message: {from: "Ollama", to: "LangChain", content: `{"tool": "${query.tool}", "arguments": ${JSON.stringify(query.args)}}`},
            description: "LLM decides tool"
        },
        {
            from: "langchain", to: "langchain",
            message: {from: "LangChain", to: "Self", content: `Extracted tool call: ${query.tool}`},
            description: "Parse tool call"
        },
        {
            from: "langchain", to: "mcpClient",
            message: {from: "LangChain", to: "MCP Client", content: `call_tool("${query.tool}", ${JSON.stringify(query.args)})`},
            description: "Request MCP tool"
        },
        {
            from: "mcpClient", to: "mcpServer",
            message: {from: "MCP Client", to: "MCP Server", content: `Execute: ${query.tool}(${JSON.stringify(query.args)})`},
            description: "Forward to server"
        },
        {
            from: "mcpServer", to: "tools",
            message: {from: "MCP Server", to: "Tools", content: `Run ${query.tool} with args`},
            description: "Execute tool"
        },
        {
            from: "tools", to: "langchain",
            message: {from: "Tools", to: "LangChain", content: `Result: ${query.result}`},
            description: "Return result"
        },
        {
            from: "langchain", to: "ollama",
            message: {from: "LangChain", to: "Ollama", content: `Tool returned: ${query.result}`},
            description: "Send result to LLM"
        },
        {
            from: "ollama", to: "user",
            message: {from: "Ollama", to: "User", content: query.answer},
            description: "Final answer"
        }
    ];
}

let steps2 = getSteps2(currentQuery2);

function initFlowchart() {
    const svg = document.getElementById('flowchart');
    const svgNS = "http://www.w3.org/2000/svg";

    svg.innerHTML = '';

    const edges = [
        {from: 'user', to: 'langchain'},
        {from: 'langchain', to: 'ollama'},
        {from: 'langchain', to: 'mcpClient'},
        {from: 'mcpClient', to: 'mcpServer'},
        {from: 'mcpServer', to: 'tools'},
    ];

    const edgeGroup = document.createElementNS(svgNS, 'g');
    edgeGroup.id = 'edges';

    edges.forEach((edge) => {
        const from = nodes[edge.from];
        const to = nodes[edge.to];

        const path = document.createElementNS(svgNS, 'path');
        const fromX = from.x;
        const fromY = from.y + from.height;
        const toX = to.x;
        const toY = to.y;

        const d = `M ${fromX} ${fromY} L ${toX} ${toY}`;
        path.setAttribute('d', d);
        path.setAttribute('class', 'edge');
        path.setAttribute('id', `edge-${edge.from}-${edge.to}`);
        path.setAttribute('stroke-dasharray', '5,5');

        edgeGroup.appendChild(path);
    });

    svg.appendChild(edgeGroup);

    const nodeGroup = document.createElementNS(svgNS, 'g');
    nodeGroup.id = 'nodes';

    Object.entries(nodes).forEach(([id, node]) => {
        const g = document.createElementNS(svgNS, 'g');
        g.setAttribute('class', 'node');
        g.setAttribute('id', `node-${id}`);

        const rect = document.createElementNS(svgNS, 'rect');
        rect.setAttribute('class', 'node-rect');
        rect.setAttribute('x', node.x - node.width/2);
        rect.setAttribute('y', node.y);
        rect.setAttribute('width', node.width);
        rect.setAttribute('height', node.height);

        const text = document.createElementNS(svgNS, 'text');
        text.setAttribute('class', 'node-text');
        text.setAttribute('x', node.x);
        text.setAttribute('y', node.y + node.height/2 + 5);

        const lines = node.label.split('\n');
        lines.forEach((line, i) => {
            const tspan = document.createElementNS(svgNS, 'tspan');
            tspan.textContent = line;
            tspan.setAttribute('x', node.x);
            tspan.setAttribute('dy', i === 0 ? 0 : '1.2em');
            text.appendChild(tspan);
        });

        g.appendChild(rect);
        g.appendChild(text);
        nodeGroup.appendChild(g);
    });

    svg.appendChild(nodeGroup);

    const packetGroup = document.createElementNS(svgNS, 'g');
    packetGroup.id = 'packets';
    svg.appendChild(packetGroup);
}

function animateStep(stepIndex) {
    if (stepIndex >= steps2.length) return;

    const step = steps2[stepIndex];

    document.querySelectorAll('.node').forEach(n => n.classList.remove('active', 'pulsing'));
    document.querySelectorAll('.edge').forEach(e => e.classList.remove('active'));
    document.querySelectorAll('.data-packet').forEach(p => p.remove());

    const fromNode = document.getElementById(`node-${step.from}`);
    const toNode = document.getElementById(`node-${step.to}`);

    if (fromNode) fromNode.classList.add('active', 'pulsing');

    setTimeout(() => {
        if (fromNode) fromNode.classList.remove('pulsing');

        if (step.from !== step.to) {
            animateDataPacket(step.from, step.to);

            setTimeout(() => {
                if (toNode) toNode.classList.add('active');
            }, 500);
        }
    }, 300);

    updateMessages(stepIndex);
}

function animateDataPacket(fromId, toId) {
    const svgNS = "http://www.w3.org/2000/svg";
    const packetGroup = document.getElementById('packets');

    const from = nodes[fromId];
    const to = nodes[toId];

    if (!from || !to || fromId === toId) return;

    const edgeId = `edge-${fromId}-${toId}`;
    const edge = document.getElementById(edgeId);
    if (edge) edge.classList.add('active');

    const packet = document.createElementNS(svgNS, 'circle');
    packet.setAttribute('class', 'data-packet active');
    packet.setAttribute('cx', from.x);
    packet.setAttribute('cy', from.y + from.height);

    packetGroup.appendChild(packet);

    const startX = from.x;
    const startY = from.y + from.height;
    const endX = to.x;
    const endY = to.y;

    const duration = 1000 / playbackSpeed;
    const startTime = Date.now();

    function animate() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);

        const currentX = startX + (endX - startX) * progress;
        const currentY = startY + (endY - startY) * progress;

        packet.setAttribute('cx', currentX);
        packet.setAttribute('cy', currentY);

        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            setTimeout(() => {
                packet.remove();
                if (edge) edge.classList.remove('active');
            }, 200);
        }
    }

    animate();
}

function updateMessages(stepIndex) {
    const messageLog = document.getElementById('messageLog');
    const messages = steps2.slice(0, stepIndex + 1).map((step, idx) => {
        const isActive = idx === stepIndex;
        return `
            <div class="message ${isActive ? 'active' : ''}">
                <div class="timestamp">Step ${idx + 1}</div>
                <div class="from-to">${step.message.from} → ${step.message.to}</div>
                <div class="content">${step.message.content}</div>
            </div>
        `;
    });

    messageLog.innerHTML = messages.join('');

    const activeMsg = messageLog.querySelector('.message.active');
    if (activeMsg) {
        activeMsg.scrollIntoView({behavior: 'smooth', block: 'nearest'});
    }
}

function updateProgress2() {
    const progress = ((currentStep2 + 1) / totalSteps2) * 100;
    document.getElementById('progressFill2').style.width = progress + '%';
    document.getElementById('currentStep2').textContent = currentStep2 + 1;
}

function play() {
    if (isPlaying) return;
    isPlaying = true;
    document.getElementById('playBtn').style.display = 'none';
    document.getElementById('pauseBtn').style.display = 'block';

    playInterval = setInterval(() => {
        if (currentStep2 < totalSteps2 - 1) {
            currentStep2++;
            animateStep(currentStep2);
            updateProgress2();
        } else {
            pause();
        }
    }, 2000 / playbackSpeed);
}

function pause() {
    isPlaying = false;
    document.getElementById('playBtn').style.display = 'block';
    document.getElementById('pauseBtn').style.display = 'none';
    if (playInterval) {
        clearInterval(playInterval);
        playInterval = null;
    }
}

function next2() {
    pause();
    if (currentStep2 < totalSteps2 - 1) {
        currentStep2++;
        animateStep(currentStep2);
        updateProgress2();
    }
}

function prev2() {
    pause();
    if (currentStep2 > 0) {
        currentStep2--;
        animateStep(currentStep2);
        updateProgress2();
    }
}

function reset2() {
    pause();
    currentStep2 = 0;
    animateStep(currentStep2);
    updateProgress2();
}

// Event listeners for Tab 2
document.getElementById('playBtn').addEventListener('click', play);
document.getElementById('pauseBtn').addEventListener('click', pause);
document.getElementById('nextBtn2').addEventListener('click', next2);
document.getElementById('prevBtn2').addEventListener('click', prev2);
document.getElementById('resetBtn2').addEventListener('click', reset2);

document.getElementById('speedSlider').addEventListener('input', (e) => {
    playbackSpeed = parseFloat(e.target.value);
    document.getElementById('speedValue').textContent = playbackSpeed.toFixed(1);

    if (isPlaying) {
        pause();
        play();
    }
});

document.querySelectorAll('.query-option').forEach(option => {
    option.addEventListener('click', () => {
        document.querySelectorAll('.query-option').forEach(o => o.classList.remove('selected'));
        option.classList.add('selected');

        const queryType = option.dataset.query;
        currentQuery2 = queries2[queryType];
        steps2 = getSteps2(currentQuery2);
        totalSteps2 = steps2.length;
        document.getElementById('totalSteps2').textContent = totalSteps2;

        reset2();
    });
});

document.getElementById('liveMode').addEventListener('click', () => {
    document.getElementById('liveMode').classList.add('active');
    document.getElementById('replayMode').classList.remove('active');
    reset2();
    play();
});

document.getElementById('replayMode').addEventListener('click', () => {
    document.getElementById('replayMode').classList.add('active');
    document.getElementById('liveMode').classList.remove('active');
    pause();
});

// Keyboard shortcuts for Tab 2
document.addEventListener('keydown', (e) => {
    // Only handle if Tab 2 is active
    if (!document.getElementById('animated').classList.contains('active')) return;

    if (e.key === ' ') {
        e.preventDefault();
        if (isPlaying) pause();
        else play();
    } else if (e.key === 'ArrowRight') {
        next2();
    } else if (e.key === 'ArrowLeft') {
        prev2();
    } else if (e.key === 'r' || e.key === 'R') {
        reset2();
    }
});

// Initialize Tab 2
initFlowchart();
animateStep(currentStep2);
updateProgress2();
