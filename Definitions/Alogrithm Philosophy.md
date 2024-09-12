# Meta-heuristics[1]
Meta-heuristics may be classified into three main classes:evolutionary, physics-based, and SI algorithms.  
1. EAs are usually inspired by the concepts of evolution in nature. The most popular algorithm in this branch is GA.Generally speaking, the optimization is done by evolving an initial random solution in EAs. Each new population is created by the combination and mutation of the individuals in the previous generation. Since the best individuals have higher probability of participating in generating the new population, the new population is likely to be better than the previous generation(s). This can guarantee that the initial random population is optimized over the course of generations  
2. The second main branch of meta-heuristics is physics-based
techniques.
For example, the BBBC algorithm was inspired by the big bang and big crunch theories. The search agents of BBBC are scattered from a point in random directions in a search space according to the principles of the big bang theory. They search randomly and then gather in a final point (the best point obtained so far) according to the principles of the big crunch theory. GSA is another physics- based algorithm. The basic physical theory from which GSA is inspired is Newton’s law of universal gravitation. The GSA algorithm performs search by employing a collection of agents that have masses proportional to the value of a fitness function. During iteration, the masses are attracted to each other by the gravitational forces between them. The heavier the mass, the bigger the attractive force. Therefore, the heaviest mass, which is possibly close to the global optimum, attracts the other masses in proportion to their distances.  
3. The third subclass of meta-heuristics is the SI methods.  
These algorithms mostly mimic the social behavior of swarms, herds, flocks, or schools of creatures in nature. The mechanism is almost similar to physics-based algorithm, but the search agents navigate using the simulated collective and social intelligence of creatures. The most popular SI technique is PSO. The PSO algorithm employs multiple particles that chase the position of the best particle and their own best positions obtained so far. In other words, a particle is moved considering its own best solution as well as the best solution the swarm has obtained.

# Multi-objective Optimization[2]  
There are three approaches to solve a multi-objective problem: a priori approaches, interactive approaches, and a posteriori approaches. In
a priori approaches, a decision-maker provides preferences for the different objectives. In interactive approaches, the decision-maker’s choices are made during the problem solving process. In a posteriori approaches, a set of potentially non-dominated solutions is first generated, and then the decision-maker chooses among those solutions.


# References  
[1]	S. Mirjalili, S. M. Mirjalili, and A. Lewis, "Grey Wolf Optimizer," Advances in Engineering Software, vol. 69, pp. 46-61, 2014, doi: 10.1016/j.advengsoft.2013.12.007.
[2]	N. Jozefowiez, F. Semet, and E.-G. Talbi, "Multi-objective vehicle routing problems," European Journal of Operational Research, vol. 189, no. 2, pp. 293-309, 2008, doi: 10.1016/j.ejor.2007.05.055.
