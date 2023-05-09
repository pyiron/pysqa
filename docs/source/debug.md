# Debugging
The configuration of a queuing system adapter, in particular in a remote configuration with a local installation of `pysqa` communicating to a remote installation on your HPC can be tricky. 

## Local Queuing System
To simplify the process `pysqa` provides a series of steps for debugging: 

* When `pysqa` submits a calculation to a queuing system it creates an `run_queue.sh` script. You can submit this script using your batch command e.g. `sbatch` for `SLURM` and take a look at the error message. 
* The error message the queuing system returns when submitting the job is also stored in the `pysqa.err` file. 
* Finally, if the `run_queue.sh` script does not match the variables you provided, then you can test your template using `jinja2`: `Template(open("~/.queues/queue.sh", "r").read()).render(**kwargs)` here `"~/.queues/queue.sh"` is the path to the queuing system submit script you want to use and `**kwargs` are the arguments you provide to the `submit_job()` function. 

## Remote HPC
The failure to submit to a remote HPC cluster can be related with to an issue with the local `pysqa` configuration or an issue with the remote `pysqa` configuration. To identify which part is causing the issue, it is recommended to first test the remote `pysqa` installation on the remote HPC cluster:

* Login to the remote HPC cluster and import `pysqa` on a python shell. 
* Validate the queue configuration by importing the queue adapter using `from pysqa import QueueAdapter` then initialize the object from the configuration dictionary `qa = QueueAdapter(directory="~/.queues")`. The current configuration can be printed using `qa.config`. 
* Try to submit a calculation to print the hostname from the python shell on the remote HPC cluster using the `qa.submit_job(command="hostname")`.
* If this works successfully then the next step is to try the same on the command line using `python -m pysqa --submit --command hostname`.

This is the same command the local `pysqa` instance calls on the `pysqa` instance on the remote HPC cluster, so if the steps above were executed successfully, then the remote HPC configuration seems to be correct. The final step is validating the local configuration to see the SSH connection is successfully established and maintained. 

