#!/usr/bin/env python3
"""Check the non-secret prerequisites for the Luna Ultra installer."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def main() -> int:
    if sys.version_info < (3, 9):
        return fail("Python 3.9 or newer is required.")
    print(f"Python: {sys.version.split()[0]} (ok)")

    codex = shutil.which("codex")
    if not codex:
        return fail("codex was not found on PATH.")
    version = subprocess.run(
        [codex, "--version"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=False
    )
    if version.returncode != 0:
        return fail("codex --version failed.")
    print(f"Codex: {version.stdout.strip() or 'version unavailable'}")

    catalog = subprocess.run(
        [codex, "debug", "models"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False
    )
    if catalog.returncode != 0:
        return fail("codex debug models failed; check Codex setup and provider access.")
    try:
        payload = json.loads(catalog.stdout)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return fail("codex debug models did not return the expected JSON catalog.")
    models = payload.get("models") if isinstance(payload, dict) else None
    if not isinstance(models, list):
        return fail("the catalog has no models list.")
    matches = [model for model in models if isinstance(model, dict) and model.get("slug") == "gpt-6-luna"]
    if len(matches) != 1:
        return fail("the catalog does not contain exactly one gpt-6-luna entry.")
    luna = matches[0]
    levels = luna.get("supported_reasoning_levels")
    efforts = [item.get("effort") for item in levels] if isinstance(levels, list) else []
    if luna.get("multi_agent_version") != "v2":
        return fail("gpt-6-luna is not advertised as multi_agent_version v2.")
    if "max" not in efforts:
        return fail("gpt-6-luna does not advertise max reasoning.")
    print(f"Catalog: {len(models)} models; Luna v2 with max (ok)")
    print("All prerequisites passed. The installer can now be previewed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
