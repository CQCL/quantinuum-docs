r"""Use and comparison of the paraparticle mapping from fermions to qubits"""

# imports
from pytket import Qubit
from pytket.extensions.qiskit import AerStateBackend

from inquanto.algorithms.vqe import AlgorithmVQE
from inquanto.ansatzes import FermionSpaceAnsatzUCCSD
from inquanto.computables.atomic import (
    ExpectationValue,
    ExpectationValueDerivative,
)
from inquanto.express import load_h5
from inquanto.mappings import QubitMappingJordanWigner, QubitMappingParaparticular
from inquanto.minimizers import MinimizerScipy
from inquanto.minimizers._minimizer_scipy import OptimizationMethod
from inquanto.protocols import SparseStatevectorProtocol
from inquanto.spaces import FermionSpace
from inquanto.states import FermionState

# Load in and generate data
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
fermion_operator = h2.hamiltonian_operator
fermion_space = FermionSpace(4)
fermion_hf_state = FermionState([1, 1, 0, 0])
qubits = [Qubit(i) for i in range(4)]

# Map the Hamiltonian using a Jordan-Wigner transformation
qubit_hamiltonian = QubitMappingJordanWigner.operator_map(fermion_operator, qubits)

# Generate an ansatz using both Jordan-Wigner and paraparticular mappings
# Using the paraparticle mapping reduces ansatz preparation gates & circuit depth.
ansatz_jw = FermionSpaceAnsatzUCCSD(
    fermion_space, fermion_hf_state, QubitMappingJordanWigner
)
ansatz_paraparticle = FermionSpaceAnsatzUCCSD(
    fermion_space, fermion_hf_state, QubitMappingParaparticular
)
print(
    "JW ansatz preparation circuit depth: {}".format(
        ansatz_jw.circuit_resources()["depth"]
    )
)
print(
    "Paraparticle ansatz preparation circuit depth: {}".format(
        ansatz_paraparticle.circuit_resources()["depth"]
    )
)

# Do VQE to validate that ground state energies are the same for both mappings
minimizer = MinimizerScipy(method=OptimizationMethod.L_BFGS_B_smooth, disp=False)

expectation_value_jw = ExpectationValue(ansatz_jw, qubit_hamiltonian)
gradient_expression_jw = ExpectationValueDerivative(
    ansatz_jw, qubit_hamiltonian, set(ansatz_jw.state_symbols.symbols)
)
protocol = SparseStatevectorProtocol(AerStateBackend())
jw_vqe = (
    AlgorithmVQE(
        objective_expression=expectation_value_jw,
        minimizer=minimizer,
        initial_parameters=ansatz_jw.state_symbols.construct_random(0, 0, 0.01),
        gradient_expression=gradient_expression_jw,
    )
    .build(
        protocol_objective=protocol,
        protocol_gradient=protocol,
    )
    .run()
)

expectation_value_pp = ExpectationValue(ansatz_paraparticle, qubit_hamiltonian)
gradient_expression_pp = ExpectationValueDerivative(
    ansatz_paraparticle,
    qubit_hamiltonian,
    set(ansatz_paraparticle.state_symbols.symbols),
)
protocol = SparseStatevectorProtocol(AerStateBackend())
parapart_vqe = (
    AlgorithmVQE(
        minimizer=minimizer,
        objective_expression=expectation_value_pp,
        initial_parameters=ansatz_paraparticle.state_symbols.construct_random(
            0, 0, 0.01
        ),
        gradient_expression=gradient_expression_pp,
    )
    .build(
        protocol_objective=protocol,
        protocol_gradient=protocol,
    )
    .run()
)

# compare final results
jw_energy = jw_vqe.generate_report()["final_value"]
parapart_energy = parapart_vqe.generate_report()["final_value"]
print(
    "Difference in energy between paraparticle and JW ansatz: {}".format(
        abs(jw_energy - parapart_energy)
    )
)

# should give the same energy to some numerical noise for each mapping
# but with a shallower ansatz for paraparticular
