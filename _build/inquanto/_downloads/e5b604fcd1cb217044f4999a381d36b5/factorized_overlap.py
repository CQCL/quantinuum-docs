r"""Calculating complex overlaps with the FactorizedOverlap protocols and comparing to HadamardTestOverlap."""
from inquanto.operators import QubitOperator
from inquanto.states import FermionState
from inquanto.ansatzes import (
    FermionSpaceAnsatzkUpCCGSD,
    FermionSpaceAnsatzkUpCCGSDSinglet,
)
from inquanto.computables import Overlap
from inquanto.protocols import (
    HadamardTestOverlap,
    SwapFactorizedOverlap,
    ComputeUncomputeFactorizedOverlap,
)
from pytket.extensions.qiskit import AerBackend
from pytket.partition import PauliPartitionStrat

# set up a 2-layered ansatz to show the circuit depth advantages brought about by FactorizedOverlap protocols
bra = FermionSpaceAnsatzkUpCCGSD(4, FermionState([1, 1, 0, 0], 1), 2)
# ansatzes can be of distinct classes
ket = FermionSpaceAnsatzkUpCCGSDSinglet(4, FermionState([1, 1, 0, 0], 1), 2)

# give the symbols in the bra and ket ansatzes distinct names
bra.symbol_substitution("{}_bra")
ket.symbol_substitution("{}_ket")

# obtain random values for these symbols
params = bra.state_symbols.construct_random(
    seed=0
) | ket.state_symbols.construct_random(seed=1)

# define an arbitrary non-trivial kernel with which to evaluate the overlap
kernel = QubitOperator.from_string("(-0.1, Z0), (0.1, Z1), (0.25, X0 X1)")

# define the overlap as a computable
ovlp = Overlap(bra, ket, kernel)

# all protocols instantiated below are expected to give the same result in the limit of a large number of shots
shots_per_circuit = 20000

# first, the SwapFactorizedOverlap
protocol = SwapFactorizedOverlap(
    AerBackend(),
    shots_per_circuit=shots_per_circuit,
    direct=True,
    pauli_partition_strategy=PauliPartitionStrat.CommutingSets,
)
protocol.build_from(params, ovlp)
protocol.compile_circuits()

protocol.run(seed=0)

# it has ~2x the qubits but significantly shallower circuits
print("\nSwapFactorizedOverlap (direct)")
depths = [c.depth() for c in protocol.get_circuits()]
print("Qubit count:          ", protocol.get_circuits()[0].n_qubits)
print("Circuit count:        ", len(depths))
print("Mean circuit depth:   ", int(sum(depths) / len(depths)))
print("Overlap:              ", f"{ovlp.evaluate(protocol.get_evaluator()):.4f}")

protocol = SwapFactorizedOverlap(
    AerBackend(), shots_per_circuit=shots_per_circuit, direct=False
)
protocol.build_from(params, ovlp)
protocol.compile_circuits()

protocol.run(seed=0)

print("\nSwapFactorizedOverlap (indirect)")
depths = [c.depth() for c in protocol.get_circuits()]
print("Qubit count:          ", protocol.get_circuits()[0].n_qubits)
print("Circuit count:        ", len(depths))
print("Mean circuit depth:   ", int(sum(depths) / len(depths)))
print("Overlap:              ", f"{ovlp.evaluate(protocol.get_evaluator()):.4f}")

# next, the ComputeUncomputeFactorizedOverlap
protocol = ComputeUncomputeFactorizedOverlap(
    AerBackend(), shots_per_circuit=shots_per_circuit
)
protocol.build_from(params, ovlp)
protocol.compile_circuits()

protocol.run(seed=0)

# it has the same number of qubits as the HadamardTestOverlap but shallower circuits. However, it's incompatible with
# direct operator averaging
print("\nComputeUncomputeFactorizedOverlap")
depths = [c.depth() for c in protocol.get_circuits()]
print("Qubit count:          ", protocol.get_circuits()[0].n_qubits)
print("Circuit count:        ", len(depths))
print("Mean circuit depth:   ", int(sum(depths) / len(depths)))
print("Overlap:              ", f"{ovlp.evaluate(protocol.get_evaluator()):.4f}")

# finally, compare with the HadamardTestOverlap
protocol = HadamardTestOverlap(
    AerBackend(),
    shots_per_circuit=shots_per_circuit,
    direct=True,
    pauli_partition_strategy=PauliPartitionStrat.CommutingSets,
)
protocol.build_from(params, ovlp)

protocol.compile_circuits()
protocol.run(seed=0)

print("\nHadamardTestOverlap (direct)")
depths = [c.depth() for c in protocol.get_circuits()]
print("Qubit count:          ", protocol.get_circuits()[0].n_qubits)
print("Circuit count:        ", len(depths))
print("Mean circuit depth:   ", int(sum(depths) / len(depths)))
print("Overlap:              ", f"{ovlp.evaluate(protocol.get_evaluator()):.4f}")

protocol = HadamardTestOverlap(
    AerBackend(), shots_per_circuit=shots_per_circuit, direct=False
)
protocol.build_from(params, ovlp)
protocol.compile_circuits()

protocol.run(seed=0)

print("\nHadamardTestOverlap (indirect)")
depths = [c.depth() for c in protocol.get_circuits()]
print("Qubit count:          ", protocol.get_circuits()[0].n_qubits)
print("Circuit count:        ", len(depths))
print("Mean circuit depth:   ", int(sum(depths) / len(depths)))
print("Overlap:              ", f"{ovlp.evaluate(protocol.get_evaluator()):.4f}")
