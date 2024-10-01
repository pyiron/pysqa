#!/bin/bash
  
#PBS -l walltime=1:00:00
#PBS -l mem=10gb
#PBS -l ncpus=8
#PBS -l software=vasp
#PBS -l wd
  
# Load module, always specify version number.
module load vasp/5.4.4
  
# Must include `#PBS -l storage=scratch/ab12+gdata/yz98` if the job
# needs access to `/scratch/ab12/` and `/g/data/yz98/`
  
mpirun vasp_std >vasp.log