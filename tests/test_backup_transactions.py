import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import install


class BackupTransactionTests(unittest.TestCase):
    def test_repeated_backups_get_unique_names(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "luna-ultra-models.json"
            target.write_text("original", encoding="utf-8")
            first = install.backup_existing([target])
            second = install.backup_existing([target])
            self.assertNotEqual(first[0][1], second[0][1])
            self.assertEqual(first[0][1].read_text(encoding="utf-8"), "original")
            self.assertEqual(second[0][1].read_text(encoding="utf-8"), "original")
            self.assertEqual(first[0][1].stat().st_mode & 0o777, 0o600)

    def test_prevalidation_failure_does_not_leave_orphan_backup(self):
        with tempfile.TemporaryDirectory() as temp:
            regular = Path(temp) / "first.json"
            directory = Path(temp) / "second.json"
            regular.write_text("untouched", encoding="utf-8")
            directory.mkdir()
            with self.assertRaises(install.InstallError):
                install.backup_existing([regular, directory])
            self.assertEqual(regular.read_text(encoding="utf-8"), "untouched")
            self.assertEqual(list(Path(temp).glob("*.bak")), [])

    def test_transaction_rolls_back_first_replacement_if_second_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            first = Path(temp) / "first.json"
            second = Path(temp) / "second.json"
            first.write_text("old-first", encoding="utf-8")
            second.write_text("old-second", encoding="utf-8")
            real_replace = install.os.replace
            failed = False

            def replace_once_then_fail(source, destination):
                nonlocal failed
                if Path(destination) == second and not failed:
                    failed = True
                    raise PermissionError("simulated replacement failure")
                return real_replace(source, destination)

            with mock.patch.object(install.os, "replace", side_effect=replace_once_then_fail):
                with self.assertRaises(PermissionError):
                    install.transactional_write(
                        {first: b"new-first", second: b"new-second"}, force=True
                    )
            self.assertEqual(first.read_text(encoding="utf-8"), "old-first")
            self.assertEqual(second.read_text(encoding="utf-8"), "old-second")
            self.assertTrue(list(Path(temp).glob("*.bak")))
            self.assertEqual(
                [path.name for path in Path(temp).iterdir() if path.name.startswith((".first.json.", ".second.json."))],
                [],
            )


if __name__ == "__main__":
    unittest.main()
