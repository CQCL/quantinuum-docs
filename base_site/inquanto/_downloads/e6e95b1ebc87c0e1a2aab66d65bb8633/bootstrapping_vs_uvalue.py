r"""Comparing error bars obtained from bootstrapping (using BackendResultsBootstrap) and linear error propagation."""
from pytket.extensions.qiskit import AerBackend
from pytket.backends.backendresult import BackendResult
from pytket.utils.outcomearray import OutcomeArray

# 4-qubit Heisenberg model Hamiltonian
from inquanto.express import operatorXYZ4q
from inquanto.express import ansatzYXXX
from inquanto.protocols import PauliAveraging, BackendResultBootstrap

backend = AerBackend()

pa = PauliAveraging(backend, shots_per_circuit=2000)

pa.build({"theta": 0.2}, ansatzYXXX, operatorXYZ4q)
pa.compile_circuits()
handles = pa.launch()

results = backend.get_results(handles)

# Instantiate BackendResultsBootstrap object, selecting 20 bootstrapped samples, and the seed for sample generation.
resample = BackendResultBootstrap(20, seed=0)

re = resample.get_sampled_results(results)

# We generated 20 bootstrapped samples, and now we print the expectation values for the first 4.
print(
    "Expectation from bootstrapped sample 1:",
    pa.retrieve(re[0]).evaluate_expectation_value(ansatzYXXX, operatorXYZ4q),
)
print(
    "Expectation from bootstrapped sample 2:",
    pa.retrieve(re[1]).evaluate_expectation_value(ansatzYXXX, operatorXYZ4q),
)
print(
    "Expectation from bootstrapped sample 3:",
    pa.retrieve(re[2]).evaluate_expectation_value(ansatzYXXX, operatorXYZ4q),
)
print(
    "Expectation from bootstrapped sample 4:",
    pa.retrieve(re[3]).evaluate_expectation_value(ansatzYXXX, operatorXYZ4q),
)

ur = resample.calculate_mean_with_uncertainty(
    re,
    lambda r: pa.retrieve(r).evaluate_expectation_value(ansatzYXXX, operatorXYZ4q),
)

# We can estimate an expectation value with error bars in different ways. First we get this by bootstrapping.
# Then we estimate from linear error propagation (without bootstrapping) to compare.

print("Mean expectation value with standard error from 20 bootstrapped samples:", ur)

print(
    "Expectation value with standard error estimated from linear error propagation theory:",
    pa.retrieve(results).evaluate_expectation_uvalue(ansatzYXXX, operatorXYZ4q),
)


# We can also look at the outcome counts for the measurement shots, comparing the original shots to what we get
# from bootstrapping.
readouts = [
    [0, 0],
    [0, 1],
    [0, 1],
    [1, 0],
    [1, 0],
    [1, 0],
    [1, 1],
    [1, 1],
    [1, 1],
    [1, 1],
]
result = BackendResult(shots=OutcomeArray.from_readouts(readouts))

# The original shot counts.
print("\nMeasurement shot counts from original result:", result.get_counts())

# Generate a new set of bootstrapped samples, this time selecting 3 samples and a different seed.
resample = BackendResultBootstrap(3, seed=1)
print("Now instantiating BackendResultBootstrap for 3 samples and a different seed.")

result_bootstrap = resample.get_sampled_result(result)

print(
    "Measurement shot counts from bootstrapped sample 1:",
    result_bootstrap[0].get_counts(),
)
print(
    "Measurement shot counts from bootstrapped sample 2:",
    result_bootstrap[1].get_counts(),
)
print(
    "Measurement shot counts from bootstrapped sample 3:",
    result_bootstrap[2].get_counts(),
)
