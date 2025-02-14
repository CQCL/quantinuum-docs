r"""Noiseless statevector computation of one element of GF of Hubbard dimer by sandwiching Hamiltonian moments."""


# imports
import numpy

from sympy import Symbol

from matplotlib import pyplot

from pytket.extensions.qiskit import AerStateBackend

from inquanto.computables.composite import (
    ParticleGFComputable,
    HoleGFComputable,
)
from inquanto.express import DriverHubbardDimer
from inquanto.operators import FermionOperator
from inquanto.ansatzes import FermionSpaceAnsatzChemicallyAwareUCCSD
from inquanto.express import run_vqe
from inquanto.computables import ExpectationValue, ComputableTuple
from inquanto.protocols import SparseStatevectorProtocol


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

# get the exact ground state energy, to be compared with VQE energy
print(
    "Exact gs energy:",
    qubit_hamiltonian.eigenspectrum(state.single_term.hamming_weight)[0],
)

# instantiate the ansatz using the fermion space and state
ansatz = FermionSpaceAnsatzChemicallyAwareUCCSD(space, state)

# prepare a dictionary to parameterize the ansatz
parameters = ansatz.state_symbols.construct_random(2, 0.01, 0.1)

# backend for ideal noiseless statevector calculations
backend = AerStateBackend()

# run VQE, compare energy to exact value (get good approximation to ground state here), and store final parameters
vqe = run_vqe(
    ansatz,
    qubit_hamiltonian,
    backend,
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

# define the expectation values for moments for particle and hole parts of Green's function. <psi_0|c c^dagger|psi_0>
norm_computable = ExpectationValue(ansatz, ccdagger_qop)
norm_p = norm_computable.evaluate(
    SparseStatevectorProtocol(backend).get_evaluator(final_parameters)
).real

# <psi_0|c^dagger c|psi_0>
norm_computable = ExpectationValue(ansatz, cdaggerc_qop)
norm_h = norm_computable.evaluate(
    SparseStatevectorProtocol(backend).get_evaluator(final_parameters)
).real

# select dimension of Krylov space (2 sufficient for symmetric Hubbard dimer)
n_lanczos_roots = 2

# instantiate the Computables tuple for particle and hole parts of GF
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

# evaluate the Computables for GF00 element, define symbols for energy terms and broadening
gf00_p_object, gf00_h_object = lanczosgf.evaluate(
    SparseStatevectorProtocol(backend).get_evaluator(final_parameters)
)
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
pyplot.plot(linspace, gf00_list, marker="o")
pyplot.savefig("example_gf_measurenorm_element.png")
