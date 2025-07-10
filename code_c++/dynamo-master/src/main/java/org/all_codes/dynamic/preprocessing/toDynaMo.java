package org.dzhuang.dynamic.preprocessing;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;

import org.dzhuang.dynamic.DynaMo.Network;
import org.dzhuang.dynamic.util.FileUtil;

public class toDynaMo {
	public static void main(String[] args) throws IOException, ClassNotFoundException {	
		run("Cit-HepPh", 31);
		run("Cit-HepTh", 25);
		run("dblp_coauthorship", 31);
		run("facebook", 28);
		run("flickr", 24);
		run("youtube", 33);	
	}
	
	public static void run(String dataSet, int size) throws IOException{
		FileUtil.deleteDir(new File("/home/lipu/CoDeSEG_new/code_c++/dynamo-master/src/main/java/org/dzhuang/dynamic/preprocessing/data/"+dataSet+"/inct"));
		(new File("/home/lipu/CoDeSEG_new/code_c++/dynamo-master/src/main/java/org/dzhuang/dynamic/preprocessing/data/"+dataSet+"/inct")).mkdir();
		FileUtil.deleteDir(new File("/home/lipu/CoDeSEG_new/code_c++/dynamo-master/src/main/java/org/dzhuang/dynamic/preprocessing/data/"+dataSet+"/ntwk2"));
		(new File("/home/lipu/CoDeSEG_new/code_c++/dynamo-master/src/main/java/org/dzhuang/dynamic/preprocessing/data/"+dataSet+"/ntwk2")).mkdir();
		
		for(int i=1;i<=size;i++) {
			Network network = readInputFile("/home/lipu/CoDeSEG_new/code_c++/dynamo-master/src/main/java/org/dzhuang/dynamic/preprocessing/data/"+dataSet+"/ntwk/"+i);
			network.save("/home/lipu/CoDeSEG_new/code_c++/dynamo-master/src/main/java/org/dzhuang/dynamic/preprocessing/data/"+dataSet+"/ntwk2/"+i);
		}
		
		for(int i=2;i<=size;i++){
			HashSet<String> oldNetwork=new HashSet<String>();
			HashSet<String> newNetwork=new HashSet<String>();
			BufferedReader bufferedReader = new BufferedReader(new FileReader("/home/lipu/CoDeSEG_new/code_c++/dynamo-master/src/main/java/org/dzhuang/dynamic/preprocessing/data/"+dataSet+"/ntwk/"+(i)));
			String line="";
			while ((line=bufferedReader.readLine()) != null) {
				newNetwork.add(line);
			}
			bufferedReader.close();
			
			int cnt=0;
			PrintWriter pw=new PrintWriter("/home/lipu/CoDeSEG_new/code_c++/dynamo-master/src/main/java/org/dzhuang/dynamic/preprocessing/data/"+dataSet+"/inct/"+i);
			bufferedReader = new BufferedReader(new FileReader("/home/lipu/CoDeSEG_new/code_c++/dynamo-master/src/main/java/org/dzhuang/dynamic/preprocessing/data/"+dataSet+"/ntwk/"+(i-1)));
			line="";
			while ((line=bufferedReader.readLine()) != null) {
				oldNetwork.add(line);
				if(!newNetwork.contains(line))
					pw.println(cnt+"\t"+"-"+"\t"+line);				
				cnt++;
			}
			bufferedReader.close();
			
			cnt=0;
			bufferedReader = new BufferedReader(new FileReader("/home/lipu/CoDeSEG_new/code_c++/dynamo-master/src/main/java/org/dzhuang/dynamic/preprocessing/data/"+dataSet+"/ntwk/"+(i)));
			line="";
			while ((line=bufferedReader.readLine()) != null) {				
				if(!oldNetwork.contains(line))		
					pw.println(cnt+"\t"+"+"+"\t"+line);
				cnt++;
			}
			bufferedReader.close();
			pw.close();
		}
	}
	
	private static Network readInputFile(String fileName) throws IOException{
    	ArrayList<Double> edgeWeight1_List=new ArrayList<Double>();
    	ArrayList<Integer> node1_List=new ArrayList<Integer>();
    	ArrayList<Integer> node2_List=new ArrayList<Integer>();
        
        BufferedReader bufferedReader = new BufferedReader(new FileReader(fileName));
        String line="";
        int maxNode=-1;
		while ((line=bufferedReader.readLine())!=null){
            String[] lines=line.split("\t");
            int startNode=Integer.parseInt(lines[0]);
            int endNode=Integer.parseInt(lines[1]);
            double wt_new=(lines.length > 2) ? Double.parseDouble(lines[2]) : 1;
            
            node1_List.add(startNode);
            node2_List.add(endNode);
            edgeWeight1_List.add(wt_new);
            
            if (endNode > maxNode)
            	maxNode = endNode;
        }
        bufferedReader.close();

        int nNodes = maxNode + 1;
        int[] nNeighbors = new int[nNodes];
        for (int i = 0; i < node1_List.size(); i++)
            if (node1_List.get(i) < node2_List.get(i)){
                nNeighbors[node1_List.get(i)]++;
                nNeighbors[node2_List.get(i)]++;
            }

        int[] firstNeighborIndex = new int[nNodes + 1];
        int nEdges = 0;
        for (int i = 0; i < nNodes; i++){
            firstNeighborIndex[i] = nEdges;
            nEdges += nNeighbors[i];
        }
        firstNeighborIndex[nNodes] = nEdges;

        int[] neighbor = new int[nEdges];
        double[] edgeWeight2 = new double[nEdges];
        Arrays.fill(nNeighbors, 0);
        for (int i = 0; i < node1_List.size(); i++)
            if (node1_List.get(i) < node2_List.get(i)){
                int j = firstNeighborIndex[node1_List.get(i)] + nNeighbors[node1_List.get(i)];
                neighbor[j] = node2_List.get(i);
                edgeWeight2[j] = edgeWeight1_List.get(i);
                nNeighbors[node1_List.get(i)]++;
                j = firstNeighborIndex[node2_List.get(i)] + nNeighbors[node2_List.get(i)];
                neighbor[j] = node1_List.get(i);
                edgeWeight2[j] = edgeWeight1_List.get(i);
                nNeighbors[node2_List.get(i)]++;
            }
        Network network = new Network(nNodes, firstNeighborIndex, neighbor, edgeWeight2);
        return network;
    }
}