r"""Example of evaluating KrylovSubspaceComputable with sandwiched moments from shot-based protocol."""

# imports
from pytket.extensions.qiskit import AerStateBackend, AerBackend
from pytket.partition import PauliPartitionStrat

from inquanto.computables.composite import KrylovSubspaceComputable
from inquanto.express import DriverHubbardDimer
from inquanto.operators import FermionOperator
from inquanto.ansatzes import FermionSpaceAnsatzChemicallyAwareUCCSD
from inquanto.express import run_vqe
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

# instantiate the ansatz for the ground state, and run vqe as a noiseless statevector calculation
ansatz = FermionSpaceAnsatzChemicallyAwareUCCSD(space, state)
vqe = run_vqe(ansatz, qubit_hamiltonian, AerStateBackend(), with_gradient=False)
print("VQE:  ground state energy = ", vqe.final_value)
print("VQE:  parameters = ", vqe.final_parameters)
parameters = vqe.final_parameters

# backend for shot-based protocol
backend = AerBackend()

# instantiate the Computable to desired Krylov dimension (here, 3). Note only operators left = right^ are allowed
lanczos = KrylovSubspaceComputable(
    ansatz, qubit_hamiltonian, 3, left=qubit_c00.copy().dagger(), right=qubit_c00
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
result = lanczos.evaluate(evaluator=protocol.get_evaluator())

# protocol has methods to get info on measurements and circuits
print("Measurements:")
print(protocol.dataframe_measurements())
print("Circuits measured:")
print(protocol.dataframe_circuit_shot())

# the eigenvalues of tridiagonal matrix are also an approximation to the true eigenvalues
print()
print("Eigenvalues")
print("For Lanczos matrix:        ", result.eigenvalues())
exact = qubit_hamiltonian.eigenspectrum(1)
print("Exact diagonalization: ", exact)
