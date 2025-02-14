r"""Computation (shots for Lanczos, statevector for ground state) one element of GF of Hubbard dimer."""


# imports
import numpy

from sympy import Symbol

from matplotlib import pyplot

from pytket.extensions.qiskit import AerBackend, AerStateBackend  #
from pytket.partition import PauliPartitionStrat

from inquanto.computables.composite import (
    ParticleGFComputable,
    HoleGFComputable,
)
from inquanto.express import DriverHubbardDimer
from inquanto.operators import FermionOperator
from inquanto.ansatzes import FermionSpaceAnsatzChemicallyAwareUCCSD
from inquanto.express import run_vqe
from inquanto.computables import ExpectationValue, ComputableTuple
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
# AerStateBackend backend for ideal noiseless statevector calculations
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


# define the ladder operators for the 00 element of GF
create_i_from_fop = FermionOperator.from_string(f"(1.0, F{0}^)").qubit_encode()
anhil_j_from_fop = FermionOperator.from_string(f"(1.0, F{0})").qubit_encode()
ccdagger_qop = anhil_j_from_fop * create_i_from_fop
cdaggerc_qop = create_i_from_fop * anhil_j_from_fop


# use the ladder operators to define the Computables for moment expectations for particle and hole parts
part_hole_comp = ComputableTuple(
    ExpectationValue(ansatz, ccdagger_qop), ExpectationValue(ansatz, cdaggerc_qop)
)


# prepare a protocol which we can use to build circuits for measurement needed for the computable
# this uses commuting sets of Paulis to reduce the number of measured circuits
pa_protocol = PauliAveraging(
    backend=AerBackend(),  # shot based
    shots_per_circuit=10000,
    pauli_partition_strategy=PauliPartitionStrat.CommutingSets,
)

# make measurement circuits
pa_protocol.build_from(
    final_parameters,
    part_hole_comp,
).compile_circuits()

# run the protocol to get shot results from AerBackend
pa_protocol.run(seed=0)

# can inspect shot results
# print(pa_protocol.dataframe_measurements())

# use the protocol results to evaluate the computable
norm_p, norm_h = part_hole_comp.evaluate(pa_protocol.get_evaluator())


# select dimension of Krylov space
n_lanczos_roots = 2

# define Computables for particle and hole parts of GF
lanczosgf_p = ParticleGFComputable(
    ansatz,
    qubit_hamiltonian,
    n_lanczos_roots,
    left=anhil_j_from_fop,
    right=create_i_from_fop,
)
lanczosgf_h = HoleGFComputable(
    ansatz,
    qubit_hamiltonian,
    n_lanczos_roots,
    left=create_i_from_fop,
    right=anhil_j_from_fop,
)
lanczosgf = ComputableTuple(lanczosgf_p, lanczosgf_h)

# use protocol defined above to evaluate the GF00 element (symbols for energy terms and broadening)

# remove previous circuits from protocol
# keep run parameters (10000 shots, commuting sets)
pa_protocol.clear()

# built circuits for lanczos gf computable
pa_protocol.build_from(final_parameters, lanczosgf).compile_circuits()

# get shot results for lanczos
pa_protocol.run(seed=0)

# evaluate the computable using shots
gf00_p_object, gf00_h_object = lanczosgf.evaluate(pa_protocol.get_evaluator())
gf00_object = gf00_p_object + gf00_h_object
gf00_object = gf00_object.subs({Symbol("e0"): energy, Symbol("eta"): 0})
z = Symbol("z")
gf00_omega_symbolic = gf00_object.subs(z, Symbol("w") + 0.01j)

# define energy range for plotting
linspace = numpy.linspace(-3.0, 3.0, 100)

# get imaginary part of GF00 element values at each energy (or frequency, omega), and plot them
gf00_list = []
for omega in linspace:
    # gf00_omega = complex(gf00_omega_symbolic.evalf(subs={Symbol('w'): omega})).real
    gf00_omega = complex(gf00_omega_symbolic.evalf(subs={Symbol("w"): omega})).imag
    gf00_list.append(gf00_omega)

# plot the gf00 response function
pyplot.plot(linspace, gf00_list, marker="o")
pyplot.savefig("example_gf_measurenorm_element_shots_1.png")
