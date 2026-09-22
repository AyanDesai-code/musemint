"""Tests for local setup safety and command failure behavior (no Docker needed)."""
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import dev


class DevTests(unittest.TestCase):
    def test_setup_preserves_existing_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / '.env.example').write_text('EXAMPLE=local\n')
            with patch.object(dev, 'ROOT', root):
                dev.setup()
                self.assertEqual((root / '.env').read_text(), 'EXAMPLE=local\n')
                (root / '.env').write_text('EXISTING=keep\n')
                dev.setup()
                self.assertEqual((root / '.env').read_text(), 'EXISTING=keep\n')

    def test_compose_requires_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(dev, 'ROOT', Path(directory)), patch.object(dev, 'run') as run:
                with self.assertRaises(RuntimeError):
                    dev.compose('up')
                run.assert_not_called()

    def test_command_failure_is_not_hidden(self):
        with patch.object(dev, 'run', side_effect=subprocess.CalledProcessError(2, 'test')):
            self.assertEqual(dev.main(['check']), 1)

    def test_chain_id_validation(self):
        for payload, valid in [(b'{"result":"0x7a69"}', True),
                               (b'{"result":"0x1"}', False),
                               (b'{"error":{}}', False)]:
            with patch.object(dev, 'urlopen', return_value=io.BytesIO(payload)):
                if valid:
                    dev.chain_ready()
                else:
                    with self.assertRaises(ValueError):
                        dev.chain_ready()

    def test_smoke_retries_and_fails(self):
        with patch.object(dev, 'compose'), patch.object(dev.time, 'sleep'), \
                patch.object(dev, 'chain_ready', side_effect=ValueError) as ready:
            with self.assertRaises(RuntimeError):
                dev.smoke()
            self.assertEqual(ready.call_count, 30)

    def test_down_never_removes_volumes(self):
        with patch.object(dev, 'compose') as compose:
            self.assertEqual(dev.main(['down']), 0)
            compose.assert_called_once_with('down')


if __name__ == '__main__':
    unittest.main()
