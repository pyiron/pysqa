# pysqa

[![Python package](https://github.com/pyiron/pysqa/workflows/Python%20package/badge.svg)](https://github.com/pyiron/pysqa/actions)
[![Documentation Status](https://readthedocs.org/projects/pysqa/badge/?version=latest)](https://pysqa.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/pyiron/pysqa/badge.svg?branch=main)](https://coveralls.io/github/pyiron/pysqa?branch=main)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/pyiron/pysqa/HEAD?labpath=example.ipynb)

High-performance computing (HPC) does not have to be hard. In this context the aim of `pysqa` is to simplify the submission of calculation to an HPC cluster as easy as starting another subprocess locally. This is achieved based on the assumption that even though modern HPC queuing systems offer a wide range of different configuration options, most users submit the majority of their jobs with very similar parameters. 

Therefore, in `pysqa` users define submission script templates once and reuse them to submit many different calculations or workflows. These templates are defined in the [jinja2 template language](https://palletsprojects.com/p/jinja/), so current submission scripts can be easily extended to templates. In addition to the submission of new jobs to the queuing system `pysqa` also allows the users to track the progress of their jobs, delete them or enable reservations using the built-in functionality of the queuing system.

All this functionality is available from both a [Python interface](https://pysqa.readthedocs.io/en/latest/example.html) as well as a [command line interface](https://pysqa.readthedocs.io/en/latest/command.html). 

# Features
The core feature of `pysqa` is the communication to an HPC queuing system ([Flux](https://pysqa.readthedocs.io/en/latest/queue.html#flux), [LFS](https://pysqa.readthedocs.io/en/latest/queue.html#lfs), [MOAB](https://pysqa.readthedocs.io/en/latest/queue.html#moab), [SGE](hhttps://pysqa.readthedocs.io/en/latest/queue.html#sge), [SLURM](https://pysqa.readthedocs.io/en/latest/queue.html#slurm) and [TORQUE](https://pysqa.readthedocs.io/en/latest/queue.html#torque)). This includes: 

* Submission of new calculation to the queuing system. 
* List of calculation currently waiting or running on the queuing system. 
* Deleting calculation which are currently waiting or running on the queuing system. 
* List of available queue templates created by the user.
* Restriction of templates to a specific number of cores, run time or other computing resources. With integrated checks if a given calculation follows these restrictions. 

In addition to these core features, `pysqa` is continuously extended to support more use cases for a larger group of users. These new features include the support for remote queuing systems: 

* Remote connection via the secure shell protocol to access remote HPC clusters.
* Transfer of file to and from remote HPC clusters, based on a predefined mapping of the remote file system into the local file system. 
* Support for both individual connections as well as continuous connections depending on the network availability. 

Finally, there is current work in progress to support a combination of [multiple local and remote queuing systems](https://pysqa.readthedocs.io/en/latest/advanced.html) from within `pysqa`, which are represented to the user as a single resource. 

# Documentation

* [Installation](https://pysqa.readthedocs.io/en/latest/installation.html)
  * [pypi-based installation](https://pysqa.readthedocs.io/en/latest/installation.html#pypi-based-installation)
  * [conda-based installation](https://pysqa.readthedocs.io/en/latest/installation.html#conda-based-installation)
* [Queuing Systems](https://pysqa.readthedocs.io/en/latest/queue.html)
  * [Flux](https://pysqa.readthedocs.io/en/latest/queue.html#flux)
  * [LFS](https://pysqa.readthedocs.io/en/latest/queue.html#lfs)
  * [MOAB](https://pysqa.readthedocs.io/en/latest/queue.html#moab)
  * [SGE](https://pysqa.readthedocs.io/en/latest/queue.html#sge)
  * [SLURM](https://pysqa.readthedocs.io/en/latest/queue.html#slurm)
  * [TORQUE](https://pysqa.readthedocs.io/en/latest/queue.html#torque)
* [Python Interface](https://pysqa.readthedocs.io/en/latest/example.html)
  * [List available queues](https://pysqa.readthedocs.io/en/latest/example.html#list-available-queues)
  * [Submit job to queue](https://pysqa.readthedocs.io/en/latest/example.html#submit-job-to-queue)
  * [Show jobs in queue](https://pysqa.readthedocs.io/en/latest/example.html#show-jobs-in-queue)
  * [Delete job from queue](https://pysqa.readthedocs.io/en/latest/example.html#delete-job-from-queue)
* [Command Line Interface](https://pysqa.readthedocs.io/en/latest/command.html)
  * [Submit job](https://pysqa.readthedocs.io/en/latest/command.html#submit-job)
  * [Enable reservation](https://pysqa.readthedocs.io/en/latest/command.html#enable-reservation)
  * [List jobs](https://pysqa.readthedocs.io/en/latest/command.html#list-jobs)
  * [Delete job](https://pysqa.readthedocs.io/en/latest/command.html#delete-job)
  * [List files](https://pysqa.readthedocs.io/en/latest/command.html#list-files)
  * [Help](https://pysqa.readthedocs.io/en/latest/command.html#help)
* [Advanced Configuration](https://pysqa.readthedocs.io/en/latest/advanced.html)
  * [Remote HPC Configuration](https://pysqa.readthedocs.io/en/latest/advanced.html#remote-hpc-configuration)
  * [Access to Multiple HPCs](https://pysqa.readthedocs.io/en/latest/advanced.html#access-to-multiple-hpcs)
* [Debugging](https://pysqa.readthedocs.io/en/latest/debug.html)
  * [Local Queuing System](https://pysqa.readthedocs.io/en/latest/debug.html#local-queuing-system)
  * [Remote HPC](https://pysqa.readthedocs.io/en/latest/debug.html#remote-hpc)

# License
`pysqa` is released under the BSD license https://github.com/pyiron/pysqa/blob/main/LICENSE . It is a spin-off of the `pyiron` project https://github.com/pyiron/pyiron therefore if you use `pysqa` for calculation which result in a scientific publication, please cite: 

    @article{pyiron-paper,
      title = {pyiron: An integrated development environment for computational materials science},
      journal = {Computational Materials Science},
      volume = {163},
      pages = {24 - 36},
      year = {2019},
      issn = {0927-0256},
      doi = {https://doi.org/10.1016/j.commatsci.2018.07.043},
      url = {http://www.sciencedirect.com/science/article/pii/S0927025618304786},
      author = {Jan Janssen and Sudarsan Surendralal and Yury Lysogorskiy and Mira Todorova and Tilmann Hickel and Ralf Drautz and Jörg Neugebauer},
      keywords = {Modelling workflow, Integrated development environment, Complex simulation protocols},
    }
