import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

def draw_graph(graph, title="", alpha=1.0, node_scale=100, figsize=(16, 12), node_color='skyblue', edge_color='grey', font_size=12, font_color='black', save_path=None):
    """
    绘制网络图。

    Args:
        graph (nx.Graph): 要绘制的网络图。
        title (str): 图的标题。
        alpha (float): 节点和边的透明度。
        node_scale (int or float): 节点的大小比例。
        figsize (tuple): 图的大小。
        node_color (str): 节点的颜色。
        edge_color (str): 边的颜色。
        font_size (int): 节点标签的字体大小。
        font_color (str): 节点标签的字体颜色。
        save_path (str, optional): 保存图像的路径。如果为 None，则不保存图像。
    """

    plt.figure(figsize=figsize)
    plt.title(title)

    # pos = nx.spring_layout(graph, k=0.3)  # 使用spring_layout算法计算节点位置，k值调整节点间距
    pos = nx.kamada_kawai_layout(graph)
    node_sizes = [graph.degree(node) * node_scale for node in graph.nodes()] # 根据节点度数调整节点大小

    font = fm.FontProperties(family='Heiti TC')
    nx.draw_networkx_nodes(graph, pos, node_size=node_sizes, node_color=node_color, alpha=alpha)
    nx.draw_networkx_edges(graph, pos, edge_color=edge_color, alpha=alpha)
    nx.draw_networkx_labels(graph, pos, font_size=font_size, font_color=font_color, font_family=font.get_family() )

    plt.axis('off')  # 关闭坐标轴

    if save_path:
        plt.savefig(save_path, format="PNG")  # 保存图像

    plt.show()