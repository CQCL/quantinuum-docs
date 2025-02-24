r"""Statevector calculations of energy with a double factorized hamiltonian."""
from inquanto.computables import ExpectationValue
from inquanto.computables.composite import ExpectationValueSumComputable
from inquanto.express import get_system
from inquanto.ansatzes import FermionSpaceAnsatzUCCSD, rotate_ansatz_restricted

ham, space, state = get_system("lih_sto3g.h5")
state = FermionSpaceAnsatzUCCSD(space, state)
params = state.state_symbols.construct_random(1)

# first, check exact result without double factorization
exact_energy_computable = ExpectationValue(state, ham.qubit_encode())
print(f"Exact energy (SV): {exact_energy_computable.default_evaluate(params)} Ha\n")

# double factorize hamiltonian (try experimenting with args)
df_ham = ham.double_factorize(tol1=1e-3, method="cho")
print(
    f"N_DF: {len(df_ham.two_body)}"
)  # number of terms in truncated, double factorized 2e operator

# build rotated states for each term in DF hamiltonian
states = [rotate_ansatz_restricted(state, u) for u in df_ham.rotation_matrices()]

# get list of fermion number operator kernels for each term in DF hamiltonian
kernels = [fo.qubit_encode() for fo in df_ham.fermion_operators()]

# build computable for double factorized hamiltonian
df_energy_computable = ExpectationValueSumComputable(states, kernels)
print(f"DF energy (SV): {df_energy_computable.default_evaluate(params)} Ha\n")
