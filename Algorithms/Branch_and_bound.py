import gurobipy as gp
from gurobipy import GRB
import math
import time

def base_model(SUPPRESS_GUROBI_OUTPUT):
    # --- Define the Base Model (LP Relaxation of the Original Problem) ---
    # IMPORTANT: Define ALL variables as CONTINUOUS here, even those
    # that will eventually need to be integer. The B&B logic handles integrality.
    try:
        base_m = gp.Model("mip_base_lp")
        if SUPPRESS_GUROBI_OUTPUT:
             base_m.setParam(GRB.Param.OutputFlag, 0) # Silence creation messages

        # Define variables (as continuous)
        x = base_m.addVar(vtype=GRB.CONTINUOUS, name="x", lb=0.0)
        y = base_m.addVar(vtype=GRB.CONTINUOUS, name="y", lb=0.0) # Define as continuous!

        # Set Objective Function
        base_m.setObjective(5 * x + 6 * y, GRB.MAXIMIZE)

        # Add Original Constraints
        base_m.addConstr(x + y <= 50, "c0")
        base_m.addConstr(4 * x + 7 * y <= 280, "c1")

        # Update model to incorporate changes
        base_m.update()

    except gp.GurobiError as e:
        print(f"Error creating base Gurobi model: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during base model creation: {e}")
        return None
    return base_m

# --- Helper Function to Solve LP Relaxation ---
def solve_lp_relaxation(base_model, added_constraints, node_count):
    """
    Solves the LP relaxation for a given node using Gurobi.

    Args:
        base_model (gp.Model): The original Gurobi model definition (variables, objective, base constraints).
                               Variables intended to be integer should be defined as CONTINUOUS here.
        added_constraints (list): A list of tuples representing branching constraints added
                                  for this specific node. Each tuple is (variable_name, sense, rhs).
                                  e.g., ('y', GRB.LESS_EQUAL, 2.0)

    Returns:
        tuple: (status, objective_value, variable_values_dict)
               status: Gurobi status code (e.g., GRB.OPTIMAL, GRB.INFEASIBLE)
               objective_value: Objective function value of the LP relaxation (or None if not optimal)
               variable_values_dict: Dictionary mapping variable names to their values (or None if not optimal)
    """
    try:
        # Create a copy of the base model to avoid modifying it
        node_model = base_model.copy()

        # --- IMPORTANT: Ensure integer variables are treated as continuous for relaxation ---
        # (This should be handled by how base_model is defined, but double-check if needed)
        # for var_name in INTEGER_VARIABLES:
        #     var = node_model.getVarByName(var_name)
        #     if var.VType != GRB.CONTINUOUS:
        #         print(f"Warning: Variable {var_name} in base model is not continuous. Ensure base model uses continuous vars.")
        #         # Potentially change type here if base model wasn't set up correctly
        #         # var.VType = GRB.CONTINUOUS # Be careful with this approach

        # Add branching constraints specific to this node
        if node_count > 0:
            for var_name, sense, rhs in added_constraints:
                var = node_model.getVarByName(var_name)
                if sense == '<=':
                    expr = var <= rhs
                elif sense == '>=':
                    expr = var >= rhs
                else:
                    print(f" Error: Add node '{node_count}'")
                node_model.addConstr(expr, f"Node_{node_count}_cons")

        # Supress the linear relaxation problem output
        if SUPPRESS_GUROBI_OUTPUT:
            node_model.setParam(GRB.Param.OutputFlag, 0)

        # Solve the LP relaxation
        node_model.optimize()

        # Extract results of current linead relaxation problem
        status = node_model.Status
        if status == GRB.OPTIMAL:
            obj_val = node_model.ObjVal
            var_vals = {v.VarName: v.X for v in node_model.getVars()}
            return status, obj_val, var_vals
        elif status == GRB.INFEASIBLE:
            return status, None, None
        elif status == GRB.UNBOUNDED:
             # Should not happen if original problem is bounded
             print("Warning: LP relaxation is unbounded.")
             return status, None, None
        else:
            print(f"Warning: LP solve ended with status {status}")
            return status, None, None
    except gp.GurobiError as e:
        print(f"Gurobi Error code {e.errno}: {e}")
        return None, None, None # Indicate error
    except Exception as e:
        print(f"An unexpected error occurred in solve_lp_relaxation: {e}")
        return None, None, None

