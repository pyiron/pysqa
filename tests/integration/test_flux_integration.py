import unittest
import shutil
from pysqa import QueueAdapter

if shutil.which("flux") is not None:
    skip_flux_test = False
else:
    skip_flux_test = True

submission_template = """\
#!/bin/bash
# flux: --job-name={{job_name}}
# flux: --env=CORES={{cores}}
# flux: --output=time.out
# flux: --error=error.out
# flux: -n {{cores}}

{{command}}
"""


@unittest.skipIf(
    skip_flux_test, "FLUX is not installed, so the flux tests are skipped.",
)
class TestFlux(unittest.TestCase):
    def test_flux(self):
        slurm_dynamic = QueueAdapter(queue_type="flux")
        job_id = slurm_dynamic.submit_job(command="sleep 1", cores=1, submission_template=submission_template)
        self.assertEqual(slurm_dynamic.get_status_of_job(process_id=job_id), "running")
        slurm_dynamic.delete_job(process_id=job_id)
        self.assertIsNone(slurm_dynamic.get_status_of_job(process_id=job_id))