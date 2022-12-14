
# Module: tree_search
# 
# This module provides a set o classes for automated
# problem solving through tree search:
#    SearchDomain  - problem domains
#    SearchProblem - concrete problems to be solved
#    SearchNode    - search tree nodes
#    SearchTree    - search tree with the necessary methods for searhing
#
#  (c) Luis Seabra Lopes
#  Introducao a Inteligencia Artificial, 2012-2019,
#  InteligĂȘncia Artificial, 2014-2019

from abc import ABC, abstractmethod
from re import S

# Dominios de pesquisa
# Permitem calcular
# as accoes possiveis em cada estado, etc
class SearchDomain(ABC):

    # construtor
    @abstractmethod
    def __init__(self):
        pass

    # lista de accoes possiveis num estado
    @abstractmethod
    def actions(self, state):
        pass

    # resultado de uma accao num estado, ou seja, o estado seguinte
    @abstractmethod
    def result(self, state, action):
        pass

    # custo de uma accao num estado
    @abstractmethod
    def cost(self, state, action):
        pass

    # custo estimado de chegar de um estado a outro
    @abstractmethod
    def heuristic(self, state, goal):
        pass

    # test if the given "goal" is satisfied in "state"
    @abstractmethod
    def satisfies(self, state, goal):
        pass


# Problemas concretos a resolver
# dentro de um determinado dominio
class SearchProblem:
    def __init__(self, domain, initial, goal):
        self.domain = domain
        self.initial = initial
        self.goal = goal
    def goal_test(self, state):
        return self.domain.satisfies(state,self.goal)

# Nos de uma arvore de pesquisa
class SearchNode:
    def __init__(self,state,parent,depth = 0,cost = 0,heuristic = 0, action = None): 
        self.state = state
        self.parent = parent
        self.depth = depth
        self.cost = cost
        self.heuristic = heuristic
        self.action = action
    def __str__(self):
        return "no(" + str(self.state) + "," + str(self.parent) + ")"
    def __repr__(self):
        return str(self)

# Arvores de pesquisa
class SearchTree:

    # construtor
    def __init__(self,problem, strategy='breadth'): 
        self.problem = problem
        root = SearchNode(problem.initial, None)
        self.open_nodes = [root]
        self.strategy = strategy
        self.solution = None
        self.non_terminals = 0
        self.terminals = 0
        self.highest_cost_nodes = []
        self.average_depth = 0
        self.plan = []
    
    @property
    def length(self):
        return self.solution.depth

    @property
    def avg_branching(self):
        return round((self.terminals+self.non_terminals-1)/self.non_terminals,2)
    
    @property
    def cost(self):
        return self.solution.cost

    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self,node):
        if node.parent == None:
            return [node.state]
        path = self.get_path(node.parent)
        path += [node.state]
        return(path)

    # procurar a solucao
    def search(self, limit = None):
        self.non_terminals = 0
        self.terminals = 1
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)
            if limit and node.depth > limit: # used for limit search
                self.terminals-=1
                continue
            if self.problem.goal_test(node.state): # check for goal found
                self.solution = node
                max_cost = self.open_nodes[-1].cost
                for i in reversed(self.open_nodes):
                    if i.cost < max_cost: break
                    self.highest_cost_nodes = [i] + self.highest_cost_nodes
                parent = node
                while parent:
                    self.plan = [parent.action] + self.plan
                    parent = parent.parent
                self.plan = self.plan[1:]
                self.average_depth /= self.non_terminals + self.terminals
                print(self.plan)
                return self.get_path(node)
            self.non_terminals+=1
            self.terminals-=1
            lnewnodes = []
            for a in self.problem.domain.actions(node.state):
                newstate = self.problem.domain.result(node.state,a)
                # print("NEWSTATE",newstate)
                if newstate and newstate not in self.get_path(node):
                    added_cost = self.problem.domain.cost(node.state,(node.state, newstate))
                    newnode = SearchNode(
                        newstate,   
                        node,
                        depth = node.depth+1, 
                        cost = node.cost + added_cost,
                        heuristic = self.problem.domain.heuristic(newstate,self.problem.goal),
                        action=a)
                    lnewnodes.append(newnode)
                    self.average_depth += newnode.depth
                    self.terminals+=1
            self.add_to_open(lnewnodes)
        return None

    # juntar novos nos a lista de nos abertos de acordo com a estrategia
    def add_to_open(self,lnewnodes):
        if self.strategy == 'breadth':
            self.open_nodes.extend(lnewnodes)
        elif self.strategy == 'depth':
            self.open_nodes[:0] = lnewnodes
        elif self.strategy == 'uniform':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key=lambda e: e.cost)
        elif self.strategy == 'greedy':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key=lambda e: e.heuristic)
        elif self.strategy == 'a*':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key=lambda e: e.heuristic+e.cost)

