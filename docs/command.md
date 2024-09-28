# Command Line Interface
The command line interface implements a subset of the functionality of the python interface. While it can be used 
locally to check the status of your calculation, the primary use case is accessing the `pysqa` installation on a remote 
HPC cluster from your local `pysqa` installation. Still here the local execution of the commands is discussed.

The available options are the submission of new jobs to the queuing system using the submit option `--submit`, enabling
reservation for a job already submitted using the `--reservation` option, listing jobs on the queuing using the status 
option `--status`, deleting a job from the queuing system using the delete option `--delete`, listing files in the 
working directory using the list option `--list` and the help option `--help` to print a summary of the available 
options.

## Submit job
Submission of jobs to the queuing system with the submit option `--submit` is similar to the submit job function 
`QueueAdapter().submit_job()`. Example call to submit the `hostname` command to the default queue: 
```
python -m pysqa --submit --command hostname
```
The options used and their short forms are: 
* `-p`, `--submit` the submit option enables the submission of a job to the queuing system
* `-c`, `--command` the command that is executed as part of the job 

Additional options for the submission of the job with their short forms are:
* `-f`, `--config_directory` the directory which contains the `pysqa` configuration, by default `~/.queues`.
* `-q`, `--queue` the queue the job is submitted to. If this option is not defined the `primary_queue` defined in the 
  configuration is used. 
* `-j`, `--job_name` the name of the job submitted to the queuing system. 
* `-w`, `--working_directory` the working directory the job submitted to the queuing system is executed in.
* `-n`, `--cores` the number of cores used for the calculation. If the cores are not defined the minimum number of cores
  defined for the selected queue are used. 
* `-m`, `--memory` the memory used for the calculation. 
* `-t`, `--run_time` the run time for the calculation. If the run time is not defined the maximum run time defined for 
  the selected queue is used. 
* `-b`, `--dependency` other jobs the calculation depends on. 

## Enable reservation 
Enable reservation for a job already submitted to the queuing system using the reservation option `--reservation` is 
similar to the enable reservation function `QueueAdapter().enable_reservation()`. Example call to enable the reservation
for a job with the id `123`:
```
python -m pysqa --reservation --id 123
```
The options used and their short forms are: 
* `-r`, `--reservation` the reservation option enables a reservation for a specific job.
* `-i`, `--id` the id option specifies the job id of the job which should be added to the reservation.

Additional options for enabling the reservation with their short forms are:
* `-f`, `--config_directory` the directory which contains the `pysqa` configuration, by default `~/.queues`.

## List jobs 
List jobs on the queuing system option `--status`, list calculations currently running and waiting on the queuing system
for all users on the HPC cluster:
```
python -m pysqa --status
```
The options used and their short forms are: 
* `-s`, `--status` the status option lists the status of all calculation currently running and waiting on the queuing 
  system.

Additional options for listing jobs on the queuing system with their short forms are:
* `-f`, `--config_directory` the directory which contains the `pysqa` configuration, by default `~/.queues`.

## Delete job
The delete job option `--delete` deletes a job from the queuing system: 
```
python -m pysqa --delete --id 123
```
The options used and their short forms are: 
* `-d`, `--delete` the delete option enables the deletion of a job from the queuing system. 
* `-i`, `--id` the id option specifies the job id of the job which should be deleted. 

Additional options for deleting jobs from the queuing system with their short forms are:
* `-f`, `--config_directory` the directory which contains the `pysqa` configuration, by default `~/.queues`.

## List files 
The list files option `--list` lists the files in working directory: 
```
python -m pysqa --list --working_directory /path/on/remote/hpc
```
The options used and their short forms are: 
* `-l`, `--list` the list files option lists the files in the working directory.
* `-w`, `--working_directory` the working directory defines the folder whose files are listed. 

## Help
The help option `--help` prints a short version of this documentation page:
```
python -m pysqa --help
```