"""Host verification of the image launch boundary; not Linux/container acceptance."""

from pathlib import Path
import runpy
import unittest

command = runpy.run_path(str(Path(__file__).resolve().parents[2] / 'deploy/api/start.py'))['command']


class ImageLauncherTests(unittest.TestCase):
    def test_configurable_port_and_single_process_limits(self):
        default = command({})
        custom = command({'PORT': '8765'})
        self.assertEqual(default[default.index('--port') + 1], '8080')
        self.assertEqual(custom[custom.index('--port') + 1], '8765')
        self.assertEqual(custom[custom.index('--host') + 1], '0.0.0.0')
        self.assertEqual(custom[custom.index('--workers') + 1], '1')
        self.assertEqual(custom[custom.index('--limit-concurrency') + 1], '16')
        self.assertEqual(custom[custom.index('--timeout-graceful-shutdown') + 1], '2')
        self.assertIn('--no-access-log', custom)

    def test_invalid_port_is_rejected_without_execution(self):
        for port in ('', '0', '-1', '65536', '8080 --workers 4', '１２３', '1.5'):
            with self.subTest(port=port), self.assertRaises(ValueError):
                command({'PORT': port})
