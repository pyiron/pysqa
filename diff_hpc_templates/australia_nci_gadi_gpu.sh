#!/bin/bash
  
#PBS -P a99
#PBS -q gpuvolta
#PBS -l ncpus=24
#PBS -l ngpus=2
#PBS -l walltime=1:00:00
#PBS -l mem=32GB
#PBS -l jobfs=1GB
#PBS -l wd
  
# Load module, always specify version number.
module load lammps/15Sep2022
  
# Must include `#PBS -l storage=scratch/ab12+gdata/yz98` if the job
# needs access to `/scratch/ab12/` and `/g/data/yz98/`
  
ngpus=$(( PBS_NGPUS<4?PBS_NGPUS:4 ))
  
mpirun -np $PBS_NCPUS lmp_openmpi -sf gpu -pk gpu $ngpus -i input_filename > output