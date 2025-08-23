#!/bin/bash
 
#PBS -q gpuvolta
#PBS -l walltime=10:00:00
#PBS -l ncpus=48
#PBS -l ngpus=4
#PBS -l mem=160GB
#PBS -l jobfs=1GB
#PBS -l wd
 
# Load module, always specify version number.
module load vasp/6.2.1
 
# Must include `#PBS -l storage=scratch/ab12+gdata/yz98` if the job
# needs access to `/scratch/ab12/` and `/g/data/yz98/`. Details on:
# https://opus.nci.org.au/display/Help/PBS+Directives+Explained
 
mpirun -np $PBS_NGPUS --map-by ppr:1:numa vasp_std-gpu >vasp.log