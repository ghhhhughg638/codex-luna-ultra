import contextlib
import io
import json
import os
import unittest
from unittest import mock

from scripts import check_dependencies


def valid_catalog():
    return {
        "models": [
            {
                "slug": "gpt-6-luna",
                "multi_agent_version": "v2",
                "supported_reasoning_levels": [{"effort": "max"}],
            }
        ]
    }


class DependencyCheckTests(unittest.TestCase):
    def run_check(self, payload):
        catalog = subprocess_result(stdout=json.dumps(payload).encode())
        version = subprocess_result(stdout="codex-cli 0.156.1\n")
        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.object(check_dependencies.shutil, "which", return_value="codex"), mock.patch.object(
            check_dependencies.subprocess, "run", side_effect=[version, catalog]
        ), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = check_dependencies.main()
        return code, stdout.getvalue(), stderr.getvalue()

    def test_accepts_valid_catalog(self):
        code, output, error = self.run_check(valid_catalog())
        self.assertEqual(code, 0)
        self.assertIn("All prerequisites passed", output)
        self.assertEqual(error, "")

    def test_rejects_malformed_reasoning_entries_without_traceback(self):
        catalog = valid_catalog()
        catalog["models"][0]["supported_reasoning_levels"].append(None)
        code, output, error = self.run_check(catalog)
        self.assertEqual(code, 1)
        self.assertIn("invalid format", error)
        self.assertNotIn("Traceback", error)

    def test_rejects_duplicate_efforts(self):
        catalog = valid_catalog()
        catalog["models"][0]["supported_reasoning_levels"].append({"effort": "max"})
        code, _, error = self.run_check(catalog)
        self.assertEqual(code, 1)
        self.assertIn("duplicate reasoning", error)

    def test_rejects_malformed_model_entry(self):
        catalog = valid_catalog()
        catalog["models"].append(None)
        code, _, error = self.run_check(catalog)
        self.assertEqual(code, 1)
        self.assertIn("malformed model", error)

    def test_reports_codex_start_error_without_traceback(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.object(check_dependencies.shutil, "which", return_value="codex"), mock.patch.object(
            check_dependencies.subprocess, "run", side_effect=PermissionError("blocked")
        ), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = check_dependencies.main()
        self.assertEqual(code, 1)
        self.assertIn("could not be started", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_probe_does_not_forward_api_secret_and_uses_isolated_home(self):
        catalog = subprocess_result(stdout=json.dumps(valid_catalog()).encode())
        version = subprocess_result(stdout="codex-cli 0.156.1\n")
        seen_env = []

        def record_run(*args, **kwargs):
            seen_env.append(kwargs["env"])
            return version if "--version" in args[0] else catalog

        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test-secret", "CODEX_HOME": "/private/codex"}), mock.patch.object(
            check_dependencies.shutil, "which", return_value="codex"
        ), mock.patch.object(check_dependencies.subprocess, "run", side_effect=record_run), contextlib.redirect_stdout(io.StringIO()):
            code = check_dependencies.main()

        self.assertEqual(code, 0)
        self.assertEqual(len(seen_env), 2)
        for env in seen_env:
            self.assertNotIn("OPENAI_API_KEY", env)
            self.assertNotEqual(env["CODEX_HOME"], "/private/codex")


def subprocess_result(stdout=b"", returncode=0):
    return check_dependencies.subprocess.CompletedProcess(args=["codex"], returncode=returncode, stdout=stdout)


if __name__ == "__main__":
    unittest.main()
