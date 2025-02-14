r"""Calculate oscillator strengths using VQE and VQD."""

import numpy as np
from pyscf import mcscf
from inquanto.extensions.pyscf import ChemistryDriverPySCFMolecularRHF, FromActiveSpace
from pytket.extensions.qiskit import AerStateBackend

from inquanto.algorithms import AlgorithmVQD, AlgorithmVQE
from inquanto.ansatzes import FermionSpaceAnsatzUCCSD
from inquanto.computables import ExpectationValue, Overlap, OverlapSquared
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.minimizers import MinimizerScipy
from inquanto.protocols import SparseStatevectorProtocol

# Initialise the driver with the molecular information
ncas = 3
nelecas = 2
nstates = 2
driver = ChemistryDriverPySCFMolecularRHF(
    geometry="""
        O 0.0000  0.0000 -0.1173
        H 0.0000 -0.7572  0.4692
        H 0.0000  0.7572  0.4692
    """,
    basis="sto-3g",
    charge=0,
    frozen=FromActiveSpace(ncas=ncas, nelecas=nelecas),
    point_group_symmetry=True,
)

# Get the data to be mapped onto quantum computers
hamiltonian, fock_space, fock_state = driver.get_system()

# Define the mapping
mapping = QubitMappingJordanWigner()

# Find the dipole operator in each direction
dipole_x, dipole_y, dipole_z = driver.compute_one_electron_operator(oper="dm")
dipole_x_qo = mapping.operator_map(dipole_x)
dipole_y_qo = mapping.operator_map(dipole_y)
dipole_z_qo = mapping.operator_map(dipole_z)
print("Dipole operator (X):", dipole_x_qo)
print("Dipole operator (Y):", dipole_y_qo)
print("Dipole operator (Z):", dipole_z_qo)
print()

# Map the Hamiltonian to qubits
qubit_hamiltonian = mapping.operator_map(hamiltonian)


### First, the ground state (VQE):

# Define the ansatz
ansatz_vqe = FermionSpaceAnsatzUCCSD(fock_space, fock_state, mapping)

# Choose the computable, in this case the expectation value
expectation_value = ExpectationValue(ansatz_vqe, qubit_hamiltonian)

# Choose the minimizer
minimizer = MinimizerScipy()

# Initialise the parameters
initial_parameters = ansatz_vqe.state_symbols.construct_zeros()

# Run the VQE algorithm
protocol = SparseStatevectorProtocol(AerStateBackend())
vqe = AlgorithmVQE(
    objective_expression=expectation_value,
    minimizer=minimizer,
    initial_parameters=initial_parameters,
)
vqe.build(protocol_objective=protocol)
vqe.run()

# Print the results
print()
print("VQE ground state:")
print(f" - Parameters: {vqe.final_parameters}")
print(f" - Energy: {vqe.final_value}")
print()


### Next, the excited state (VQD):

# Define the ansatz by copying the VQE ansatz with new symbols
ansatz_vqd = ansatz_vqe.subs("{}_2")

# Choose the computable, we also need weight and overlap now
expectation_value = ExpectationValue(ansatz_vqd, qubit_hamiltonian)
weight_expression = ExpectationValue(ansatz_vqd, -1 * qubit_hamiltonian)
overlap_expression = OverlapSquared(ansatz_vqe, ansatz_vqd)

# Run the VQD algorithm
protocol = SparseStatevectorProtocol(AerStateBackend())
vqd = AlgorithmVQD(
    expectation_value,
    overlap_expression,
    weight_expression,
    minimizer,
    ansatz_vqd.state_symbols.construct_random(seed=0),
    vqe._final_value,
    vqe._final_parameters,
    nstates,
)
vqd.build(
    objective_protocol=protocol,
    overlap_protocol=protocol,
    weight_protocol=protocol,
)
vqd.run()

# Print the results
print()
for i, (params, value) in enumerate(zip(vqd.final_parameters, vqd.final_values)):
    if i == 0:
        # This is just the ground state
        continue
    print(f"VQD excited state {i}:")
    print(f" - Parameters: {params}")
    print(f" - Energy: {value}")
    print(f" - Gap: {value - vqe.final_value}")

    # Collect the parameters
    all_parameters = vqe.final_parameters.copy()
    all_parameters.update(vqd.final_parameters[i])

    # Find the dipole measurements for each direction
    dip = []
    for component, direction in zip(
        [dipole_x_qo, dipole_y_qo, dipole_z_qo], ["X", "Y", "Z"]
    ):
        tdm_component = Overlap(ansatz_vqe, ansatz_vqd, component)
        protocol = SparseStatevectorProtocol(AerStateBackend())
        dip.append(tdm_component.evaluate(protocol.get_evaluator(all_parameters)))
        print(f" - Dipole ({direction}): {dip[-1].real}")

    # Get the oscillator strength
    f = (2.0 / 3.0) * (value - vqe.final_value) * np.einsum("x,x->", dip, dip).real
    print(f" - Oscillator strength: {f}")


### Use PySCF to compare the results to CASCI:

# Run CASCI
mc = mcscf.CASCI(driver._mf.run(), ncas, nelecas)
mc.fcisolver.nroots = nstates + 1  # Include the ground state
es = mc.kernel()[0]
mo_cas = mc._scf.mo_coeff[:, mc.ncore : mc.ncore + mc.ncas]

# Print the results
print()
for i, e in enumerate(es):
    if i == 0:
        continue
    print(f"CASCI excited state {i}:")
    print(f" - Energy: {e}")
    print(f" - Gap: {e - es[0]}")

    # Get the transition density matrix
    tdm = mc.fcisolver.trans_rdm1(mc.ci[0], mc.ci[i], 3, 2)
    tdm = np.einsum("ij,pi,qj->pq", tdm, mo_cas, mo_cas)

    # Get the dipole measurements for each direction
    with mc._scf.mol.with_common_origin((0, 0, 0)):
        dip = -np.einsum("xij,ji->x", mc._scf.mol.intor("int1e_r"), tdm)
    for component, direction in zip(dip, ["X", "Y", "Z"]):
        print(f" - Dipole ({direction}): {component}")

    # Get the oscillator strength
    f = (2.0 / 3.0) * (e - es[0]) * np.einsum("x,x->", dip, dip)
    print(f" - Oscillator strength: {f}")
