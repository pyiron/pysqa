import unittest
from pysqa.base.validate import (
    value_error_if_none,
    value_in_range,
    check_queue_parameters,
)


class TestValidate(unittest.TestCase):
    def test_memory_string_comparison(self):
        self.assertEqual(value_in_range(1023, value_min="1K"), "1K")
        self.assertEqual(value_in_range(1035, value_min="1K"), 1035)
        self.assertEqual(value_in_range(1035, value_max="1K"), "1K")
        self.assertEqual(value_in_range("1035", value_min="1K"), "1035")
        self.assertEqual(
            value_in_range("60000M", value_min="1K", value_max="50G"),
            "50G",
        )
        self.assertEqual(
            value_in_range("60000", value_min="1K", value_max="50G"),
            "50G",
        )
        self.assertEqual(
            value_in_range("60000M", value_min="1K", value_max="70G"),
            "60000M",
        )
        self.assertEqual(
            value_in_range(60000, value_min="1K", value_max="70G"),
            60000,
        )
        self.assertEqual(
            value_in_range(90000 * 1024**2, value_min="1K", value_max="70G"),
            "70G",
        )
        self.assertEqual(
            value_in_range("90000", value_min="1K", value_max="70G"),
            "70G",
        )
        self.assertEqual(
            value_in_range("60000M", value_min="60G", value_max="70G"),
            "60G",
        )

    def test_memory_string_comparison_non_memory_strings(self):
        # "5x"/"3y"/"9z" contain a digit but are not valid memory specs, so
        # _memory_spec_string_to_value() returns them unchanged (line 149).
        self.assertEqual(value_in_range("5x", value_min="3y", value_max="9z"), "5x")

    def test_check_queue_parameters(self):
        cores, run_time_max, memory_max = check_queue_parameters(
            active_queue={
                "cores_min": 1,
                "cores_max": 100,
                "memory_max": 12,
                "run_time_max": 1000,
            },
            cores=1,
            run_time_max=100,
            memory_max=10,
        )
        self.assertEqual(cores, 1)
        self.assertEqual(run_time_max, 100)
        self.assertEqual(memory_max, 10)

    def test_value_error_if_none_raises_value_error(self):
        with self.assertRaises(ValueError) as context:
            value_error_if_none(None)
        self.assertIn("None", str(context.exception))

    def test_value_error_if_none_raises_type_error_with_message(self):
        with self.assertRaises(TypeError) as context:
            value_error_if_none(42)
        self.assertIn("int", str(context.exception))

    def test_value_error_if_none_passes_for_string(self):
        value_error_if_none("valid")  # should not raise
