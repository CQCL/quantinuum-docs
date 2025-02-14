r"""A simulation of H2 in STO-3G using the ADAPT algorithm."""

from pytket.extensions.qiskit import AerStateBackend

from inquanto.algorithms import AlgorithmAdaptVQE
from inquanto.express import load_h5
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.minimizers import MinimizerScipy
from inquanto.minimizers._minimizer_scipy import OptimizationMethod
from inquanto.protocols import SparseStatevectorProtocol
from inquanto.spaces import FermionSpace
from inquanto.states import FermionState

# Select a backend. Here we simulate the device behavior by explicitly evaluating the state vector.
state_backend = AerStateBackend()

# For this example we'll find the ground state of the h2 molecule in the sto-3g basis.
# We can load the information we need using the functionality from the express submodule.
# To see which other systems are available in express, one can import and call list_h5() from express.
# Also try out the h2_631g.h5 express to see more iterations in adapt-vqe
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
h2_hamiltonian = h2.hamiltonian_operator

# Since we are doing a variational experiment, we need to choose a minimizer. Here we select the L-BFGS-B minimizer
# available in SciPy.
scipy_minimizer = MinimizerScipy(method=OptimizationMethod.L_BFGS_B_smooth, disp=False)

# We now choose the scheme for mapping our fermionic quantities to qubit quantities. In this example we use the
# Jordan-Wigner scheme.
qubit_mapping = QubitMappingJordanWigner()

# Since we have 2 spatial orbitals in STO-3G H2, two electrons and singlet spin, our reference state is given by the
# vector [1, 1, 0, 0].
ref_state = h2.hf_state  # FermionState([1, 1, 0, 0 ])
# Since we are performing an ADAPT-VQE experiment, we must construct a pool of exponents from which we will select only
# those with the largest gradients during the optimization step(s).
space = h2.fermion_space  # FermionSpace(4)
exponent_pool = space.construct_single_ucc_operators(ref_state)
exponent_pool += space.construct_double_ucc_operators(ref_state)

# We can see from the above that we have constructed a pool of excitation operators which correspond to a UCCSD ansatz.
# Now we need to map them to qubit operators, and to map the hamiltonian to a qubit operator.
exponent_pool = qubit_mapping.operator_map(exponent_pool)

h2_hamiltonian = qubit_mapping.operator_map(h2_hamiltonian)

ref_state = qubit_mapping.state_map(ref_state)

# Now we have the components needed to perform an ADAPT-VQE experiment, we can instantiate the Algorithm object.
adapt = AlgorithmAdaptVQE(
    exponent_pool, ref_state, h2_hamiltonian, scipy_minimizer, disp=True
)

# In the next step we need to build the algorithm object, this includes providing a protocol object.
# The protocol defines the manner in which the objective function is evaluated.
# Here we use a StateVector protocol for evaluating the expectation values, the pool metric, and the gradient.
protocol = SparseStatevectorProtocol(state_backend)
adapt.build(
    protocol,
    protocol,
    protocol,
)

# Having constructed and built the algorithm object, we only need to call .run() to execute the experiment.
# By default the algorithm will report the state qubit operator exponents at each step.
adapt.run()

# All algorithm objects have a .generate_report() method for returning quantities of interest. Here we get our report
# then print our energy and parameters at the minimum of the objective function.
results = adapt.generate_report()

print("Minimum Energy: {}".format(results["final_value"]))
param_report = results["final_parameters"]
for i in range(len(param_report)):
    print(param_report[i]["Symbol"], ":", param_report[i]["Value"])
