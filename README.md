# Community Detection in Large-Scale Complex Networks via Structural Entropy Game (CoDeSEG)
## Quick start
We have published CoDeSEG on PyPI. Below are the installation and usage examples:
```bash
pip install codeseg
```
```python
from codeseg import CoDeSEG

in_path = "Input file of graph edge list"
out_path = "Output file of communities"
comms = CoDeSEG(in_path, out_path)
```
The relevant parameter descriptions are as follows:

| Parameter      | Description                                     | Type  | Default | Required |
| -------------- | ----------------------------------------------- | ----- | ------- | -------- |
| `in_path`      | Input file of the graph edge list               | file  | None    | Yes      |
| `out_path`     | Output file for the detected communities        | file  | None    | Yes      |
| `ground_truth` | Ground truth file for evaluation                | file  | None    | No       |
| `weighted`     | Whether the graph is weighted                   | bool  | false   | No       |
| `directed`     | Whether the graph is directed                   | bool  | false   | No       |
| `dynamic`      | Whether to perform dynamic community detection  | bool  | false   | No       |
| `overlap`      | Whether to detect overlapping communities       | bool  | false   | No       |
| `gamma`        | Overlapping detection factor                    | float | 1.0     | No       |
| `tau`          | Entropy threshold for non-overlapping detection | float | 0.3     | No       |
| `r`            | Stable round threshold for dynamic detection    | int   | 2       | No       |
| `it`           | Maximum number of iterations                    | int   | 10      | No       |
| `parallel`     | Number of threads to use                        | int   | 1       | No       |
| `verbose`      | Print iteration messages                        | bool  | false   | No       |



## Note
### Build Requirements
- CMake >= 3.22
- gcc/g++ >= 9
- Python >= 3.8


### data format
The format of the input edge list is as follows:
```python-repl
   1 \t 2 \n
   1 \t 3 \n
   2 \t 3 \n
    ...
``` 
For dynamic graphs, the input should be a folder containing edge list files for each network snapshot, stored in the /data/ntwk directory. The file structure is as follows:
```kotlin
<your_dataset>/ 
├── ntwk 
    ├── 1.txt
    ├── 2.txt
    ├── 3.txt
    ...
```

In addition, we provide the source code for all algorithms. The relevant details are as follows:

