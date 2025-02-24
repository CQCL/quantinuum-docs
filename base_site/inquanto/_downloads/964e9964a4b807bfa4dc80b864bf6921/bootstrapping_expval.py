r"""Low level usage of BackendResult resampling classes, like Bootstrapping."""
from inquanto.computables import ExpectationValue
from inquanto.express import ansatzYXXX, operatorXYZ4q

from pytket.extensions.qiskit import AerBackend
from inquanto.protocols import PauliAveraging

# Prepare an expectation value averaging protocol as usual:
from inquanto.protocols import BackendResultBootstrap

backend = AerBackend()
pa = PauliAveraging(backend, shots_per_circuit=1000)
pa.build(dict(theta=0.2), ansatzYXXX, operatorXYZ4q)
pa.compile_circuits()
print(pa.dataframe_circuit_shot())

# Let's launch the measurements to get the results.
handles = pa.launch(seed=0)

# Provided the measurements are completed we can obtain the backend results
results = backend.get_results(handles)
print(type(results[0]))
# Before we pass these results to the protocol we further process them:
resample = BackendResultBootstrap(20, seed=0)
print(type(resample))
sampled_results = resample.get_sampled_results(results)
print(type(sampled_results))
print(type(sampled_results[0]))
print(type(sampled_results[0][0]))
# Note: the sampled_results contains a list of list of BackendResult-s. Each list of BackendResult-s is ready to be
# used to calculate a desired computable quantity. The random sampling is performed with seed=0, and 20 new samples
# are created.

# For example we can evaluate specific resamples (first two exemplified here):
print("Results on resamples:")
print(
    pa.retrieve(sampled_results[0]).evaluate_expectation_value(
        ansatzYXXX, operatorXYZ4q
    )
)
print(
    pa.retrieve(sampled_results[1]).evaluate_expectation_value(
        ansatzYXXX, operatorXYZ4q
    )
)


# But we can also use the results to get evaluators for a computable and use it:
evaluator = pa.retrieve(sampled_results[0]).get_evaluator(results)
print("Evaluator result on a resample:")
print(ExpectationValue(ansatzYXXX, operatorXYZ4q).evaluate(evaluator))

# If the returning value is a float, we can use the static method `calculate_mean_with_uncertainty` to get the mean
# and uncertainity obtained via the `sampled_results`.
mean_with_uncertainty = resample.calculate_mean_with_uncertainty(
    sampled_results,
    lambda r: pa.retrieve(r).evaluate_expectation_value(ansatzYXXX, operatorXYZ4q),
)
# Note: the lambda function must map a list of BackendResult to a float value.
print("Mean and uncertainty from the resampling (bootstrapping):")
print(mean_with_uncertainty)

# In the case of expectation value we can compare this to the uncertainties obtained from the original backend results
# using linear error propagation via the uncertainty package:
print(
    "Mean and uncertainty from the original backend result, using linear error propagation:"
)
print(pa.retrieve(results).evaluate_expectation_uvalue(ansatzYXXX, operatorXYZ4q))
