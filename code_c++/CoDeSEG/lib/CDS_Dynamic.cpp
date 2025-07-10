//
// Created by 23000 on 2025/6/11.
//
#include "CDS_Dynamic.h"
#include <cmath>
#include <iostream>
#include "ThreadPool.h"


NodeIdx CDSDy::_add_or_get_node(const Node &node, bool DEL) {
    const auto el = node_idx.find(node);

    if (el == node_idx.end()) {
        const auto idx = node_idx.size();
        node_idx[node] = idx;
        nodes.push(node);
        node_deg.push(0.);

        node_cmty.push(idx);
        cmty_vol.push(0.);
        cmty_cut.push(0.);
        n_nodes.emplace(idx);
        graph_adj.push(NodeAdj());
        return idx;
    }


    return el->second;
}

CDSDy &CDSDy::upt_edges(EdgeArray &n_e, EdgeArray &d_e) {
    for (unsigned long i = 0; i < n_e.size(); i++) {
        auto &[src, tgt, weight] = n_e[i];
        add_edge(src, tgt, weight);
    }

    for (unsigned long i = 0; i < d_e.size(); i++) {
        auto &[src, tgt, weight] = d_e[i];
        del_edge(src, tgt);
    }

    for (size_t i = 0; i < nodes.size(); i++) {
        const auto p = node_deg[i]/graph_vol;
        se_1d -= p*log(p);
    }

    avg_se_1d = se_1d/nodes.size();

    return *this;
}

CDSDy &CDSDy::add_edge(const Node &src, const Node &tgt, const float weight) {
    const auto src_idx = _add_or_get_node(src);
    const auto tgt_idx = _add_or_get_node(tgt);
    node_deg[src_idx] += weight;
    node_deg[tgt_idx] += weight;
    c_nodes.emplace(src_idx);
    c_nodes.emplace(tgt_idx);
    graph_vol += 2 * weight;

    const auto c1 = node_cmty[src_idx];
    const auto c2 = node_cmty[tgt_idx];
    cmty_vol[c1] += weight;
    cmty_vol[c2] += weight;

    if (c1 != c2){
        cmty_cut[c1] += weight;
        cmty_cut[c2] += weight;
    }

    graph_adj[src_idx][tgt_idx] = weight;
    graph_adj[tgt_idx][src_idx] = weight;

    return *this;
}

CDSDy &CDSDy::del_edge(const Node &src, const Node &tgt, const float weight) {
    const auto src_idx = _add_or_get_node(src, true);
    const auto tgt_idx = _add_or_get_node(tgt, true);
    node_deg[src_idx] -= weight;
    node_deg[tgt_idx] -= weight;
    graph_vol -= 2 * weight;

    graph_adj[src_idx][tgt_idx] = 0.;
    graph_adj[src_idx].erase(tgt_idx);
    graph_adj[tgt_idx][src_idx] = 0.;
    graph_adj[tgt_idx].erase(src_idx);

    const auto c1 = node_cmty[src_idx];
    const auto c2 = node_cmty[tgt_idx];
    cmty_vol[c1] -= weight;
    cmty_vol[c2] -= weight;
    if (c1 != c2){
        cmty_cut[c1] -= weight;
        cmty_cut[c2] -= weight;
    }
    return *this;
}

