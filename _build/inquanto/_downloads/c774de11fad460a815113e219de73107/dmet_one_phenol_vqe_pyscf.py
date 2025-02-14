r"""An example DMET calculation simulating phenol"""

# imports
from pytket.extensions.qiskit import AerStateBackend

from inquanto.extensions.pyscf import (  # inquanto-pyscf extension required here
    FromActiveSpace,
    ChemistryDriverPySCFMolecularRHF,
    DMETRHFFragmentPySCFActive,
    DMETRHFFragmentPySCFCCSD,
    DMETRHFFragmentPySCFMP2,
    get_fragment_orbital_masks,
    get_fragment_orbitals,
)

from inquanto.algorithms.vqe import AlgorithmVQE
from inquanto.ansatzes import FermionSpaceAnsatzUCCSD
from inquanto.computables.composite import RestrictedOneBodyRDMRealComputable
from inquanto.computables.atomic import ExpectationValue, ExpectationValueDerivative
from inquanto.computables.primitive import ComputableTuple
from inquanto.geometries import GeometryMolecular
from inquanto.embeddings import DMETRHF
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.minimizers import MinimizerScipy
from inquanto.protocols import SparseStatevectorProtocol

# we create a bespoke class to model the embedded OH fragment of our system
# using a quantum circuit
class MyFragment(DMETRHFFragmentPySCFActive):

    # create bespoke fragment class abstract method 'solve_active' which is called by the dmet runner
    # this method returns system energy, the fragment energy, and the reduced density matrix of the fragment
    def solve_active(
        self,
        hamiltonian_operator,
        fragment_energy_operator,
        fermion_space,
        fermion_state,
    ):

        # takes fermionic system components, creates an ansatz circuit and resolves the
        # ground state using VQE to yield the state, and so the energies and RDMs

        jw = QubitMappingJordanWigner()
        ansatz = FermionSpaceAnsatzUCCSD(fermion_space, fermion_state, jw)

        h_op = jw.operator_map(hamiltonian_operator)
        e_op = jw.operator_map(fragment_energy_operator)

        objective_expression = ExpectationValue(ansatz, h_op)
        fragment_energy_expression = ExpectationValue(ansatz, e_op)
        vqe_rdm1_expression = RestrictedOneBodyRDMRealComputable(
            fermion_space, ansatz, jw
        )

        gradient_expression = ExpectationValueDerivative(
            ansatz, h_op, ansatz.state_symbols.symbols
        )

        vqe = AlgorithmVQE(
            objective_expression=objective_expression,
            minimizer=MinimizerScipy(),
            initial_parameters=ansatz.state_symbols.construct_random(0, 0.0, 0.01),
            auxiliary_expression=ComputableTuple(
                fragment_energy_expression, vqe_rdm1_expression
            ),
            gradient_expression=gradient_expression,
        )
        protocol = SparseStatevectorProtocol(AerStateBackend())
        vqe.build(protocol_objective=protocol, protocol_gradient=protocol)
        vqe.run()

        energy = vqe.final_value
        fragment_energy, vqe_rdm1 = vqe.final_evaluated_auxiliary_expression

        return energy, fragment_energy.real, vqe_rdm1


# Setup the system - Phenol geometry
geometry = [
    ["C", [-0.921240800, 0.001254500, 0.000000000]],
    ["C", [-0.223482600, 1.216975000, 0.000000000]],
    ["C", [1.176941000, 1.209145000, 0.000000000]],
    ["C", [1.882124000, 0.000763689, 0.000000000]],
    ["C", [1.171469000, -1.208183000, 0.000000000]],
    ["C", [-0.225726600, -1.216305000, 0.000000000]],
    ["O", [-2.284492000, -0.060545780, 0.000000000]],
    ["H", [-0.771286100, 2.161194000, 0.000000000]],
    ["H", [1.715459000, 2.156595000, 0.000000000]],
    ["H", [2.970767000, -0.000448048, 0.000000000]],
    ["H", [1.709985000, -2.155694000, 0.000000000]],
    ["H", [-0.792751600, -2.145930000, 0.000000000]],
    ["H", [-2.630400000, 0.901564000, 0.000000000]],
]


# prepare fermionic system for the chosen geometry
g = GeometryMolecular(geometry, distance_units="angstrom")
driver = ChemistryDriverPySCFMolecularRHF(basis="sto-3g", geometry=g.xyz, charge=0)
# system is given in terms of localized (lowdin) orbitals
hamiltonian_operator, space, rdm1 = driver.get_lowdin_system()

print("HF energy (trace):", hamiltonian_operator.energy(rdm1))

# use embedding methods to get list of which orbitals to freeze
maskOH, maskCCH, maskCHCH1, maskCHCH2 = get_fragment_orbital_masks(
    driver, [6, 12], [0, 1, 7], [2, 8, 3, 9], [4, 10, 5, 11]
)

# use embedding method to get list of active orbitals
get_fragment_orbitals(driver, [6, 12], [0, 1, 7], [2, 8, 3, 9], [4, 10, 5, 11])

# prepare DMET fragment solver
dmet = DMETRHF(hamiltonian_operator, rdm1)

# instantiate all fragments
frOH = MyFragment(dmet, maskOH, frozen=FromActiveSpace(2, 2))
frCCH = DMETRHFFragmentPySCFCCSD(dmet, maskCCH)
frCHCH1 = DMETRHFFragmentPySCFMP2(dmet, maskCHCH1)
frCHCH2 = DMETRHFFragmentPySCFCCSD(dmet, maskCHCH2)

fragments = [frOH, frCCH, frCHCH1, frCHCH2]

# run the dmet cycle on the full system
# this will iteratively run the fragment solvers and solve the embedding
result = dmet.run(fragments)
print(result)
