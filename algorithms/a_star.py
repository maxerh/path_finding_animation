import math
import heapq
from helpers import haversine, reconstruct


def algo_astar(G, source, target, weight='length', max_speed_ms: float = None):
    # Heuristic must be unit-compatible with edge weights.
    # distance mode: h = haversine metres (admissible: straight line <= road length)
    # time mode:     h = haversine / max_speed_in_graph seconds
    #   Dividing by the fastest possible speed gives a lower bound on remaining
    #   travel time -> always admissible -> A* returns the true optimum.
    def heuristic(u):
        d_m = haversine(G, u, target)
        if weight == 'travel_time':
            spd = max_speed_ms if (max_speed_ms and max_speed_ms > 0) else 50 / 3.6
            return d_m / spd
        return d_m

    dist = {source: 0}
    prev = {source: None}
    visited = []
    seen = set()
    pq = [(heuristic(source), 0, source)]
    while pq:
        f, d, u = heapq.heappop(pq)
        if u in seen:
            continue
        seen.add(u)
        visited.append((u, d))
        if u == target:
            break
        for _, v, data in G.edges(u, data=True):
            w = data.get(weight, 1)
            nd = d + w
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd + heuristic(v), nd, v))
    return visited, reconstruct(prev, source, target)