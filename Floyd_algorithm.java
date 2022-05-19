package datastructure;
import java.util.*;
import java.lang.*;
import java.io.*;
public class Floyd_algorithm {
	static int MAX=99999;
	// main
	public static void main(String[] args) {
		int g[][]= {{0,5,MAX,MAX,MAX},
			{MAX,0,6,MAX,-3},
			{MAX,MAX,0,MAX,2},
			{4,MAX,8,0,MAX},
			{4,MAX,MAX,-2,0}};
		Floyd_algorithm m= new Floyd_algorithm();
		int l=g.length;
		m.floyd(l,g);
			}
// floyd algorithm
	void floyd(int l,int matrix[][]) {
		//run a loop,k range from 0 to 5
		for(int k=0;k<l;k++) {//loop k
			for (int i=0;i<l;i++) {	//i is row and j is column
				for(int j=0;j<l;j++) {
					if(matrix[i][k]+matrix[k][j]<matrix[i][j]) {
						matrix[i][j]=matrix[i][k]+matrix[k][j];	//update matrix
													  }
								     }
								  }
							 }
		printfun(matrix,l);									 
	}
	//print the distance matrix
	void printfun(int matrix[][],int l) {
		System.out.println("Floyd Algorithm result:");
		for( int i=0;i<l;i++) {
			for(int j=0;j<l;j++) {
				if(matrix[i][j]==MAX) {
					System.out.print("MAX"+" ");}
				else {
				System.out.print(matrix[i][j]+"  ");}
			}
			System.out.println();
		}
	}
}