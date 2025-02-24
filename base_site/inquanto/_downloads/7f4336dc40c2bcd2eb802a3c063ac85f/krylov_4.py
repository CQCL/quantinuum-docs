r"""Example of evaluating LanczosMatrixComputable with sandwiched moments from shot-based protocol."""

# imports
from sympy import Symbol
from pytket.partition import PauliPartitionStrat
from pytket.extensions.qiskit import AerStateBackend, AerBackend

from inquanto.computables.composite import LanczosMatrixComputable
from inquanto.express import DriverHubbardDimer
from inquanto.operators import FermionOperator
from inquanto.ansatzes import FermionSpaceAnsatzChemicallyAwareUCCSD
from inquanto.protocols import PauliAveraging

# define Hamiltonian H (here we use Hubbard dimer at half filling). Note t is negated in DriverHubbardDimer
u_hub = 2.15
t_hub = 0.3
n_sites = 2
driver = DriverHubbardDimer(t=t_hub, u=u_hub)
h, space, state = driver.get_system()

# this sets the chemical potential to -U/2 in the Hamiltonian
n1u = FermionOperator(((space.index(0, 0), 1), (space.index(0, 0), 0)))
n1d = FermionOperator(((space.index(0, 1), 1), (space.index(0, 1), 0)))
n2u = FermionOperator(((space.index(1, 0), 1), (space.index(1, 0), 0)))
n2d = FermionOperator(((space.index(1, 1), 1), (space.index(1, 1), 0)))
h -= 0.5 * u_hub * (n1u + n1d + n2u + n2d)
h += 0.5 * FermionOperator.identity() * u_hub

# define the ladder operator to sandwich the H moments in the expectation wrt GS, e.g. <c H c^> for particle GF00
c00 = FermionOperator(((space.index(0, 0), 0),))

# qubit encode the Fermion operators
qubit_c00 = c00.qubit_encode()
qubit_hamiltonian = h.qubit_encode()

# instantiate the ansatz (with some random parameters just to exemplify)
ansatz = FermionSpaceAnsatzChemicallyAwareUCCSD(space, state)
# Create sympy symbols
s0 = Symbol("s0")
s1 = Symbol("s1")
d0 = Symbol("d0")

# Initialize the parameters as a standard dictionary with the sympy symbols as keys
parameters = {
    s0: 0.24381667361759024,
    s1: -0.05628539080668208,
    d0: 0.04948596212311631,
}


# backend for shot-based protocol
backend = AerBackend()

# instantiate the Lanczos Computable up to desired Krylov space dimension (here, 2) using operators defined above
lanczos = LanczosMatrixComputable(
    ansatz, qubit_hamiltonian, krylov=2, left=qubit_c00.copy().dagger(), right=qubit_c00
)

# PauliAveraging protocol to measure H moments, commuting sets of Paulis to reduce the number of measured circuits
protocol = PauliAveraging(
    backend,
    shots_per_circuit=10000,
    pauli_partition_strategy=PauliPartitionStrat.CommutingSets,
)
# build measurement circuits for the computable
protocol.build_from(parameters, lanczos).compile_circuits()
# run the protocol to get shot results
protocol.run(seed=2)

# evaluate the Computable using shot results
krylov = lanczos.evaluate(evaluator=protocol.get_evaluator())

# protocol has methods to get info on measurements and circuits
print("Measurements:")
print(protocol.dataframe_measurements())
print("Circuits measured:")
print(protocol.dataframe_circuit_shot())

# the results: tridiagonal matrix rep of H
print()
print("Tridiagonal H representation (run1):")
print(krylov)
