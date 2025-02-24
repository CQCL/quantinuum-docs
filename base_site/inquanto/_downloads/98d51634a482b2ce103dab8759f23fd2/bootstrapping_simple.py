r"""Computable level usage of BackendResult resampling classes for bootstrapping.

Here a simple Hamiltonian and ansatz are used to demonstrate the Bootstrapping method.
"""
from pytket import Circuit
from pytket.extensions.qiskit import AerBackend

from inquanto.ansatzes import CircuitAnsatz
from inquanto.computables import ExpectationValue

from inquanto.operators import QubitOperator
from inquanto.protocols import BackendResultBootstrap
from inquanto.protocols import PauliAveraging

backend = AerBackend()

operator = QubitOperator("Z0")
ansatz = CircuitAnsatz(Circuit(1).Ry(1 / 3, 0))

print("operator:", operator)
print("ansatz:", repr(ansatz.get_circuit()))
expectation_value = ExpectationValue(ansatz, operator)
print("exact <op>: ", expectation_value.default_evaluate({}))

pa = PauliAveraging(backend, shots_per_circuit=100).build_from({}, expectation_value)
pa.compile_circuits()
pa.run(seed=0)

result = expectation_value.evaluate(pa.get_evaluator())
print("shot <op>: ", result)

stddev_protocol = pa.evaluate_expectation_uvalue(ansatz, operator).s

resampler = BackendResultBootstrap(10000, seed=0)
evaluators = pa.get_evaluators_for_results(resampler)
stddev_bootstrap = expectation_value.evaluate_std(evaluators)

print("stddev from variance:    ", stddev_protocol)
print("stddev from bootstrapping:", stddev_bootstrap)
