from collections import defaultdict

import pandas as pd
from harvesttext import get_sanguo, get_sanguo_entity_dict, HarvestText, get_baidu_stopwords
from matplotlib import pyplot as plt

from draw_graph import draw_graph
from draw_community import draw_community
import networkx as nx
from pyecharts.charts import Graph
import community

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

partition = community.best_partition(G_main)         # Louvain算法划分社区
comm_dict = defaultdict(list)
for person in partition:
    comm_dict[partition[person]].append(person)

draw_community(0, G_main, comm_dict)  # 绘制社区 1 的子图

