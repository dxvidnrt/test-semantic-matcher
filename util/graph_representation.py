import json
import os
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def show_graph(directory, image_path):
    G = nx.MultiDiGraph()

    # Iterate over all JSON files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "r") as file:
                matches = json.load(file)
                for match in matches:
                    base_semantic_id = match["base_semantic_id"]
                    match_semantic_id = match["match_semantic_id"]
                    score = match["score"]
                    # Add edge from base_semantic_id to match_semantic_id with the score as weight
                    G.add_edge(base_semantic_id, match_semantic_id, score=score)

    # Modify the label of each node
    node_labels = {node: node.split("/")[-1] for node in G.nodes()}  # Use only the last part of the ID
    nx.set_node_attributes(G, node_labels, "label")

    # Group nodes by the first part of their ID
    groups = {node: node.split("/")[0] for node in G.nodes()}
    nx.set_node_attributes(G, groups, "group")

    # Assign a color to each group
    unique_groups = list(set(groups.values()))
    color_map = {group: plt.cm.tab20(i / len(unique_groups)) for i, group in enumerate(unique_groups)}
    node_colors = [color_map[groups[node]] for node in G.nodes()]

    # Draw the graph
    pos = nx.spring_layout(G, seed=42)  # Positions nodes using Fruchterman-Reingold force-directed algorithm
    nx.draw_networkx_nodes(G, pos, node_size=200, node_color=node_colors)
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5, edge_color="gray")
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8)

    # Draw edge labels for MultiDiGraph
    edge_labels = {}
    for u, v, key, data in G.edges(data=True, keys=True):
        if (u, v) in edge_labels:
            edge_labels[(u, v)].append(f"{key}: {data['score']}")
        else:
            edge_labels[(u, v)] = [f"{key}: {data['score']}"]

    edge_labels = {key: '\n'.join(value) for key, value in edge_labels.items()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)

    # Create legend
    legend_handles = [mpatches.Patch(color=color_map[group], label=group) for group in unique_groups]
    plt.legend(handles=legend_handles, title="Groups", loc="best")

    plt.title("Semantic ID Graph")
    plt.axis("off")

    plt.savefig(f'{image_path}/graph.png')
    plt.show()