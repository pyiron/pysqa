---
title: 'pysqa - Python Simple Queuing System Adapter'
tags:
  - Python
  - High Performance Computing
  - Workflows
authors:
  - name: Jan Janssen
    orcid: 0000-0001-9948-7119
    affiliation: 1
  - name: Joerg Neugebauer
    orcid: 0000-0002-7903-2472
    affiliation: 1

affiliations:
 - name: Max Planck Institute for Sustainable Materials, Düsseldorf, Germany
   index: 1
date: 22 March 2026
bibliography: paper.bib
---

# Summary
The Python Simple Queuing System Adapter (pysqa) provides a Python interface to interact with local and remote high-performance computing (HPC) job schedulers. While the majority of HPC clusters use the Simple Linux Utility for Resource Management (SLURM) as job scheduler, their configurations vary drastically, requiring the users to configure their Python workflows for each HPC cluster separately. pysqa addresses this challenge by providing a Python interface not only for SLURM, but for a number of different job schedulers. In contrast to alternative Python interfaces for HPC job schedulers, which commonly indroduce their own configuration format for the different HPC job schedulers, pysqa leverages jinja2 templates. For the users this is beneficial as they can use the submission script templates provided by the administrators of the HPC cluster and just replace the settings they want to adjust by jinja2 variables. This concept of focusing on easy-of-use by providing a minimal Python layer around HPC job schedulers is the software design principle of the pysqa package. 

# Statement of Need
With the rise of centralized computing centers in Europe and internationally, the need to run the same workflow on different high-performance computing (HPC) clusters becomes more and more relevant. Without a generalized abstraction layer, this requires the workflow to be updated for each HPC cluster. The Python Simple Queuing System Adapter (pysqa) addresses this challenge, by providing a unified interface to different HPC job schedulers, including Flux, IBM Spectrum Load Sharing Facility (LSF), MOAB, Sun Grid Engine (SGE), Simple Linux Utility for Resource Management (SLURM) and Terascale Open-source Resource and Queue Manager (TORQUE). To minimize the overhead for the users to translate the submission script examples provided by the administrators of the HPC cluster to the pysqa specific input files, pysqa leverages jinja2 templates, so the users can start with the example scripts and simply replace the parameters which they want to access from Python with jinja2 variables. This is in contrast to alternative solutions like myqueue [@myqueue] or PSI/j [@psij] which which introduce their own configuration file syntax. Furthermore, pysqa provides a Python abstraction layer for the connection to remove HPC clusters using SSH based on the paramiko package, enabling multi-facility workflows.  

# Features and Implementation


# Usage To-Date 

# Additional Details 
The full documentation including a number of examples for the individual features is available at [pysqa.readthedocs.io](https://pysqa.readthedocs.io) with the corresponding source code at [github.com/pyiron/pysqa](https://github.com/pyiron/pysqa). pysqa is developed an as open-source library with a focus on stability. 

# AI usage disclosure
No generative AI tools were used in the development of this software, the writing of this manuscript, or the preparation of supporting materials.

# Acknowledgements
J.J. and J.N. acknowledge funding from the Deutsche Forschungsgemeinschaft (DFG) through the CRC1394 “Structural and Chemical Atomic Complexity – From Defect Phase Diagrams to Material Properties”, project ID 409476157. 

# References
