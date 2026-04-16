import math
import heapq

def algo_bidirectional_dijkstra(G, source, target):
    """
    Expands from source and target simultaneously over forward and reversed edges.
    Terminates when the sum of the two frontier distances exceeds the best known path.
    Typically explores roughly sqrt of the nodes that standard Dijkstra would explore.
    """
    if source == target:
        return [], [source]

    dist_f = {source: 0}
    prev_f = {source: None}
    pq_f = [(0, source)]
    settled_f = set()

    dist_b = {target: 0}
    prev_b = {target: None}
    pq_b = [(0, target)]
    settled_b = set()

    visited = []
    best = math.inf
    meeting = None

    def update_best(node):
        nonlocal best, meeting
        if node in dist_f and node in dist_b:
            c = dist_f[node] + dist_b[node]
            if c < best:
                best = c
                meeting = node

    while pq_f or pq_b:
        df = pq_f[0][0] if pq_f else math.inf
        db = pq_b[0][0] if pq_b else math.inf
        if df + db >= best:
            break

        if df <= db:
            d, u = heapq.heappop(pq_f)
            if u in settled_f:
                continue
            settled_f.add(u)
            visited.append((u, d))
            update_best(u)
            for _, v, data in G.edges(u, data=True):
                w = data.get("length", 1)
                nd = d + w
                if nd < dist_f.get(v, math.inf):
                    dist_f[v] = nd
                    prev_f[v] = u
                    heapq.heappush(pq_f, (nd, v))
                    update_best(v)
        else:
            d, u = heapq.heappop(pq_b)
            if u in settled_b:
                continue
            settled_b.add(u)
            visited.append((u, d))
            update_best(u)
            for p, _, data in G.in_edges(u, data=True):
                w = data.get("length", 1)
                nd = d + w
                if nd < dist_b.get(p, math.inf):
                    dist_b[p] = nd
                    prev_b[p] = u
                    heapq.heappush(pq_b, (nd, p))
                    update_best(p)

    if meeting is None:
        return visited, []

    # Forward half: source -> meeting
    path_f = []
    cur = meeting
    seen_r = set()
    while cur is not None:
        if cur in seen_r:
            break
        seen_r.add(cur)
        path_f.append(cur)
        cur = prev_f.get(cur)
    path_f.reverse()

    # Backward half: meeting -> target (follow prev_b forward)
    path_b = []
    cur = prev_b.get(meeting)
    seen_r2 = set()
    while cur is not None:
        if cur in seen_r2:
            break
        seen_r2.add(cur)
        path_b.append(cur)
        cur = prev_b.get(cur)

    return visited, path_f + path_b