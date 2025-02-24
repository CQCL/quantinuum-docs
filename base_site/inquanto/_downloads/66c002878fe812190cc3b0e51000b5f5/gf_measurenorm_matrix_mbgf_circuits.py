r"""Generation of the circuits required for the full GF matrix of the Hubbard dimer."""

# imports
import numpy as np

from pytket.extensions.qiskit import AerBackend, AerStateBackend
from pytket.partition import PauliPartitionStrat

from inquanto.computables.composite import (
    ManyBodyGFComputable,
)
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

# get fermionic ham, space, and state from driver
h, space, state = driver.get_system()
# we can print the hamiltonian for inspection
# print(h.df())

# create set of one-body excitation operators
n1u = FermionOperator(((space.index(0, 0), 1), (space.index(0, 0), 0)))
n1d = FermionOperator(((space.index(0, 1), 1), (space.index(0, 1), 0)))
n2u = FermionOperator(((space.index(1, 0), 1), (space.index(1, 0), 0)))
n2d = FermionOperator(((space.index(1, 1), 1), (space.index(1, 1), 0)))

# this sets the chemical potential to -U/2 in the Hamiltonian
# and adds the set of created operators
h -= 0.5 * u_hub * (n1u + n1d + n2u + n2d)

# add a constant term
h += 0.5 * FermionOperator.identity() * u_hub
# print(h.df())

# Jordan-Wigner encode the extended dimer hamiltonian
qubit_hamiltonian = h.qubit_encode()

# get the exact ground state energy through diagonalization, to be compared with VQE energy
print(
    "Exact gs energy:",
    qubit_hamiltonian.eigenspectrum(state.single_term.hamming_weight)[0],
)

# instantiate the ansatz using the fermion space and state
ansatz = FermionSpaceAnsatzChemicallyAwareUCCSD(space, state)

# prepare a dictionary to parameterize the ansatz
parameters = ansatz.state_symbols.construct_random(2, 0.01, 0.1)

# run VQE, compare energy to exact value (noiseless calculation for ground state), and store final parameters
vqe = run_vqe(
    ansatz,
    qubit_hamiltonian,
    AerStateBackend(),
    with_gradient=False,
    initial_parameters=parameters,
)
energy = vqe.generate_report()["final_value"]
print("Minimum Energy: {}".format(energy))
final_parameters = vqe.final_parameters


# select dimension of Krylov space (2 sufficient for symmetric Hubbard dimer)
n_lanczos_roots = 2

# backend for shot-based protocol (needed for circuits)
backend = AerBackend()

# PauliAveraging protocol to measure H moments, commuting sets of Paulis to reduce the number of measured circuits
protocol = PauliAveraging(
    backend,
    shots_per_circuit=10000,
    pauli_partition_strategy=PauliPartitionStrat.CommutingSets,
)

# instantiate the GF Computable
gf_class = ManyBodyGFComputable(
    space, ansatz, qubit_hamiltonian, n_lanczos_roots, ground_state_energy=energy
)

# build the computable's protocol,
protocol.build_from(final_parameters, gf_class)

# examine circuit information
print(
    "Number of measurement circuits for lanczos: " + str(len(protocol.get_circuits()))
)

print(protocol.dataframe_circuit_shot())

# next steps
# protocol.run()
# gf_object_matrix_func = gf_class.evaluate(protocol.get_evaluator(final_parameters))
