r"""Use of minimizers in shot-based calculations."""

# Imports
from pytket.extensions.qiskit import AerBackend
from inquanto.ansatzes import FermionSpaceAnsatzUCCSD
from inquanto.algorithms import AlgorithmVQE
from inquanto.computables.atomic import ExpectationValue
from inquanto.express import load_h5
from inquanto.minimizers import MinimizerRotosolve, MinimizerScipy
from inquanto.minimizers._minimizer_scipy import OptimizationMethod
from inquanto.protocols import PauliAveraging

# Get a model system from express
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
hamiltonian = h2.hamiltonian_operator
space = h2.fermion_space
state = h2.hf_state

# Initialize ansatz, qubit Hamiltonian, and expectation value calculator
ansatz = FermionSpaceAnsatzUCCSD(space, state)
qubit_hamiltonian = hamiltonian.qubit_encode()
expectation_value = ExpectationValue(ansatz, qubit_hamiltonian)
protocol = PauliAveraging(AerBackend(), shots_per_circuit=10000)

# Generate initial parameters
initial_parameters = ansatz.state_symbols.construct_zeros()

minimizer = MinimizerRotosolve(disp=False)
# Simple modified VQE function
def execute_vqe_with_minimizer(minimizer_in):
    vqe = (
        AlgorithmVQE(
            minimizer_in,
            expectation_value,  # Pass expectation_value defined outside the function
            initial_parameters=initial_parameters,  # Pass initial_parameters defined outside the function
        )
        .build(
            protocol_objective=protocol,
        )
        .run()
    )
    final_energy = vqe._final_value
    diff = abs(-1.13684657547 - final_energy)
    print("Minimum Energy: {}".format(final_energy))
    print("Difference with UCCSD: {}".format(diff))


# energy from UCCSD: -1.13684657547
# energy from HF: -1.11750588420

# Rotosolve minimizer
minimizer = MinimizerRotosolve(disp=True)
execute_vqe_with_minimizer(minimizer)

# Wrapped Scipy minimizers with different methods

# L-BFGS-B method with updated default settings
minimizer = MinimizerScipy(method=OptimizationMethod.L_BFGS_B_coarse, disp=True)
execute_vqe_with_minimizer(minimizer)

# L-BFGS-B method with Scipy default settings
minimizer = MinimizerScipy(method=OptimizationMethod.L_BFGS_B_smooth, disp=True)
execute_vqe_with_minimizer(minimizer)

# COBYLA method with Scipy default settings
minimizer = MinimizerScipy(method="COBYLA", disp=True)
execute_vqe_with_minimizer(minimizer)
