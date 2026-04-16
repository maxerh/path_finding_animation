# Path finding animation

This project visualizes the shortest path between two selected points on a map. The path finding process is animated.

## Path finding algorithms
- A*
- Dijkstra
- Bidirectional Dijkstra
- Bellman-Ford
- BFS
- DFS

## Getting started

Setting up environment
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Start app
```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

Open Browser at http://127.0.0.1:8000

NOTE: Fetching street data may take some time