#!/bin/bash
#SBATCH --output=time.out
#SBATCH --job-name={{job_name}}
#SBATCH --workdir={{working_directory}}
#SBATCH --get-user-env=L
#SBATCH --partition=slurm
{%- if run_time_max %}
#SBATCH --time={{ [1, run_time_max // 60]|max }}
{%- endif %}
{%- if memory_max %}
#SBATCH --mem={{memory_max}}
{%- endif %}
#SBATCH --cpus-per-task={{cores}}

{{command}}
