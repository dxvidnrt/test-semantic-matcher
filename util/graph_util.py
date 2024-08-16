from typing import List
from semantic_matcher import model


def find_reachable_matches(start_semantic_id: str, matches: List[model.SemanticMatch], cut_off_score: float) -> List[
    model.SemanticMatch]:
    if start_semantic_id is None:
        return []
    # Dictionary to store adjacency list
    graph = {}

    # Build the graph
    for match in matches:
        if match.base_semantic_id not in graph:
            graph[match.base_semantic_id] = []
        graph[match.base_semantic_id].append(match)

    # To store the result
    reachable_matches = []

    def dfs(current_node: str, current_score: float, path: List[str]):
        # Check each neighbor of the current node
        if current_node in graph and current_node not in path:
            new_path = path + [current_node]
            for neighbor in graph[current_node]:
                new_score = current_score * neighbor.score
                # Check if the new score is above the cut-off limit
                if new_score > cut_off_score:
                    # Add the neighbor to the path and the results
                    reachable_matches.append(neighbor)
                    # Recursively call dfs for the neighbor
                    dfs(neighbor.match_semantic_id, new_score, new_path)

    # Start DFS from the starting semantic ID with an initial score of 1
    dfs(start_semantic_id, 1.0, [])

    return reachable_matches
