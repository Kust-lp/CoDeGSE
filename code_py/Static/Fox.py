import os
from datetime import datetime
import onmi
import xmeasures
from comm_utils import DATASETS
import glob
import os
import re
import shutil
import subprocess
from typing import Tuple, List


lazy_fox_binary = "../../code_c++/fox/build/LazyFox"

dataset_directory = "../fox_cache/lazy_fox_in"
output_directory = "../fox_cache/lazy_fox_out"


class LazyFox:
    def __init__(self, queue_size=1, thread_count=1,
                 wcc_threshold=0.1):
        self.queue_size = queue_size
        self.thread_count = thread_count
        self.wcc_threshold = wcc_threshold

        self.labels_ = None

    def fit(self, node_num, edges: List[Tuple[int, int]]):
        shutil.rmtree(dataset_directory, ignore_errors=True)
        shutil.rmtree(output_directory, ignore_errors=True)

        os.makedirs(dataset_directory, exist_ok=True)
        os.makedirs(output_directory, exist_ok=True)

        graph_path = os.path.join(dataset_directory, "graph.txt")
        with open(graph_path, 'w', encoding='utf8') as f:
            for v1, v2 in edges:
                f.write(f"{v1}\t{v2}\n")
            f.flush()

        cmd_lazy_fox = [
            lazy_fox_binary,
            "--input-graph", graph_path,
            "--output-dir", output_directory,
            "--queue-size", str(self.queue_size),
            "--thread-count", str(self.thread_count),
            "--wcc-threshold", str(self.wcc_threshold),
        ]


        out = subprocess.run(cmd_lazy_fox, capture_output=True,text=True)
        cluster_files = glob.glob(os.path.join(output_directory, "*/*/*clusters.txt"))
        cluster_files.sort(key=os.path.getmtime, reverse=True)
        cluster_result = cluster_files[-1]
        clusters = []
        with open(cluster_result, 'r', encoding='utf8') as f:
            for line in f:
                line = line.strip()
                nodes = re.split(r"\s+", line)
                if len(nodes) > 0:
                    nodes = [int(n) for n in nodes]
                    clusters.append(nodes)


        return clusters
def read_graph(edge_file, cmty_file):
    edges = set()
    with open(edge_file) as f:
        for line in f:
            if line.startswith('#'): continue
            if line==" ": continue
            e = line.rstrip('\n').split('\t')

            edges.add((int(e[0]), int(e[1])) if e[0] < e[1] else (int(e[1]), int(e[0])))

    cmty = []
    with open(cmty_file) as f:
        for line in f:
            if line.startswith('#'): continue

            nodes = line.rstrip('\n').split('\t')
            # nodes = line.rstrip('\n').split(' ')
            nodes = [int(n) for n in nodes]
            cmty.append(nodes)

    return list(edges), cmty



def fox(edge_file, cmty_file, data_name, out_path):
    os.makedirs(out_path, exist_ok=True)

    start = datetime.now()

    edges, gt_cmty = read_graph(edge_file, cmty_file)

    gt_cmty = [c for c in gt_cmty if len(c) > 2]
    gt_nodes = set(int(n) for c in gt_cmty for n in c)
    all_nodes = set(n for e in edges for n in e)
    fox = LazyFox()
    div = fox.fit(node_num=len(all_nodes), edges=edges)


    pred_div = []
    nodes =[]
    for v in div:
        nodes += v
        v = set(v).intersection(gt_nodes)
        if len(v) > 0:
            pred_div.append(list(v))

    end = datetime.now()
    time_diff = end - start
    time_diff = round(time_diff.total_seconds(), 1)

    print(f"time consuming:{time_diff}")
    with open(out_path+'fox.txt', 'w', encoding='utf8') as f:
        for c in pred_div:
            f.write("\t".join([str(n) for n in c]))
            f.write("\n")
        f.flush()


    nmi = onmi.overlapping_normalized_mutual_information(pred_div, gt_cmty,data_name)
    print('onmi: ', nmi, flush=True)

    f1 = xmeasures.f1(pred_div, gt_cmty,data_name)
    print('f1: ', f1)

    print("-" * 20)


if __name__ == "__main__":
    for name in [ "amazon" ,"youtube", "dblp","LiveJournal","orkut", "friendster","wiki"]:
        print(name)
        fox(DATASETS[name]["graph"], DATASETS[name]["ground_truth"],name,DATASETS[name]["out_file"])


