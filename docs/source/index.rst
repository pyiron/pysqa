=========================================
pysqa - a simple queue adapter for python
=========================================

:Author:  Jan Janssen
:Contact: janssen@mpie.de

High-performance computing (HPC) does not have to be hard. In this context the aim of pysqa is to simplify the submission of calculation to an HPC cluster as easy as starting another subprocess locally. This is achieved based on the assumption that even though modern HPC queuing systems offer a wide range of different configuration options, most users submit the majority of their jobs with very similar parameters. 

Therefore, in pysqa users define submission script templates once and reuse them to submit many different calculations or workflows. These templates are defined in the jinja2 template language, so current submission scripts can be easily extended to templates. In addition to the submission of new jobs to the queuing system pysqa also allows the users to track the progress of their jobs, delete them or enable reservations using the built-in functionality of the queuing system.

Features
--------
The core feature of pysqa is the communication to an HPC queuing system. This includes: 

* Submission of new calculation to the queuing system. 
* List of calculation currently waiting or running on the queuing system. 
* Deleting calculation which are currently waiting or running on the queuing system. 
* List of available queue templates created by the user.
* Restriction of templates to a specific number of cores, run time or other computing resources. With integrated checks if a given calculation follows these restrictions. 

In addition to these core features, pysqa is continously extended to support more usecases for a larger group of users. These new features include the support for remote queuing systems: 

* Remote connection via the secure shell protocol to access remote HPC clusters.
* Transfer of file to and from remote HPC clusters, based on a predefined mapping of the remote file system into the local file system. 
* Support for both individual connections as well as continous connections depending on the network availability. 

Finally, there is current work in progress to support a combination of multiple local and remote queuing systems from within pysqa, which are represented to the user as a single resource. 

Documentation
-------------

.. toctree::
   :maxdepth: 2

   installation
   queue
   python
   command
   advanced
   debug
