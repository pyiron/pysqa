# Command Line Interface
The command line interface implements a subset of the functionality of the python interface. While it can be used locally to check the status of your calculation, the primary use case is accessing the `pysqa` installation on a remote HPC cluster from your local `pysqa` installation. Still here the local execution of the commands is discussed. 

Starting with the `--help` command: 
```
python -m pysqa --help
```
This prints a short version of this documentation page. 

Besides the `--help` command there are 

* `-f`, `--config_directory`
* `-p`, `--submit`
* `-q`, `--queue`
* `-j`, `--job_name`
* `-w`, `--working_directory`
* `-n`, `--cores`
* `-m`, `--memory`
* `-t`, `--run_time`
* `-b`, `--dependency`
* `-c`, `--command`
* `-r`, `--reservation`
* `-i`, `--id`
* `-d`, `--delete`
* `-s`, `--status`
* `-l`, `--list`
* `-h`, `--help`
