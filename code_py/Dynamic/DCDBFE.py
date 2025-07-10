
import os

import networkx as nx

from collections import defaultdict
import time
from tqdm import tqdm
from comm_utils import *


def str_to_int(x):
    return [[int(v) for v in line.split()] for line in x]


def node_addition(G, addnodes, communitys):
    change_comm = set()
    processed_edges = set()

    for u in tqdm(addnodes, desc='Adding nodes'):
        neighbors_u = G.neighbors(u)
        neig_comm = set()
        pc = set()
        for v in neighbors_u:
            if v in communitys:
                neig_comm.add(communitys[v])
            pc.add((u, v))
            pc.add((v, u))
        if len(neig_comm) > 1:
            change_comm |=  neig_comm
            lab = max(communitys.values()) + 1
            communitys[u] = lab
            change_comm.add(lab)
        else:
            if len(neig_comm) == 1:
                communitys[u] = list(neig_comm)[0]
                processed_edges |=  pc
            else:
                x = max(communitys.values()) + 1
                communitys[u] = x

    return change_comm, processed_edges, communitys



def node_deletion(G, delnodes, communitys):
    change_comm = set()
    processed_edges = set()
    for u in delnodes:
        neighbors_u = G.neighbors(u)
        neig_comm = set()
        for v in neighbors_u:
            if v in communitys:
                neig_comm.add(communitys[v])
            processed_edges.add((u, v))
            processed_edges.add((v, u))
        del communitys[u]
        change_comm = change_comm | neig_comm
    return change_comm, processed_edges, communitys


def edge_addition(addedges, communitys):
    change_comm = set()
    for item in tqdm(addedges, desc='Adding edges'):
        neig_comm = set()
        neig_comm.add(communitys[item[0]])
        neig_comm.add(communitys[item[1]])
        if len(neig_comm) > 1:
            change_comm |=  neig_comm
    return change_comm

def edge_deletion(deledges, communitys):
    change_comm = set()
    for item in deledges:
        neig_comm = set()
        neig_comm.add(communitys[item[0]])
        neig_comm.add(communitys[item[1]])
        if len(neig_comm) == 1:
            change_comm = change_comm | neig_comm

    return change_comm

def getchangegraph(all_change_comm, newcomm, Gt):
    Gte = nx.Graph(undirected=True)
    com_key = newcomm.keys()
    for v in Gt.nodes():
        if v not in com_key or newcomm[v] in all_change_comm:
            neig_v = Gt.neighbors(v)
            for u in neig_v:
                if u not in com_key or newcomm[u] in all_change_comm:
                    Gte.add_edge(v, u)

    return Gte




nodecount_comm = defaultdict(int)


def CDBFE(G):
    deg = G.degree()
    node_community = {node: node for node in G.nodes()}
    Neigb = {node: set(neighbors) for node, neighbors in G.adj.items()}
    nodes = list(G.nodes())
    comm_map = {node: {node} for node in nodes}

    st_coff = defaultdict(float)
    for node in tqdm(nodes, desc='Calculating Sorensen Similarity'):
        Nv = Neigb[node]
        for u in Nv:
            if (node, u) in st_coff: continue
            k1 = (node, u)
            k2 = (u, node)

            Nu = Neigb[u]
            c1, c2, c3 = len(Nv & Nu), len(Nv), len(Nu)
            y = c1 / (c2 + c3)
            st_coff[k1] = y
            st_coff[k2] = y




    for node in tqdm(nodes, desc='Confirming initial community'):
        deg_node = deg[node]
        flag = True
        maxsimdeg = 0
        selected = node
        if deg_node == 1:
            node_community[node] = node_community[list(Neigb[node])[0]]
            comm_map[node_community[list(Neigb[node])[0]]].add(node)
        else:
            for neig in Neigb[node]:
                deg_neig = deg[neig]
                if flag is True and deg_node <= deg_neig:
                    flag = False
                    break

            if flag is False:
                for neig in Neigb[node]:

                    nodesimdeg = deg[neig] * st_coff[(node, neig)]
                    if nodesimdeg > maxsimdeg:
                        selected = neig
                        maxsimdeg = nodesimdeg
                    node_community[node] = node_community[selected]
                    comm_map[node_community[selected]].add(node)
                    comm_map[node_community[node]].discard(node)



    per_Neigh = defaultdict(int)
    t_Neigh = defaultdict(set)
    init_inf_nodes = defaultdict(set)

    for node in tqdm(nodes, desc="BFS for 3-hop neighbors"):
        visited = {node}  # 已访问节点（包括自身）
        current_level = {node}  # 当前层节点
        all_neighbors = set()  # 存储所有阶邻居（不含自身）

        for _ in range(2):
            next_level = set()
            for n in current_level:
                # 扩展未访问的邻居
                new_neighbors = Neigb[n] - visited
                next_level |= new_neighbors
                visited |= new_neighbors
            all_neighbors |= next_level
            current_level = next_level
        t_Neigh[node] = all_neighbors
        comm_nodes = comm_map[node_community[node]]
        x_nodes = comm_nodes & t_Neigh[node]
        init_inf_nodes[node] = x_nodes
        per_Neigh[node] = len(x_nodes)

    itern = 0
    while itern < 5:
        itern += 1
        for node in tqdm(nodes, desc= f'round{itern}'):
            neiglist = Neigb[node]
            cur_p = per_Neigh[node]
            nodeneig_comm =  [node_community[n] for n in neiglist]
            cur_p_neig = sum(per_Neigh[neig] for neig in neiglist)

            for neig_comm in nodeneig_comm:

                node_pre_comm = node_community[node]
                new_p_neig = 0
                if node_pre_comm != neig_comm:
                    inf_nodes = comm_map[node_pre_comm] & comm_map[neig_comm]
                    new_p = len(inf_nodes)

                    if cur_p <= new_p:

                        if cur_p == new_p:
                            for newneig in neiglist:
                                if newneig in inf_nodes:
                                    new_p_neig += per_Neigh[newneig]+1
                                elif newneig in init_inf_nodes[node]:
                                    new_p_neig += per_Neigh[newneig]-1
                                else:
                                    new_p_neig += per_Neigh[newneig]
                            if cur_p_neig < new_p_neig:
                                cur_p = new_p
                                cur_p_neig = new_p_neig
                                node_community[node] = neig_comm
                                for newneig in neiglist:
                                    if newneig in inf_nodes:
                                       per_Neigh[newneig] += 1
                                    elif newneig in init_inf_nodes[node]:
                                        per_Neigh[newneig] -= 1

                        else:
                            cur_p_neig = sum(per_Neigh[neig] for neig in neiglist)
                            cur_p = new_p
                            per_Neigh[node] = new_p



    return node_community









