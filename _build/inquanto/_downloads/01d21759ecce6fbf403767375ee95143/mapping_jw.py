r"""Use of the Jordan-Wigner mapping from fermions to qubits."""

# imports
from inquanto.express import load_h5
from inquanto.mappings import QubitMappingJordanWigner

# instantiate mapping class
jw_map = QubitMappingJordanWigner()
# get example fermionic system from express
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
fermion_operator = h2.hamiltonian_operator

# perform JW mapping on fermionic operator
jw_qubit_operator = jw_map.operator_map(fermion_operator)
print(jw_qubit_operator)
# equivalently we can perform this mapping from the fermion operator
jw_qubit_operator = fermion_operator.qubit_encode(mapping=jw_map)

# perform JW mapping on an example fermionic state
fermion_state = h2.hf_state
jw_qubit_state = jw_map.state_map(fermion_state, qubits=4)
print(jw_qubit_state)
# this can equivalently done with a list representing fermionic occupancies
jw_qubit_state = jw_map.state_map([1, 1, 0, 0], qubits=4)
print(jw_qubit_state)
