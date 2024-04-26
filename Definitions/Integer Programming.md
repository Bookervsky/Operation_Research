# Integer Programming
As we know, the Integer Programming problem is NP-hard. However, a Linear Programming problem is a P and can be solved in polynominal time using the simplex method. So naturally, we come up with the idea that:
1. Relax the Integer Programming problem to a Linear Programming problem, we have the optimal solution __X*__ (assume that __X*__ is not an integer solution).
2. Add linear constraints to the Linear Programming problem so that its optimal solution __X*__ can be cut out(since __X*__ is not integer and hence not the optimal solution to the initial Integer Programming problem).

Geometrically, what the above methdology does is reducing the size of the feasible region of LP by means of adding new linear constraints. Each time a constraint is added, the feasible region is reduced and hence a step further to the [convex hull](https://github.com/Bookervsky/Operation_Research/blob/main/Definitions/Convex.md#convex-hull)  that feasible integer solutions formulates.

![image](https://upload.wikimedia.org/wikipedia/commons/3/31/TSP_cutting_plane.png)
## Gomory Cutting Plane Method

**Steps:**<br />
Step 1: Solve the relaxed linear programming, let __X*__ be an optimal solution.\
Step 2: If __X*__ is integer, stop; otherwise turn to Step 3.\
Step 3: Add a linear inequality constraint that integer solutions satisfy but linear solution does not(In this way, we approximate to the Convex hull further). Then, turn to Step 2 and solve the linear program.<br />

**Problems:**
A difficulty with general purpose cutting plane algorithms is that the added inequalities cut only a very small piece of the feasible set of the linear programming relaxation.

## Branch and Bound
**Steps:**<br />
Step 1: 
![image](/Definitions/Pictures/Branch%20and%20bound%20method%20example1.PNG)