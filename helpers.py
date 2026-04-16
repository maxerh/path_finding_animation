import math




def node_coords(G, node_id):
    d = G.nodes[node_id]
    return d["y"], d["x"]


def edge_coords(G, u, v):
    data = G.get_edge_data(u, v)
    if data is None:
        return []
    edge = list(data.values())[0]
    if "geometry" in edge:
        return [[lat, lng] for lng, lat in edge["geometry"].coords]
    u_d, v_d = G.nodes[u], G.nodes[v]
    return [[u_d["y"], u_d["x"]], [v_d["y"], v_d["x"]]]


def path_edges(G, path):
    edges = []
    for i in range(len(path) - 1):
        edges.extend(edge_coords(G, path[i], path[i + 1]))
    return edges


def haversine(G, u, v):
    u_d, v_d = G.nodes[u], G.nodes[v]
    lat1, lon1 = math.radians(u_d["y"]), math.radians(u_d["x"])
    lat2, lon2 = math.radians(v_d["y"]), math.radians(v_d["x"])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371000 * 2 * math.asin(math.sqrt(a))


def path_length(G, path):
    total = 0
    for i in range(len(path) - 1):
        data = G.get_edge_data(path[i], path[i + 1])
        if data:
            total += list(data.values())[0].get("length", 0)
    return round(total)


def reconstruct(prev, source, target):
    path = []
    cur = target
    visited_set = set()
    while cur is not None:
        if cur in visited_set:
            return []
        visited_set.add(cur)
        path.append(cur)
        cur = prev.get(cur)
    path.reverse()
    if not path or path[0] != source:
        return []
    return path