r"""An example showing how to use evaluate gradients"""

# imports
from sympy import pi as PI, Symbol

from pytket import Circuit

from inquanto.ansatzes import CircuitAnsatz
from inquanto.computables import (
    ExpectationValueDerivative,
    ExpectationValueBraDerivativeReal,
    ExpectationValueBraDerivativeImag,
)
from inquanto.operators import QubitOperator

# Use pytket to construct a symbolic circuit
circ = Circuit(2)
circ.Ry(-2 * Symbol("a") / PI, 0)
circ.CX(0, 1)
circ.Rz(-2 * Symbol("b") / PI, 1)
circ.Rx(-2 * Symbol("c") / PI, 1)
circ.CX(1, 0)
circ.Ry(-2 * Symbol("d") / PI, 0)

# use the CircuitAnsatz class to create an ansatz based from the constructed circuit
ansatz = CircuitAnsatz(circ)

# for our ansatz prepare a dictionary to insert parameter values later
initial = ansatz.state_symbols.construct_from_array([0.1, 0.2, 0.3, 0.4])

# prepare a simple operator
kernel = (
    QubitOperator("X0 X1", 2) + QubitOperator("Y0 Y1", 2) + QubitOperator("Z0 Z1", 2)
)

# Below we evaluate a range of Computables for derivatives with a range of Protocols.
# Therefore we import a noise-free shot based backend and a statevector backend
# which we use to evaluate our protocols
from pytket.extensions.qiskit import AerBackend, AerStateBackend

from inquanto.protocols import (
    HadamardTestDerivative,
    SparseStatevectorProtocol,
    SymbolicProtocol,
)

backend = AerBackend()
sv_backend = AerStateBackend()

## Derivative

# evaluated with respect to the ansatz parameters
# make one of these computables for all evaluations in this section
expr = ExpectationValueDerivative(ansatz, kernel, ansatz.free_symbols())

runner = SymbolicProtocol().get_runner(expr)
# perform symbolic protocol to get evaluation
print("\nExpectationValueDerivative SymbolicProtocol \n", runner(initial))

# initialize statevector runner
runner = SparseStatevectorProtocol(sv_backend).get_runner(expr)
print("\nExpectationValueDerivative SparseStatevectorProtocol \n", runner(initial))

# initialize shot based runner with parallelized measurement
runner = HadamardTestDerivative(
    backend, shots_per_circuit=10000, direct=True
).get_runner(expr)
print("\nExpectationValueDerivative HadamardTestDerivative Direct \n", runner(initial))

# initialize shot based runner with ancilla measurement only
runner = HadamardTestDerivative(
    backend, shots_per_circuit=10000, direct=False
).get_runner(expr)
print(
    "\nExpectationValueDerivative HadamardTestDerivative Indirect \n", runner(initial)
)

## REAL BRA
# evaluated with respect to the ansatz parameters
# make one of these computables for all evaluations in this section
expr = ExpectationValueBraDerivativeReal(ansatz, kernel, ansatz.free_symbols())

runner = SymbolicProtocol().get_runner(expr)
print("\nExpectationValueBraDerivativeReal SymbolicProtocol\n", runner(initial))

runner = SparseStatevectorProtocol(sv_backend).get_runner(expr)
print(
    "\nExpectationValueBraDerivativeReal SparseStatevectorProtocol\n", runner(initial)
)

runner = HadamardTestDerivative(
    backend, shots_per_circuit=10000, direct=True
).get_runner(expr)
print(
    "\nExpectationValueBraDerivativeReal HadamardTestDerivative Direct\n",
    runner(initial),
)

runner = HadamardTestDerivative(
    backend, shots_per_circuit=10000, direct=False
).get_runner(expr)
print(
    "\nExpectationValueBraDerivativeReal HadamardTestDerivative Indirect\n",
    runner(initial),
)

## IMAG BRA
# make one of these computables for all evaluations in this section
expr = ExpectationValueBraDerivativeImag(ansatz, kernel, ansatz.free_symbols())

runner = SymbolicProtocol().get_runner(expr)
print("\nExpectationValueBraDerivativeImag SymbolicProtocol\n", runner(initial))

runner = SparseStatevectorProtocol(sv_backend).get_runner(expr)
print(
    "\nExpectationValueBraDerivativeImag SparseStatevectorProtocol\n", runner(initial)
)

runner = HadamardTestDerivative(
    backend, shots_per_circuit=10000, direct=True
).get_runner(expr)
print(
    "\nExpectationValueBraDerivativeImag HadamardTestDerivative Direct\n",
    runner(initial),
)

runner = HadamardTestDerivative(
    backend, shots_per_circuit=10000, direct=False
).get_runner(expr)
print(
    "\nExpectationValueBraDerivativeImag HadamardTestDerivative Indirect\n",
    runner(initial),
)
