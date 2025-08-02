import os
import unittest
from pysqa import QueueAdapter

try:
    skip_flux_test = "FLUX_URI" not in os.environ
    pmi = os.environ.get("EXECUTORLIB_PMIX", None)
except ImportError:
    skip_flux_test = True


@unittest.skipIf(
    skip_flux_test, "Flux is not installed, so the flux tests are skipped."
)
class TestFlux(unittest.TestCase):
    def test_flux(self):
        qa = QueueAdapter(queue_type="flux")
        job_id = qa.submit_job(command="sleep 1")
        status = qa.get_status_of_job(process_id=job_id)
        self.assertEqual(status, "running")