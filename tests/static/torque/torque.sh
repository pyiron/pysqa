#!/bin/bash
#PBS -q normal # Insert the queue that you want to use here
#PBS -l ncpus={{cores}}
#PBS -N {{job_name}}
{%- if memory_max %}
#PBS -l mem={{ [16, memory_max]| int |max }}GB # Set minimum 16 GB RAM, or user-set limit
{%- endif %}
{%- if run_time_max %}
#PBS -l walltime={{ [1*3600, run_time_max*3600]|max }} # Replace 3600 if you want to use seconds as input, currently HOURS
{%- endif %}
#PBS -l wd
#PBS -l software=vasp # If your system requires this kind of command (check your HPC webpage/ask your admin)
#PBS -l storage=scratch/a01+gdata/a01 # If your system requires you to set visibility of storage partitions 
#PBS -P a01 # If you have multiple projects and want to charge to project named "a01"

# Remove all the trailing # instructions in the headers above before use!

# Put a command to activate your conda environment with pyiron in it, if required
# e.g. source /software_path/mambaforge/bin/activate pyiron
 
{{command}}
