r"""Using context for logging standard outputs"""

# imports
from inquanto.core import InQuantoContext

with InQuantoContext("my_experiment_1"):
    # std outputs capture here
    # ...
    print("Results: ", 1)

# example output
# my_experiment_1.log
# # INQUANTO BEGINS AT 2022-05-17 18:28:06.421230
# Results:  1
# # INQUANTO ENDS AT 2022-05-17 18:28:06.421279 - DURATION (s):  0.0000441 [0:00:00.000044]

# write stdout to file
with InQuantoContext("my_experiment_2", __file__, file_only=True):
    # std outputs capture here
    # ...
    print("Results: ", 2)

# example output 2
# In context_printing.my_experiment_2.log
# # INQUANTO BEGINS AT 2022-05-17 18:00:24.554631
# Results:  2
# # INQUANTO ENDS AT 2022-05-17 18:00:24.554685 - DURATION (s):  0.0000473 [0:00:00.000047]
