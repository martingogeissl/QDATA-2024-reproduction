# Quantum Data Encoding Patterns and their Consequences

## Overview
This repository contains the necessary artefacts to reproduce the results of the experiments carried out as part of the work "Quantum Data Encoding Patterns and their Consequences". The [Jupyter Notebook](Encodings.ipynb) covers the steps from a provided Sudoku graph to the final QAOA circuit for every encoding instance.

The [code](code) and [data](data) folders contain the implementations and results of experiments conducted on the binary boolean encoding for a $4\times 4$ Sudoku. 

## Framework
We implemented the encodings on the quantum simulator [QLM](https://atos.net/en/solutions/quantum-learning-machine). As the QLM has restricted access, it may not be possible to execute the algorithms on the simulated QPU.

## [Encodings.ipynb](Encodings.ipynb)
The notebook starts of by introducing the Sudoku graph representation. AFter some required functions, the encodings are initiated using the [SymPy](https://www.sympy.org/en/index.html) library. For each encoding the amount of CNOTs and the circuit depth is outputted. The depth can vary, as some Observable to Ansatz strategies rely on heuristics.

## QAOA implementation
Due to prior research, we assessed the binary encoding on standard QAOA and two adapted Warm-Starting QAOA, as proposed by [Egger et al.](https://quantum-journal.org/papers/q-2021-06-17-479/)

The algorithm parameters and experiment details are as follows:

  * Algorithm executions per variant = $10$
  * QAOA depth = $1$
  * max optimizer iterations = $10000$
  * number of shots = $0$ (if $0$ => maximum possible number of shots)

Warm-starting specic details:
  * $\varepsilon$ = $0.25$

The python source code used in this project can be found in the [code](code) directory.

### Standard QAOA (QAOA)
> [QAOA.py](code/qaoa.py)

### Warm-starting QAOA with random initialization (WS-QAOA-RAND)
We simulated a relaxed solution to the general Sudoku problem by initializing the vector $c^\*$ with random values $c_i = [0,1]$ and regulated it with $\varepsilon$.
The $c^\*$ was then fed as a parameter into the adapted initial state and mixer operator of the QAOA circuit.

### Warm-starting QAOA with random row initialization (WS-QAOA-ROW)
For this variant, a random permuatation of the values from $1$ to $N$ is assgined to each row in the Sudoku. This produces a Sudoku, in which the row constraint is met.
This Sudoku is then translated to the $c^*$ vector, $\varepsilon$-regulated and fed to the warm-starting adapted QAOA circuit.


### Data
To conserve the results, the result objects have been serialised with the pickling based [dill](https://dill.readthedocs.io/en/latest/) module.
In each iteration folder the "minimize_result" object contains the results from the first QAOA phase, namely minimised final energy and optimal parameters $\gamma$ and $\beta$.

"success_probability" contains the total probability of retrieving a valid Sudoku.

"valid_samples" contain the set of valid binary encoded Sudokus with their measured probability after the number of shots.