## Datasets
### Snap networks [1]
Download Amazon, YouTube, DBLP, LiveJournal, Orkut, Friendster, and Wiki datasets from [https://snap.stanford.edu/data](https://snap.stanford.edu/data), and place them in the `./data` folder.
For Wiki, please run `wiki_preprocess.py` to update its format.
```bash
cd code_py/
python wiki_preprocess.py
```

### X12 [2], X18 [3], X12_static, and X18_static
The x12 dataset contains 68,841 annotated English tweets covering 503 different event categories, encompassing tweets over a consecutive 29-day period.
The x18 includes 64,516 annotated French tweets covering 257 different event categories, with data spanning over a consecutive 23-day period. 
For X12, X18, X12_static ,and X18_static netwrks, please run `tweet_preprocess.py`:
```bash
cd code_py/
python tweet_preprocess.py
```

### LFR_50K, LFR_100K, LFR_200K, LFR_500K, and LFR_1M
To generate synthetic networks, start by compiling the LFR benchmark in `code_C++/LFR-Benchmark_UndirWeightOvp-master/`  directory into an executable, and then run LFR_con.py.
The original code address of LFR Benchmark is at [https://github.com/eXascaleInfolab/LFR-Benchmark_UndirWeightOvp](https://github.com/eXascaleInfolab/LFR-Benchmark_UndirWeightOvp).
```bash
cd code_c++/LFR-Benchmark_UndirWeightOvp-master/
make

cd code_py/
python LFR_con.py
```
Please update the file paths for all networks in code_py/comm_utils.py

## Evaluation metrics
### F1 and NMI
Compile the xmeasures into an executable file:
```bash
cd code_c++/xmeasures/
make
```
The original code address of xmeasures is at [https://github.com/eXascaleInfolab/xmeasures](https://github.com/eXascaleInfolab/xmeasures).

### ONMI
Compile the OvpNMI into an executable file:
```bash
cd code_c++/OvpNMI/
make
```
The original code address of OvpNMI is at [https://github.com/eXascaleInfolab/OvpNMI](https://github.com/eXascaleInfolab/OvpNMI).


## Codes
### CoDeSEG (ours)
Compile the CoDeSEG into an executable file, and then run `CoDeGSE.py`:
```bash
cd code_c++/CoDeSEG/
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS="-O3" ..
make

cd code_py/Static
python CoDeGSE.py
```
Importantly, our method is versatile and can be applied to overlapping, non-overlapping, and dynamic networks.

### Overlapping community detection
#### Bigclam [4]
Compile the Bigclam into an executable file, and then run `bigclam.py`:
```bash
cd code_c++/Snap-6.0/examples/bigclam/
make

cd code_py/Static
python bigclam.py
```
The original code address of Bigclam is at  [https://github.com/snap-stanford/snap](https://github.com/snap-stanford/snap).

#### SLPA [5]
We implement this algorithm in Python3.8 with the NetworkX package in CDlib, with the number of iterations set to 21 and the filtering threshold set to 0.01. 
The original code is available at [https://github.com/kbalasu/SLPA](https://github.com/kbalasu/SLPA).
```bash
cd code_py/Static
python SLPA.py
```

#### NCGame [6]
We implement this algorithm with python3.8 via open-source code available in the paper’s supplementary material [https://doi.org/10.1038/s41598-022-15095-9](https://doi.org/10.1038/s41598-022-15095-9).
```bash
cd code_py/Static
python NCGame.py
```

#### Fox [7]
Compile the Fox into an executable file, and then run `Fox.py`:
```bash
cd code_c++/fox/
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS="-O3" ..
make

cd code_py/Static
python Fox.py
```
We implement this algorithm through the open-source code provided in the paper [8].

### Non-overlapping community detection
#### Louvain [9]
We implement this algorithm in Python3.8 with API provided by igraph library, and its open-source code is available at [https://github.com/taynaud/python-louvain](https://github.com/taynaud/python-louvain).
```bash
cd code_py/Static
python louvain.py
```

#### DER [10]
We implement this algorithm in Python3.8 with the NetworkX package in CDlib, and its original code is available at [https://github.com/komarkdev/der_graph_clustering](https://github.com/komarkdev/der_graph_clustering).
```bash
cd code_py/Static
python DER.py
```

#### Leiden [8]
We implement this algorithm using open-source code available at [https://github.com/vtraag/leidenalg](https://github.com/vtraag/leidenalg).
```bash
cd code_py/Static
python leiden.py
```

#### FLPA [11]
We implement this algorithm in Python3.8 with API provided by igraph library, and its open-source code is available at [https://github.com/vtraag/igraph/tree/flpa](https://github.com/vtraag/igraph/tree/flpa).
```bash
cd code_py/Static
python FLPA.py
```

### Dynamic community detection
#### QCA [13] and DynaMo [14]
We use the open-source code provided by DynaMo (available at [https://github.com/nogrady/dynamo](https://github.com/nogrady/dynamo)) to implement QCA and DynaMo.
To run them, please update the network paths in the Java files located in the `code_c++/dynamo-master/src/main/java/org/all_codes/dynamic/` directory.

#### DCDME [15]
We used the official code released by the authors, which can be found at [https://github.com/sunwww168/DCDME](https://github.com/sunwww168/DCDME).
```bash
cd code_py/Dynamic
python DCDME.py
```
#### DCDBFE [16]
We used the official code released by the authors, which can be found at [https://github.com/sitiharyanti/DCDBFE_2024](https://github.com/sitiharyanti/DCDBFE_2024).
```bash
cd code_py/Dynamic
python DCDBFE.py
```

# Citation
If you find this repository helpful, please consider citing the following paper.
[1] Leskovec Jure. 2014. SNAP Datasets: Stanford large network dataset collection. Retrieved December 2021 from [http://snap.stanford.edu/data](http://snap.stanford.edu/data) (2014).

[2] Andrew J McMinn, Yashar Moshfeghi, and Joemon M Jose. 2013. Building a large-scale corpus for evaluating event detection on twitter. In Proceedings ofthe 22nd ACM international conference on Information & Knowledge Management. ACM, 409–418.

[3] Mazoyer, Béatrice, et al. "A french corpus for event detection on twitter." Twelfth Language Resources and Evaluation Conference. European Language Resources Association (ELRA), 2020.

[4] Jaewon Yang and Jure Leskovec. 2013. Overlapping community detection at scale: a nonnegative matrix factorization approach. In Proceedings of the sixth ACM international conference on Web search and data mining. 587–596.

[5] Jierui Xie, Boleslaw K Szymanski, and Xiaoming Liu. 2011. Slpa: Uncoverin overlapping communities in social networks via a speaker-listener interaction dynamic process. In 2011 ieee 11th international conference on data mining workshops. IEEE, 344–349.

[6]Farhad Ferdowsi and Keivan Aghababaei Samani. 2022. Detecting overlapping communities in complex networks using non-cooperative games. Scientific Reports 12, 1 (2022), 11054.

[7] Tianshu Lyu, Lidong Bing, Zhao Zhang, and Yan Zhang. 2020. Fox: fast overlapping community detection algorithm in big weighted networks. ACM Transactions on Social Computing 3, 3 (2020), 1–23.

[8] Tim Garrels, Athar Khodabakhsh, Bernhard Y Renard, and Katharina Baum. 2023. LazyFox: Fast and parallelized overlapping community detection in large graphs. PeerJ Computer Science 9 (2023), e1291.

[9] Vincent D Blondel, Jean-Loup Guillaume, Renaud Lambiotte, and Etienne Lefebvre. 2008. Fast unfolding of communities in large networks. Journal of statistical mechanics: theory and experiment 2008, 10 (2008), P10008.

[10] Mark Kozdoba and Shie Mannor. 2015. Community detection via measure space embedding. In Proceedings of the 28th International Conference on Neural Information Processing Systems-Volume 2. 2890–2898.

[11] VA Traag, L Waltman, and NJ van Eck. 2019. From Louvain to Leiden: guaranteeing well-connected communities. Scientific Reports 9 (2019), 5233.

[12] Vincent A Traag and Lovro Šubelj. 2023. Large network community detection by fast label propagation. Scientific Reports 13, 1 (2023), 2701.

[13] Nguyen, Nam P., et al. "Adaptive algorithms for detecting community structure in dynamic social networks." 2011 Proceedings IEEE INFOCOM. IEEE, 2011.

[14] Zhuang, Di, J. Morris Chang, and Mingchen Li. "DynaMo: Dynamic community detection by incrementally maximizing modularity." IEEE Transactions on Knowledge and Data Engineering 33.5 (2019): 1934-1945.

[15] Sun, Zejun, et al. "Dynamic community detection based on the Matthew effect." Physica A: Statistical Mechanics and its Applications 597 (2022): 127315.

[16] Anuar, Siti Haryanti Hairol, et al. "Bird flock effect-based dynamic community detection: Unravelling network patterns over time." Alexandria Engineering Journal 112 (2025): 177-208.
