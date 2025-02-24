r"""Use of minimizers."""

# imports
import numpy as np

from pytket.extensions.qiskit import AerStateBackend

from inquanto.ansatzes import FermionSpaceAnsatzUCCSD
from inquanto.computables.atomic import ExpectationValue, ExpectationValueDerivative
from inquanto.core import vector_to_dict, dict_to_vector
from inquanto.express import load_h5
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.minimizers import (
    MinimizerRotosolve,
    MinimizerSGD,
    MinimizerSPSA,
    MinimizerScipy,
)
from inquanto.minimizers._minimizer_scipy import OptimizationMethod
from inquanto.protocols import SparseStatevectorProtocol
from inquanto.spaces import FermionSpace
from inquanto.states import FermionState

# get a model system from express
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
hamiltonian_operator = h2.hamiltonian_operator
space = FermionSpace(4)
state = FermionState([1, 1, 0, 0])

jw_map = QubitMappingJordanWigner()
qubit_hamiltonian_operator = jw_map.operator_map(hamiltonian_operator)
ansatz = FermionSpaceAnsatzUCCSD(space, state)

# Define and build expression to be evaluated inside objective function
expression = ExpectationValue(ansatz, qubit_hamiltonian_operator)
gradient = ExpectationValueDerivative(
    ansatz, qubit_hamiltonian_operator, ansatz.state_symbols
)
runner_objective = SparseStatevectorProtocol(AerStateBackend()).get_runner(expression)
gradient_objective = SparseStatevectorProtocol(AerStateBackend()).get_runner(gradient)

# generate random initial amplitudes
initial_parameters = ansatz.state_symbols.construct_random(seed=0, mu=0.0, sigma=0.01)
ordered_symbols = list(expression.free_symbols_ordered())

# simple modified expectationvalue function
def my_objective_function(numpy_parameters):
    parameters = vector_to_dict(ordered_symbols, numpy_parameters)
    result = runner_objective(parameters)
    return (1.0 - (result.conjugate() * result).real) ** 2


# example gradient function to use in SGD
def my_gradient_function(numpy_parameters):
    parameters = vector_to_dict(ordered_symbols, numpy_parameters)
    result = np.asarray(list(gradient_objective(parameters).values()))
    return result


numpy_initial_parameters = dict_to_vector(ordered_symbols, initial_parameters)

minimizer = MinimizerRotosolve(disp=True)
minimizer.minimize(my_objective_function, numpy_initial_parameters)

# SGD requires a gradient function
minimizer = MinimizerSGD(
    learning_rate=0.01, decay_rate=0.05, max_iterations=5, disp=True, callback=None
)
minimizer.minimize(
    my_objective_function, numpy_initial_parameters, my_gradient_function
)

# Simultaneous Perturbation Stochastic Approximation
minimizer = MinimizerSPSA(max_iterations=5, disp=True)
minimizer.minimize(my_objective_function, numpy_initial_parameters)

# Wrapped Scipy minimizers with different methods
minimizer = MinimizerScipy(method=OptimizationMethod.L_BFGS_B_smooth, disp=True)
minimizer.minimize(my_objective_function, numpy_initial_parameters)

minimizer = MinimizerScipy(method="COBYLA", disp=True)
minimizer.minimize(my_objective_function, numpy_initial_parameters)
