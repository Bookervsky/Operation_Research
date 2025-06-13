# Benders decomposition for uncapacitated facility location problem
from typing import List
import random
import numpy as np
from itertools import product
from math import sqrt

import gurobipy as gp
from gurobipy import GRB

class facility_location:
    def __init__(self,parameters):
        self.stores_loc = parameters['stores_loc']
        self.warehouses_loc = parameters['warehouses_loc']
        self.fixed_costs = parameters['fixed_costs']
        self.transport_cost = parameters['transport_cost']
        self.num_stores = len(self.stores_loc)
        self.num_warehouses = len(self.warehouses_loc)
        self.permutations = list(product(range(self.num_stores), range(self.num_warehouses)))
        self.c_ij = {(m, n): self.transport_cost * self.compute_distance(self.stores_loc[m], self.warehouses_loc[n]) for m, n in self.permutations}

        self.maxiter = 100
        self.tolerance = 1e-6
        self.cut_count = 0

    # This function determines the Euclidean distance between a facility and customer sites.
    def compute_distance(self, loc1, loc2):
        dx = loc1[0] - loc2[0]
        dy = loc1[1] - loc2[1]
        return sqrt(dx*dx + dy*dy)

    def setup(self):
        self.master = Master_Problem(self.num_warehouses, self.fixed_costs, self.permutations)
        self.master.setup()
        self.sub = Sub_problem(self.num_stores, self.num_warehouses, self.c_ij, [0]*self.num_warehouses)  # Initialize select with zeros
        self.sub.setup()

    def _benders_cut(self, model, where):
        if where == GRB.Callback.MIPSOL:
            # Retrieve current solution
            select_vals = model.cbGetSolution(model._select)
            select = [select_vals[j] for j in range(self.num_warehouses)]
            q = model.cbGetSolution(model._q)
            # Solve subproblem
            optimal = self.sub.solve_dual(select)

            # Add feasibility cut
            if not optimal:
                print(f"Adding feasibility cut #{self.cut_count + 1}")
                model.cbLazy(gp.quicksum(model._select[j] for j in range(self.num_warehouses)) >= 1)
                self.cut_count += 1
                return

            # Add optimality cut
            pi = self.sub.pi
            sigma = self.sub.sigma
            sub_obj = self.sub.model.objVal if self.sub.model.status == GRB.OPTIMAL else float('inf')

            # Correct gap calculation (q should be >= subproblem objective)
            gap = sub_obj - q
            if gap > self.tolerance:
                cut_expr = (gp.quicksum(pi[i] for i in range(self.num_stores)) +
                            gp.quicksum(sigma[i, j] * model._select[j] for i, j in self.permutations))

                model.cbLazy(model._q >= cut_expr)
                self.cut_count += 1
            else:
                print(f"Solution is optimal for current node, gap = {gap:.6f}")

    def solve(self):
        self.setup()

        self.master.model._facility_location = self # Allow access to the facility location instance in the callback
        self.master.model.optimize(self._benders_cut)

        # print results
        if self.master.model.status == GRB.OPTIMAL:
            print("\n" + "=" * 60)
            print("OPTIMAL SOLUTION FOUND")
            print("=" * 60)
            selected_warehouses = [j for j in range(self.num_warehouses) if self.master.model._select[j].X > 0.5]
            obj = self.master.model.objVal
            print(f"Selected warehouses: {selected_warehouses}")

            fixed_costs = sum(self.master.model._select[j].X * self.fixed_costs[j] for j in range(self.num_warehouses))
            shipping_cost = self.master.model._q.X
            print(f"Optimal cost: {obj}")
            print(f"Fixed costs: ${fixed_costs:.2f}")
            print(f"Transportation costs: ${shipping_cost:.2f}")
            print(f"Solve time: {self.master.model.Runtime:.2f} seconds")


