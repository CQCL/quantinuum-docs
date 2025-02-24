r"""Estimating energy using QCM4 computable."""

# imports

from pytket.extensions.qiskit import AerStateBackend

from inquanto.computables import ExpectationValue
from inquanto.computables.composite import QCM4Computable
from inquanto.ansatzes import CircuitAnsatz, reference_circuit_builder
from inquanto.express import load_h5
from inquanto.protocols import (
    SparseStatevectorProtocol,
)

# obtain a model system from express
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
hamiltonian = h2.hamiltonian_operator.qubit_encode()

# create an initial ansatz state for QCM4, in this case the Hartree-Fock state will suffice.
init_state = CircuitAnsatz(reference_circuit_builder([1, 1, 0, 0]))

# initialize the quantum computed moments computable
qcm4 = QCM4Computable(init_state, hamiltonian)

# prepare a state vector protocol to evaluate the computable
protocol_sv = SparseStatevectorProtocol(AerStateBackend())

# run the protocol to evaluate the computable
energy_qcm4 = qcm4.evaluate(protocol_sv.get_evaluator({}))
# an empty parameter dict was passed due to non-symbolic initial state
# for general symbolic ansatzes, parameters are needed.

# The energy computed up to 4th order Hamiltonian moments can be better than energy of initial input state.
print("QCM4 Energy (statevector calculation):", energy_qcm4)
print(
    "Energy from Hartree-Fock state:",
    ExpectationValue(init_state, hamiltonian).default_evaluate({}),
)
print("Classical CCSD Energy:", h2.energy_ccsd)
