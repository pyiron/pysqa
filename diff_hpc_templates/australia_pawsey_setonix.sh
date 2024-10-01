#!/bin/bash -l
##SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --ntasks-per-node=32
#SBATCH --cpus-per-task=1
#SBATCH --account=pawsey0380
#SBATCH --job-name=TSR_RATTLE_struct_1871_2_Mn_8.sh
#SBATCH --time=4:00:00
#SBATCH --partition=work
#SBATCH --export=NONE
#SBATCH --mem=32GB
##SBATCH --exclusive

module load vasp/5.4.4
cd "$PBS_O_WORKDIR"

ulimit -s unlimited
run_cmd="srun --export=ALL -N 1 -n 32"

$run_cmd vasp_std &> vasp.log
