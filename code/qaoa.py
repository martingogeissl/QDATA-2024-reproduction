import numpy as np
import dill

from qat.opt import CombinatorialProblem
from qat.lang.AQASM import *
from qat.core import Observable, Term
from qat.vsolve.ansatz import AnsatzFactory
from qat.qpus import get_default_qpu
from qat.plugins import ScipyMinimizePlugin

# problem variables
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


# algorithm vars
depth = 2
max_iter = 10000
nbshots = 0 #nbshots=0 => max possible number of shots
niter = 10

problem_observable = create_observable()
qaoa_ansatz = AnsatzFactory.qaoa_circuit(problem_observable, depth, strategy="coloring")

# circuit to qaoa job
qpu = get_default_qpu()
stack = ScipyMinimizePlugin(method="COBYLA",
                            tol=1e-5, 
                            options={"maxiter": max_iter}) | qpu
job = qaoa_ansatz.to_job(observable=problem_observable)

valid_sudokus = []
with open('valid_sudokus/valid_integers', 'rb') as file:
    valid_sudokus = dill.load(file)

path = 'results/QAOA/p' + str(depth) + '/'
    
print('Beginning standard QAOA (coloring) execution with parameters:')
print('QAOA depth: ' + str(depth))
print('Number of shots = ' + str(nbshots))
print('Number of algorithm iterations: ' + str(niter))

for i in range(niter):
    # minimization process
    result = stack.submit(job)
    print('Iteration '+ str(i+1) +': Final Energy: ' + str(result.value))
    result.dump(path + str(i+1) + '/minimize_result')
    
    # sampling process
    sampling_job = qaoa_ansatz.to_job()(**eval(result.meta_data["parameter_map"]))
    sampling_result = qpu.submit(sampling_job)
    
    # filtering valid sudokus
    valid_samples = []
    success_probability = 0
    for sudoku in valid_sudokus:
        valid_sample = sampling_result[sudoku]
        valid_samples.append(valid_sample)
        success_probability += valid_sample.probability
    print('Valid Sudokus: ' + str(success_probability))
    
    # storing results
    with open(path + str(i+1) + '/valid_samples', 'wb') as file:
        dill.dump(valid_samples, file)
        
    with open(path + str(i+1) + '/success_probability', 'w') as file:
        file.write(str(success_probability))
        
    print()
    
print('Finished algorithm!')
