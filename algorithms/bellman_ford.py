import math


def algo_bellman_ford(G, source, target):
    dist = {n: math.inf for n in G.nodes}
    dist[source] = 0
    prev = {source: None}
    visited = []
    edges = [(u, v, d.get("length", 1)) for u, v, d in G.edges(data=True)]
    # Limit iterations for large graphs to keep response time reasonable
    nodes = list(G.nodes)
    n = min(len(nodes), 800)
    for i in range(n - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                visited.append((v, dist[v]))
                updated = True
        if not updated:
            break
    path = []
    cur = target
    while cur is not None and cur in prev or cur == source:
        path.append(cur)
        cur = prev.get(cur)
        if cur is None:
            break
    path.reverse()
    if not path or path[0] != source:
        return visited, []
    return visited, path