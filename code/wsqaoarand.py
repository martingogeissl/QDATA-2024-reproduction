import numpy as np
import random
import dill

from qat.lang.AQASM import *
from qat.opt import CombinatorialProblem
from qat.core import Observable, Term
from qat.vsolve.ansatz import AnsatzFactory
from qat.qpus import get_default_qpu
from qat.plugins import ScipyMinimizePlugin


n=2
N=n*n
ncells = N*N
nedges = 0.5 * pow(n,4) * (3*pow(n,2)-2*n-1)
nqubits = 2*ncells

# Sudoku graph creation
def get_edges():
    edges = []
    # rows
    for i in range(N):
        for j in range(N):
            current_cell1 = (i*N+j)*2
            for k in range(j+1,N):
                current_cell2 = (i*N+k)*2
                edges.append([current_cell1, current_cell2])
    # columns
    for j in range(N):
        for i in range(N):
            current_cell1 = (j+i*N)*2
            for k in range(i+1,N):
                current_cell2 = (j+k*N)*2
                edges.append([current_cell1, current_cell2])
    # subgrids
    for grid_i in range(n):
        for grid_j in range(n):
            for i1 in range(grid_i * n, grid_i * n + n):
                for j1 in range(grid_j * n, grid_j * n + n):
                    current_cell1 = (i1*N+j1)*2
                    for i2 in range(grid_i * n, grid_i * n + n):
                        for j2 in range(grid_j * n, grid_j * n + n):
                            if (i1 == i2 and j1 == j2):
                                continue
                            current_cell2 = (i2*N+j2)*2
                            if (current_cell2 < current_cell1):
                                continue
                            if ([current_cell1, current_cell2] not in edges):
                                edges.append([current_cell1, current_cell2])
    return edges

def create_observable():
    edges = get_edges()
    problem = CombinatorialProblem("Binary Sudoku Encoding")
    q = problem.new_vars(nqubits)

    for e in edges:
        clause = ~(q[e[0]]^q[e[1]] | q[e[0]+1]^q[e[1]+1])
        problem.add_clause(clause)

    observable = problem.get_observable()
    return observable

# computes epsilon regulated angle
def get_theta(c):
    if (c<epsilon):
        return 2*np.arcsin(np.sqrt(epsilon))
    elif (c> 1-epsilon):
        return 2*np.arcsin(np.sqrt(1-epsilon))
    else:
        return 2*np.arcsin(np.sqrt(c))

    
def change_initial_state(circuit, prog, c_vector):
    # remove the inital H operators
    del circuit.ops[0:nqubits]
    
    # create new initial state 
    qubits = prog.qalloc(nqubits)
    for qubit, c in zip(qubits, c_vector):
        RY(get_theta(c))(qubit)
    initial_state = prog.to_circ()
    
    # combine the two circuits
    circuit = initial_state + circuit
    return circuit
                     
def change_mixer(circuit, c_vector):
    ops = circuit.ops
    
    # get indexes of the first mixer element in each mixer group
    index_list = []
    for gate in ops:
        index = ops.index(gate)
        if (len(gate.qbits) == 1 and index > nqubits):
            if (gate.qbits[0] == 0):
                index_list.append(index)

    index_list.reverse()

    # replace the old mixer with new mixer
    for i in index_list:
        beta_index = len(index_list) - index_list.index(i) - 1
        beta = prog.new_var(float, '\\beta_{'+ str(beta_index) +'}')
        del circuit.ops[i:i+nqubits]
        for qubit in range(nqubits):
            theta = get_theta(c_vector[qubit])
            circuit.insert_gate(i+qubit, RY(theta), [qubit])
            circuit.insert_gate(i+qubit, RZ(beta*(-2)), [qubit])
            circuit.insert_gate(i+qubit, RY(-theta), [qubit])
    return circuit

# random c vector generation
def c_random():
    c_vector = []
    for a in range(nqubits):
        r = random.random()
        c_vector.append(r)
    return c_vector

# relaxation method decision
def get_c():
    return c_random()

# get observable
problem_observable = create_observable()

# load list of valid sudokus
valid_sudokus = []
with open('valid_sudokus/valid_integers', 'rb') as file:
    valid_sudokus = dill.load(file)

# algorithm vars
depth = 1
nbshots = 0
max_iter = 10000
niter = 10
epsilon = 0.25

path = 'results/WS-QAOA-RAND/p' + str(depth) + '/'

# define qpu
qpu = get_default_qpu()
stack = ScipyMinimizePlugin(method="COBYLA",
                            tol=1e-5, 
                            options={"maxiter": max_iter}) | qpu

print('Beginning WS-QAOA (coloring) execution with parameters:')
print('WS-QAOA depth: ' + str(depth))
print('Number of shots: ' + str(nbshots))
print('Number of algorithm iterations: ' + str(niter))
print('Epsilon regulation: ' + str(epsilon))
print()

# main loop
for i in range(niter):
    # get initial relaxation
    c_vector = get_c()
    print('Iteration ' + str(i+1) + ': c_vector: ' + str(c_vector))
    with open(path + str(i+1) + '/c_vector', 'w') as file:
        file.writelines(str(c_vector))

    # create quantum circuit
    prog = Program()
    circuit = AnsatzFactory.qaoa_circuit(problem_observable, depth, strategy="coloring")
    circuit = change_initial_state(circuit, prog, c_vector)
    circuit = change_mixer(circuit, c_vector)

    job = circuit.to_job(observable=problem_observable)
    result = stack.submit(job)
    result.dump(path + str(i+1) + '/minimize_result')
    print('Final Energy: ' + str(result.value))
    
    # sampling process
    sampling_job = circuit.to_job()(**eval(result.meta_data["parameter_map"]))
    sampling_result = qpu.submit(sampling_job)
    
    # filtering valid sudokus
    valid_samples = []
    success_probability = 0
    for sudoku in valid_sudokus:
        valid_sample = sampling_result[sudoku]
        valid_samples.append(valid_sample)
        success_probability += valid_sample.probability
    print('Valid Sudokus %: ' + str(success_probability))
    
    # storing results
    with open(path + str(i+1) + '/valid_samples', 'wb') as file:
        dill.dump(valid_samples, file)
        
    with open(path + str(i+1) + '/success_probability', 'w') as file:
        file.write(str(success_probability))
        
    print()

print('Finished Algorithm!')    