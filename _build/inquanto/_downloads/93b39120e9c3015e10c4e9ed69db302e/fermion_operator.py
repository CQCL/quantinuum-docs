r"""Examples of some FermionOperator methods."""

# imports
from inquanto.operators import FermionOperator, FermionOperatorString

# construct a simple fermion operator
# FO string represents annihilation in spin-orbital/mode indexed 0
# follow by creation in mode 0
# this is equal to the number operator
op0 = FermionOperator({FermionOperatorString([(0, 1), (0, 0)]): 1.0})
print(op0)
print("is operator anti-hermitian?", op0.is_antihermitian())

# with an imaginary coefficient this operator is anti hermitian
op0 = FermionOperator({FermionOperatorString([(0, 1), (0, 0)]): 1.0j})
print(op0)
print("is operator anti-hermitian?", op0.is_antihermitian())

print("")
# now multiply by its adjoint
op = op0 * op0.dagger()

# does it commute with itself? Yes!
print("commutator of op with itself:", op.commutator(op))
print("does op commute with itself?", op.commutes_with(op))


# instantiate from string
# op2 creates in the second fermionic mode and annihilates in the first
op2 = FermionOperator({FermionOperatorString.from_string("F1 F2^"): 3.5})
print(op2)
# or equivalently
fos0 = FermionOperatorString(((1, 0), (2, 1)))
op2 = FermionOperator({FermionOperatorString(((1, 0), (2, 1))): 3.5})
print(op2)
# or
op2 = FermionOperator.from_list([(3.5, fos0)])
print(op2)


# is this operator normal ordered?
print("is op2 normal ordered?", op2.is_normal_ordered())
# We reorder the operators
op2 = op2.normal_ordered()
print("what about now?", op2.is_normal_ordered())
print("is operator number conserving?", op2.is_two_body_number_conserving())
print("is operator anti-hermitian?", op2.is_antihermitian())


# sum of operators so far:
op3 = op0 + op2
print("summing: op3 =", op3)
# remove terms with coefficients of absolute value < 3
print("truncated op3 =", op3.truncated(3.0))

# map this fermion operator to a qubit operator
print("JW mapped op3 =", op3.qubit_encode())

# we can apply the operators kets and bras defined in the fermion space to retrieve a new FermionState
from inquanto.states import FermionState

# model the h2 Hartree-fock state
fock_state = FermionState([1, 1, 0, 0])
print("<HF|op3 = ", op3.apply_bra(fock_state))
print("op3|HF> = ", op3.apply_ket(fock_state))
