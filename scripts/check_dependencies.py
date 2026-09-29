#!/usr/bin/env python3
"""Check the non-secret prerequisites for the Luna Ultra installer."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def clean_cli_environment(codex_home: Path) -> dict[str, str]:
    """Run catalog probes with an isolated Codex home and without API secrets."""
    allowed = {
        "HOME", "PATH", "PREFIX", "TMPDIR", "TMP", "TEMP", "LANG", "LC_ALL",
        "TERMUX_VERSION", "ANDROID_DATA", "ANDROID_ROOT", "LD_LIBRARY_PATH", "SHELL",
        "USER", "LOGNAME", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY",
        "http_proxy", "https_proxy", "all_proxy", "no_proxy", "SSL_CERT_FILE", "SSL_CERT_DIR",
    }
    env = {key: value for key, value in os.environ.items() if key in allowed}
    env["CODEX_HOME"] = str(codex_home)
    return env


def main() -> int:
    if sys.version_info < (3, 9):
        return fail("Python 3.9 or newer is required.")
    print(f"Python: {sys.version.split()[0]} (ok)")

    codex = shutil.which("codex")
    if not codex:
        return fail("codex was not found on PATH.")
    try:
        with tempfile.TemporaryDirectory(prefix="codex-luna-ultra-check-") as temp:
            isolated_home = Path(temp) / "codex-home"
            isolated_home.mkdir(mode=0o700)
            env = clean_cli_environment(isolated_home)
            version = subprocess.run(
                [codex, "--version"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                text=True, check=False, timeout=30, env=env,
            )
            if version.returncode != 0:
                return fail("codex --version failed.")
            print(f"Codex: {version.stdout.strip() or 'version unavailable'}")
            catalog = subprocess.run(
                [codex, "debug", "models"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                check=False, timeout=120, env=env,
            )
    except subprocess.TimeoutExpired as exc:
        command = "codex --version" if exc.cmd and "--version" in exc.cmd else "codex debug models"
        return fail(f"{command} timed out.")
    except OSError:
        return fail("Codex prerequisite command could not be started.")
    if catalog.returncode != 0:
        return fail("codex debug models failed; check the Codex CLI and its catalog setup.")
    try:
        payload = json.loads(catalog.stdout)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return fail("codex debug models did not return the expected JSON catalog.")
    models = payload.get("models") if isinstance(payload, dict) else None
    if not isinstance(models, list):
        return fail("the catalog has no models list.")
    if any(not isinstance(model, dict) for model in models):
        return fail("the catalog contains a malformed model entry.")
    slugs = [model.get("slug") for model in models]
    if any(not isinstance(slug, str) or not slug for slug in slugs):
        return fail("the catalog contains an invalid model slug.")
    if len(set(slugs)) != len(slugs):
        return fail("the catalog contains duplicate model slugs.")
    matches = [model for model in models if model.get("slug") == "gpt-6-luna"]
    if len(matches) != 1:
        return fail("the catalog does not contain exactly one gpt-6-luna entry.")
    luna = matches[0]
    levels = luna.get("supported_reasoning_levels")
    if not isinstance(levels, list) or not levels or any(not isinstance(item, dict) for item in levels):
        return fail("gpt-6-luna reasoning levels have an invalid format.")
    efforts = [item.get("effort") for item in levels]
    if any(not isinstance(effort, str) or not effort for effort in efforts):
        return fail("gpt-6-luna reasoning effort values have an invalid format.")
    if len(set(efforts)) != len(efforts):
        return fail("gpt-6-luna has duplicate reasoning effort values.")
    if luna.get("multi_agent_version") != "v2":
        return fail("gpt-6-luna is not advertised as multi_agent_version v2.")
    if "max" not in efforts:
        return fail("gpt-6-luna does not advertise max reasoning.")
    print(f"Catalog: {len(models)} models; Luna v2 with max (ok)")
    print("All prerequisites passed. The installer can now be previewed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
