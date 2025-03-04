r"""Example of building your own Lanczos routine, then comparing it to KrylovSubspaceComputable."""

# imports
import numpy

import cmath

from pytket.partition import PauliPartitionStrat
from pytket.extensions.qiskit import AerBackend

from inquanto.computables.composite import KrylovSubspaceComputable
from inquanto.computables.primitive import ComputableTuple
from inquanto.express import DriverHubbardDimer
from inquanto.operators import FermionOperator
from inquanto.ansatzes import FermionSpaceAnsatzChemicallyAwareUCCSD

from inquanto.protocols import PauliAveraging
from inquanto.computables import ExpectationValue
from inquanto.operators import QubitOperator
from inquanto.core import pd_safe_eigh

# define Hamiltonian H (here we use Hubbard dimer at half filling). Note t is negated in DriverHubbardDimer
u_hub = 2.15
t_hub = 0.3
n_sites = 2
driver = DriverHubbardDimer(t=t_hub, u=u_hub)
h, space, state = driver.get_system()

# this sets the chemical potential to -U/2 in the Hamiltonian
n1u = FermionOperator(((space.index(0, 0), 1), (space.index(0, 0), 0)))
n1d = FermionOperator(((space.index(0, 1), 1), (space.index(0, 1), 0)))
n2u = FermionOperator(((space.index(1, 0), 1), (space.index(1, 0), 0)))
n2d = FermionOperator(((space.index(1, 1), 1), (space.index(1, 1), 0)))
h -= 0.5 * u_hub * (n1u + n1d + n2u + n2d)
h += 0.5 * FermionOperator.identity() * u_hub

# Jordan-Wigner encode H, then instantiate the ansatz (random parameters here just to exemplify)
qubit_hamiltonian = h.qubit_encode()
ansatz = FermionSpaceAnsatzChemicallyAwareUCCSD(space, state)
parameters = ansatz.state_symbols.construct_random(2, 0.01, 0.1)

# backend for shot-based protocol
backend = AerBackend()

# below we build our own Lanczos routine


def _generate_powers(kernel, power):
    # function to generate powers (moments) of H
    op = QubitOperator.identity()
    yield op.copy()
    for _ in range(power):
        op *= kernel
        yield op.copy()


# select krylov space dimension, max power of H related to this
krylov = 3
power = 2 * krylov - 1

# return a tuple of Computables corresponding to each power
moments_expr = ComputableTuple(
    *[
        ExpectationValue(ansatz, kernel)
        for kernel in _generate_powers(qubit_hamiltonian, power)
    ]
)

# evaluate those moments from the Computables
moments = moments_expr.default_evaluate(parameters)

# print the results from the custom routine
print(moments)
h = numpy.zeros((krylov, krylov), dtype=complex)
s = numpy.zeros((krylov, krylov), dtype=complex)

for n in range(krylov):
    for m in range(krylov):
        d = cmath.sqrt(moments[2 * m] * moments[2 * n])
        h[n, m] = moments[n + m + 1] / d
        s[n, m] = moments[n + m] / d

ee, ew, es = pd_safe_eigh(h, s)

print(ee)
print(es)


# now do the same as above, but via KrylovSubspaceComputable
lanczos = KrylovSubspaceComputable(ansatz, qubit_hamiltonian, 3)

# PauliAveraging protocol to measure H moments, commuting sets of Paulis to reduce the number of measured circuits
protocol = PauliAveraging(
    backend,
    shots_per_circuit=10000,
    pauli_partition_strategy=PauliPartitionStrat.CommutingSets,
)

# build measurement circuits for the computable
protocol.build_from(parameters, lanczos).compile_circuits()
# run the protocol to get shot results
protocol.run(seed=2)

# evaluate the Computable using the protocol shot results
result = lanczos.evaluate(evaluator=protocol.get_evaluator())

# protocol has methods to get info on measurements and circuits
print("Measurements:")
print(protocol.dataframe_measurements())
print("Circuits measured:")
print(protocol.dataframe_circuit_shot())

# the results from KrylovSubspaceComputable
print(result.construct_tridiagonal_representation())
print(result.eigenvalues())
