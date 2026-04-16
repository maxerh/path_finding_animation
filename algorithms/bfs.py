from collections import deque

def algo_bfs(G, source, target):
    visited = []
    prev = {source: None}
    queue = deque([source])
    seen = {source}
    while queue:
        u = queue.popleft()
        visited.append((u, len(visited)))
        if u == target:
            break
        for _, v in G.edges(u):
            if v not in seen:
                seen.add(v)
                prev[v] = u
                queue.append(v)
    path = []
    cur = target
    while cur is not None:
        path.append(cur)
        cur = prev.get(cur)
    path.reverse()
    if path[0] != source:
        return visited, []
    return visited, path