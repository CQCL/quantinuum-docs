r"""An example running QSE using computables"""

# imports
import numpy as np

from pytket.extensions.qiskit import AerBackend, AerStateBackend
from pytket.partition import PauliPartitionStrat

# These calculations can be attempted with a simple NoiseModel using the imports below
# from from qiskit_aer.noise import ReadoutError, NoiseModel

from inquanto.computables.composite import QSEMatricesComputable
from inquanto.core import pd_safe_eigh
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.ansatzes import TrotterAnsatz
from inquanto.express import load_h5
from inquanto.operators import QubitOperator, QubitOperatorList
from inquanto.protocols import (
    SparseStatevectorProtocol,
)
from inquanto.protocols import PauliAveraging
from inquanto.spaces import FermionSpace
from inquanto.states import QubitState


# applied when printing out matrix results
np.set_printoptions(linewidth=1000, precision=6, suppress=True)

# obtain a model system from express
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
hamiltonian = h2.hamiltonian_operator.qubit_encode()
space = FermionSpace(4)

# prepare a compare state
ansatz = TrotterAnsatz(
    QubitOperatorList.from_list([QubitOperator("Y0 X1 X2 X3", 1j)]),
    QubitState([1, 1, 0, 0]),
)
# generate a dictionary for the state parameters
parameters = ansatz.state_symbols.construct_from_array([0.01])

# generate excitation space
expansion_operators = QubitMappingJordanWigner.operator_map(
    space.generate_subspace_singlet_singles()
)

# initialize the quantum subspace expansion computable
m = QSEMatricesComputable(ansatz, hamiltonian, expansion_operators)

# prepare a state vector protocol to evaluate the computable
protocol_sv = SparseStatevectorProtocol(AerStateBackend())

# run the protocol to evaluate the computable matrices
H, S = m.evaluate(evaluator=protocol_sv.get_evaluator(parameters))

print("STATEVECTOR CALCULATION:")
print("H matrix:")
print(H)
print("S matrix:")
print(S)
# next line yields a complex>real warning as statevectors yield amplitudes
e, _, _ = pd_safe_eigh(H.astype(float), S.astype(float))

# Check the ground state energy.
# NOTE: it does not need to be E(QSE) = E(FCI) in general, but it should be
#       in the minimal-basis H2 with YXXX ansatz with a nonzero parameter.
print(f"E(QSE) = {e[0]}, E(FCI) = {h2.energy_casci}")
assert np.isclose(e[0], h2.energy_casci)


# Here introduce a shot based quantum measurement protocol to compare to state vector
protocol_oa = PauliAveraging(
    AerBackend(),
    shots_per_circuit=10000,
    pauli_partition_strategy=PauliPartitionStrat.CommutingSets,
)

# In comparison to the SV protocol, PauliAveraging is a measurement circuit based protocol,
# it needs to build measurement circuits for the target computable expressions. We use the build_from method
# which takes the computable expression and parameters and produces measurement circuits.
protocol_oa.build_from(parameters, m).compile_circuits()

# Furthermore, the measurement circuits also need to be measured on the backend device or simulator.
# For example with the run method.
protocol_oa.run(seed=0)
# the protocol now contains shot results


# After the measurement circuits are measured, the protocol can provide an evaluator function for the
# computable expression it was built for, or any computable expressions that the same measurement circuits are
# compatible with.
H, S = m.evaluate(evaluator=protocol_oa.get_evaluator())

# The results below are 'noisy' due to finite sampling.
# Increasing shots will improve the matrix elements and the final eigenvalues
print("SHOT BASED CALCULATION:")
print("H matrix:")
print(H.astype(complex))
print("S matrix:")
print(S.astype(complex))
e, _, _ = pd_safe_eigh(H.astype(complex), S.astype(complex))
print(f"E(QSE) = {e[0]}, E(FCI) = {h2.energy_casci}")
