r"""A canonical VQE simulation of OH(-) using (classical) CCSD or MP2 amplitudes."""
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

# === PYSCF calculations ===
#
# If the CCSD amplitudes are used both for the initial guess and the excitation
# oprator filterling, separate CCSD caluclation on the driver side is required.

# RHF with PySCF.
n_frozen_core = 1
mol = gto.Mole(
    atom="H 0 0 0; O 0 0 1.0",
    basis="sto3g",
    charge=-1,
)
mol.build()
mf = scf.RHF(mol).run()

# Unconverged CCSD to generate initial guess for the UCCSD ansatz.
mycc = cc.CCSD(mf)
mycc.frozen = n_frozen_core
mycc.max_cycle = 3
mycc.run()

# Generate the driver from the PySCF mean-field object.
driver = ChemistryDriverPySCFMolecularRHF.from_mf(
    mf,
    frozen=FrozenCore(n_frozen_core),
)
hamiltonian_operator, space, state_hf = driver.get_system()

# Prepare the qubit Hamiltonian.
jw = QubitMappingJordanWigner()
hermitian_operator = jw.operator_map(hamiltonian_operator)

# Generate the UCCSD ansatz with the filterd excitation operators and parameters.
compact = True
threshold = 1e-8
excitations_orig = driver.get_excitation_operators(space)

excitations = driver.get_excitation_operators(
    space,
    t1=mycc.t1,
    t2=mycc.t2,
    compact=compact,
    threshold=threshold,
)
amplitudes = driver.get_excitation_amplitudes(
    space,
    t1=mycc.t1,
    t2=mycc.t2,
    compact=compact,
    threshold=threshold,
)
print(f"Excitation operator reduction: {len(excitations_orig)} -> {len(excitations)}")

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
