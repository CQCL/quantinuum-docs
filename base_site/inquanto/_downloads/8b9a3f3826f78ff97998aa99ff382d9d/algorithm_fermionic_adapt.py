r"""A simulation of H2 in STO-3G using the ADAPT algorithm with fermionic helper functions."""
from pytket.extensions.qiskit import AerStateBackend

from inquanto.algorithms import AlgorithmFermionicAdaptVQE
from inquanto.express import load_h5
from inquanto.minimizers import MinimizerScipy
from inquanto.minimizers._minimizer_scipy import OptimizationMethod
from inquanto.protocols import SparseStatevectorProtocol
from inquanto.spaces import FermionSpace
from inquanto.states import FermionState

# Choose a backend for simulating the circuits/communicating with the device. Here we will explicitly construct
# the state-vector.
state_backend = AerStateBackend()

# We select the H2 STO-3G molecule and use the helper functions from the express module to accelerate the process.
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
h2_hamiltonian = h2.hamiltonian_operator

# For this experiment we use the scipy minimizer with the L-BFGS-B quasi-newton method.
scipy_minimizer = MinimizerScipy(method=OptimizationMethod.L_BFGS_B_smooth, disp=False)

# Since we have two spatial molecular orbitals, two electrons and singlet spin, we know the reference state is described
# by the occupation number vector [1, 1, 0, 0]. Notice we use FermionState, not QubitState since we're doing a
# Fermionic-ADAPT experiment.
ref_state = h2.hf_state  # FermionState([1, 1, 0, 0])

# Now we construct a pool of excitation operators to use when constructing the ansatz. In this case we use the set of
# exponents in the popular UCCSD ansatz. A FermionSpace object can be used to build the exponent pool with minimal
# effort from the user.
space = h2.fermion_space  # FermionSpace(4)
exponent_pool = space.construct_single_ucc_operators(ref_state)
exponent_pool += space.construct_double_ucc_operators(ref_state)

# Now we create the fermionic adapt algorithm object. Notice that we pass fermionic quantities, not qubit quantities.
fermionic_adapt = AlgorithmFermionicAdaptVQE(
    exponent_pool, ref_state, h2_hamiltonian, scipy_minimizer, disp=True
)

# Now we build and run the algorithm object using the state-vector protocol, as we chose a state-vector backend.
# The protocol dictates to the algorithm how we evaluate the quantities of interest.
# Here we build using the StateVector protocol for evaluating the expectation values, the pool metric, and the gradient.
protocol = SparseStatevectorProtocol(state_backend)
fermionic_adapt.build(protocol, protocol, protocol)

# Having constructed and built the algorithm object, we only need to call .run() to execute the experiment.
# By default the algorithm will report the state fermionic exponents at each step.
fermionic_adapt.run()

# Here we generate a report for the experiment which is a dictionary containing any important information the user might be
# interested in.
results = fermionic_adapt.generate_report()

print("Minimum Energy: {}".format(results["final_value"]))
param_report = results["final_parameters"]
for i in range(len(param_report)):
    print(param_report[i]["Symbol"], ":", param_report[i]["Value"])
