import copy
import os
from collections import defaultdict
from datetime import datetime
import numpy as np
import pandas as pd
import networkx as nx
from tqdm import tqdm

import onmi
import xmeasures
from comm_utils import read_ture_cluster, filter_nodes

from comm_utils import DATASETS


def slpa_nx(G, T, r):
    """
    Speaker-Listener Label Propagation Algorithm (SLPA)
    see http://arxiv.org/abs/1109.5720
    """
    np.random.seed(0)
    # Stage 1: Initialization
    print("Initialization...",end=" ")
    memory = {i: {i: 1} for i in G.nodes()}
    print("done")
    # Stage 2: Evolution
    print("Evolution:",end=" ")
    for t in range(T):
        print(t+1,end=", ")
        listeners_order = list(G.nodes())
        np.random.shuffle(listeners_order)

        for listener in listeners_order:
            speakers = G[listener].keys()
            if len(speakers) == 0:
                continue

            labels = defaultdict(int)

            for j, speaker in enumerate(speakers):
                # Speaker Rule
                total = float(sum(memory[speaker].values()))
                labels[
                    list(memory[speaker].keys())[
                        np.random.multinomial(
                            1, [freq / total for freq in memory[speaker].values()]
                        ).argmax()
                    ]
                ] += 1

            # Listener Rule
            accepted_label = max(labels, key=labels.get)

            # Update listener memory
            if accepted_label in memory[listener]:
                memory[listener][accepted_label] += 1
            else:
                memory[listener][accepted_label] = 1

    # Stage 3:
    for node, mem in memory.items():
        its = copy.copy(list(mem.items()))
        for label, freq in its:
            if freq / float(T + 1) < r:
                del mem[label]

    # Find nodes membership
    communities = {}
    for node, mem in memory.items():
        for label in mem.keys():
            if label in communities:
                communities[label].add(node)
            else:
                communities[label] = {node}
    print("done")

    # Remove nested communities
    nested_communities = set()
    keys = list(communities.keys())
    size = len(keys)-1
    print(f"community Num: {len(keys)}: ")
    for i, label0 in enumerate(keys[:-1]):
        print(f"\rFind duplicate communities: {i/size*100:.4f} %" ,end="",flush=True)
        comm0 = communities[label0]
        for label1 in keys[i + 1:]:
            comm1 = communities[label1]
            if comm0.issubset(comm1):
                nested_communities.add(label0)
            elif comm0.issuperset(comm1):
                nested_communities.add(label1)

    for comm in nested_communities:
        del communities[comm]

    return  list(communities.values())



def SLPA(g_path, t_path, name, save_path):
    if name == "wiki":
        df = pd.read_csv(g_path, delimiter='\t', skiprows=4, header=None, names=['FromNodeId', 'ToNodeId'])
        df['FromNodeId'], df['ToNodeId'] = np.minimum(df['FromNodeId'], df['ToNodeId']), np.maximum(
            df['FromNodeId'], df['ToNodeId'])

        df = df.drop_duplicates()

    else:
        df = pd.read_csv(g_path, delimiter='\t', skiprows=4, header=None, names=['FromNodeId', 'ToNodeId'])
    edges = df.values

    G = nx.Graph()
    G.add_edges_from(edges)
    start = datetime.now()

    coms =slpa_nx(G, T=11, r=0.1)

    end = datetime.now()
    time_diff = end - start
    time_diff = round(time_diff.total_seconds(), 1)

    print(f"time consuming:{time_diff}")

    ture_comm, keep_nodes, _ = read_ture_cluster(t_path, name)

    pre_comm = filter_nodes(coms, keep_nodes)

    print('n_clusters gt: ', len(ture_comm))
    print('n_clusters pred: ', len(pre_comm))

    with open(save_path+'SLPA.txt', 'w') as f:
        for comm in pre_comm:
            if len(comm) > 1:
                f.write('\t'.join(map(str, comm)) + '\n')

    nmi = onmi.overlapping_normalized_mutual_information(pre_comm, ture_comm, name)
    print('onmi: ', nmi, flush=True)

    f1 = xmeasures.f1(pre_comm, ture_comm, name)
    print('f1: ', f1)




if __name__ == '__main__':
    for name in [ "amazon" ,"youtube", "dblp","LiveJournal","orkut", "friendster","wiki"]:
        out_path = DATASETS[name]["out_file"]
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        print("-" * 40)
        print(f"dataset:{name}")

        SLPA(DATASETS[name]["graph"], DATASETS[name]["ground_truth"], name, out_path)



