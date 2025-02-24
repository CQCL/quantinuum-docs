r"""Use of a general Fermionic Ansatz."""

# imports
from pytket import OpType

from inquanto.mappings import QubitMappingJordanWigner
from inquanto.spaces import FermionSpace
from inquanto.states import FermionState

# Several fermion space ansatzes are available in InQuanto. Some of them will be shown here. Our example case is an
# 8 spin orbital Fock space, 4 electrons and a singlet, closed-shell reference occupation number vector.
space = FermionSpace(8)
state = FermionState([1, 1, 1, 1, 0, 0, 0, 0])
jw_map = QubitMappingJordanWigner()


# For each of the fermionic ansatz we prepare we can examine the operators created for the given space
# and their corresponding symbol.

from inquanto.ansatzes import FermionSpaceAnsatzUCCSD

ansatz_uccsd = FermionSpaceAnsatzUCCSD(
    fermion_space=space, fermion_state=state, qubit_mapping=jw_map
)
for (op, sym) in ansatz_uccsd.fermion_operator_exponents:
    print(op, sym)
print("\n UCCSD CNOT GATES:  {}".format(ansatz_uccsd.circuit_resources()["gates_2q"]))


from inquanto.ansatzes import FermionSpaceAnsatzkUpCCGSD

ansatz_kupccsd = FermionSpaceAnsatzkUpCCGSD(
    fermion_space=space, fermion_state=state, k_input=4, qubit_mapping=jw_map
)
print(
    "\n kUpCCGSD CNOT GATES:  {}".format(ansatz_kupccsd.circuit_resources()["gates_2q"])
)


from inquanto.ansatzes import FermionSpaceAnsatzUCCGSD

ansatz_uccgsd = FermionSpaceAnsatzUCCGSD(
    fermion_space=space, fermion_state=state, qubit_mapping=jw_map
)

# here we create a uccd ansatz without the help of the existing object
from inquanto.ansatzes import FermionSpaceStateExp

operator_exponents = space.construct_single_ucc_operators(state)
operator_exponents += space.construct_double_ucc_operators(state)
ansatz_uccd = FermionSpaceStateExp(operator_exponents, state, jw_map)
print("\n UCCGSD CNOT GATES:  {}".format(ansatz_uccd.circuit_resources()["gates_2q"]))

# or equivalently
from inquanto.ansatzes import FermionSpaceStateExpChemicallyAware

# this includes a compilation pass, among other tools

print("\n")
ansatz = FermionSpaceStateExpChemicallyAware(operator_exponents, state)
for (op, sym) in ansatz.fermion_operator_exponents:
    print(op, sym)

print("\n CAExp CNOT GATES:  {}".format(ansatz.circuit_resources()["gates_2q"]))
