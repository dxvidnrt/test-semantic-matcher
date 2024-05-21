import json
import networkx as nx
import matplotlib.pyplot as plt

"""
# JSON data
json_data = '''
{
    "s-heppner.com/semanticID/one": [
        {
            "base_semantic_id": "s-heppner.com/semanticID/one",
            "match_semantic_id": "s-heppner.com/semanticID/1",
            "score": 1.0,
            "meta_information": {
                "matchSource": "Defined by Sebastian Heppner"
            }
        },
        {
            "base_semantic_id": "s-heppner.com/semanticID/one",
            "match_semantic_id": "s-heppner.com/semanticID/two",
            "score": 0.8,
            "meta_information": {
                "matchSource": "Defined by Sebastian Heppner"
            }
        }
    ],
    "s-heppner.com/semanticID/two": [
        {
            "base_semantic_id": "s-heppner.com/semanticID/two",
            "match_semantic_id": "s-heppner.com/semanticID/2",
            "score": 1.0,
            "meta_information": {
                "matchSource": "Defined by Sebastian Heppner"
            }
        }
    ]
}
'''

# Load JSON data
data = json.loads(json_data)

"""

# Initialize a directed graph
G = nx.DiGraph()


# Function to extract the last part of the ID
def extract_last_part(semantic_id):
    return semantic_id.split('/')[-1]


# Assign subset levels
subset_levels = {
    "s-heppner.com": 0,
    "semanticID": 1,
}


def show_sms(graph: dict):
    # Iterate over the data to add nodes and edges
    nodes = []
    edges = []
    for base_id, matches in graph.items():
        nodes.append(base_id)
        for match in matches:
            base_semantic_id = match["base_semantic_id"]
            match_semantic_id = match["match_semantic_id"]
            score = match["score"]

            nodes.append(match_semantic_id)
            edges.append((base_semantic_id, match_semantic_id, score))

    G.add_nodes_from(set(nodes))
    for edge in edges:
        source, target, score = edge
        G.add_edge(source, target, weight=score)

    for node in G.nodes:
        subset = node.split("/")[0]
        G.nodes[node]["subset"] = subset
        G.nodes[node]["name"] = extract_last_part(node)

    # Create a hierarchical layout
    pos = nx.multipartite_layout(G, subset_key="subset")

    # Create labels
    labels = {node: G.nodes[node]["name"] for node in G.nodes}

    # Draw the graph
    plt.figure(figsize=(10, 8))
    nx.draw_networkx(G, pos, labels=labels, with_labels=True, node_size=2000, node_color="lightblue", font_size=12, font_weight="bold",
                     arrowsize=20)

    # Draw edge labels with the score
    edge_labels = {(u, v): d["weight"] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)

    plt.title("Hierarchical Graph Representation")
    plt.axis("off")  # Turn off the axis
    plt.show()
