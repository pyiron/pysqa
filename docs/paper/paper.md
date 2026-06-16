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
High-performance computing (HPC) resources are commonly accessed through batch scheduling systems such as LSF [@lsf], Torque/PBS [@pbs], SGE [@sge],  SLURM [@slurm], Moab [@moab] and Flux [@flux]. These schedulers provide powerful command-line interfaces for job submission and resource management, but integrating scheduler interactions into Python applications often requires scheduler-specific scripts, shell wrappers, and custom parsing of scheduler outputs. As a result, scientific software frequently contains infrastructure code that is difficult to maintain and port across HPC environments.

![Schematic overview of pysqa. The package provides a scheduler-independent interface for submitting, monitoring, and managing HPC jobs from Python or the command line. Reusable Jinja2-based templates are translated to the native syntax of supported queuing systems (e.g., SLURM, PBS, LSF, and SGE), while built-in support for remote connections, reservations, and job management simplifies the integration of HPC resources into scientific workflows.\label{fig:pysqa}](pysqa.png){width="100%"}

pysqa (Python Simple Queue Adapter) is an open-source Python library that provides a lightweight, scheduler-independent interface for submitting, monitoring, and managing HPC jobs. The design of pysqa is based on reusable queue templates written in the Jinja2 templating language. Users define scheduler-specific submission scripts once and subsequently reuse them across many computational tasks and workflows. This approach separates scheduler configuration from application logic while preserving transparency by generating native scheduler submission scripts. pysqa currently supports Flux, LSF, Moab, SGE, SLURM, and Torque queuing systems and includes optional support for remote job submission via SSH.

Unlike workflow orchestration frameworks, pysqa focuses exclusively on the scheduler interaction layer. It enables computational scientists and research software engineers to integrate HPC resources into Python applications with minimal complexity while retaining full control over scheduler-specific configurations. A schematic overview of pysqa is illustrated in \autoref{fig:pysqa}.

# Statement of Need
Modern computational research increasingly relies on automated execution of simulations, machine learning workloads, and data-processing pipelines on shared HPC infrastructure. While scheduler command-line tools such as sbatch, squeue, and scancel provide direct access to HPC resources, scientific applications often require programmatic job submission and monitoring capabilities. Embedding scheduler-specific commands directly into software reduces portability and increases maintenance costs when users operate across multiple clusters.

Several software projects address related challenges. MyQueue [@myqueue] provides a higher-level task and workflow abstraction designed for scientific computing campaigns. PSI/J [@psij] offers a portable job execution API spanning multiple schedulers and execution backends. Jobflow-Remote focuses on remote execution of workflow graphs within the Jobflow ecosystem [@jobflow]. These tools provide broader workflow or interoperability capabilities, but they also introduce additional abstractions and infrastructure requirements.

pysqa addresses a different use case. It provides a minimal abstraction layer between Python applications and HPC schedulers while deliberately avoiding workflow management, databases, or orchestration services. The resulting design minimizes dependencies, simplifies deployment, and allows users to continue working with familiar scheduler submission scripts. This approach is particularly valuable for scientific software projects that require scheduler portability without adopting a complete workflow framework. Additionaly, pysqa can also be implemented as a module in existing workflow frameworks and task schedulers [@pyiron], [@executorlib].


# Features and Implementation
The central abstraction in pysqa is the QueueAdapter, which provides a scheduler-independent Python interface for submitting, monitoring, and managing jobs. Rather than invoking scheduler commands such as `sbatch`, `qsub`, `bsub`, or `flux submit` directly from shell scripts, users can interact with HPC resources through a small set of Python methods:

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

This Python interface simplifies the integration of HPC resources into scientific software, high-throughput simulation frameworks, and automated workflows. Resource requests and scheduler interactions can be expressed directly in Python without embedding scheduler-specific commands or parsing scheduler outputs. At the same time, pysqa does not replace the underlying scheduler command-line interface. Instead, it builds on top of existing scheduler functionality and generates standard submission scripts that remain fully transparent to users and administrators.

To achieve portability across different computing environments, pysqa separates scheduler configuration from submission script generation. Cluster-specific settings are defined in a YAML configuration file, which describes available queues, resource limits, and scheduler properties:

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

This configuration provides a machine-readable description of the HPC environment and can be shared across users and projects.

The scheduler submission scripts themselves are defined using Jinja2 templates. For example, a Slurm submission template can be written as:

```
#!/bin/bash
#SBATCH --job-name={{job_name}}
#SBATCH --cpus-per-task={{cores}}
#SBATCH --time={{run_time_max}}
#SBATCH --output={{job_name}}.out

{{command}}
```

The use of Jinja2 templates preserves the familiar scheduler-native submission scripts that HPC users and administrators already maintain. Existing Slurm, PBS, or Flux scripts can typically be converted with only minor modifications by replacing fixed values with template variables. During job submission, pysqa combines the resource parameters provided through the Python interface with the cluster configuration and renders the corresponding scheduler script before submitting it through the scheduler’s native command-line tools.

This separation of concerns provides three advantages. First, application developers interact with a consistent Python API independent of the underlying scheduler. Second, cluster-specific configuration is maintained centrally in YAML files rather than being embedded in application code. Third, scheduler experts retain full control over the generated submission scripts using familiar scheduler directives and scripting practices. As a result, pysqa combines the programmability of a Python interface with the transparency and flexibility of traditional scheduler-native workflows.

# Usage To-Date 
pysqa was initially developed as a module of the pyiron workflow environment [@pyiron]. It was spun-off into an standalone package to be used in different components of the pyiron ecosystem including executorlib [@executorlib]. Since the spin-off external projects started to use pysqa including ropt [@ropt], DREAMS [@dreams], nipoppy [@nipoppy] and matsci-agent [@matsci-agent].

# Additional Details 
The full documentation including a number of examples for the individual features is available at [pysqa.readthedocs.io](https://pysqa.readthedocs.io) with the corresponding source code at [github.com/pyiron/pysqa](https://github.com/pyiron/pysqa). pysqa is developed an as open-source library with a focus on stability. 

# AI usage disclosure
The initial version of pysqa was developed without the usage of AI. Github Co-pilot and Claude Code from Anthropic were used to extend type hints, docstrings and encrich the documentation of pysqa. Finally, ChatGPT was used for writing the first draft of the manuscript, proofreading and the conceptualization of the visuals.

# Acknowledgements
J.J. and J.N. acknowledge funding from the Deutsche Forschungsgemeinschaft (DFG) through the CRC1394 “Structural and Chemical Atomic Complexity – From Defect Phase Diagrams to Material Properties”, project ID 409476157. 

# References
