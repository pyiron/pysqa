# pysqa
Simple queue adapter for python 

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/9db80cb2477f46be870d1446540b4bf3)](https://www.codacy.com/app/pyiron-runner/pysqa?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=pyiron/pysqa&amp;utm_campaign=Badge_Grade_Dashboard)
[![Build Status](https://travis-ci.org/pyiron/pysqa.svg?branch=master)](https://travis-ci.org/pyiron/pysqa)
[![Build status](https://ci.appveyor.com/api/projects/status/9lpjai8rvt8324aj/branch/master?svg=true)](https://ci.appveyor.com/project/pyiron-runner/pysqa/branch/master)
[![Coverage Status](https://coveralls.io/repos/github/pyiron/pysqa/badge.svg?branch=master)](https://coveralls.io/github/pyiron/pysqa?branch=master)

The goal of pysqa is to make submitting to an HPC cluster as easy as starting another subprocess. This is based on the assumption that even though modern queuing systems allow for an wide range of different configuration, most users submit the majority of their jobs with very similar parameters. Therefore pysqa allows the users to store their submission scripts as jinja2 templates for quick access. After the submission pysqa allows the users to track the progress of their jobs, delete them or enable reservations using the built-in functionality of the queuing system. The currently supported queuing systems are: LFS, MOAB, SGE (tested), SLURM (tested), TORQUE. 

# Installation
pysqa can either be installed via pip using:

    pip install pysqa

Or via anaconda from the conda-forge channel

    conda install -c conda-forge pysqa


# Usage 
pysqa requires the user to configure the type of queuing system as well as the available templates. Example configuration are available at:
https://github.com/pyiron/pysqa/tree/master/tests/config
By default pysqa is searching for the queue configuration in `~/.queues/queue.yaml` and the corresponding jinja2 templates in the same folder.

Import pysqa:

    from pysqa import QueueAdapter 
    sqa = QueueAdapter(directory=‘~/.queues’)  # directory which contains the queue.yaml file 

List available queues as list of queue names: 

    sqa.queue_list 

List available queues in an pandas dataframe: 

    sqa.queue_view 

Submit a job to the queue - if no queue is specified it is submitted to the default queue defined in the queue configuration:

    sqa.submit_job(command=‘python test.py’)

Get status of all jobs currently handled by the queuing system:

    sqa.get_queue_status()

Get status of a specifc job from the queuing system:

    sqa.get_status_of_job(process_id=1234)

Delete a job from the queuing sytem:

    sqa.delete_job(process_id=1234) 

Sample configurations for the specific queuing systems are availabe in the tests: 

* lsf - https://github.com/pyiron/pysqa/tree/master/tests/config/lsf
* moab - https://github.com/pyiron/pysqa/tree/master/tests/config/moab
* SGE - https://github.com/pyiron/pysqa/tree/master/tests/config/sge
* slurm - https://github.com/pyiron/pysqa/tree/master/tests/config/slurm
* torque - https://github.com/pyiron/pysqa/tree/master/tests/config/torque

# License
pysqa is released under the BSD license https://github.com/pyiron/pysqa/blob/master/LICENSE . It is a spin-off of the pyiron project https://github.com/pyiron/pyiron therefore if you use pysqa for your publication, please cite: 

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
