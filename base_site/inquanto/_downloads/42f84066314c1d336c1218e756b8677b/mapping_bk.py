r"""Use of the Bravyi-Kitaev mapping from fermions to qubits."""

# imports
from inquanto.express import load_h5
from inquanto.mappings import QubitMappingBravyiKitaev

# instantiate mapping class
bk_map = QubitMappingBravyiKitaev()
# get example fermionic system from express
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
fermion_operator = h2.hamiltonian_operator

# perform BK mapping on fermionic operator in a four-qubit register

bk_qubit_operator = bk_map.operator_map(fermion_operator, 4)
print(bk_qubit_operator)

# perform BK mapping on an example fermionic state
fermion_state = h2.hf_state
bk_qubit_state = bk_map.state_map(fermion_state, qubits=4)
# this can equivalently done with an array representing fermionic occupancies
bk_qubit_state = bk_map.state_map([1, 1, 0, 0], qubits=4)
print(bk_qubit_state)
