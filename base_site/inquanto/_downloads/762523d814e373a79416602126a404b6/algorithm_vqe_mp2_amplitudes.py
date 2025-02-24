r"""A canonical VQE simulation of OH(-) using (classical) MP2 amplitudes."""
###
from pyscf import gto, scf, cc

from pytket.extensions.qiskit import AerStateBackend

from inquanto.algorithms import AlgorithmVQE
from inquanto.ansatzes import FermionSpaceStateExp
from inquanto.computables import ExpectationValue, ExpectationValueDerivative
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.minimizers import MinimizerScipy
from inquanto.protocols import SparseStatevectorProtocol

from inquanto.extensions.pyscf import ChemistryDriverPySCFMolecularRHF, FrozenCore

# The MP2 amplitudes are used only for preparing the initial parameters,
# following simplified method is available.
# More precisely, the initial guess is taken from CCSD initial guess of PySCF.

n_frozen_core = 1

driver = ChemistryDriverPySCFMolecularRHF(
    geometry="H 0 0 0; O 0 0 1.0",
    basis="sto3g",
    charge=-1,
    frozen=FrozenCore(n_frozen_core),
)

hamiltonian_operator, space, state_hf = driver.get_system()

# Prepare the qubit Hamiltonian.
jw = QubitMappingJordanWigner()
hermitian_operator = jw.operator_map(hamiltonian_operator)

# Generate the UCCSD ansatz with the MP2 amplitudes.
excitations = driver.get_excitation_operators(space)
amplitudes = driver.get_excitation_amplitudes(space)
ansatz = FermionSpaceStateExp(
    fermion_operator_exponents=excitations,
    fock_state=state_hf,
    qubit_mapping=jw,
)

# The quantity we wish to minimize is the expectation value of the Hamiltonian, so we can create the appropriate
# computable.
expectation_value = ExpectationValue(ansatz, hermitian_operator)

# To accelerate the VQE we can evaluate analytic gradients, to do this we have a convenience function available from
# the expectation value computable.
gradient_expression = ExpectationValueDerivative(
    ansatz, hermitian_operator, ansatz.free_symbols_ordered()
)

# Since we are doing a state-vector simulation we need to choose a state-vector protocol.
protocol = SparseStatevectorProtocol(AerStateBackend())

# Now we can run our VQE experiment after instantiation and calling the build method.
vqe = (
    AlgorithmVQE(
        objective_expression=expectation_value,
        minimizer=MinimizerScipy(options={"disp": False}),
        # initial_parameters=ansatz.state_symbols.construct_zeros(),
        initial_parameters=amplitudes,
        gradient_expression=gradient_expression,
    )
    .build(
        protocol_objective=protocol,
        protocol_gradient=protocol,
    )
    .run()
)

# Show the results.
print("CCSD Energy:    {}".format(driver.run_ccsd()))
print("Minimum Energy: {}".format(vqe.generate_report()["final_value"]))
param_report = vqe.generate_report()["final_parameters"]
for i in range(len(param_report)):
    s = param_report[i]["Symbol"]
    v = param_report[i]["Value"]
    print(f"{s:10s}: {v:15.8f}")
