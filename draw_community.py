from draw_graph import draw_graph

def draw_community(community_id, graph, comm_dict, title="", alpha=1.0, node_scale=100, figsize=(8, 6), node_color='skyblue', edge_color='grey', font_size=10, font_color='black', save_path=None):
    members = comm_dict[community_id]
    subgraph = graph.subgraph(members)

    draw_graph(subgraph, title=f"Community {community_id}", alpha=alpha, node_scale=node_scale, figsize=figsize, node_color=node_color, edge_color=edge_color, font_size=font_size, font_color=font_color, save_path=save_path)