float CDSDy::_delta_leave(const NodeIdx i, const NodeIdx cmty_idx, const FloatValue deg_i_cmty,
                            const bool i_in_cmty) {
    // 单一结点社区
    if (i_in_cmty && std::abs(cmty_vol[cmty_idx] - node_deg[i]) < 1e-8) return 0.;

    const auto i_deg = node_deg[i];
    float src_div_vol;
    float tgt_div_vol;
    float src_div_cut;
    float tgt_div_cut;

    // 节点 i 不在社区 cmty_idx
    if (!i_in_cmty) {
        src_div_vol = cmty_vol[cmty_idx] + i_deg;
        tgt_div_vol = cmty_vol[cmty_idx];
        src_div_cut = cmty_cut[cmty_idx] - 2 * deg_i_cmty + i_deg;
        tgt_div_cut = cmty_cut[cmty_idx];
    }
        // 节点 i 在社区 cmty_idx
    else {
        src_div_vol = cmty_vol[cmty_idx];
        tgt_div_vol = cmty_vol[cmty_idx] - i_deg;
        src_div_cut = cmty_cut[cmty_idx];
        tgt_div_cut = cmty_cut[cmty_idx] + 2 * deg_i_cmty - i_deg;
    }

    const float tgt_div_se = (tgt_div_cut / graph_vol) * log(tgt_div_vol / graph_vol);
    const float src_div_se = (src_div_cut / graph_vol) * log(src_div_vol / graph_vol);
    const float node_i_se = (i_deg / graph_vol) * log(src_div_vol / graph_vol);
    const float src_tgt_se = (tgt_div_vol / graph_vol) * log(src_div_vol / tgt_div_vol);

    return tgt_div_se - src_div_se + node_i_se + src_tgt_se;
}

std::tuple<float, float, float, unsigned long, float, unsigned long, float>
CDSDy::_node_strategy(const NodeIdx i) {
    const auto src_cmty = node_cmty[i];
    auto tgt_cmty = src_cmty;

    auto cmty_in = std::unordered_map<unsigned long, float>{};
    const auto adj_i = graph_adj[i];
    for (const auto [j, w]: adj_i) {
        const auto div_j = node_cmty[j];
        cmty_in[div_j] = cmty_in[div_j] + w;
    }

    const float delta_leave_div_i = _delta_leave(i, src_cmty, cmty_in[src_cmty]);

    float delta_max = delta_leave_div_i;
    float delta_join_div_j = .0;
    for (const auto [cmty_j, cmty_j_i_in]: cmty_in) {
        if (cmty_j != src_cmty) {
            const auto delta_leave_div_j = _delta_leave(i, cmty_j, cmty_j_i_in, false);
             const auto delta_trans_div_j = delta_leave_div_i - delta_leave_div_j;
            if (delta_trans_div_j > delta_max) {
                delta_join_div_j = -delta_leave_div_j;
                delta_max = delta_trans_div_j;
                tgt_cmty = cmty_j;
            }
        }
    }

    return std::tuple{
            delta_max, delta_leave_div_i, delta_join_div_j,
            src_cmty, cmty_in[src_cmty], tgt_cmty, cmty_in[tgt_cmty]
    };
}



