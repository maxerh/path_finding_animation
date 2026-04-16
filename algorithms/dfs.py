def algo_dfs(G, source, target):
    """
    Note: DFS is not a shortest-path algorithm
    :param G:
    :param source:
    :param target:
    :return:
    """
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
    path = []
    cur = target
    while cur is not None:
        path.append(cur)
        cur = prev.get(cur)
    path.reverse()
    return visited_order, path
