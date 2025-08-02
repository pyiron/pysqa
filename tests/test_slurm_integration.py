import unittest
import shutil
from pysqa import QueueAdapter

if shutil.which("srun") is not None:
    skip_slurm_test = False
else:
    skip_slurm_test = True


@unittest.skipIf(
    skip_slurm_test, "SLRUM is not installed, so the slurm tests are skipped.",
)
class TestSlurm(unittest.TestCase):
    def test_slurm(self):
        qa = QueueAdapter(queue_type="slurm")
        job_id = qa.submit_job(command="sleep 1")
        status = qa.get_status_of_job(process_id=job_id)
        self.assertEqual(status, "running")