// backend/static/script.js

document.addEventListener('DOMContentLoaded', () => {
    const graphContainer = document.getElementById('network-graph');
    const apiStatusLight = document.getElementById('api-status-light');
    const apiStatusText = document.getElementById('api-status-text');

    let network = null; // This will hold our Vis.js network instance

    // --- Graph Configuration ---
    const options = {
        nodes: {
            shape: 'dot',
            size: 20,
            font: {
                size: 14,
                color: '#ffffff'
            },
            borderWidth: 2
        },
        edges: {
            width: 2,
            font: {
                size: 12,
                color: '#d1d5db', // text-gray-300
                strokeWidth: 4,
                strokeColor: '#1f2937' // bg-gray-800
            }
        },
        physics: {
            enabled: true,
            solver: 'forceAtlas2Based',
            forceAtlas2Based: {
                gravitationalConstant: -50,
                centralGravity: 0.01,
                springLength: 100,
                springConstant: 0.08,
            },
        },
        interaction: {
            hover: true,
            tooltipDelay: 200,
        },
    };

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
            // If the network hasn't been created yet, create it
            const visData = {
                nodes: new vis.DataSet(data.nodes),
                edges: new vis.DataSet(data.edges),
            };
            network = new vis.Network(graphContainer, visData, options);
        } else {
            // If the network already exists, just update its data
            network.setData({
                nodes: data.nodes,
                edges: data.edges
            });
        }
    }

    // Initial fetch
    fetchGraphData();

    // Set up polling to keep the graph live
    setInterval(fetchGraphData, 3000);
});
