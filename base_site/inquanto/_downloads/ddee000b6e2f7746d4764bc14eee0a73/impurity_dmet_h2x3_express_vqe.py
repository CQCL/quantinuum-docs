r"""An example impurity DMET simulation of a 3-dihydrogen ring using the express module."""

# imports
import numpy

from pytket.extensions.qiskit import AerStateBackend

from inquanto.algorithms.vqe import AlgorithmVQE
from inquanto.ansatzes import FermionSpaceAnsatzUCCSD
from inquanto.computables.atomic import ExpectationValue
from inquanto.embeddings import ImpurityDMETROHF, ImpurityDMETROHFFragmentActive
from inquanto.express import load_h5
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.minimizers import MinimizerScipy
from inquanto.operators import ChemistryRestrictedIntegralOperator
from inquanto.protocols import SparseStatevectorProtocol
from inquanto.spaces import FermionSpace
from inquanto.states import FermionState

# we create a bespoke class from ImpurityDMETROHFFragmentActive which returns the
# fragment active space uccsd vqe energy
class MyFragment(ImpurityDMETROHFFragmentActive):
    def solve_active(
        self,
        hamiltonian_operator: ChemistryRestrictedIntegralOperator,
        fermion_space: FermionSpace,
        fermion_state: FermionState,
    ):
        jw = QubitMappingJordanWigner()
        ansatz = FermionSpaceAnsatzUCCSD(fermion_space, fermion_state, jw)

        h_op = jw.operator_map(hamiltonian_operator)

        objective_expression = ExpectationValue(ansatz, h_op)

        vqe = AlgorithmVQE(
            objective_expression=objective_expression,
            minimizer=MinimizerScipy(),
            initial_parameters=ansatz.state_symbols.construct_random(0, 0.0, 0.01),
        )

        vqe.build(protocol_objective=SparseStatevectorProtocol(AerStateBackend()))
        vqe.run()

        energy = vqe.final_value

        return energy


# load example fermionic system from inquanto.express
h2_3_ring_sto3g = load_h5("h2_3_ring_sto3g.h5", as_tuple=True)

print("HF energy (ref):  ", h2_3_ring_sto3g.energy_hf)
print(
    "HF energy (trace):",
    h2_3_ring_sto3g.hamiltonian_operator_lowdin.energy(
        h2_3_ring_sto3g.one_body_rdm_hf_lowdin
    ),
)

# define dmet solver using the full system lowdin localized hamiltonian and RDM
dmet = ImpurityDMETROHF(
    h2_3_ring_sto3g.hamiltonian_operator_lowdin, h2_3_ring_sto3g.one_body_rdm_hf_lowdin
)

# prepare ImpurityDMETROHFFragmentActive class defined above
fragment = MyFragment(
    dmet, numpy.array([True, True, False, False, False, False]), frozen=[0, 3]
)

# run the impurity dmet for the VQE fragments
result = dmet.run(fragment)
print(result)

# -3.2137621792612543
