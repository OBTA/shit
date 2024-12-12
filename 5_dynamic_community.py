from collections import defaultdict

import numpy as np
import pandas as pd
from harvesttext import get_sanguo, get_sanguo_entity_dict, HarvestText, get_baidu_stopwords
from matplotlib import pyplot as plt

from draw_graph import draw_graph
from draw_community import draw_community
import networkx as nx
from pyecharts.charts import Graph
import community
from moviepy.video.io.VideoFileClip import VideoClip
import imageio

# 文本列表，每个元素为一章的文本
chapters = get_sanguo()

# 获取指称
entity_mention_dict, entity_type_dict = get_sanguo_entity_dict()


ht = HarvestText()
# 加载模型
ht.add_entities(entity_mention_dict, entity_type_dict)

# 准备工作
# 由于有时使用缩写，这里做一个微调
doc = chapters[0].replace("操", "曹操")
# 分句
ch1_sentences = ht.cut_sentences(doc)
# 获得所有的二连句
doc_ch01 = [ch1_sentences[i] + ch1_sentences[i + 1] for i in range(len(ch1_sentences) - 1)]
ht.set_linking_strategy("freq")

# 建立网络
G = ht.build_entity_graph(doc_ch01, used_types=["人名"])  # 对所有人物建立网络，即社交网络

# 挑选主要人物画图
important_nodes = [node for node in G.nodes if G.degree[node] >=5]
G_sub = G.subgraph(important_nodes).copy()

# draw_graph(G_sub,alpha=0.5,node_scale=30,figsize=(12,8))

# 过滤停用词以提高质量
stopwords = get_baidu_stopwords()

# for i, doc in enumerate(ht.get_summary(doc_ch01, topK=3, stopwords=stopwords)):
#     print(i, doc)

G_chapters = []
for chapter in chapters:
    sentences = ht.cut_sentences(chapter)  # 分句
    docs = [sentences[i] + sentences[i + 1] for i in range(len(sentences) - 1)]
    G_chapters.append(ht.build_entity_graph(docs, used_types=["人名"]))

# 合并各张子图
G_global = nx.Graph()
for G0 in G_chapters:
    for (u, v) in G0.edges:
        if G_global.has_edge(u, v):
            G_global[u][v]["weight"] += G0[u][v]["weight"]
        else:
            G_global.add_edge(u, v, weight=G0[u][v]["weight"])

# 忽略游离的小分支只取最大连通分量
largest_comp = max(nx.connected_components(G_global), key=len)
G_global = G_global.subgraph(largest_comp).copy()
# print(G_global)

important_nodes = [node for node in G_global.nodes if G_global.degree[node]>=30]
G_main = G_global.subgraph(important_nodes).copy()


# 或者其他中文字体，例如 'Heiti TC', 'Microsoft YaHei' 等
plt.rcParams['font.sans-serif'] = ['Heiti TC']
plt.rcParams['axes.unicode_minus'] = False
width, step = 10, 5
range0 = range(0, len(G_chapters) - width + 1, step)
num_frames, fps = len(range0), 1
duration = num_frames / fps
pos_global = nx.spring_layout(G_main, k=0.3) #  建议添加 k 参数调整节点间距


def make_frame_mpl(t):
    i = step * int(t * fps)
    G_part = nx.Graph()

    for G0 in G_chapters[i:i + width]:
        for u, v, weight in G0.edges(data='weight', default=1): # 获取边的权重
            if G_part.has_edge(u, v):
                G_part[u][v]["weight"] =  G_part[u][v].get("weight", 0) + weight # 处理可能没有 'weight' 属性的情况
            else:
                G_part.add_edge(u, v, weight=weight)

    largest_comp = max(nx.connected_components(G_part), key=len)
    used_nodes = set(largest_comp) & set(G_main.nodes)
    G = G_part.subgraph(used_nodes)

    fig = plt.figure(figsize=(12, 8), dpi=100)
    nx.draw_networkx_nodes(G, pos_global, node_size=[G.degree(x) * 10 for x in G.nodes])
    # nx.draw_networkx_edges(G, pos_global)  # 如果需要绘制边
    nx.draw_networkx_labels(G, pos_global, font_size=10, font_family='Heiti TC') #  设置字体大小和字体
    plt.xlim([-1.2, 1.2]) #  稍微扩大xlim和ylim范围，避免标签被裁剪
    plt.ylim([-1.2, 1.2])
    plt.axis("off")
    plt.title(f"第{i + 1}到第{i + width + 1}章的社交网络", fontsize=16, fontfamily='Heiti TC') # 设置标题字体大小和字体

    fig.canvas.draw()
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
    image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    plt.close(fig)  # 关闭图形，释放资源
    return image


animation = VideoClip(make_frame_mpl, duration=duration)
animation.write_gif("./images/三国社交网络变化.gif", fps=fps)
