---
title: 'pysqa - Python Simple Queuing System Adapter'
tags:
  - Python
  - High Performance Computing
  - Job Scheduler
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
date: 14 June 2026
bibliography: paper.bib
---

# Summary
High-performance computing (HPC) resources are commonly accessed through batch scheduling systems such as SLURM [@slurm], PBS/Torque, SGE, LSF, Moab, and Flux [@flux]. These schedulers provide powerful command-line interfaces for job submission and resource management, but integrating scheduler interactions into Python applications often requires scheduler-specific scripts, shell wrappers, and custom parsing of scheduler outputs. As a result, scientific software frequently contains infrastructure code that is difficult to maintain and port across computing environments.

pysqa (Python Simple Queue Adapter) is an open-source Python library that provides a lightweight, scheduler-independent interface for submitting, monitoring, and managing HPC jobs. The design of pysqa is based on reusable queue templates written in the Jinja2 templating language. Users define scheduler-specific submission scripts once and subsequently reuse them across many computational tasks and workflows. This approach separates scheduler configuration from application logic while preserving transparency by generating native scheduler submission scripts. pysqa currently supports Flux, LSF, Moab, SGE, SLURM, and Torque queuing systems and includes optional support for remote job submission via SSH.

Unlike workflow orchestration frameworks, pysqa focuses exclusively on the scheduler interaction layer. It enables computational scientists and research software engineers to integrate HPC resources into Python applications with minimal complexity while retaining full control over scheduler-specific configurations. A schematic overview of pysqa is illustrated in \autoref{fig:pysqa}.

![Schematic overview of pysqa. The package provides a scheduler-independent interface for submitting, monitoring, and managing HPC jobs from Python or the command line. Reusable Jinja2-based templates are translated to the native syntax of supported queuing systems (e.g., SLURM, PBS, LSF, and SGE), while built-in support for remote connections, reservations, and job management simplifies the integration of HPC resources into scientific workflows.\label{fig:pysqa}](pysqa.png){width="100%"}

# Statement of Need
Modern computational research increasingly relies on automated execution of simulations, machine learning workloads, and data-processing pipelines on shared HPC infrastructure. While scheduler command-line tools such as sbatch, squeue, and scancel provide direct access to HPC resources, scientific applications often require programmatic job submission and monitoring capabilities. Embedding scheduler-specific commands directly into software reduces portability and increases maintenance costs when users operate across multiple clusters.

Several software projects address related challenges. MyQueue [@myqueue] provides a higher-level task and workflow abstraction designed for scientific computing campaigns. PSI/J [@psij] offers a portable job execution API spanning multiple schedulers and execution backends. Jobflow-Remote focuses on remote execution of workflow graphs within the Jobflow ecosystem [@jobflow]. These tools provide broader workflow or interoperability capabilities, but they also introduce additional abstractions and infrastructure requirements.

pysqa addresses a different use case. It provides a minimal abstraction layer between Python applications and HPC schedulers while deliberately avoiding workflow management, databases, or orchestration services. The resulting design minimizes dependencies, simplifies deployment, and allows users to continue working with familiar scheduler submission scripts. This approach is particularly valuable for scientific software projects that require scheduler portability without adopting a complete workflow framework.


# Features and Implementation
The central abstraction in pysqa is the QueueAdapter, which exposes a small set of scheduler-independent operations:

```python
from pysqa import QueueAdapter

queue_adapter = QueueAdapter(directory="queues")

job_id = queue_adapter.submit_job(
    queue="standard",
    job_name="example",
    cores=16,
    run_time_max=3600,
    command="python simulation.py"
)

status = queue_adapter.get_queue_status()
queue_adapter.delete_job(job_id)
```

The scheduler-specific details are defined in a queue configuration and associated Jinja2 templates. A simplified Slurm configuration is shown below:

```YAML
queue_type: SLURM
queue_primary: standard

queues:
  standard:
    cores_min: 1
    cores_max: 128
    run_time_max: 86400
    script: slurm.sh
```

The corresponding Slurm submission template may be defined as:

```
#!/bin/bash
#SBATCH --job-name={{job_name}}
#SBATCH --cpus-per-task={{cores}}
#SBATCH --time={{run_time_max}}
#SBATCH --output={{job_name}}.out

{{command}}
```

During submission, pysqa renders the template using the supplied resource parameters and submits the resulting scheduler-native script. This template-based architecture allows users to preserve local scheduler conventions while exposing a consistent Python interface to scientific applications.

# Usage To-Date 
Pysqa was initially developed as a module of the pyiron workflow environment [@pyiron]. It was spun-off into an standalone package to be used in different components of the pyiron ecosystem including executorlib. Since then external projects started to use pysqa including nipoppy, DREAMS, matsci-agent and ropt.

# Additional Details 
The full documentation including a number of examples for the individual features is available at [pysqa.readthedocs.io](https://pysqa.readthedocs.io) with the corresponding source code at [github.com/pyiron/pysqa](https://github.com/pyiron/pysqa). pysqa is developed an as open-source library with a focus on stability. 

# AI usage disclosure
The initial version of pysqa was developed without the usage of AI. Github Co-pilot and Claude Code from Anthropic were used to extend type hints, docstrings and encrich the documentation of pysqa. Finally, ChatGPT was used for writing the first draft of the manuscript, proofreading and the conceptualization of the visuals.

# Acknowledgements
J.J. and J.N. acknowledge funding from the Deutsche Forschungsgemeinschaft (DFG) through the CRC1394 “Structural and Chemical Atomic Complexity – From Defect Phase Diagrams to Material Properties”, project ID 409476157. 

# References
