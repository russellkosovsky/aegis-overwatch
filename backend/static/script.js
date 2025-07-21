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

    let network = null; // This will hold our Vis.js network instance

    // --- Graph Configuration (Restored) ---
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
        } catch (error) {
            displayResult(`Error: ${error.message}`, true);
        }
    });

    // --- Initial Application Load ---
    function initialize() {
        fetchGraphData();
        populateNodeSelectors();
        setInterval(fetchGraphData, 3000); // Polling for graph updates
    }

    initialize();
});
