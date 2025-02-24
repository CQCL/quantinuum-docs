r"""Use of KrylovSubspaceComputable to get Green's function element from shot-based protocol from 1st Lanczos vector."""

# imports
from pytket.partition import PauliPartitionStrat
from pytket.extensions.qiskit import AerBackend

from inquanto.computables.composite import KrylovSubspaceComputable
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

# Jordan-Wigner encode H, then instantiate the ansatz (random parameters here just to exemplify)
qubit_hamiltonian = h.qubit_encode()
# here, the ansatz is the 1st Lanczos vector (e.g. |v_1> = c^|psi_GS> for particle GF00), not ground state
ansatz = FermionSpaceAnsatzChemicallyAwareUCCSD(space, state)
parameters = ansatz.state_symbols.construct_random(2, 0.01, 0.1)

# shot-based protocol and evaluation, so use AerBackend
backend = AerBackend()

# instantiate the Computable up to the desired Krylov space dimension (here, 4)
lanczos = KrylovSubspaceComputable(ansatz, qubit_hamiltonian, 4)

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

# from the Lanczos coefficients, the GF elements are calculated in the continued fraction representation
print("G_00 for the Lanczos matrix:")
print(result.construct_symbolic_recursive_lanczos_gf00())

# the eigenvalues of tridiagonal matrix are also an approximation to the true eigenvalues
print()
print("Eigenvalues")
print("For Lanczos matrix:        ", result.eigenvalues())
exact = qubit_hamiltonian.eigenspectrum(state.single_term.hamming_weight)
print("Exact diagonalization: ", exact)
