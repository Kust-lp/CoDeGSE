import os
import random
from datetime import datetime

import leidenalg
import numpy as np
import igraph as ig
from sklearn.metrics import normalized_mutual_info_score

import xmeasures
from comm_utils import DATASETS


def Leiden(in_path,ground_truth,out_path,name):
    edges = []
    with open(in_path, 'r') as f:
        for line in f:
            if line.startswith('#'):continue
            if line.strip():
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    a, b, w = parts[0], parts[1], parts[2]
                    edges.append((int(a), int(b), float(w)))

    node_idx = {}
    nodes = []
    edges_m = []
    weight = []
    for a, b, w in edges:
        a = int(a)
        b = int(b)

        if a not in node_idx:
            node_idx[a] = len(nodes)
            nodes.append(a)

        if b not in node_idx:
            node_idx[b] = len(nodes)
            nodes.append(b)
        edges_m.append((node_idx[a], node_idx[b]))
        weight.append(w)

    print(f"edges: {len(edges)}  nodes: {len(nodes)} avg_degree: {2*len(edges)/len(nodes)}",end=" ")

    G = ig.Graph()
    G.add_vertices(len(nodes))
    G.add_edges(edges_m)
    G.es['weight'] = weight

    random.seed(1)
    ig.set_random_number_generator(random)
    start = datetime.now()

    pre_l = leidenalg.find_partition(G, leidenalg.ModularityVertexPartition).membership

    end = datetime.now()
    time_diff = end - start
    time_diff = round(time_diff.total_seconds(), 1)
    print(f"time consuming:{time_diff}")


    gt_comm = []
    with open(ground_truth, "r") as f:
        for line in f:
            ns = line.strip().split()
            ns = [int(n) for n in ns]
            gt_comm.append(ns)

    pre_comm_d = {}
    for n, com in enumerate(pre_l):
        if com not in pre_comm_d:
            pre_comm_d[com] = []
        pre_comm_d[com].append(nodes[n])

    pre_comm = list(pre_comm_d.values())

    nmi = xmeasures.nmi(pre_comm, gt_comm, name)

    f1 = xmeasures.f1(pre_comm, gt_comm, name)

    print(f'NMI: {float(nmi)*100:1.2f}, F1:, {float(f1.split()[0])*100:1.2f}')

    with open(out_path, 'w') as f:
        for  nodes in pre_comm:
            nodes = [str(n) for n in nodes]
            f.write("\t".join(nodes) + '\n')



    print("-" * 40)

if __name__ == "__main__":
    for name in ["tweet2012", "tweet2018", "LFR_50K", "LFR_100K", "LFR_200K", "LFR_500K", "LFR_1M"]:
        print("-" * 40)
        print(f"dataset:{name}")
        path = DATASETS[name]["out_file"]
        os.makedirs(os.path.dirname(path), exist_ok=True)
        out_path = os.path.join(path, "Leiden.txt")
        Leiden(DATASETS[name]["graph"], DATASETS[name]["ground_truth"], out_path, name)





