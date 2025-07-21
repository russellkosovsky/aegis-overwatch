# **Project Overwatch: A Real-Time Network Dashboard**

**Project Overwatch** is a full-stack web application that provides a real-time, interactive dashboard for visualizing and controlling the "Project Aegis" network simulator. It features a Python/Flask backend that runs the core simulation and exposes a REST API, and a vanilla JavaScript frontend that provides a dynamic user interface.

This project demonstrates a full software development lifecycle, from backend logic and API design to a responsive, user-friendly frontend interface.


## **Core Features**

* **Real-Time Visualization:** An interactive, physics-based graph of the network topology is rendered directly in the browser using Vis.js.  
* **Live Status Updates:** The dashboard automatically polls the backend every 3 seconds, updating node statuses (ONLINE/OFFLINE) and link latencies in real time.  
* **Interactive Simulation Control:**  
  * **Toggle Node Status:** Click directly on a node in the graph to take it offline or bring it back online.  
  * **Pathfinding:** Use UI controls to select two nodes and instantly calculate the fastest path between them using Dijkstra's algorithm.  
  * **Message Routing:** Send messages between any two nodes and see the result of the routing attempt.  
* **Live Event Log:** A running log on the dashboard displays the latest simulation events, such as status changes and message routing outcomes.  
* **RESTful API Backend:** A clean, well-documented Flask API serves as the bridge between the simulation engine and the frontend.  
* **Robust Backend Logic:** Built on the fully tested and documented Project Aegis simulation engine.

## **Technology Stack**

* **Backend:** Python, Flask  
* **Frontend:** HTML, Tailwind CSS, Vanilla JavaScript  
* **Visualization:** Vis.js (Network Module)  
* **Core Simulation:** The Python codebase from Project Aegis.  
* **Testing:** pytest, Flask Test Client, unittest.mock  
* **Code Quality:** black (Formatter)

## **Getting Started**

Follow these instructions to set up and run the project locally.

### **Prerequisites**

* Python 3.10+  
* A Python virtual environment tool (venv)

### **Setup and Installation**

1. **Clone the Repository**  
   git clone <https://gitlab.com/russellkosovsky/project-overwatch.git>  
   cd project-overwatch

2. Navigate to the Backend Directory  
   The Python application lives in the backend/ directory.  
   cd backend

3. **Create and Activate a Virtual Environment**  
   \# For macOS / Linux  
   python3 \-m venv venv  
   source venv/bin/activate

   \# For Windows  
   \# py \-m venv venv  
   \# .\\venv\\Scripts\\activate

4. Install Dependencies  
   Install all required Python packages from the requirements file.  
   pip install \-r requirements.txt

### **Running the Application**

Once the setup is complete, you can run the Flask web server.

1. Make sure you are in the project-overwatch/backend/ directory and your virtual environment is activated.  
2. Run the following command:  
   flask run

3. The server will start, and you will see output like this:  
    \* Running on http://127.0.0.1:5000

4. Open your web browser and navigate to **http://127.0.0.1:5000** to see the dashboard.

## **Running the Test Suite**

The project includes a comprehensive test suite for both the core simulator logic and the Flask API.

1. From the project-overwatch/backend/ directory (with your venv activated), run:  
   pytest

## **Project Structure**

project-overwatch/  
│  
├── .gitignore  
├── README.md               \# This file  
│  
└── backend/  
    ├── aegis\_simulator/    \# The core simulation engine  
    ├── static/             \# Frontend JavaScript and CSS  
    │   └── script.js  
    ├── templates/          \# Frontend HTML  
    │   └── index.html  
    ├── tests/              \# Python test suite  
    │   ├── test\_app.py  
    │   └── ...  
    ├── app.py              \# Flask application and API entry point  
    ├── network\_config.yml  \# Network definition file  
    ├── pytest.ini  
    ├── pyproject.toml  
    └── requirements.txt    \# Python dependencies  