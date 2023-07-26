# Queuing Systems 
`pysqa` is based on the idea of reusable templates. These templates are defined in the `jinja2` templating language. By default `pysqa` expects to find these templates in `~/.queues`. Still it is also possible to store them in a different directory. 

In this directory `pysqa` expects to find one queue configuration and one jinja template per queue. The `queue.yaml` file which defines the available queues and their restrictions in terms of minimum and maximum number of CPU cores, required memory or run time. In addition, this file defines the type of the queuing system and the default queue. 

A typical `queue.yaml` file looks like this: 
```
queue_type: <supported types are FLUX, LSF, MOAB, SGE, SLURM, ...>
queue_primary: <default queue to use if no queue is defined by the user>
queues:
  <queue name>: {
     cores_max: <maximum number of CPU cores>,
     cores_min: <minimum number of CPU cores>,
     run_time_max: <maximum run time typically in seconds>, 
     script: <file name of the queue submission script template>
  }
```
The `queue.yaml` files and some templates for the most common queuing systems are defined below. By default `pysqa` supports the following variable for the submission script templates:

* `job_name` - the name of the calculation which appears on the queuing system 
* `working_directory` - the directory on the file system the calculation is executed in 
* `cores` - the number of cores used for the calculation
* `memory_max` - the amount of memory requested for the total calculation
* `run_time_max` - the run time requested for a given calculation - typically in seconds 
* `command` - the command which is executed on the queuing system

Beyond these standardized keywords, additional flags can be added to the template which are then available through the python interface. 

## Flux
For the flux framework the `queue.yaml` file defines the `queue_type` as `FLUX`: 
```
queue_type: FLUX
queue_primary: flux
queues:
  flux: {cores_max: 64, cores_min: 1, run_time_max: 172800, script: flux.sh}
```
The queue named `flux` is defined based on a submission script template named `flux.sh` with the following content: 
```
#!/bin/bash
# flux:--job-name={{job_name}}
# flux: --env=CORES={{cores}}
# flux: --output=time.out
# flux: --error=error.out
# flux: --cores {{cores}}
{%- if run_time_max %}
# flux: -t {{ [1, run_time_max // 60]|max }}
{%- endif %}

{{command}}
```
In this case only the number of cores `cores`, the name of the job `job_name` , the maximum run time of the job `run_time_max` and the command `command` are communicated. 

## LFS
For the load sharing facility framework from IBM the `queue.yaml` file defines the `queue_type` as `LSF`:
```
queue_type: LSF
queue_primary: lsf
queues:
  lsf: {cores_max: 100, cores_min: 10, run_time_max: 259200, script: lsf.sh}
```
The queue named `lsf` is defined based on a submission script template named `lsf.sh` with the following content:
```
#!/bin/bash
#BSUB -q queue
#BSUB -J {{job_name}}
#BSUB -o time.out
#BSUB -n {{cores}}
#BSUB -cwd {{working_directory}}
#BSUB -e error.out
{%- if run_time_max %}
#BSUB -W {{run_time_max}}
{%- endif %}
{%- if memory_max %}
#BSUB -M {{memory_max}}
{%- endif %}

{{command}}
```
In this case the name of the job `job_name`, the number of cores `cores,` the working directory of the job `working_directory` and the command that is executed `command` are defined as mendatory inputs. Beyond these two optional inputs can be defined, namely the maximum run time for the job `run_time_max` and the maximum memory used by the job `memory_max`. 

## MOAB
For the Maui Cluster Scheduler the `queue.yaml` file defines the `queue_type` as `MOAB`: 
```
queue_type: MOAB
queue_primary: moab
queues:
  moab: {cores_max: 100, cores_min: 10, run_time_max: 259200, script: moab.sh}
```
The queue named `moab` is defined based on a submission script template named `moab.sh` with the following content: 
```
#!/bin/bash

{{command}}
```
Currently, no template for the Maui Cluster Scheduler is available. 

## SGE
For the sun grid engine (SGE) the `queue.yaml` file defines the `queue_type` as `SGE`: 
```
queue_type: SGE
queue_primary: sge
queues:
  sge: {cores_max: 1280, cores_min: 40, run_time_max: 259200, script: sge.sh}
```
The queue named `sge` is defined based on a submission script template named `sge.sh` with the following content:
```
#!/bin/bash
#$ -N {{job_name}}
#$ -wd {{working_directory}}
{%- if cores %}
#$ -pe impi_hy* {{cores}}
{%- endif %}
{%- if memory_max %}
#$ -l h_vmem={{memory_max}}
{%- endif %}
{%- if run_time_max %}
#$ -l h_rt={{run_time_max}}
{%- endif %}
#$ -o time.out
#$ -e error.out

{{command}}
```
In this case the name of the job `job_name`, the number of cores `cores,` the working directory of the job `working_directory` and the command that is executed `command` are defined as mendatory inputs. Beyond these two optional inputs can be defined, namely the maximum run time for the job `run_time_max` and the maximum memory used by the job `memory_max`. 

## SLURM
For the Simple Linux Utility for Resource Management (SLURM) the `queue.yaml` file defines the `queue_type` as `SLURM`: 
```
queue_type: SLURM
queue_primary: slurm
queues:
  slurm: {cores_max: 100, cores_min: 10, run_time_max: 259200, script: slurm.sh}
```
The queue named `slurm` is defined based on a submission script template named `slurm.sh` with the following content:
```
#!/bin/bash
#SBATCH --output=time.out
#SBATCH --job-name={{job_name}}
#SBATCH --chdir={{working_directory}}
#SBATCH --get-user-env=L
#SBATCH --partition=slurm
{%- if run_time_max %}
#SBATCH --time={{ [1, run_time_max // 60]|max }}
{%- endif %}
{%- if memory_max %}
#SBATCH --mem={{memory_max}}G
{%- endif %}
#SBATCH --cpus-per-task={{cores}}

{{command}}
```
In this case the name of the job `job_name`, the number of cores `cores,` the working directory of the job `working_directory` and the command that is executed `command` are defined as mendatory inputs. Beyond these two optional inputs can be defined, namely the maximum run time for the job `run_time_max` and the maximum memory used by the job `memory_max`. 

## TORQUE
For the Terascale Open-source Resource and Queue Manager (TORQUE) the `queue.yaml` file defines the `queue_type` as `TORQUE`: 
```
queue_type: TORQUE
queue_primary: torque
queues:
  torque: {cores_max: 100, cores_min: 10, run_time_max: 259200, script: torque.sh}

```
The queue named `torque` is defined based on a submission script template named `torque.sh` with the following content:
```
#!/bin/bash
#PBS -q normal
#PBS -l ncpus={{cores}}
#PBS -N {{job_name}}
{%- if memory_max %}
#PBS -l mem={{ [16, memory_max]| int |max }}GB
{%- endif %}
{%- if run_time_max %}
#PBS -l walltime={{ [1*3600, run_time_max*3600]|max }}
{%- endif %}
#PBS -l wd
#PBS -l software=vasp
#PBS -l storage=scratch/a01+gdata/a01 
#PBS -P a01
 
{{command}}
```
In this case the name of the job `job_name`, the number of cores `cores,` the working directory of the job `working_directory` and the command that is executed `command` are defined as mendatory inputs. Beyond these two optional inputs can be defined, namely the maximum run time for the job `run_time_max` and the maximum memory used by the job `memory_max`. 
