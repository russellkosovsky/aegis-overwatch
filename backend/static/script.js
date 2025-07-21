// backend/static/script.js

document.addEventListener('DOMContentLoaded', () => {
    const nodesContainer = document.getElementById('nodes-container');
    const apiStatusLight = document.getElementById('api-status-light');
    const apiStatusText = document.getElementById('api-status-text');

    async function fetchNetworkStatus() {
        try {
            const response = await fetch('/api/network/status');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const nodes = await response.json();
            
            apiStatusLight.className = 'w-4 h-4 rounded-full bg-green-500';
            apiStatusText.textContent = 'Live';
            renderNodes(nodes);
        } catch (error) {
            console.error("Failed to fetch network status:", error);
            apiStatusLight.className = 'w-4 h-4 rounded-full bg-red-500';
            apiStatusText.textContent = 'Error';
            // To prevent the error message from overwriting user actions,
            // we only show it if there's no content.
            if (nodesContainer.innerHTML.includes('col-span-full')) {
                nodesContainer.innerHTML = `<div class="col-span-full bg-red-900/50 text-red-300 p-4 rounded-lg"><strong>Connection Error:</strong> Could not fetch data from the backend server.</div>`;
            }
        }
    }

    async function updateNodeStatus(nodeName, action) {
        try {
            const response = await fetch(`/api/node/${nodeName}/${action}`, {
                method: 'POST',
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            // Immediately refresh the dashboard to show the change instantly
            fetchNetworkStatus();

        } catch (error) {
            console.error(`Failed to set node ${nodeName} to ${action}:`, error);
        }
    }

    function renderNodes(nodes) {
        nodesContainer.innerHTML = '';
        if (nodes.length === 0) {
            nodesContainer.innerHTML = '<p class="col-span-full">No nodes found.</p>';
            return;
        }

        nodes.forEach(node => {
            const statusColor = node.is_active ? 'text-green-400' : 'text-red-400';
            const statusText = node.is_active ? 'ONLINE' : 'OFFLINE';
            
            const actionButton = node.is_active 
                ? `<button data-node-name="${node.name}" data-action="offline" class="node-action-btn mt-4 w-full text-center bg-yellow-600 hover:bg-yellow-700 text-white font-bold py-2 px-4 rounded transition-colors duration-300">Take Offline</button>`
                : `<button data-node-name="${node.name}" data-action="online" class="node-action-btn mt-4 w-full text-center bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors duration-300">Bring Online</button>`;

            const nodeCard = document.createElement('div');
            nodeCard.className = 'bg-gray-800 rounded-lg p-5 shadow-lg flex flex-col justify-between';
            
            nodeCard.innerHTML = `
                <div>
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
                </div>
                ${actionButton} 
            `;
            nodesContainer.appendChild(nodeCard);
        });
    }

    nodesContainer.addEventListener('click', (event) => {
        if (event.target.classList.contains('node-action-btn')) {
            const nodeName = event.target.dataset.nodeName;
            const action = event.target.dataset.action;
            event.target.textContent = 'Updating...';
            event.target.disabled = true;
            updateNodeStatus(nodeName, action);
        }
    });

    // Fetch the status when the page loads
    fetchNetworkStatus();

    // --- NEW: Set up polling to refresh the status every 3 seconds (3000ms) ---
    setInterval(fetchNetworkStatus, 3000);
});
