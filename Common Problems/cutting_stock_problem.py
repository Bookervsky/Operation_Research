import gurobipy as gp
import numpy as np
from gurobipy import GRB

class Cutting_stock_problem:
    def __init__(self, stock_length, pieces):
        self.stock_length = stock_length
        self.pieces, self.lengths, self.demand = gp.multidict(pieces)
        self.patterns = None
        self.dual_var = [0] * len(pieces)
        req = [length * demand for length, demand in pieces.values()]
        self.min_rolls = np.ceil(np.sum(req) / self.stock_length)
        self.solution = {}
        self.master = Masterproblem()
        self.sub = Subproblem()

    def _initialize_patterns(self):
        patterns = []
        for index, length in self.lengths.items():
            pattern = [0] * len(self.pieces)
            pattern[index] = self.stock_length // length
            patterns.append(pattern)
        self.patterns = patterns

    def _generate_patterns(self):
        self._initialize_patterns()
        self.master.setup(self.patterns, self.demand)
        self.sub.setup(self.stock_length, self.lengths, self.dual_var)

        while True:
            self.master.model.optimize()
            self.dual_var = self.master.model.getAttr('pi', self.master.constrs)
            self.sub.update(self.dual_var)
            self.sub.model.optimize()
            reduced_cost = 1 - self.sub.model.objVal
            if reduced_cost >= 0:
                break

            pattern = [0] * len(self.lengths)
            for piece,var in self.sub.vars.items():
                if var.x > 0.5:
                    pattern[piece] = round(var.x)
            self.master.update(pattern, len(self.patterns))
            self.patterns.append(pattern)

    def solve(self):
        self._generate_patterns()
        self.master.model.setAttr('vType', self.master.vars, GRB.INTEGER)
        self.master.model.optimize()
        for pattern, var in self.master.vars.items():
            if var.x > 0.5:
                self.solution[pattern] = round(var.x)

class Masterproblem:
    def __init__(self):
        self.model = gp.Model()
        self.vars = None
        self.constrs = None

    def setup(self, patterns, demand):
        num_patterns = len(patterns)
        self.vars = self.model.addVars(num_patterns, vtype=GRB.CONTINUOUS, obj=1, name='pattern')
        self.constrs = self.model.addConstrs((gp.quicksum(
            patterns[i][j] * self.vars[i] for i in range(num_patterns)) >= demand[j]
                                             for j in demand.keys()), name='demand')
        self.model.modelSense = GRB.MINIMIZE
        self.model.params.outputFlag = 0
        self.model.update()

    def update(self, pattern, index):
        new_var = gp.Column(coeffs=pattern, constrs=self.constrs.values())
        self.vars[index] = self.model.addVar(obj=1, name=f"Pattern[{index}]", column=new_var)
        self.model.update()

class Subproblem:
    def __init__(self):
        self.model = gp.Model()
        self.vars = None
        self.constrs = None

    def setup(self, stock_length, lengths, dual_var):
        self.vars = self.model.addVars(len(lengths), obj=dual_var, vtype=GRB.INTEGER, name='frequency')
        self.constrs = self.model.addConstr(
            (gp.quicksum(self.vars[i] * lengths[i] for i in range(len(lengths))) <= stock_length),
            name='stock_length'
        )
        self.model.modelSense = GRB.MAXIMIZE
        self.model.params.outputFlag = 0
        self.model.params.BestBdStop = 1
        self.model.update()

    def update(self, dual_var):
        self.model.setAttr('obj',self.vars, dual_var)  # reset coefficients
        self.model.update()


orders = {0:[1380,22],
          1:[1520,25],
          2:[1560,12],
          3:[1710,14],
          4:[1820,18],
          5:[1880,18],
          6:[1930,20],
          7:[2000,10],
          8:[2050,12],
          9:[2100,14],
          10:[2140,16],
          11:[2150,18],
          12:[2200,20]}

csp = Cutting_stock_problem(5600, orders)
csp.solve()
print(csp.solution)
print(csp.min_rolls)