from helpers import reconstruct


def algo_dfs(G, source, target, weight='length'):
    """DFS is not a shortest-path algorithm. It finds *a* path, often much longer than optimal."""
    visited_order = []
    prev = {source: None}
    stack = [source]
    seen = {source}
    found = False
    while stack:
        u = stack.pop()
        visited_order.append((u, len(visited_order)))
        if u == target:
            found = True
            break
        for _, v in G.edges(u):
            if v not in seen:
                seen.add(v)
                prev[v] = u
                stack.append(v)
    if not found:
        return visited_order, []
    return visited_order, reconstruct(prev, source, target)