def conver_comm_to_lab(comm1):
    overl_community = {}
    for node_v, com_lab in comm1.items():
        if com_lab in overl_community.keys():
            overl_community[com_lab].append(node_v)
        else:
            overl_community.update({com_lab: [node_v]})
    return overl_community







if __name__ == '__main__':
    for name in ["tweet2012_dy", "tweet2018_dy"]:
        print("-" * 40)
        print(f"dataset:{name}")
        all_time=[]
        edges_added = set()
        edges_removed = set()
        nodes_added = set()
        nodes_removed = set()
        t1_s = time.time()
        G = nx.Graph(undirected=True)
        path = DATASETS[name]["graph"]
        r_path = os.path.join(DATASETS[name]["out_file"], "DCDBFE")
        os.makedirs(r_path, exist_ok=True)

        print('T1:')
        with open(path + "/1.txt", 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        a, b, w = int(parts[0]), int(parts[1]), float(parts[2])
                        G.add_edge(a, b)

        comm = CDBFE(G)
        initcomm = conver_comm_to_lab(comm)
        comm_va = list(initcomm.values())
        t1_e = time.time()
        all_time.append(round(t1_e - t1_s, 2))
        with open(r_path + "1.txt", "w") as f_new:
            for nodes in comm_va:
                nodes = [str(n) for n in nodes]
                f_new.write("\t".join(nodes) + "\n")

        G1 = G
        G2 = nx.Graph(undirected=True)
        i = 2
        while os.path.exists(path + f"/{i}.txt"):
                print(f'T{i}:')

                t_s = time.time()
                with open(path + f"/{i}.txt", 'r') as f:
                    for line in f:
                        if line.strip():
                            parts = line.strip().split('\t')
                            if len(parts) >= 2:
                                a, b, w = int(parts[0]), int(parts[1]), float(parts[2])
                                G2.add_edge(a, b)

                total_nodes = set(G1.nodes()) | set(G2.nodes())
                nodes_added = set(G2.nodes()) - set(G1.nodes())
                nodes_removed = set(G1.nodes()) - set(G2.nodes())
                edges_added = set(G2.edges()) - set(G1.edges())
                edges_removed = set(G1.edges()) - set(G2.edges())

                all_change_comm = set()
                addn_ch_comm, addn_pro_edges, addn_commu = node_addition(G2, nodes_added, comm)

                edges_added = edges_added - addn_pro_edges

                all_change_comm = all_change_comm | addn_ch_comm


                deln_ch_comm, deln_pro_edges, deln_commu = node_deletion(G1, nodes_removed, addn_commu)
                all_change_comm = all_change_comm | deln_ch_comm
                edges_removed = edges_removed - deln_pro_edges

                adde_ch_comm = edge_addition(edges_added, deln_commu)
                all_change_comm = all_change_comm | adde_ch_comm
                dele_ch_comm = edge_deletion(edges_removed, deln_commu)
                all_change_comm = all_change_comm | dele_ch_comm
                newcomm = deln_commu
                unchangecomm = set(newcomm.values()) - all_change_comm
                unchcommunity = {key: value for key, value in newcomm.items() if value in unchangecomm}
                Gtemp = getchangegraph(all_change_comm, newcomm, G2)

                unchagecom_maxlabe = 0
                if len(unchangecomm) > 0:
                    unchagecom_maxlabe = max(unchangecomm)
                if Gtemp.number_of_edges() < 1:
                    comm = newcomm
                else:
                    getnewcomm = CDBFE(Gtemp)

                    mergecomm = {}
                    mergecomm.update(unchcommunity)
                    mergecomm.update(getnewcomm)
                    comm = mergecomm
                t_e = time.time()
                all_time.append(round(t_e - t_s, 2))
                r_comm = conver_comm_to_lab(comm)
                with open(r_path + f"/{i}.txt", "w") as f_new:
                    for _, nodes in r_comm.items():
                        nodes = [str(n) for n in nodes]
                        f_new.write("\t".join(nodes) + "\n")
                G1.clear()
                G1.add_edges_from(G2.edges())
                G2.clear()
                i += 1
        print('Done')
        print('All time:', all_time)
        Evaluate_Xmeasures(r_path, DATASETS[name]["ground_truth"])
        print("-" * 40)

