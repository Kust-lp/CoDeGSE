
import os

import networkx as nx

from collections import defaultdict
import time

import numpy as np

from tqdm import tqdm

from comm_utils import DATASETS, Evaluate_Xmeasures


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



nodecount_comm = set()


def CDME(G):
    deg = G.degree()
    nodes = list(G.nodes())



    inv_log_deg = {node: 1.0 / (np.log(d)+0.00000001) for node,d in deg}



    Neigb = {node: set(neighbors) for node, neighbors in G.adj.items()}
    node_community =  {node: node for node in G.nodes()}
    st = defaultdict(float)
    for node in tqdm(G.nodes(), desc="compute the AA"):
        Nv = Neigb[node]
        for u in Nv:
            if (node, u) in st: continue
            k1 = (node, u)
            k2 = (u, node)
            Nu = Neigb[u]
            common_neighbors = Nv & Nu
            sim = sum(inv_log_deg[node] for node in  common_neighbors)
            st[k1] = sim
            st[k2] = sim

    per = defaultdict(float)
    for node in tqdm(nodes, desc="Matthew effect"):
        deg_node = deg[node]
        flag = True
        maxsimdeg = 0
        selected = node
        if deg_node <= 1:
            if deg_node == 0: continue
            node_community[node] = node_community[list(Neigb[node])[0]]
            nodecount_comm.add(node_community[node])

        else:
            for neig in Neigb[node]:
                if flag  and deg_node <= deg[neig]:
                    flag = False
                    break

            if flag is False:
                for neig in Neigb[node]:
                    deg_neig = deg[neig]
                    keys = (node, neig)
                    nodesimdeg = deg_neig *  st[keys]
                    if nodesimdeg > maxsimdeg:
                        selected = neig
                        maxsimdeg = nodesimdeg

                    node_community[node] = node_community[selected]

                    nodecount_comm.add(node_community[selected])
                    per[node] += 1
                    per[neig] += 1



    for node in tqdm(nodes, desc="Community detection"):
        neiglist = Neigb[node]
        cur_p = per[node]
        cur_p_neig = sum(per[neig] for neig in neiglist)
        Neigb_comm = [node_community[n] for n in neiglist]

        for neig_comm in set(Neigb_comm):

            node_pre_comm = node_community[node]
            new_p_neig = 0
            if node_pre_comm != neig_comm:
                new_p = Neigb_comm.count(neig_comm)

                if cur_p <= new_p:

                    if cur_p == new_p:

                        for newneig in neiglist:
                            if Neigb[newneig] == neig_comm:
                                new_p_neig += per[newneig]+1
                            elif Neigb[newneig] == node_pre_comm:
                                new_p_neig += per[newneig] - 1
                            else:
                                new_p_neig += per[newneig]

                        if cur_p_neig < new_p_neig:
                            per[node] = new_p
                            cur_p = new_p
                            cur_p_neig = new_p_neig
                            for newneig in neiglist:
                                if Neigb[newneig] == neig_comm:
                                    per[newneig] += 1
                                elif Neigb[newneig] == node_pre_comm:
                                    per[newneig] -= 1
                                node_community[node] = neig_comm


                    else:
                        per[node] = new_p
                        cur_p = new_p
                        cur_p_neig = sum(per[neig] for neig in neiglist)



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
        r_path = os.path.join(DATASETS[name]["out_file"], "DCDME")
        os.makedirs(r_path, exist_ok=True)

        print('T1:')
        with open(path + "/1.txt", 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        a, b, w = int(parts[0]), int(parts[1]), float(parts[2])
                        G.add_edge(a, b)

        comm = CDME(G)
        initcomm = conver_comm_to_lab(comm)
        comm_va = list(initcomm.values())
        t1_e = time.time()
        all_time.append(round(t1_e - t1_s, 2))
        with open(r_path + "/1.txt", "w") as f_new:
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
                    getnewcomm = CDME(Gtemp)

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

