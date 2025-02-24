r"""A simulation of H2 in STO-3G using IQEB algorithm."""
from pytket.extensions.qiskit import AerStateBackend

from inquanto.algorithms.adapt import AlgorithmIQEB
from inquanto.express import load_h5
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.minimizers import MinimizerScipy
from inquanto.minimizers._minimizer_scipy import OptimizationMethod
from inquanto.protocols import SparseStatevectorProtocol
from inquanto.spaces import ParaFermionSpace
from inquanto.states import QubitState

# Choose a backend for the experiment. We'll be constructing the state-vector explicitly with the AerStateBackend.
state_backend = AerStateBackend()

# Now, by using the convenience functionality in the express submodule, we can load in the necessary molecular
# quantities for the experiment. In this case, we only need the hamiltonian operator.
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
h2_hamiltonian = h2.hamiltonian_operator

# We're performing a VQE experiment, so we need a minimizer. In this example we choose the SciPy implementation of
# the L-BFGS-B quasi-newton method.
scipy_minimizer = MinimizerScipy(method=OptimizationMethod.L_BFGS_B_smooth, disp=False)

# Our Hamiltonian is expressed as a fermionic Hamiltonian, so we need to choose a mapping scheme. Jordan-Wigner is the
# most popular and most intuitive mapping, so we will proceed with that.
qubit_mapping = QubitMappingJordanWigner()

# We know that our system has two spatial orbitals, two electrons and is of singlet spin. So we choose our reference
# state to be the [1, 1, 0, 0] occupation number vector.
ref_state = QubitState([1, 1, 0, 0])

# Since we're performing an iterative qubit excitation based ansatz, we need to construct a pool of exponents. We will
# construct single and double qubit excitations using the ParaFermionSpace object.
space = ParaFermionSpace(4)
exponent_pool = space.construct_single_qubit_excitation_operators()
exponent_pool += space.construct_double_qubit_excitation_operators()

# Now we just need to map our fermionic Hamiltonian to a qubit Hamiltonian using the QubitMappingJordanWigner object we
# constructed earlier. This can be done by calling the .operator_map() method.
h2_hamiltonian = qubit_mapping.operator_map(h2_hamiltonian)

# Now we instantiate the AlgorithmIQEB object with the exponent pool, reference state, qubit Hamiltonian and minimizer.
# We also specify the number of VQEs we want to run per IQEB iteration to narrow down the excitation pool by passing
# the n_grads argument.
iqeb = AlgorithmIQEB(
    exponent_pool,
    ref_state,
    h2_hamiltonian,
    scipy_minimizer,
    disp=True,
    n_grads=3,
)

# We will be running this on a state-vector backend, so the algorithm must be built with a state-vector protocol.
protocol = SparseStatevectorProtocol(state_backend)

# Here we build using the StateVector protocol for evaluating the expectation values, the pool metric, and the gradient.
iqeb.build(
    protocol,
    protocol,
    protocol,
)

iqeb.run()

# Now we have the results, we can generate a report and print the quantities of interest.
print("Minimum Energy: {}".format(iqeb.generate_report()["final_value"]))
param_report = iqeb.generate_report()["final_parameters"]
for i in range(len(param_report)):
    print(param_report[i]["Symbol"], ":", param_report[i]["Value"])
