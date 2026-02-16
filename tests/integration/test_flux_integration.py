import unittest
import os
from pysqa import QueueAdapter

try:
    import flux

    skip_flux_test = False
except ImportError:
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
    skip_flux_test, "Flux is not installed, so the flux tests are skipped."
)
class TestFlux(unittest.TestCase):
    def test_flux(self):
        flux = QueueAdapter(queue_type="flux")
        job_id = flux.submit_job(command="sleep 1", cores=1, submission_template=submission_template)
        self.assertEqual(flux.get_status_of_job(process_id=job_id), "running")
        flux.delete_job(process_id=job_id)
        self.assertEqual(flux.get_status_of_job(process_id=job_id), "error")

    def test_flux_integration(self):
        path = os.path.dirname(os.path.abspath(__file__))
        flux = QueueAdapter(directory=os.path.join(path, "../static/flux"))
        job_id = flux.submit_job(
            queue="flux",
            job_name="test",
            working_directory=".",
            cores=1,
            command="sleep 1",
        )
        self.assertEqual(flux.get_status_of_job(process_id=job_id), "running")
        flux.delete_job(process_id=job_id)
        self.assertEqual(flux.get_status_of_job(process_id=job_id), "error")

    def test_flux_dependencies(self):
        path = os.path.dirname(os.path.abspath(__file__))
        flux = QueueAdapter(directory=os.path.join(path, "../static/flux"))
        job_id_1 = flux.submit_job(
            queue="flux",
            job_name="test",
            working_directory=".",
            cores=1,
            command="sleep 1",
        )
        job_id_2 = flux.submit_job(
            queue="flux",
            job_name="test",
            working_directory=".",
            cores=1,
            command="sleep 1",
            dependency_list=[job_id_1],
        )
        self.assertEqual(flux.get_status_of_job(process_id=job_id_1), "running")
        self.assertEqual(flux.get_status_of_job(process_id=job_id_2), "pending")
        flux.delete_job(process_id=job_id_1)
        self.assertEqual(flux.get_status_of_job(process_id=job_id_1), "error")
        flux.delete_job(process_id=job_id_2)
        self.assertEqual(flux.get_status_of_job(process_id=job_id_2), "error")

    def test_flux_integration_dynamic(self):
        flux_dynamic = QueueAdapter(queue_type="flux")
        job_id = flux_dynamic.submit_job(
            cores=1,
            command="sleep 1",
        )
        self.assertEqual(flux_dynamic.get_status_of_job(process_id=job_id), "running")
        flux_dynamic.delete_job(process_id=job_id)
        self.assertEqual(flux_dynamic.get_status_of_job(process_id=job_id), "error")