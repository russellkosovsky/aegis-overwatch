// backend/static/script.js

document.addEventListener('DOMContentLoaded', () => {
    const nodesContainer = document.getElementById('nodes-container');
    const apiStatusLight = document.getElementById('api-status-light');
    const apiStatusText = document.getElementById('api-status-text');

    // Function to fetch network status from our Flask API
    async function fetchNetworkStatus() {
        try {
            const response = await fetch('/api/network/status');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const nodes = await response.json();
            
            // Update API status indicator
            apiStatusLight.classList.remove('bg-yellow-500', 'bg-red-500', 'animate-pulse');
            apiStatusLight.classList.add('bg-green-500');
            apiStatusText.textContent = 'Live';

            renderNodes(nodes);

        } catch (error) {
            console.error("Failed to fetch network status:", error);
            apiStatusLight.classList.remove('bg-yellow-500', 'bg-green-500');
            apiStatusLight.classList.add('bg-red-500');
            apiStatusText.textContent = 'Error';
            nodesContainer.innerHTML = `
                <div class="col-span-full bg-red-900/50 text-red-300 p-4 rounded-lg">
                    <strong>Connection Error:</strong> Could not fetch data from the backend server. Is it running?
                </div>
            `;
        }
    }

    // Function to render the node data onto the page
    function renderNodes(nodes) {
        // Clear any existing content (like loading skeletons)
        nodesContainer.innerHTML = '';

        if (nodes.length === 0) {
            nodesContainer.innerHTML = '<p class="col-span-full">No nodes found in the network.</p>';
            return;
        }

        nodes.forEach(node => {
            const statusColor = node.is_active ? 'text-green-400' : 'text-red-400';
            const statusText = node.is_active ? 'ONLINE' : 'OFFLINE';

            const nodeCard = document.createElement('div');
            nodeCard.className = 'bg-gray-800 rounded-lg p-5 shadow-lg transform hover:scale-105 transition-transform duration-300';
            
            nodeCard.innerHTML = `
                <div class="flex justify-between items-start">
                    <h3 class="text-xl font-bold text-white">${node.name}</h3>
                    <span class="font-semibold ${statusColor}">${statusText}</span>
                </div>
                <div class="mt-4">
                    <p class="text-sm text-gray-400 font-medium">Neighbors:</p>
                    <ul class="text-sm text-gray-300 mt-2 space-y-1">
                        ${node.neighbors.length > 0 ? 
                            node.neighbors.map(n => `<li>- ${n.name} (${n.latency}ms)</li>`).join('') : 
                            '<li>None</li>'
                        }
                    </ul>
                </div>
            `;
            nodesContainer.appendChild(nodeCard);
        });
    }

    // Fetch the status when the page loads
    fetchNetworkStatus();
});
