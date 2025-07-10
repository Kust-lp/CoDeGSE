# -*- coding: utf8 -*-
import os
import subprocess
from datetime import datetime

import numpy as np

import onmi
import xmeasures
from comm_utils import read_ture_cluster, filter_nodes, DATASETS

bigclam = "../../code_c++/Snap-6.0/examples/bigclam/bigclam"


def Bigclam(in_path,out_path,ground_truth,name, cmty_num= 25000):
    os.makedirs(out_path, exist_ok=True)
    ture_comm, keep_nodes, _ = read_ture_cluster(ground_truth, name)

    args = [
        bigclam,
        f"-i:{in_path}",
        f"-o:{out_path}",
        f"-d:{name}",
        f"-c:{cmty_num}",
        f"-nt:1",
    ]

    start = datetime.now()
    result = subprocess.run(
        args,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    output = result.stdout
    print(output)

    end = datetime.now()
    time_diff = end - start
    time_diff = round(time_diff.total_seconds(), 1)

    print(f"time consuming:{time_diff}")

    division = []
    with open(out_path + f"{name}cmtyvv.txt") as f:
        for line in f:
            nodes = line.strip().split()
            nodes = [int(n) for n in nodes]

            division.append(nodes)

    nxx = set()
    for x in division:
        for y in x:
            nxx.add(y)
    pre_comm = filter_nodes(division, keep_nodes)
    with open(out_path + "bigclam.txt", 'w', encoding='utf8') as f:
        for c in pre_comm:
            f.write("\t".join([str(n) for n in c]))
            f.write("\n")
        f.flush()

    nmi = onmi.overlapping_normalized_mutual_information(pre_comm, ture_comm, name)
    print('onmi: ', nmi, flush=True)

    f1 = xmeasures.f1(pre_comm, ture_comm, name)
    print('f1: ', f1)





if __name__ == '__main__':
   for name in [ "amazon" ,"youtube", "dblp","LiveJournal","orkut", "friendster","wiki"]:
            print("-" * 40)
            print(f"dataset:{name}")
            Bigclam(DATASETS[name]["graph"],DATASETS[name]["out_file"],DATASETS[name]["ground_truth"], name)

