import networkx as nx #type: ignore
from qiskit_optimization import QuadraticProgram #type: ignore
from qiskit_optimization.converters import LinearEqualityToPenalty #type: ignore

def build_routing_ising(graph: nx.DiGraph, source: int, target: int, penalty_factor: float = None):

    qp = QuadraticProgram("Routage_Bateau")

    # place les qubits
    for u, v in graph.edges():
        qp.binary_var(name=f"x_{u}_{v}")
        
    #minimisation du temps
    linear_objective = {f"x_{u}_{v}": graph.edges[u, v]['weight'] for u, v in graph.edges()}
    qp.minimize(linear=linear_objective)
    
    # règles de déplacement 
    for node in graph.nodes():
        in_edges = [f"x_{u}_{v}" for u, v in graph.in_edges(node)]
        out_edges = [f"x_{u}_{v}" for u, v in graph.out_edges(node)]
        if in_edges or out_edges:
            if node == source:
                rhs = -1
            elif node == target:
                rhs = 1
            else:
                rhs = 0
                
            constraint = {var: 1 for var in in_edges}
            constraint.update({var: -1 for var in out_edges})
            qp.linear_constraint(linear=constraint, sense='==', rhs=rhs, name=f"flow_{node}")
    
    # si règle pas réspectée 
    if penalty_factor is None:
        all_weights = [graph.edges[u, v]['weight'] for u, v in graph.edges()]
        max_w = max(all_weights) if all_weights else 1.0
        penalty_factor = max_w * 3.0 

    # résultat
    lineq2penalty = LinearEqualityToPenalty(penalty=penalty_factor)
    qubo = lineq2penalty.convert(qp)
    
    return qubo