void CDSDy::_transfer(const NodeIdx i,
                        const NodeIdx src_cmty, const float deg_i_src_cmty,
                        const NodeIdx tgt_cmty, const float deg_i_tgt_cmty) {
    const auto deg_i = node_deg[i];

    // update source community
    cmty_vol[src_cmty] -= deg_i;
    if (cmty_vol[src_cmty] > 0) {
        cmty_cut[src_cmty] += 2 * deg_i_src_cmty - deg_i;
    } else {
        cmty_cut[src_cmty] = 0.;
    }

    // update target community
    node_cmty[i] = tgt_cmty;
    cmty_vol[tgt_cmty] += deg_i;
    cmty_cut[tgt_cmty] -= 2 * deg_i_tgt_cmty - deg_i;
}
CDSDy &CDSDy::detect_cmty(const unsigned int max_iter,  const float tau, const bool verbose, const int g_idx, const int r) {
    time_t tm_start, tm_finish;


    std::vector<int> fix_nodes(nodes.size(), 0);
    // community formation game main loop

    auto leave_se = se_1d;

    if (verbose) time(&tm_start);
    if (g_idx == 1) { //static detection for G_0
        for (unsigned short it = 1; it < max_iter + 1; it++) {
            float delta_se_sum = 0.;
            unsigned long it_num_stay = 0;
            unsigned long it_num_trans = 0;

            for (std::size_t i = 0; i < nodes.size(); i++) {
                const auto [
                        delta_se,
                        delta_leave_div_i,
                        delta_join_div_j,
                        src_cmty, deg_i_src_cmty,
                        tgt_cmty, deg_i_tgt_cmty
                ] = _node_strategy(i);


                if (delta_se > 0 && src_cmty != tgt_cmty) {
                    delta_se_sum += delta_se;
                    _transfer(i, src_cmty, deg_i_src_cmty, tgt_cmty, deg_i_tgt_cmty);
                    it_num_trans += 1;

                } else {
                    it_num_stay += 1;

                }
            }
            leave_se -= delta_se_sum;
            if (verbose) {
                time(&tm_finish);
                const auto tm_diff = difftime(tm_finish, tm_start);

                std::cout << "{ iter: " << it << ", ";
                std::cout << "delta_se_sum: " << delta_se_sum << ", ";
                std::cout << "leave_se: " << leave_se << ", ";
                std::cout << "se_sum: " << se_1d << ", ";
                std::cout << "avg_se_sum: " << avg_se_1d << ", ";
                std::cout << "#stay: " << it_num_stay << ", ";
                std::cout << "#trans: " << it_num_trans << ", ";
                std::cout << "time: \"" << tm_diff << " sec \"}" << std::endl;
            }

            // converged, break
            if (it_num_trans <= 0 ) break;
            if ( delta_se_sum/it_num_trans <= tau * avg_se_1d) break;
        }
    }else{
        for (unsigned short it = 1; it < max_iter + 1; it++) {
            float delta_se_sum = 0.;
            unsigned long it_num_stay = 0;
            unsigned long it_num_trans = 0;
            NodeIdxSet c_nodes_copy = c_nodes;
            for (const auto& i : c_nodes_copy) {

                const auto [
                        delta_se,
                        delta_leave_div_i,
                        delta_join_div_j,
                        src_cmty, deg_i_src_cmty,
                        tgt_cmty, deg_i_tgt_cmty
                ] = _node_strategy(i);



                if (delta_se > 0 && src_cmty != tgt_cmty) {
                    fix_nodes[i] = 0;
                    if (n_nodes.find(i) == n_nodes.end()){
                        if (a_nodes.find(i) != a_nodes.end()) a_nodes.erase(i);

                        for (const auto [j, w]: graph_adj[i]) {
                            if (c_nodes.find(j) == c_nodes.end()) {
                                a_nodes.emplace(j);
                                c_nodes.emplace(j);
                            }
                        }
                    }
                    delta_se_sum += delta_se;
                    _transfer(i, src_cmty, deg_i_src_cmty, tgt_cmty, deg_i_tgt_cmty);
                    it_num_trans += 1;


                } else {
                    fix_nodes[i] += 1;
                    it_num_stay += 1;
                    if(a_nodes.find(i) != a_nodes.end()){
                        a_nodes.erase(i);
                        c_nodes.erase(i);
                    }else if (fix_nodes[i] >= r){
                        c_nodes.erase(i);
                    }

                }
            }

            leave_se -= delta_se_sum;
            if (verbose) {
                time(&tm_finish);
                const auto tm_diff = difftime(tm_finish, tm_start);

                std::cout << "{ iter: " << it << ", ";
                std::cout << "delta_se_sum: " << delta_se_sum << ", ";
                std::cout << "leave_se: " << leave_se << ", ";
                std::cout << "se_sum: " << se_1d << ", ";
                std::cout << "avg_se_sum: " << avg_se_1d << ", ";
                std::cout << "#affected nodes: " << c_nodes.size() << ", ";
                std::cout << "#stay: " << it_num_stay << ", ";
                std::cout << "#trans: " << it_num_trans << ", ";
                std::cout << "time: \"" << tm_diff << " sec \"}" << std::endl;
            }

            if (it_num_trans <= 0 ) break;
            if ( delta_se_sum/it_num_trans <= tau * avg_se_1d ) break;
        }
    }


    c_nodes.clear();
    a_nodes.clear();
    n_nodes.clear();

    return *this;
}


CmtyMap &CDSDy::communities() {
    cmtis.clear();

    for (std::size_t i = 0; i < node_cmty.size(); i++) {
        const auto node_label = node_cmty[i];
        const auto node = nodes[i];

        cmtis[node_label].insert(node);
    }

    return cmtis;
}











