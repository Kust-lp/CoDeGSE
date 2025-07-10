import os

from sklearn.metrics import normalized_mutual_info_score

import xmeasures

DATASETS={
   "amazon":{"graph":"../../data/amazon/com-amazon.ungraph.txt", "ground_truth":"../../data/amazon/com-amazon.all.dedup.cmty.txt",
             "overlapping":True, "weighted":False, "directed":False,"dynamic":False, "out_file":"../../data/amazon/result/"},

    "youtube":{"graph":"../../data/youtube/com-youtube.ungraph.txt", "ground_truth":"../../data/youtube/com-youtube.all.cmty.txt",
               "overlapping":True, "weighted":False, "directed":False,"dynamic":False, "out_file":"../../data/youtube/result/"},

    "LiveJournal":{"graph":"../../data/LiveJournal/com-lj.ungraph.txt", "ground_truth":"../../data/LiveJournal/com-lj.all.cmty.txt",
                   "overlapping":True, "weighted":False, "directed":False,"dynamic":False, "out_file":"../../data/LiveJournal/result/"},

    "dblp":{"graph":"../../data/dblp/com-dblp.ungraph.txt", "ground_truth":"../../data/dblp/com-dblp.all.cmty.txt",
            "overlapping":True, "weighted":False, "directed":False,"dynamic":False, "out_file":"../../data/dblp/result/"},

    "orkut":{"graph":"../../data/orkut/com-orkut.ungraph.txt", "ground_truth":"../../data/orkut/com-orkut.all.cmty.txt",
             "overlapping":True, "weighted":False, "directed":False,"dynamic":False, "out_file":"../../data/orkut/result/"},

    "friendster":{"graph":"../../data/friendster/com-friendster.ungraph.txt", "ground_truth":"../../data/friendster/com-friendster.all.cmty.txt",
                  "overlapping":True, "weighted":False, "directed":False,"dynamic":False,    "out_file":"../../data/friendster/result/"},

    "wiki":{"graph":"../../data/wiki/com-Wiki.ungraph.txt", "ground_truth":"../../data/wiki/com-Wiki.all.cmty.txt",
            "overlapping":True, "weighted":False, "directed":True,"dynamic":False, "out_file":"../../data/wiki/result/"},

    "tweet2012":{"graph":"../../data/tweet2012/awgraph.txt", "ground_truth":"../../data/tweet2012/cmty.txt",
                 "overlapping":False, "weighted":True, "directed":False,"dynamic":False, "out_file":"../../data/tweet2012/result/"},

    "tweet2018":{"graph":"../../data/tweet2018/awgraph.txt", "ground_truth":"../../data/tweet2018/cmty.txt",
                 "overlapping":False, "weighted":True, "directed":False,"dynamic":False, "out_file":"../../data/tweet2018/result/"},

    "LFR_50K":{"graph":"../../data/LFR_50K/awgraph.txt", "ground_truth":"../../data/LFR_50K/cmty.txt",
               "overlapping":False, "weighted":True, "directed":False,"dynamic":False, "out_file":"../../data/LFR_50K/result/"},

    "LFR_100K":{"graph":"../../data/LFR_100K/awgraph.txt", "ground_truth":"../../data/LFR_100K/cmty.txt",
                "overlapping":False, "weighted":True, "directed":False,"dynamic":False, "out_file":"../../data/LFR_100K/result/"},

    "LFR_200K":{"graph":"../../data/LFR_200K/awgraph.txt", "ground_truth":"../../data/LFR_200K/cmty.txt",
                "overlapping":False, "weighted":True, "directed":False,"dynamic":False, "out_file":"../../data/LFR_200K/result/"},

    "LFR_500K":{"graph":"../../data/LFR_500K/awgraph.txt", "ground_truth":"../../data/LFR_500K/cmty.txt",
                "overlapping":False, "weighted":True, "directed":False,"dynamic":False, "out_file":"../../data/LFR_500K/result/"},

    "LFR_1M":{"graph":"../../data/LFR_1M/awgraph.txt", "ground_truth":"../../data/LFR_1M/cmty.txt",
              "overlapping":False, "weighted":True, "directed":False,"dynamic":False, "out_file":"../../data/LFR_1M/result/"},

    "tweet2012_dy": {"graph": "../../data/tweet2012_dy/ntwk", "ground_truth": "../../data/tweet2012_dy/gt",
                  "overlapping": False, "weighted": True, "directed": False, "dynamic": True, "out_file": "../../data/tweet2012_dy/result/"},

    "tweet2018_dy": {"graph": "../../data/tweet2018/ntwk", "ground_truth": "../../data/tweet2018_dy/gt",
                  "overlapping": False, "weighted": True, "directed": False, "dynamic": True, "out_file": "../../data/tweet2018_dy/result/"},
}

def read_ture_cluster(path,name):
    cmty = []
    keep_nodes = []
    cmty_num = 0
    with open(path) as f:
        for line in f:
            if line.startswith('#') : continue
            nodes = line.rstrip('\n').split('\t')
            # nodes = line.rstrip('\n').split(' ')
            nodes = [int(n) for n in nodes]
            cmty_num += 1
            if name == "tweet2012" or name =="tweet2018" or name == "wiki":
                cmty.append(nodes)
                keep_nodes += nodes
            else:
                if len(nodes)>2:
                    cmty.append(nodes)
                    keep_nodes += nodes

    return cmty, set(keep_nodes),cmty_num

def filter_nodes(division,gt_nodes):
    pred_comm = []
    if type(division) == list:
        for v in division:
            v = gt_nodes.intersection(v)
            if len(v) > 0:
                pred_comm.append(v)
    else:
        for k, v in division.items():
            v = gt_nodes.intersection(v)
            if len(v) > 0:
                pred_comm.append(v)
    return pred_comm



def Evaluate_Xmeasures(R_path,G_path):
    scores = []
    j = 1
    while os.path.exists(os.path.join(R_path, str(j) + ".txt")) and os.path.exists(os.path.join(G_path, str(j)+  ".txt")):
        result_path = os.path.join(R_path, str(j) + ".txt")
        gt_path = os.path.join(G_path, str(j)+  ".txt")

        division = []
        with open(result_path, "r") as f:
            for line in f:
                nodes = line.strip().split()
                nodes = [int(n) for n in nodes]
                division.append(nodes)


        gt_comm = []
        all_nodes = []
        with open(gt_path, "r") as f:
            for line in f:
                nodes = line.strip().split()
                nodes = [int(n) for n in nodes]
                gt_comm.append(nodes)
                all_nodes += nodes

        all_nodes = list(set(all_nodes))


        pred = [-1]*(len(all_nodes))
        for c,nodes in enumerate(division):
            for n in nodes:
                pred[n] = c

        gt = [-1]*(len(all_nodes))
        for c,nodes in enumerate(gt_comm):
            for n in nodes:
                gt[n] = c
        nmi = normalized_mutual_info_score(gt, pred)

        f1 = xmeasures.f1(division, gt_comm, "tmp")
        scores.append({'NMI': float(nmi), 'F1 ': float(f1.split()[0])})
        j += 1
    line = [' ' * 5] + [f'  T{i:02d}  ' for i in range(1,len(scores)+1)]
    print("".join(line))

    score_names = ["NMI", "F1 "]
    for n in score_names:
        line = [f'{n} '] + [f'  {s[n]*100:1.2f}' for s in scores]
        print("".join(line))

    print('\n', flush=True)












