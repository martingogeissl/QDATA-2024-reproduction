# Data Encoding Patterns and their Impact on Quantum Algorithms in the NISQ Era

## Overview
This repository contains the necessary artefacts to reproduce the results of the experiments carried out as part of the work "Data Encoding Patterns and their Impact on Quantum Algorithms in the NISQ Era"
As the execution was performed on the quantum simulator [QLM](https://atos.net/en/solutions/quantum-learning-machine) with restricted access, we offer two ways to reproduce our results. For those who do not have access to the QLM, we provide the retrieved raw data to reproduce the recorded data.

## Algorithms
The conducted resarch contains three variants of the QAOA, the standard version and two war-starting versions.
As detailed in our paper in section *Warm-starting graph coloring problems*, there is no definitive way to determine a warm-starting option for graph coloring problems and derivations of such. 
Hence we examined the usage of a random initialization to simulate a warm-starting deviation from the standard QAOA.

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


## Data

## Reproduction with QLM

## Reproduction without QLM
