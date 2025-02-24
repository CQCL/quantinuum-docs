r"""Compare different shot based protocols for calculating an overlap squared."""

# imports
from pytket.extensions.qiskit import AerBackend

from inquanto.protocols import ComputeUncompute, SwapTest, DestructiveSwapTest
from inquanto.computables import OverlapSquared
from inquanto.ansatzes import FermionSpaceAnsatzUCCSD, MultiConfigurationAnsatz
from inquanto.states import FermionState, QubitStateString

# prepare two states, one multiconfig, one chemical UCCSD
bra = MultiConfigurationAnsatz(
    [QubitStateString([1, 1, 0, 0]), QubitStateString([0, 1, 1, 0])]
)
ket = FermionSpaceAnsatzUCCSD(4, FermionState([1, 1, 0, 0], 1))

# prepare dicts with numerics for states
parameters = bra.state_symbols.construct_random(
    seed=0
) | ket.state_symbols.construct_random(seed=0)

# instance computable to evaluate OverlapSquared |<1|2>|^2
# all protocols will be used to evaluate this object
overlap_sq = OverlapSquared(bra, ket)

# instance a shot based backend
backend = AerBackend()

# ComputeUncompute protocol can be used to evaluate OverlapSquare computable
cu_protocol = ComputeUncompute(backend, n_shots=10000)
# protocol builds the circuits for the computable
cu_protocol.build_from(parameters, overlap_sq)
cu_protocol.compile_circuits()
print("Number of circuits:", len(cu_protocol.get_circuits()))
cu_protocol.run()
# use shot table to evaluate computable
cu_result = overlap_sq.evaluate(cu_protocol.get_evaluator())

# inspect circuits for computeuncompute
c_uc_circuits = cu_protocol.get_circuits()
print(f"ComputeUncompute overlap squared:\t{cu_result}")
print(f"\tnum_qubits: {c_uc_circuits[0].n_qubits}")
print(f"\tcircuit depth: {c_uc_circuits[0].depth()}\n")

# use controlled operations to do state comparison
st_protocol = SwapTest(backend, n_shots=100000)
st_protocol.build_from(parameters, overlap_sq)
st_protocol.compile_circuits()
st_protocol.run()
st_result = overlap_sq.evaluate(st_protocol.get_evaluator())
swaptest_circuits = st_protocol.get_circuits()
print(f"SwapTest overlap squared:\t{st_result}")
print(f"\tnum_qubits: {swaptest_circuits[0].n_qubits}")
print(f"\tcircuit depth: {swaptest_circuits[0].depth()}\n")


# Prepares both bra and ket states in parallel and perform bit wise comparison
# no ancilla
dst_protocol = DestructiveSwapTest(backend, n_shots=100000)
dst_protocol.build_from(parameters, overlap_sq)
dst_protocol.compile_circuits()
dst_protocol.run()
dst_result = overlap_sq.evaluate(dst_protocol.get_evaluator())
dswaptest_circuits = dst_protocol.get_circuits()
print(f"DestructiveSwapTest overlap squared:\t{dst_result}")
print(f"\tnum_qubits: {dswaptest_circuits[0].n_qubits}")
print(f"\tcircuit depth: {dswaptest_circuits[0].depth()}\n")
