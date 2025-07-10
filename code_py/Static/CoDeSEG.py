# -*- coding: utf8 -*-
import os
import subprocess
from datetime import datetime
import numpy as np

import onmi
import xmeasures
from comm_utils import read_ture_cluster, filter_nodes, DATASETS, Evaluate_Xmeasures
from dynamic.dynamic_netk_proprecess import Get_ntwk_change

Game_se = "../../code_c++/CoDeSEG/build/CoDeSEG"


def CodeSEG(in_path,out_path,ground_truth,name,overlap,weighted,directed,dynamic, it,tau, gamma,r, parallel,verbose):

    if not dynamic:
        out_path = os.path.join(out_path, "CoDeSEG.txt")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
    else:
        out_path = out_path + "CoDeSEG/"
        os.makedirs(out_path, exist_ok=True)
        in_path = os.path.dirname(in_path) + "/changed"
        if not os.path.exists(in_path):
            print("Get and save network snapshot changes...")
            Get_ntwk_change(os.path.dirname(in_path))

    args = [
        Game_se,
        "-i", in_path,
        "-o", out_path,
        "-n", str(it),
        "-t", ground_truth,
        "-e", str(tau),
        "-r", str(r),
        "-g", str(gamma),
        "-p", str(parallel),
    ]
    if (overlap):
        args.append("-x")
    if (weighted):
        args.append("-w")
    if (directed):
        args.append("-d")
    if verbose:
        args.append("-v")
    if dynamic:
        args.append("-c")

    result = subprocess.run(
        args,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    output = result.stdout
    print(output)

    if not dynamic:
        ture_comm, keep_nodes, _ = read_ture_cluster(ground_truth, name)

        division = []
        with open(out_path) as f:
            for line in f:
                nodes = line.strip().split()
                nodes = [int(n) for n in nodes]
                division.append(nodes)

        pre_comm = filter_nodes(division, keep_nodes)

        if not overlap:
            xnmi = xmeasures.nmi(pre_comm, ture_comm, name)
            print('nmi: ', xnmi, flush=True)
        else:
            nmi = onmi.overlapping_normalized_mutual_information(pre_comm, ture_comm, name)
            print('onmi: ', nmi, flush=True)

        f1 = xmeasures.f1(pre_comm, ture_comm, name)
        print('f1: ', f1)
    else:
        Evaluate_Xmeasures(out_path, ground_truth)

    print("\n")




if __name__ == '__main__':
    for name in [ "amazon" ,"youtube", "dblp","LiveJournal","wiki","orkut", "friendster","tweet2012","tweet2018",
                  "LFR_50K","LFR_100K","LFR_200K","LFR_500K","LFR_1M" ,"tweet2012_dy","tweet2018_dy"]:
            print("-" * 40)
            print(f"dataset:{name}")
            out_path = DATASETS[name]["out_file"]
            os.makedirs(os.path.dirname(out_path), exist_ok=True)

            CodeSEG(DATASETS[name]["graph"],out_path, DATASETS[name]["ground_truth"], name,DATASETS[name]["overlapping"],DATASETS[name]["weighted"],
                    DATASETS[name]["directed"],DATASETS[name]["dynamic"],it=10,tau=0.3, gamma=1,r=2, parallel=1,verbose=True)



