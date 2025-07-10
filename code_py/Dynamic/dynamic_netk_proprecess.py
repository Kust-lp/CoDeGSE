import os

def save_first_network(file_path):
    g1 = file_path + f"/ntwk/1.txt"
    output_path = file_path + "/changed/"
    os.makedirs(output_path, exist_ok=True)
    output_txt_path = output_path + f"1.txt"
    with open(g1, 'r') as file:
        g_l1 = file.readlines()
        with open(output_txt_path, 'w') as output_file:
            output_file.write("# New Edges:\n")
            for line in g_l1:
                parts = line.strip().split('\t')
                output_file.write(f"{parts[0]}\t{parts[1]}\t{parts[2]}\n")
def filter_changed_nodes(file_path):
    i = 1
    e_save = None
    print("Processing:", end=" ")
    while True:
        print(i, end=" ")
        g1 = file_path+f"/ntwk/{i}.txt"
        g2 = file_path+f"/ntwk/{i+1}.txt"

        if not (os.path.exists(g1) and os.path.exists(g2)): break
        if  e_save:
            e1 = e_save
        else:
            e1 = set()
            with open(g1, 'r') as file:
                g_l1 =  file.readlines()
            for line in g_l1:
                if line.strip():
                    parts = line.strip().split('\t')

                    # if len(parts) >= 2:
                    #     a, b = int(parts[0]), int(parts[1])
                    #     edge = (a, b) if a < b else (b, a)
                    #     e1.add(edge)
                    if len(parts) >= 2:
                        a, b, w = int(parts[0]), int(parts[1]), float(parts[2])
                        edge = (a, b, w) if a < b else (b, a, w)
                        e1.add(edge)

        e2 = set()
        with open(g2, 'r') as file:
            g_l2 =  file.readlines()
            for line in g_l2:
                if line.strip():
                    parts = line.strip().split('\t')
                    # if len(parts) >= 2:
                    #     a, b = int(parts[0]), int(parts[1])
                    #     edge = (a, b) if a < b else (b, a)
                    #     e2.add(edge)

                    if len(parts) >= 2:
                        a, b, w = int(parts[0]), int(parts[1]),float(parts[2])
                        edge = (a, b, w) if a < b else (b, a, w)
                        e2.add(edge)

        new_edges = e2 - e1
        del_edges = e1 - e2
        e_save = e2

        output_path = file_path+"/changed/"
        os.makedirs(output_path, exist_ok=True)
        output_txt_path = output_path+f"{i+1}.txt"
        with open(output_txt_path, 'w') as output_file:
            output_file.write("# New Edges:\n")
            for edge in new_edges:
                # output_file.write(f"{edge[0]}\t{edge[1]}\n")
                output_file.write(f"{str(edge[0])}\t{str(edge[1])}\t{str(edge[2])}\n")
            output_file.write("# Deleted Edges:\n")
            for edge in del_edges:
                # output_file.write(f"{edge[0]}\t{edge[1]}\n")
                output_file.write(f"{str(edge[0])}\t{str(edge[1])}\t{str(edge[2])}\n")
        i += 1
    print("Done.")

def no_weighted_method(file_path):
    i = 1
    output_file = file_path + f"/non_w_ntwk/"
    os.makedirs(output_file, exist_ok=True)
    while os.path.exists(file_path + f"/ntwk/{i}.txt"):
        g = file_path+f"/ntwk/{i}.txt"

        with open(g, 'r') as file:
            g_l = file.readlines()
        of = output_file + f"/{i}"
        with open(of, 'w') as output:
            for line in g_l:
                if line.strip():
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        a, b = int(parts[0]), int(parts[1])
                        edge = (a, b) if a < b else (b, a)
                        output.write(f"{str(edge[0])}\t{str(edge[1])}\n")
        i += 1
def Get_ntwk_change(path):
    save_first_network(path)
    filter_changed_nodes(path)
    no_weighted_method(path)
if __name__ == '__main__':

    for name in ["tweet2012", "tweet2018"]:
        path = f"../../data/{name}"
        save_first_network(path)
        filter_changed_nodes(path)
        no_weighted_method(path)