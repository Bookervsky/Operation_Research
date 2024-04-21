# Integer Programming
## Gomory Cutting Plane Method
General idea: to find the Convex hull of the feasible integer solutions Set.<br />

**Steps:**\
Step 1: Solve the relaxed linear programming, let __x*__ be an optimal solution.\
Step 2: If __x*__ is integer, stop; otherwise turn to Step 3.\
Step 3: Add a linear inequality constraint that integer solutions satisfy but linear solution does not(In this way, we approximate to the Convex hull further). Then, turn to Step 2 and solve the linear program.<br />

**Problems:**
A difficulty with general purpose cutting plane algorithms is that the added inequalities cut only a very small piece of the feasible set of the linear programming relaxation.