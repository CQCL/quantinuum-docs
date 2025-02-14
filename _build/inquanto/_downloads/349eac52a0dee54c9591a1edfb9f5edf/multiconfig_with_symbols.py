r"""Use of a linear combination of fermionic occupation states as a variational ansatz."""

# imports
from pytket import OpType

from inquanto.states import QubitStateString
from inquanto.ansatzes import MultiConfigurationAnsatz
from sympy import Symbol

# 4 qubit, 2 configuration example
# define the configurations
qss_ref = QubitStateString([1, 1, 0, 0])
qss_2 = QubitStateString([0, 0, 1, 1])

# Use the MultiConfigurationAnsatz class which allows for free symbols
ansatz = MultiConfigurationAnsatz([qss_ref, qss_2])

# |psi> = a|1100> + b|0011>, b = SQRT(1 - |a|^2) => only 1 parameter

print("\n4 qubit variational MultiConfigurationAnsatz info")
print("symbols:", ansatz.state_symbols.symbols)
print("N_parameters:", ansatz.n_symbols)
print("Report:\n", ansatz.generate_report())
print("CNOT GATES:  {}".format(ansatz.circuit_resources()["gates_2q"]))

# If you'd like to change the symbols by appending strings to existing symbol labels, you can do this
ansatz.symbol_substitution("{}_a")
print("symbols after symbol_substitution:", ansatz.state_symbols.symbols)

# 6 qubit, 3 configuration example
# define the configurations
qss_ref = QubitStateString([1, 1, 0, 0, 0, 0])
qss_2 = QubitStateString([0, 0, 1, 1, 0, 0])
qss_3 = QubitStateString([0, 0, 0, 0, 1, 1])

# Use the MultiConfigurationAnsatz class which allows for free symbols
ansatz = MultiConfigurationAnsatz([qss_ref, qss_2, qss_3])
print("\n6 qubit variational MultiConfigurationAnsatz info")
print("symbols:", ansatz.state_symbols.symbols)
print("N_parameters:", ansatz.n_symbols)
print("Report:\n", ansatz.generate_report())
print("CNOT GATES:  {}".format(ansatz.circuit_resources()["gates_2q"]))

# If you'd like to rename the symbols, you can do this
ansatz.symbol_substitution(dict(theta0=Symbol("coeff1"), theta1=Symbol("coeff2")))
print("symbol names after symbol_substitution:", ansatz.state_symbols.symbols)