# --- Main Branch and Bound Algorithm ---
def branch_and_bound(base_m, INTEGER_TOLERANCE, INTEGER_VARIABLES):
    """
    Implements the Branch and Bound algorithm using gurobipy as a linear continuous solver.
    Core ideas:
    (1) Prune by feasibility
    (2) Prune by bound: upper bound lower than global lower bound (Maximization problems)
    (3) Prune by optimality: found integer solutions
    """
    start_time = time.time()

    # --- 1. Initialization ---
    incumbent_solution = None


    # Active nodes list (using a list as a stack for Depth First Search)
    # Each element: (node_id, added_constraints_list)
    active_nodes = [(0,[],0)] # Start with a dummy constraint
    constraints = []
    # For maximization problem
    global_lb = 0
    node_count = 0
    # Create and solve the root node (original LP relaxation)
    print("Solving root node LP relaxation...")


    # --- 3. Branch and Bound Loop ---
    print("\nStarting Branch and Bound...")
    while active_nodes:
        # Select node to explore (Depth First Search - LIFO)
        current_node_id, current_constraints, var_value = active_nodes.pop()
        # Solve LP relaxation problem
        if node_count == 0:
            status, current_obj, current_vars = solve_lp_relaxation(base_m, current_constraints, node_count)
        else:
            status, current_obj, current_vars = solve_lp_relaxation(base_m, current_constraints, node_count)
            if status == GRB.OPTIMAL:
                print(f"\nExploring Node {current_node_id}: LP Obj = {current_obj:.4f}, Constraints = {current_constraints}")
            else:
                print(f"\nNode {current_node_id} infeasible, prune it")
                continue

        # --- Pruning criteria 1: Prune by feasibility ---
        # If this node is infeasible, naturally, prune it.
        if status != GRB.OPTIMAL:
            print(f" Prune node {current_node_id} by feasibility, LP relaxation problem ends with status {status}.")
            #return None
            continue
        else:
            print(f"Node {current_node_id} LP relaxation problem optimal value: {current_obj:.4f}")

        # --- Pruning criteria 2: Prune by Bound ---
        # If this node's LP objective is not better than the best integer solution found so far, prune it.
        if current_obj <= global_lb:
            print(f" Prune Node {current_node_id} by bound ({current_obj:.4f} <= {global_lb:.4f})")
            continue

        # --- Pruning criteria 3: Prune by optimality
        # If a node solution is integer, update the bounds and prune it.
        frac_nums = []
        for var_name in INTEGER_VARIABLES:
            var_value = current_vars.get(var_name, None)
            # Most franctional branching strategy: choose the variable whose fractional number closest to 0.5 as the branch.
            if (frac := abs(var_value - round(var_value))) > INTEGER_TOLERANCE:
                branch_var_name = var_name
                frac_nums.append(frac)

        # --- Processing Based on Feasibility ---
        if not frac_nums:
            # All integer variables are integers at this node
            print(f"  Node {current_node_id}: Integer feasible solution found. Objective: {current_obj:.4f}")
            # Update incumbent if this solution is better
            if current_obj > global_lb:
                global_lb = current_obj
                incumbent_solution = current_vars.copy() # Store a copy
                print(f"  *** New Incumbent Found! Objective = {global_lb:.4f} ***")
                print(f"      Solution: { {k: round(v, 4) for k, v in incumbent_solution.items()} }") # Print rounded solution

            # Prune this node (fathomed) - already found an integer solution here
            print(f"  Prune Node {current_node_id} by optimality (integer solution).")
            continue
        else:
            # --- Branching Step ---
            branch_var_value = current_vars[branch_var_name]

            # (1) Create Left Branch (<= floor)
            floor_val = int(branch_var_value)
            left_constraints = current_constraints + [(branch_var_name, '<=', floor_val)]
            print(f"  Left Branch: {branch_var_name} <= {floor_val}")

            active_nodes.append((node_count, left_constraints, branch_var_value))
            node_count += 1

            # (2) Create Right Branch (>= ceil)
            ceil_val = floor_val + 1
            right_constraints = current_constraints + [(branch_var_name, '>=', ceil_val)]
            print(f"  Right Branch: {branch_var_name} >= {ceil_val}")

            active_nodes.append((node_count, right_constraints, branch_var_value))
            node_count += 1

    # --- 4. End of Algorithm ---
    end_time = time.time()
    print("\n------------------------------------")
    print("Branch and Bound Finished.")
    print(f"Total Nodes Explored: {node_count}")
    print(f"Total Time: {end_time - start_time:.4f} seconds")

    if incumbent_solution:
        print(f"\nOptimal Integer Objective: {global_lb:.4f}")
        print("Optimal Integer Solution:")
        # Round final solution for display
        final_solution_display = {k: round(v) if k in INTEGER_VARIABLES else round(v, 4) for k, v in incumbent_solution.items()}
        for var_name, value in final_solution_display.items():
             print(f"  {var_name}: {value}")
        return global_lb, incumbent_solution
    else:
        print("\nNo integer feasible solution found.")
        return None, None

# --- Run the Algorithm ---
if __name__ == "__main__":
    # --- Configuration ---
    # Define which variables must be integer (by name)
    INTEGER_VARIABLES = ["x", "y"]
    # Tolerance for checking if a variable is integer
    INTEGER_TOLERANCE = 1e-5
    # Suppress Gurobi output for LP solves
    SUPPRESS_GUROBI_OUTPUT = True

    base_m = base_model(True)
    optimal_obj, optimal_sol = branch_and_bound(base_m, INTEGER_TOLERANCE, INTEGER_VARIABLES)

    # Example of how to access the solution if needed later
    # if optimal_sol:
    #     print("\nAccessing final solution details:")
    #     print(f"Final x = {optimal_sol.get('x', 'N/A')}")
    #     print(f"Final y = {optimal_sol.get('y', 'N/A')}")

