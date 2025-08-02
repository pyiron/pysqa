import unittest
import shutil
from pysqa import QueueAdapter

if shutil.which("srun") is not None:
    skip_slurm_test = False
else:
    skip_slurm_test = True


submission_template = """\
#!/bin/bash
#SBATCH --output=time.out
#SBATCH --job-name={{job_name}}
#SBATCH --chdir={{working_directory}}
#SBATCH --get-user-env=L
#SBATCH --ntasks={{cores}}

{{command}}
"""


@unittest.skipIf(
    skip_slurm_test, "SLURM is not installed, so the slurm tests are skipped.",
)
class TestSlurm(unittest.TestCase):
    def test_slurm(self):
        slurm_dynamic = QueueAdapter(queue_type="slurm")
        job_id = slurm_dynamic.submit_job(command="sleep 1", cores=1, submission_template=submission_template)
        self.assertEqual(slurm_dynamic.get_status_of_job(process_id=job_id), "running")
        slurm_dynamic.delete_job(process_id=job_id)
        self.assertEqual(slurm_dynamic.get_status_of_job(process_id=job_id), "error")