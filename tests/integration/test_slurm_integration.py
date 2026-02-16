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
{%- if dependency_list %}
#SBATCH --dependency=afterok:{{ dependency_list | join(',') }}
{%- endif %}

{{command}}
"""


@unittest.skipIf(
    skip_slurm_test, "SLURM is not installed, so the slurm tests are skipped.",
)
class TestSlurm(unittest.TestCase):
    def test_slurm(self):
        slurm_dynamic = QueueAdapter(queue_type="slurm")
        job_id = slurm_dynamic.submit_job(command="sleep 1", cores=1, submission_template=submission_template)
        self.assertEqual(slurm_dynamic.get_status_of_job(process_id=job_id), "pending")
        slurm_dynamic.delete_job(process_id=job_id)
        self.assertIsNone(slurm_dynamic.get_status_of_job(process_id=job_id))

    def test_slurm_dependencies(self):
        slurm_dynamic = QueueAdapter(queue_type="slurm")
        job_id_1 = slurm_dynamic.submit_job(command="sleep 1", cores=1, submission_template=submission_template)
        job_id_2 = slurm_dynamic.submit_job(command="sleep 1", cores=1, submission_template=submission_template, dependency_list=[job_id_1])
        self.assertEqual(slurm_dynamic.get_status_of_job(process_id=job_id_1), "pending")
        self.assertEqual(slurm_dynamic.get_status_of_job(process_id=job_id_2), "pending")
        slurm_dynamic.delete_job(process_id=job_id_1)
        slurm_dynamic.delete_job(process_id=job_id_2)
        self.assertIsNone(slurm_dynamic.get_status_of_job(process_id=job_id_1))
        self.assertIsNone(slurm_dynamic.get_status_of_job(process_id=job_id_2))