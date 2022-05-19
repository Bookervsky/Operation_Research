package datastructure;
import java.util.*;
import java.lang.*;
import java.io.*;
public class Dijkstra_shortest_path{
	int min_distance(int dist[],boolean set[]) {
		int min=Integer.MAX_VALUE,min_vertex=-1;
		int l=dist.length;
		for(int i=0;i<l;i++) {
			if(set[i]==false && dist[i]<=min) {
				min=dist[i];
				min_vertex=i;
			}
		}
		return min_vertex;
	}
    void printSolution(int dist[],int l)
    {
        System.out.println("Vertex \t\t Distance from Source");
        for (int i = 0; i < l; i++)
            System.out.println(i + " \t\t " + dist[i]);
    }
	void dijkstra(int matrix[][],int source) {
		int l=matrix.length;
		int[] dist=new int[l];	//dist[i] means the shortest path between i and source in every loop
		boolean[] set= new boolean[l];	//create new set to store vertex
		for(int i=0;i<l;i++) {
			dist[i]=Integer.MAX_VALUE;	//initialize all the distance as MAX
			set[i]=false;	//Initialize the set so that all the vertex are not in the set,including the source vertex
		}
		dist[source]=0;		//initialize source,dist[source]=0
		for(int k=0;k<l;k++)	//this loop aims to add vertexes to the set that has the permanent mark.
		{
			int m=min_distance(dist,set);	//find the vertex in the set that is closest to the source vertex
			set[m]=true;//update set[l]
			for(int j=0;j<l;j++) 
			{
				if(!set[j] && matrix[m][j]!=0 && matrix[m][j]+dist[m]<dist[j])		//最短路的子路还是最短路
				{
					dist[j]=matrix[m][j]+dist[m];	
				}
			}
		}
		printSolution(dist,l);
}
	public static void main(String[] args) {
		int matrix[][]={
				{0, 10, 20, 0, 0, 0},
				{10, 0, 0, 50, 10, 0},
				{20, 0, 0, 20, 33, 0},
				{0, 50, 20, 0, 20, 2},
				{0, 10, 33, 20, 0, 1},
				{0, 0, 0, 2, 1, 0}};
	Dijkstra_shortest_path u=new Dijkstra_shortest_path();
	u.dijkstra(matrix,0);
}
}
