// backend/static/script.js

document.addEventListener('DOMContentLoaded', () => {
    // --- UI Elements ---
    const graphContainer = document.getElementById('network-graph');
    const apiStatusLight = document.getElementById('api-status-light');
    const apiStatusText = document.getElementById('api-status-text');
    const fromNodeSelect = document.getElementById('from-node');
    const toNodeSelect = document.getElementById('to-node');
    const payloadInput = document.getElementById('payload');
    const findPathBtn = document.getElementById('find-path-btn');
    const routeMsgBtn = document.getElementById('route-msg-btn');
    const resultsDisplay = document.getElementById('results-display');
    const eventLog = document.getElementById('event-log');

    let network = null; // This will hold our Vis.js network instance

    // --- Graph Configuration ---
    const options = {
        nodes: {
            shape: 'dot',
            size: 20,
            font: { size: 14, color: '#ffffff' },
            borderWidth: 2
        },
        edges: {
            width: 2,
            font: { size: 12, color: '#d1d5db', strokeWidth: 4, strokeColor: '#1f2937' }
        },
        physics: {
            enabled: true,
            solver: 'forceAtlas2Based',
        },
        interaction: {
            hover: true,
            tooltipDelay: 200,
        },
    };

    // --- API & Rendering Functions ---

    async function fetchGraphData() {
        try {
            const response = await fetch('/api/network/graph-data');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const graphData = await response.json();
            
            apiStatusLight.className = 'w-4 h-4 rounded-full bg-green-500';
            apiStatusText.textContent = 'Live';

            renderGraph(graphData);

        } catch (error) {
            console.error("Failed to fetch graph data:", error);
            apiStatusLight.className = 'w-4 h-4 rounded-full bg-red-500';
            apiStatusText.textContent = 'Error';
        }
    }

    function renderGraph(data) {
        if (!network) {
            const visData = {
                nodes: new vis.DataSet(data.nodes),
                edges: new vis.DataSet(data.edges),
            };
            network = new vis.Network(graphContainer, visData, options);

            // Add click listener only once when the network is created
            network.on("click", async (params) => {
                if (params.nodes.length > 0) {
                    const nodeId = params.nodes[0];
                    const node = network.body.data.nodes.get(nodeId);
                    const action = node.color === '#f87171' ? 'online' : 'offline'; // If red, action is 'online'
                    
                    try {
                        await fetch(`/api/node/${node.label}/${action}`, { method: 'POST' });
                        fetchGraphData(); // Refresh graph
                        fetchEventLog(); // Refresh log
                    } catch(error) {
                        console.error(`Failed to set node ${node.label} to ${action}:`, error);
                    }
                }
            });
        } else {
            network.setData({
                nodes: data.nodes,
                edges: data.edges
            });
        }
    }

    async function populateNodeSelectors() {
        try {
            const response = await fetch('/api/nodes');
            if (!response.ok) throw new Error('Failed to fetch node list');
            const nodeNames = await response.json();
            
            fromNodeSelect.innerHTML = '';
            toNodeSelect.innerHTML = '';

            nodeNames.forEach(name => {
                fromNodeSelect.add(new Option(name, name));
                toNodeSelect.add(new Option(name, name));
            });
            if (nodeNames.length > 1) {
                toNodeSelect.selectedIndex = 1;
            }
        } catch (error) {
            console.error(error);
            displayResult('Error: Could not load node list.', true);
        }
    }

    function displayResult(message, isError = false) {
        resultsDisplay.textContent = message;
        resultsDisplay.className = isError 
            ? 'mt-4 p-4 bg-red-900/50 rounded-md min-h-[100px] text-red-300 whitespace-pre-wrap'
            : 'mt-4 p-4 bg-gray-900 rounded-md min-h-[100px] text-green-300 whitespace-pre-wrap';
    }

    async function fetchEventLog() {
        try {
            const response = await fetch('/api/events');
            if (!response.ok) throw new Error('Failed to fetch event log');
            const events = await response.json();
            renderEventLog(events);
        } catch (error) {
            console.error(error);
        }
    }

    function renderEventLog(events) {
        eventLog.innerHTML = '';
        if (events.length === 0) {
            eventLog.innerHTML = '<p class="text-gray-500">No events yet...</p>';
            return;
        }
        events.forEach(event => {
            const logEntry = document.createElement('div');
            logEntry.className = 'text-xs p-2 rounded';
            let statusIndicator = '';

            if (event.status === 'SUCCESS') {
                logEntry.classList.add('bg-green-900/50', 'text-green-300');
                statusIndicator = '✅';
            } else if (event.status === 'FAILED') {
                logEntry.classList.add('bg-red-900/50', 'text-red-300');
                statusIndicator = '❌';
            } else {
                logEntry.classList.add('bg-blue-900/50', 'text-blue-300');
                statusIndicator = 'ℹ️';
            }

            logEntry.innerHTML = `
                <span class="font-mono">${event.timestamp}</span>
                <span class="font-bold mx-2">${statusIndicator}</span>
                <span>${event.details}</span>
            `;
            eventLog.appendChild(logEntry);
        });
    }

    // --- Event Listeners for Controls ---
    findPathBtn.addEventListener('click', async () => {
        const fromNode = fromNodeSelect.value;
        const toNode = toNodeSelect.value;
        displayResult('Finding path...');
        
        try {
            const response = await fetch('/api/network/path', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ from_node: fromNode, to_node: toNode })
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.error || 'Pathfinding failed');
            
            const pathString = result.path.join(' -> ');
            displayResult(`Fastest Path:\n${pathString}\n\nTotal Latency: ${result.latency}ms`);
        } catch (error) {
            displayResult(`Error: ${error.message}`, true);
        }
    });

    routeMsgBtn.addEventListener('click', async () => {
        const fromNode = fromNodeSelect.value;
        const toNode = toNodeSelect.value;
        const payload = payloadInput.value;
        if (!payload) {
            displayResult('Error: Message payload cannot be empty.', true);
            return;
        }
        displayResult('Routing message...');

        try {
            const response = await fetch('/api/network/route', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ from_node: fromNode, to_node: toNode, payload: payload })
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.message || 'Routing failed');
            
            displayResult(result.message);
            fetchEventLog(); // Refresh log after action
        } catch (error) {
            displayResult(`Error: ${error.message}`, true);
        }
    });

    // --- Initial Application Load ---
    function initialize() {
        fetchGraphData();
        populateNodeSelectors();
        fetchEventLog();
        // Update both graph and log every 3 seconds
        setInterval(() => {
            fetchGraphData();
            fetchEventLog();
        }, 3000);
    }

    initialize();
});
