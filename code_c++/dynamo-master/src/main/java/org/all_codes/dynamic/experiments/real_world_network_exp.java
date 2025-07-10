package org.dzhuang.dynamic.experiments;

import org.dzhuang.dynamic.DynaMo.ModularityOptimizer_DynaMo;
import org.dzhuang.dynamic.DynaMo.ModularityOptimizer_Louvain;
import org.dzhuang.dynamic.Runnable.RunAlgorithm;
import org.dzhuang.dynamic.preprocessing.toComparison;
import org.dzhuang.dynamic.preprocessing.toDynaMo;

public class real_world_network_exp {
	public static void main(String[] args) throws Exception {
		run("tweet2012", 10);
		run("tweet2018", 8);
		
	}
	
	public static void run(String data_name, int cnt) throws Exception {
		// toDynaMo.run(data_name, cnt);
		// toComparison.trans2Comparisons(data_name, cnt);
		// ModularityOptimizer_Louvain.runLouvain(data_name, cnt);
		// ModularityOptimizer_DynaMo.runDynamicModularity(data_name, cnt);
  		RunAlgorithm.runIncremental(data_name);
  		// RunAlgorithm.runLBTR(data_name, cnt);
	}
}
