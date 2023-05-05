# Debugging
The configuration of a queuing system adapter, in particular in a remote configuration with a local installation of `pysqa` communicating to a remote installation on your HPC can be tricky. To simplify the process `pysqa` provides a series of utility functions:
* Login to the remote HPC cluster and import `pysqa` on a python shell. 
* Validate the queue configuration by importing the queue adapter using `from pysqa import QueueAdapter` then initialize the object from the configuration dictionary `qa = QueueAdapter(directory="~/.queues")`. The current configuration can be printed using `qa.config`. 
* Try to submit a calculation to print the hostname from the python shell on the remote HPC cluster using the `qa.submit_job(command="hostname")`.
* If this works successfully then the next step is to try the same on the command line using `python -m pysqa --submit --command hostname`.

This is the same command the local `pysqa` instance calls on the `pysqa` instance on the remote HPC cluster, so if the steps above were executed successfully, then the remote HPC configuration seems to be correct. The final step is validating the local configuration to see the SSH connection is successfully established and maintained. 

