import math
import osmnx as ox
import networkx as nx
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from algorithms.bfs import algo_bfs
from algorithms.dfs import algo_dfs
from algorithms.a_star import algo_astar
from algorithms.dijkstra import algo_dijkstra
from algorithms.bellman_ford import algo_bellman_ford
from algorithms.bi_dijkstra import algo_bidirectional_dijkstra

from helpers import path_edges, path_length, node_coords

app = FastAPI()

# Cache: place_name -> G
graph_cache: dict[str, nx.MultiDiGraph] = {}
graph_bounds: dict[str, tuple] = {}


def _store_graph(key: str, G: nx.MultiDiGraph):
    graph_cache[key] = G
    lats = [d["y"] for _, d in G.nodes(data=True)]
    lngs = [d["x"] for _, d in G.nodes(data=True)]
    graph_bounds[key] = (min(lats), max(lats), min(lngs), max(lngs))


def get_graph_by_coords(lat: float, lng: float, dist: int) -> tuple[str, nx.MultiDiGraph]:
    key = f"coords:{round(lat, 3)},{round(lng, 3)},{dist}"
    if key not in graph_cache:
        G = ox.graph_from_point((lat, lng), dist=dist, network_type="drive")
        G = ox.add_edge_speeds(G)
        G = ox.add_edge_travel_times(G)
        _store_graph(key, G)
    return key, graph_cache[key]


def get_graph_by_place(place: str) -> tuple[str, nx.MultiDiGraph]:
    key = f"place:{place.lower().strip()}"
    if key not in graph_cache:
        G = ox.graph_from_place(place, network_type="drive")
        G = ox.add_edge_speeds(G)
        G = ox.add_edge_travel_times(G)
        _store_graph(key, G)
    return key, graph_cache[key]


def find_covering_graph(slat, slng, elat, elng) -> tuple[str, nx.MultiDiGraph]:
    """
    Load a graph that is guaranteed to contain both start and end points.
    Uses the bounding box of both points + 20% padding on each side.
    Checks all cached graphs first before downloading.
    """
    # Check if any existing cached graph already covers both points
    for key, G in graph_cache.items():
        b = graph_bounds[key]
        pad_lat = (b[1] - b[0]) * 0.02
        pad_lng = (b[3] - b[2]) * 0.02
        if (b[0] - pad_lat <= slat <= b[1] + pad_lat and
                b[0] - pad_lat <= elat <= b[1] + pad_lat and
                b[2] - pad_lng <= slng <= b[3] + pad_lng and
                b[2] - pad_lng <= elng <= b[3] + pad_lng):
            return key, G

    # Download new graph centered on midpoint, radius = max(dist_to_start, dist_to_end) + 25%
    mid_lat = (slat + elat) / 2
    mid_lng = (slng + elng) / 2
    cos_lat = math.cos(math.radians(mid_lat))

    # Distance from midpoint to each endpoint in meters
    dlat_s = abs(slat - mid_lat) * 111000
    dlng_s = abs(slng - mid_lng) * 111000 * cos_lat
    dlat_e = abs(elat - mid_lat) * 111000
    dlng_e = abs(elng - mid_lng) * 111000 * cos_lat

    max_half = max(dlat_s, dlng_s, dlat_e, dlng_e)
    dist = max(2000, int(max_half * 1.5))  # 50% buffer beyond furthest point

    return get_graph_by_coords(mid_lat, mid_lng, dist)


ALGORITHMS = {
    "dijkstra": algo_dijkstra,
    "bidirectional_dijkstra": algo_bidirectional_dijkstra,
    "astar": algo_astar,
    "bfs": algo_bfs,
    "dfs": algo_dfs,
    "bellman_ford": algo_bellman_ford,
}

# Algorithms that do NOT guarantee shortest path by distance
NON_SHORTEST = {"dfs", "bfs"}


# ---- API models ----

class LoadRequest(BaseModel):
    place: str


class PathRequest(BaseModel):
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    algorithm: str
    weight: str = "length"  # "length" (metres) or "travel_time" (seconds)
    place: str = ""  # optional hint; reused if covers both points


@app.post("/api/load")
def load_graph(req: LoadRequest):
    try:
        key, G = get_graph_by_place(req.place)
        b = graph_bounds[key]
        return {
            "key": key,
            "nodes": G.number_of_nodes(),
            "edges": G.number_of_edges(),
            "bounds": {"min_lat": b[0], "max_lat": b[1], "min_lng": b[2], "max_lng": b[3]},
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/path")
def find_path(req: PathRequest):
    if req.algorithm not in ALGORITHMS:
        raise HTTPException(status_code=400, detail="Unknown algorithm")

    try:
        if req.place:
            key, G = get_graph_by_place(req.place)
            b = graph_bounds[key]
            covers = (b[0] <= req.start_lat <= b[1] and b[0] <= req.end_lat <= b[1] and
                      b[2] <= req.start_lng <= b[3] and b[2] <= req.end_lng <= b[3])
            if not covers:
                key, G = find_covering_graph(req.start_lat, req.start_lng, req.end_lat, req.end_lng)
        else:
            key, G = find_covering_graph(req.start_lat, req.start_lng, req.end_lat, req.end_lng)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not load street graph: {e}")

    source = ox.nearest_nodes(G, req.start_lng, req.start_lat)
    target = ox.nearest_nodes(G, req.end_lng, req.end_lat)

    src_lat, src_lng = node_coords(G, source)
    tgt_lat, tgt_lng = node_coords(G, target)

    if source == target:
        raise HTTPException(status_code=400, detail="Start and end snap to the same node - pick points further apart")

    weight = req.weight if req.weight in ("length", "travel_time") else "length"
    algo_fn = ALGORITHMS[req.algorithm]
    visited, path = algo_fn(G, source, target, weight)

    step_sample = max(1, len(visited) // 600)
    steps = [
        {"lat": G.nodes[nid]["y"], "lng": G.nodes[nid]["x"]}
        for i, (nid, _) in enumerate(visited)
        if i % step_sample == 0
    ]

    polyline = path_edges(G, path)
    length_m = path_length(G, path, "length")
    travel_time_s = path_length(G, path, "travel_time")
    b = graph_bounds[key]

    return {
        "steps": steps,
        "path": polyline,
        "nodes_explored": len(visited),
        "path_length_m": length_m,
        "travel_time_s": travel_time_s,
        "path_nodes": len(path),
        "snapped_start": {"lat": src_lat, "lng": src_lng},
        "snapped_end": {"lat": tgt_lat, "lng": tgt_lng},
        "graph_nodes": G.number_of_nodes(),
        "graph_edges": G.number_of_edges(),
        "non_shortest": req.algorithm in NON_SHORTEST,
        "weight": weight,
        "bounds": {"min_lat": b[0], "max_lat": b[1], "min_lng": b[2], "max_lng": b[3]},
    }


app.mount("/", StaticFiles(directory="static", html=True), name="static")