r"""An example using protocol list for finite differences"""

# imports
from pytket.extensions.qiskit import AerBackend
from pytket.partition import PauliPartitionStrat

from sympy import Symbol

from inquanto.ansatzes import TrotterAnsatz
from inquanto.computables import (
    ExpectationValue,
)
from inquanto.computables.primitive import ComputableFunction
from inquanto.express import load_h5
from inquanto.operators import QubitOperatorList
from inquanto.protocols import PauliAveraging
from inquanto.states import QubitState

backend = AerBackend()

# Load a simple system from express
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
hamiltonian = h2.hamiltonian_operator
qubit_hamiltonian = hamiltonian.qubit_encode()

# prepare states and symbols for finite difference approach
# see finite_difference example for more details
exponents = QubitOperatorList.from_string("theta [(1j, Y0 X1 X2 X3)]")
delta = Symbol("delta")
theta = Symbol("theta")
delta_value = 0.1
symbol_dict = {theta: 0.4, delta: delta_value}
ref = QubitState([1, 1, 0, 0])
state = TrotterAnsatz(exponents, ref)
state1p = state.subs({theta: theta + delta})
state1m = state.subs({theta: theta - delta})

# prepare finite difference function and computable
fd = lambda fp, fm: (fp - fm) / 2 / delta_value
c1gfd = ComputableFunction(
    fd,
    ExpectationValue(state1p, qubit_hamiltonian),
    ExpectationValue(state1m, qubit_hamiltonian),
)

# Note: this computable has two different states, therefore a single instance of PauliAveraging protocol
# will not be able to fully evaluate it, as the PauliAveraging protocol only builds circuits for a single state.
# Instead we will use the static method `build_protocols_from` to instantiate and build
# a list of PauliAveraging protocols. This combined protocol will be able to generate circuits for
# the computable which uses many different ansaztes.
protocols = PauliAveraging.build_protocols_from(
    symbol_dict,
    c1gfd,
    backend=backend,
    shots_per_circuit=30000,
    pauli_partition_strategy=PauliPartitionStrat.CommutingSets,
).compile_circuits()
# Can inspect the protocols and circuits:
print(protocols.dataframe_protocol_circuit())

# And use launch/retrieve or run to run the measurements of this list of protocols.
protocols.run(seed=0)

# Finally, you can get the evaluator to evaluate the computable holding multiple states:
c1gfd_ev = c1gfd.evaluate(evaluator=protocols.get_evaluator())

print()
print("(<Psi(t+h)|H|Psi(t+h)> - <Psi(t-h)|H|Psi(t-h)>)/(2h)")
print("SV:", c1gfd.default_evaluate(symbol_dict))
print("PC:", c1gfd_ev)
