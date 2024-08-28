import json
import os
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.spatial import ConvexHull
import numpy as np

show_source_name = False
show_source_overlay = False
show_source_legend = False

show_UML_legend = True


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
                    score = round(match["score"], 2)
                    match_source = match["meta_information"]["matchSource"]
                    # Add edge from base_semantic_id to match_semantic_id with the score as weight
                    G.add_edge(base_semantic_id, match_semantic_id, score=score, matchSource=match_source)
                    for semantic_id in [base_semantic_id, match_semantic_id]:
                        if G.has_node(match_semantic_id):
                            if "matchSource" in G.nodes[semantic_id]:
                                G.nodes[semantic_id]["matchSource"].add(match_source)
                            else:
                                G.nodes[semantic_id]["matchSource"] = set(match_source)
                        else:
                            G.add_node(semantic_id, matchSource=set(match_source))

    # Modify the label of each node
    node_labels = {node: node.split("/")[-1] for node in G.nodes()}  # Use only the last part of the ID
    nx.set_node_attributes(G, node_labels, "label")

    # Group nodes by the first part of their ID
    groups = {node: node.split("/")[0] for node in G.nodes()}
    nx.set_node_attributes(G, groups, "group")

    # Assign a color to each group
    unique_groups = sorted(list(set(groups.values())))

    # Use tab20c for distinct colors
    distinct_colors = plt.cm.get_cmap('tab20c')  # Create a colormap with specific number of colors

    # Create the color map for each group
    color_map = {group: distinct_colors(i / 20) for i, group in enumerate(unique_groups)}

    # Apply the color map to nodes
    node_colors = [color_map[groups[node]] for node in G.nodes()]

    # Draw the graph
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx_nodes(G, pos, node_size=500, node_color=node_colors)
    nx.draw_networkx_edges(G, pos, width=2.0, alpha=0.8, edge_color="black")

    # Draw labels manually to ensure centering
    for node, (x, y) in pos.items():
        plt.text(x, y, node_labels[node], fontsize=12, ha='center', va='center')

    # Draw edge labels manually above the edges
    edge_labels = {}
    for u, v, key, data in G.edges(data=True, keys=True):
        if (u, v) in edge_labels:
            edge_labels[(u, v)].append(str(data['score']))
        else:
            edge_labels[(u, v)] = [str(data['score'])]

    edge_labels = {key: '\n'.join(value) for key, value in edge_labels.items()}

    # Calculate positions for edge labels above the edges
    for (u, v), label in edge_labels.items():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        midpoint = ((x0 + x1) / 2, (y0 + y1) / 2)
        direction = np.array([x1 - x0, y1 - y0])
        normal = np.array([-direction[1], direction[0]])
        normal = normal / np.linalg.norm(
            normal) * 0.1  # Adjust this value to control the distance of labels above edges
        plt.text(midpoint[0] + normal[0], midpoint[1] + normal[1], label,
                 fontsize=10, ha='center', va='center', bbox=dict(facecolor='none', edgecolor='none'))

    # Get the matchSource for each edge and use it to group nodes
    match_sources = {}
    for u, v, data in G.edges(data=True):
        match_source = data["matchSource"]
        if match_source not in match_sources:
            match_sources[match_source] = set()
        match_sources[match_source].update([u, v])

    # Draw convex hulls around nodes with the same matchSource
    handles = []
    labels = []
    hull_color_map = plt.cm.get_cmap('Set2', len(match_sources))
    for idx, (match_source, nodes) in enumerate(match_sources.items()):
        if len(nodes) > 2:  # Convex hull requires at least 3 points
            points = np.array([pos[node] for node in nodes])
            hull = ConvexHull(points)
            hull_points = points[hull.vertices]
            centroid = np.mean(hull_points, axis=0)
            enlarged_hull_points = centroid + 1.1 * (hull_points - centroid)  # Scale points outward from the centroid
            polygon = plt.Polygon(enlarged_hull_points, fill=True, edgecolor=None, alpha=0.15,
                                  facecolor=hull_color_map(idx))
            if show_source_overlay:
                plt.gca().add_patch(polygon)
                handles.append(polygon)
                labels.append(match_source)
            # Add matchSource label at the centroid of the hull
            if show_source_name:
                plt.text(centroid[0], centroid[1], match_source, horizontalalignment='center',
                         verticalalignment='center',
                         fontsize=8, bbox=dict(facecolor='white', alpha=0.5))
        elif len(nodes) == 2:  # Special case for two points
            points = np.array([pos[node] for node in nodes])
            # Calculate the midpoint and create a larger rectangle around the line
            node_radius = 0.035
            vector = points[1] - points[0]
            vector_node_radius = vector / np.linalg.norm(vector) * 2 * node_radius
            perp_vector = np.array([-vector[1], vector[0]])
            perp_vector = perp_vector / np.linalg.norm(perp_vector) * 0.05  # Adjust the scale as needed
            rectangle = np.array([points[0] + perp_vector - vector_node_radius,
                                  points[1] + perp_vector + vector_node_radius,
                                  points[1] - perp_vector + vector_node_radius,
                                  points[0] - perp_vector - vector_node_radius])
            polygon = plt.Polygon(rectangle, fill=True, edgecolor=None, alpha=0.15, facecolor=hull_color_map(idx))
            if show_source_overlay:
                plt.gca().add_patch(polygon)
                handles.append(polygon)
                labels.append(match_source)
            # Add matchSource label above the area
            midpoint = np.mean(points, axis=0)
            above_point = midpoint + np.array([0, 0.1])  # Shift the label above the midpoint
            if show_source_name:
                plt.text(above_point[0], above_point[1], match_source, horizontalalignment='center',
                         verticalalignment='center',
                         fontsize=8, bbox=dict(facecolor='white', alpha=0.5))
        elif len(nodes) == 1:  # Special case for a single node
            node = next(iter(nodes))
            point = pos[node]
            circle = plt.Circle(point, radius=0.1, edgecolor=None, fill=True,
                                alpha=0.15, facecolor=hull_color_map(idx))  # Adjusted the radius to be larger
            if show_source_overlay:
                plt.gca().add_patch(circle)
                handles.append(circle)
                labels.append(match_source)
            # Add matchSource label next to the node
            if show_source_name:
                plt.text(point[0], point[1] + 0.12, match_source, horizontalalignment='center',
                         verticalalignment='center',
                         fontsize=8, bbox=dict(facecolor='white', alpha=0.5))

    # Create legend
    legend_handles = [mpatches.Patch(color=color_map[group], label=group) for group in unique_groups]

    if show_UML_legend:
        uml_legend = plt.legend(handles=legend_handles, title="UML", loc="best")
        plt.gca().add_artist(uml_legend)

    if show_source_legend:
        match_source_legend = plt.legend(handles, labels, title="Match Source", loc="best")
        plt.gca().add_artist(match_source_legend)

    plt.title("Semantic Matches of SMS", loc="center")
    plt.axis("off")

    plt.savefig(f'{image_path}/graph.png')
    plt.show()


def main():
    data_path = os.path.join('./')
    image_path = os.path.join('./images')
    os.makedirs(image_path, exist_ok=True)  # Ensure the image directory exists
    show_graph(data_path, image_path)


if __name__ == "__main__":
    main()
