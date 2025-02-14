r"""A canonical VQE simulation of H2 in STO-3G using a variational configuration interaction Ansatz."""

# imports
from math import sqrt

from pytket import OpType
from pytket.extensions.qiskit import AerStateBackend

from inquanto.ansatzes import MultiConfigurationAnsatz
from inquanto.computables.atomic import (
    ExpectationValue,
    ExpectationValueDerivative,
)
from inquanto.states import QubitState, QubitStateString
from inquanto.express import load_h5
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.protocols import SparseStatevectorProtocol
from inquanto.algorithms import AlgorithmVQE
from inquanto.minimizers import MinimizerScipy


# In this example we will find the ground state energy of the H2 molecule in the STO-3G basis using VQE. First, we load
# in the system Hamiltonian from the express module.
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
hamiltonian_operator = h2.hamiltonian_operator

# We express our Hamiltonian as a qubit operator using the Jordan-Wigner mapping.
jw = QubitMappingJordanWigner()
hermitian_operator = jw.operator_map(hamiltonian_operator)

# Define the occupation state objects we'll use to construct the CI ansatz. These represent Slater determinants to be
# linearly combined.
qss_ref = QubitStateString([1, 1, 0, 0])
qss_2 = QubitStateString([0, 0, 1, 1])

# MultiConfigurationAnsatz takes a list of QubitStateStrings as its input argument.
qss_list = [qss_ref, qss_2]

# Now we can instantiate our ansatz easily by creating the object below. The circuit is generated at instantiation and
# can be accessed through the ansatz.state_circuit attribute.
# |psi> = a|1100> + b|0011>, b = SQRT(1 - |a|^2) => only 1 parameter in VQE
ansatz = MultiConfigurationAnsatz(qss_list)
print(ansatz.state_circuit)


print("Ansatz parameter info")
print("symbols:", ansatz.state_symbols.symbols)
# in this example we optimize 1 symbol that describes the normalized mixing of the two qubit state
print("N_parameters:", ansatz.n_symbols)
print("Ansatz report:\n", ansatz.generate_report())

# Define computables, protocol, and carry out VQE as usual.
expectation_value = ExpectationValue(ansatz, hermitian_operator)
gradient_expression = ExpectationValueDerivative(
    ansatz, hermitian_operator, ansatz.free_symbols()
)

protocol = SparseStatevectorProtocol(AerStateBackend())

vqe = (
    AlgorithmVQE(
        MinimizerScipy(disp=False),
        expectation_value,
        gradient_expression=gradient_expression,
        initial_parameters=ansatz.state_symbols.construct_zeros(),
    )
    .build(
        protocol,
        protocol,
    )
    .run()
)
energy = vqe.generate_report()["final_value"]
param_report = vqe.generate_report()["final_parameters"]
for i in range(len(param_report)):
    print(param_report[i]["Symbol"], ":", param_report[i]["Value"])

# circuit = ansatz.get_circuit(vqe.final_parameters)
print("\nState vector dataframe:\n", ansatz.df_numeric(vqe.final_parameters))

# energy from UCCSD: -1.13684657547
# energy from HF: -1.11750588420
print("energy from optimized multiconfiguration ansatz:", energy)
