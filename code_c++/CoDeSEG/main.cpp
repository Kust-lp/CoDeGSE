#include <iostream>
#include <string>
#include <regex>
#include <chrono>
#include <iomanip>
#include <filesystem>

#include "lib/CxxOpts.h"
#include "lib/CoDeSEG.h"
#include "lib/CDS_Dynamic.h"
#include "lib/DynamicArray.h"
#include "lib/Utility.h"



int main(const int argc, const char **argv) {
    cxxopts::Options options(
            "codeseg",
            "CoDeSEG: A fast Community Detection for large-scale networks via Structural Entropy Game");

    options.add_options()
            ("i,input", "Input file of graph edge list", cxxopts::value<std::string>())
            ("o,output", "Output file of communities, each line a community", cxxopts::value<std::string>())
            ("t,ground_truth", "Ground truth file of communities, each line a community", cxxopts::value<std::string>())
            ("w,weighted", "Indicate edge is weighted or not", cxxopts::value<bool>()->default_value("false"))
            ("d,directed", "Indicate edge is directed or not", cxxopts::value<bool>()->default_value("false"))
            ("c,dynamic", "dynamic community detection", cxxopts::value<bool>()->default_value("false"))
            ("x,overlapping", "Detect overlapping communities", cxxopts::value<bool>()->default_value("false"))
            ("g,gamma", " Overlapping detecting factor", cxxopts::value<float>()->default_value("1.0"))
            ("r,round", " Stable round threshold for dynamic detection", cxxopts::value<int>()->default_value("2"))
            ("v,verbose", "Print detection iteration messages", cxxopts::value<bool>()->default_value("false"))
            ("n,max_iteration", "Max iterations", cxxopts::value<int>()->default_value("5"))
            ("e,entropy_threshold", "Non-overlapping entropy threshold", cxxopts::value<float>()->default_value("0.3"))
            ("p,parallel", "Number of threads", cxxopts::value<int>()->default_value("1"))
            ("h,help", "Print usage");

    const auto args = options.parse(argc, argv);

    // print the usage help.
    if (args.count("help")) {
        std::cout << options.help() << std::endl;
        exit(0);
    }

    // start and finish time
    time_t tm_start, tm_finish;

    const auto max_iter = args["n"].as<int>();
    const auto ovlp = args["x"].as<bool>();
    const auto verb = args["v"].as<bool>();
    const auto num_workers = args["p"].as<int>();
    const auto directed = args["d"].as<bool>();
    const auto se_tau = args["e"].as<float>();
    const auto gamma = args["g"].as<float>();
    const auto dynamic = args["c"].as<bool>();
    const auto weighted = args["w"].as<bool>();
    


    if (dynamic){
        const auto edge_file = args["i"].as<std::string>() ;
        const auto round = args["r"].as<int>();
        bool inNewEdges = false;
        int i = 1;
        CDSDy dnmc;

        while (true){
            std::string name = std::to_string(i);
            std::filesystem::path fpath = std::filesystem::path(edge_file) / (name + ".txt");
            EdgeArray new_edges;
            EdgeArray del_edges;
            time(&tm_start);
            long n_count = 0;
            long d_count = 0;
            if (std::ifstream file(fpath); file.is_open()) {
                std::string line;
                while (std::getline(file, line)) {
                    if (line == "# New Edges:") {
                        inNewEdges = true;
                        continue;
                    } else if (line == "# Deleted Edges:") {
                        inNewEdges = false;
                        continue;
                    }
                    if (line.empty() || line[0] == '#') {
                        continue;
                    }
                    std::istringstream line_stream(line);
                    Node src_node, tgt_node;
                    float weight = 1.0;

                    if (!weighted) {
                        line_stream >> src_node >> tgt_node;
                    } else {
                        line_stream >> src_node >> tgt_node >> weight;
                    }
                    if (inNewEdges){
                        new_edges.push(Edge(src_node, tgt_node, weight));
                        n_count++;
                    } else{
                        del_edges.push(Edge(src_node, tgt_node, weight));
                        d_count++;
                    }
                }
                file.close();
            }
            time(&tm_finish);

            if (n_count > 0 || d_count > 0) {
                const auto tm_diff = difftime(tm_finish, tm_start);
                std::cout << "Graph "<< i << ": " << n_count << " edges added,"<<d_count<< " edges deleted;"<<" network file: " << fpath
                          << " time: " << tm_diff << " sec" << std::endl;
            } else {
                std::cout << "Can not open the edge text file: " << fpath << std::endl;
                break;
            }


            time(&tm_start);
            dnmc.upt_edges(new_edges,del_edges);
            time(&tm_finish);

            auto tm_diff = difftime(tm_finish, tm_start);
            std::cout <<"The "<< i <<" graph updated in " << tm_diff << " sec" << std::endl;

            auto t_start = std::chrono::high_resolution_clock::now();
            
            dnmc.detect_cmty(max_iter, se_tau,  verb, i, round);
            
            auto t_finish = std::chrono::high_resolution_clock::now();
            std::chrono::duration<double> elapsed = t_finish - t_start;
            std::cout << "detection done in " << std::fixed << std::setprecision(2) << elapsed.count() << " sec" << std::endl;
            CmtyMap cmty = dnmc.communities();


            std::set<std::string> gt_nodes;
            if (args.count("o") <= 0) {
                for (const auto &[key, nodes]: cmty) {
                    for (const auto &node: nodes) {
                        std::cout << node << " ";
                    }
                    std::cout << std::endl;
                }
            } else {
                const auto opath = args["o"].as<std::string>();
                std::filesystem::path cmty_file = std::filesystem::path(opath) / (name + ".txt");
                time(&tm_start);
                const auto cmty_num = save_cmty(cmty_file, cmty, gt_nodes);
                time(&tm_finish);

                auto tm_diff = difftime(tm_finish, tm_start);
                std::cout << "write " << cmty_num << " communities to file: " << cmty_file <<
                          ", in " << tm_diff << " sec" << std::endl;
            }

            i++;

        }



    } else{
        // load graph edges from a demo graph or an edge text file.
        EdgeArray edges;

        const auto edge_file = args["i"].as<std::string>();

        time(&tm_start);
        const auto edge_num = load_edges(edge_file, edges, weighted);
        time(&tm_finish);

        if (edge_num >= 0) {
            const auto tm_diff = difftime(tm_finish, tm_start);
            std::cout << edge_num << " edges loaded from: " << edge_file
                      << ", in " << tm_diff << " sec" << std::endl;
        } else {
            std::cout << "Can not open the edge text file: " << edge_file << std::endl;
            exit(0);
        }


        time(&tm_start);

        CoDeSEG codeseg;
        codeseg.add_edges(edges,directed);

        time(&tm_finish);
        auto tm_diff = difftime(tm_finish, tm_start);
        std::cout << "graph built in " << tm_diff << " sec" << std::endl;

        // time(&tm_start);
        auto t_start = std::chrono::high_resolution_clock::now();

        if (directed){
            if (num_workers <= 1) {
                codeseg.detect_cmty_direct(max_iter, ovlp, se_tau, gamma, verb);
            } else {
                codeseg.detect_cmty_direct(num_workers, max_iter, ovlp, se_tau, gamma, verb);
            }
        }else{
            if (num_workers <= 1) {
                codeseg.detect_cmty(max_iter, ovlp, se_tau, gamma, verb);
            } else {
                codeseg.detect_cmty(num_workers, max_iter, ovlp, se_tau, gamma, verb);
            }
        }


        auto t_finish = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> elapsed = t_finish - t_start;
        std::cout << "detection done in " << std::fixed << std::setprecision(2) << elapsed.count() << " sec" << std::endl;

        const auto cmty = codeseg.communities();
        std::cout << cmty.size() << " communities detected in graph, #nodes: "
                  << codeseg.get_nodes().size() << ", #edges: " << edges.size() << std::endl;

        std::set<std::string> gt_nodes;
        if (args.count("t") > 0) {
            const auto truth_cmty = args["t"].as<std::string>();
            const auto num_cmty = load_ground_truth_nodes(truth_cmty, gt_nodes);
            std::cout << gt_nodes.size() << " unique nodes in " << num_cmty << " communities, "
                      << truth_cmty << std::endl;
        }

        if (args.count("o") <= 0) {
            for (const auto &[key, nodes]: cmty) {
                for (const auto &node: nodes) {
                    std::cout << node << " ";
                }
                std::cout << std::endl;
            }
        } else {
            const auto cmty_file = args["o"].as<std::string>();
            time(&tm_start);
            const auto cmty_num = save_cmty(cmty_file, cmty, gt_nodes);
            time(&tm_finish);

            tm_diff = difftime(tm_finish, tm_start);
            std::cout << "write " << cmty_num << " communities to file: " << cmty_file <<
                      ", in " << tm_diff << " sec" << std::endl;
        }
    }


    return 0;
}
