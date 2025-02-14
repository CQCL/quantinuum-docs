r"""Calculating complex overlaps with the HadamardTestOverlap protocol."""
from inquanto.computables import Overlap
from inquanto.protocols import HadamardTestOverlap
from inquanto.ansatzes import FermionSpaceAnsatzUCCD
from inquanto.states import FermionState
from pytket.extensions.qiskit import AerBackend

# Prepare a 4-qubit UCCD ansatz. This has 1 free parameter
state0 = FermionSpaceAnsatzUCCD(4, FermionState([1, 1, 0, 0], 1))

# Create a copy of the state and rename the parameter
state1 = state0.copy().symbol_substitution("{}_1")

symbol_set = state0.state_symbols.update(state1.state_symbols)
overlap_computable = Overlap(bra_state=state0, ket_state=state1)

# Initialize a shot-based protocol for measuring overlaps
protocol = HadamardTestOverlap(backend=AerBackend(), shots_per_circuit=100000)

# Create an executor function for this computable. It stores symbolic circuits and, when called, substitutes parameters
# and executes circuits.
executor = protocol.get_runner(overlap_computable, compile_symbolic=True)

# 2 circuits required; one for real part, one for imaginary
print(f"Number of circuits: {protocol.n_circuit}\n")

# Observe how the overlap varies as the ansatz parameters are varied
# Note that circuits do not need to be recompiled for each parameter value due to the use of compile_symbolic.
for sym in [1, 0.8, 0.6, 0.4, 0.2, 0.0]:
    overlap = executor(symbol_set.construct_from_array([1, sym]))
    print(f"{sym}\t{overlap}")
