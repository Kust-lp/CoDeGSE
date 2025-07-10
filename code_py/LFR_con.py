import os
from collections import defaultdict
import subprocess

LFR = "../code_c++/LFR-Benchmark_UndirWeightOvp-master/lfrbench_udwov"
def generate_graph(path, n,k,max_k,muw = 0.6):
    args = [
        LFR,
        "-N", str(n),
        "-k", str(k),
        "-maxk", str(max_k),
        "-muw", str(muw),
        "-name", path +"LFR",
        "-seed", "0"
    ]
    try:
        result = subprocess.run(
            args,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(e.stdout)





def read_edge_and_write_to_txt(edge_file_path, output_txt_path, weighted=False):
    with open(edge_file_path, 'r') as nse_file:
        lines = nse_file.readlines()

    
    with open(output_txt_path, 'w') as output_file:
        for line in lines[1:]:
            
            if line.strip(): 
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    if weighted:
                        edge = f"{parts[0]}\t{parts[1]}\t{parts[2]}"
                        output_file.write(edge + '\n')
                    else:
                        edge = f"{parts[0]}\t{parts[1]}\t1"
                        output_file.write(edge + '\n')

def read_com_and_write_to_txt(com_file_path, output_txt_path):
    with open(com_file_path, 'r') as com_file:
        lines = com_file.readlines()
    comms= defaultdict(str)
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2:
            comms[parts[0]] = parts[1]
    cmty = defaultdict(list)
    for node, comm in comms.items():
            cmty[comm].append(node)
    with open(output_txt_path, 'w') as output_file:
        for _, nodes in cmty.items():
            output_file.write("\t".join(nodes) + '\n')

#for overlapping communities, we can use the following code.
# def read_com_and_write_to_txt(com_file_path, output_txt_path):
#     with open(com_file_path, 'r') as com_file:
#         lines = com_file.readlines()
#     comms= defaultdict(list)
#     for line in lines:
#         parts = line.strip().split()
#         if len(parts) >= 2:
#             node = parts[0]
#             communities = parts[1:]
#
#         for community in communities:
#             comms[community].append(node)
#     with open(output_txt_path, 'w') as output_file:
#         for community, nodes in comms.items():
#             output_file.write("\t".join(nodes) + '\n')


if __name__ == '__main__':
    for name, num, k, max_k in zip(["LFR_50K","LFR_100K","LFR_200K","LFR_500K","LFR_1M","LFR_2M"],[ 50000, 100000, 200000, 500000, 1000000,2000000],[50,50,50, 50, 50,50],[100, 200, 400, 1000, 2000, 4000]):
        print(f"Generating {name} with {num} nodes, {k} avg. degree, {max_k} max degree")

        path = f'../data/{name}/'
        os.makedirs(path, exist_ok=True)
        generate_graph(path, num, k, max_k)

        edge_file_path = path + 'LFR.nse'
        com_file_path =path + 'LFR.nmc'
        output_edge_path = path + 'awgraph.txt'
        output_com_path =  path + 'cmty.txt'
        read_edge_and_write_to_txt(edge_file_path, output_edge_path, True)
        read_com_and_write_to_txt(com_file_path, output_com_path)