class Master_Problem:
        def __init__(self,num_warehouses: int, fixed_costs: List, permutations: List):
            self.num_warehouses = num_warehouses
            self.fixed_costs = fixed_costs
            self.permutations = permutations
            self.model = None

        def setup(self):
            self.model = gp.Model('Master problem')
            self.model._select = self.model.addVars(self.num_warehouses,vtype=GRB.BINARY,name='select')
            self.model._q = self.model.addVar(obj=1,vtype=GRB.CONTINUOUS,lb=0,name='q') # q is the optimal value of the subproblem
            # Initial constraint: at least one warehouse must be selected
            self.model.addConstr(
                gp.quicksum(self.model._select[j] for j in range(self.num_warehouses)) >= 1,
                name='min_one_warehouse'
            )
            self.model.setObjective(self.model._select.prod(self.fixed_costs)+self.model._q, GRB.MINIMIZE)

            self.model.setParam('OutputFlag', 0)
            self.model.setParam('PreCrush', 1)
            self.model.setParam('Cuts', 0)
            self.model.setParam('lazyConstraints',1)

            self.model.update()

class Sub_problem:
    def __init__(self, num_stores: int,num_warehouses: int, c_ij: dict, select: List):
        self.num_stores = num_stores
        self.num_warehouses = num_warehouses
        self.c_ij = c_ij
        self.permutations = list(self.c_ij.keys())
        self.select = select
        # Initialize model and variables
        self.model = None
        self.assign = None
        self.shipping = None
        self.demand = None
        self.pi = None
        self.sigma = None
    
    def setup(self):
        self.model = gp.Model('Sub problem')
        self.assign = self.model.addVars(
            self.permutations, vtype=GRB.CONTINUOUS, name='assign',lb=0,ub=1)
        self.shipping = self.model.addConstrs(
            (self.assign[i,j] <= self.select[j] for i,j in self.permutations), name = 'shipping')
        self.demand = self.model.addConstrs(
            (gp.quicksum(self.assign[i,j] for j in range(self.num_warehouses)) == 1 for i in range(self.num_stores))
            , name = 'demand')
        self.model.setObjective(self.assign.prod(self.c_ij), GRB.MINIMIZE)

        self.model.setParam('OutputFlag', 0)

        self.model.update()

    def solve_dual(self,select):
        self.update(select)
        self.model.optimize()

        # Add optimality cuts
        if self.model.status == GRB.OPTIMAL:
            self.pi = self.model.getAttr('Pi', self.demand)
            self.sigma = self.model.getAttr('Pi', self.shipping)
            return True
        elif self.model.status == GRB.INFEASIBLE:
            # Add feasibility cuts
            self.model.computeIIS()
            return False

    def update(self,select):
        self.select = select
        for i, j in self.permutations:
            self.shipping[i, j].RHS = self.select[j]
        self.model.update()


def generate_test_data(num_stores, num_warehouses, seed=30):
    """Generate test data for the facility location problem"""
    random.seed(seed)

    stores_loc = [(random.randint(1, 100), random.randint(1, 100)) for _ in range(num_stores)]
    warehouses_loc = [(random.randint(1, 100), random.randint(1, 100)) for _ in range(num_warehouses)]
    fixed_costs = [random.randint(10, 50) for _ in range(num_warehouses)]
    transport_cost = 1

    return {
        'stores_loc': stores_loc,
        'warehouses_loc': warehouses_loc,
        'fixed_costs': fixed_costs,
        'transport_cost': transport_cost
    }


if __name__ == '__main__':
    print("Facility Location Problem - Benders Decomposition")
    print("=" * 60)

    # Test
    m, n = 6, 12
    print(f"\nTest Case: {m} stores, {n} warehouses")
    print("-" * 40)
    # Generate test data
    parameters = generate_test_data(m, n)
    # Print problem data
    print(f"Stores locations: {parameters['stores_loc']}")
    print(f"Warehouses locations: {parameters['warehouses_loc']}")
    print(f"Fixed costs of different warehouses: {parameters['fixed_costs']}")
    print(f"Transport cost per unit: {parameters['transport_cost']}")

    # Solve problem
    fl = facility_location(parameters)
    fl.solve()

    print("=" * 60)