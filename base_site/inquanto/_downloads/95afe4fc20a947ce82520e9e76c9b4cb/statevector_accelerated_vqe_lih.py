r"""LiH VQE simulation with and without gradients to demonstrate acceleration"""

# imports
from pytket.extensions.qiskit import AerStateBackend

from inquanto.extensions.pyscf import (
    ChemistryDriverPySCFMolecularRHF,
)  # inquanto-pyscf extension required here

from inquanto.computables.atomic._expectation_value_gradient import (
    ExpectationValueDerivative,
)
from inquanto.core import vector_to_dict, dict_to_vector
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.protocols import SparseStatevectorProtocol
from inquanto.ansatzes import FermionSpaceStateExp
from inquanto.computables import ExpectationValue
from inquanto.minimizers import MinimizerScipy

# instead of express, we will perform a restricted Hartree-Fock calculation of our system
# to build a mean-field description

# prepare geometry
zmatrix = """
H
Li 1 1.5
"""
# settings for HF calculation
charge = 0
basis = "STO-3G"

# instance driver
driver = ChemistryDriverPySCFMolecularRHF(
    zmatrix=zmatrix, charge=charge, basis=basis, point_group_symmetry=True, frozen=[0]
)

# run the HF and return the second quantized Fermionic operators, space, and state.
fermionic_hamiltonian, space, state = driver.get_system()
hamiltonian = QubitMappingJordanWigner().operator_map(fermionic_hamiltonian)

# use the FermionSpace of our system to construct the list of
# allowed single and double exponents for a given state
exponents = space.construct_single_ucc_operators(
    state
) + space.construct_double_ucc_operators(state)

# The exponents are a list of FermionOperators and their correspond
# symbolic coefficients. We can inspect the terms in our list
# for e in exponents:
# prints spin orbital indexes and creation/annihiliation action
#    print(e)

# This ansatz class takes the list of exponents and constructs the ansatz circuit
ansatz = FermionSpaceStateExp(exponents, state)
symbols = list(ansatz.free_symbols_ordered())
# we'll use 'zeros' to start our minimization later
initial = dict_to_vector(ansatz.state_symbols, ansatz.state_symbols.construct_zeros())

# prepare a statevector protocol to evaluate the expval computable
sv_protocol = SparseStatevectorProtocol(AerStateBackend())

# prepare the expval computable
expectation_computable = ExpectationValue(ansatz, hamiltonian)

# get the protocol runner for evaluation
runner_expectation_value = sv_protocol.get_runner(expectation_computable)


# make an objective function which evaluates the runner given a set of symbol values
def objective(parameter_array):
    return runner_expectation_value(vector_to_dict(symbols, parameter_array))


# instantiate an inquanto miminizer class
minimizer1 = MinimizerScipy(method="L-BFGS-B", disp=True)

# Manually perform an optimization to find the ansatz symbols by minimizing
# the total energy

# This will take a few minutes
minimizer1.minimize(objective, initial)
minimizer1.generate_report()


## Now we add gradients to aid our energy minimization
gradient_computable = ExpectationValueDerivative(
    ansatz, hamiltonian, ansatz.free_symbols()
)
runner_gradient = sv_protocol.get_runner(gradient_computable)


# define a new gradient function given this second computable
def gradient(parameter_array):
    gradient_dict = runner_gradient(vector_to_dict(symbols, parameter_array))
    return dict_to_vector(symbols, gradient_dict)


initial_energy = objective(
    dict_to_vector(symbols, ansatz.state_symbols.construct_zeros())
)
print(initial_energy)

initial_grad = gradient(dict_to_vector(symbols, ansatz.state_symbols.construct_zeros()))
print(initial_grad)

# Due to use of the gradients, this should be much quicker than the naive objective opt
minimizer1.minimize(objective, initial, gradient=gradient)
minimizer1.generate_report()
