from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from prepare_sources import package_check, safe_target, within


class SourcePackTests(unittest.TestCase):
    def test_target_paths_cannot_escape_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(safe_target(root, "history/v45/code/engine.py"), root / "history/v45/code/engine.py")
            for bad in ("../.env", "history/../../.env", "/tmp/escape", "solutions/v58/src/runner.py"):
                with self.subTest(path=bad), self.assertRaises(ValueError):
                    safe_target(root, bad)
            self.assertFalse(within(root.parent, root))

    def test_package_hash_drift_fails_closed(self):
        source_root = next(p for p in Path(__file__).resolve().parents if (p / "CURRENT_STATE.json").is_file())
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copied = root / "solutions/v58/frozen_sources"
            copied.parent.mkdir(parents=True)
            shutil.copytree(source_root / "solutions/v58/frozen_sources", copied)
            manifest, _bundle = package_check(root)
            relative = next(iter(manifest["files_sha256"]))
            with (copied / "files" / relative).open("ab") as stream:
                stream.write(b"drift")
            with self.assertRaisesRegex(RuntimeError, "hash mismatch"):
                package_check(root)


if __name__ == "__main__":
    unittest.main()
