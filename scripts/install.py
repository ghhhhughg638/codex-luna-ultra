#!/usr/bin/env python3
"""Install a local Luna Ultra profile with optional desktop Codex integration."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import stat
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
PROFILE_TEMPLATE = ROOT / "profiles" / "luna-ultra.config.toml"
CATALOG_NAME = "luna-ultra-models.json"
PROFILE_NAME = "luna-ultra.config.toml"
CONFIG_NAME = "config.toml"
ULTRA_DESCRIPTION = "Maximum reasoning with configured multi-agent support"


class InstallError(Exception):
    pass


def clean_cli_environment(codex_home: Path) -> dict[str, str]:
    """Keep platform runtime variables but avoid forwarding credentials to Codex."""
    allowed_exact = {
        "HOME",
        "PATH",
        "PREFIX",
        "TMPDIR",
        "TMP",
        "TEMP",
        "LANG",
        "LC_ALL",
        "TERMUX_VERSION",
        "ANDROID_DATA",
        "ANDROID_ROOT",
        "LD_LIBRARY_PATH",
        "SHELL",
        "USER",
        "LOGNAME",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "NO_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
        "no_proxy",
        "SSL_CERT_FILE",
        "SSL_CERT_DIR",
    }
    env = {key: value for key, value in os.environ.items() if key in allowed_exact}
    env["CODEX_HOME"] = str(codex_home)
    return env


def read_catalog(codex: str) -> dict:
    with tempfile.TemporaryDirectory(prefix="codex-luna-ultra-source-") as temp:
        isolated_home = Path(temp) / "codex-home"
        isolated_home.mkdir(mode=0o700)
        try:
            result = subprocess.run(
                [codex, "debug", "models"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=clean_cli_environment(isolated_home),
                timeout=180,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise InstallError("Codex catalog query timed out; no files were written.") from exc
        except OSError as exc:
            raise InstallError(f"Could not run Codex catalog query: {exc}; no files were written.") from exc
        if result.returncode != 0:
            raise InstallError(
                f"Codex catalog query failed (exit {result.returncode}); no files were written."
            )
        try:
            catalog = json.loads(result.stdout)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise InstallError("Codex returned an unexpected catalog format; no files were written.") from exc
    return catalog


def add_luna_ultra(catalog: dict) -> dict:
    models = catalog.get("models") if isinstance(catalog, dict) else None
    if not isinstance(models, list) or not models:
        raise InstallError("Catalog has no model list; no files were written.")

    slugs = [model.get("slug") for model in models if isinstance(model, dict)]
    if (
        len(slugs) != len(models)
        or any(not isinstance(slug, str) or not slug for slug in slugs)
        or len(set(slugs)) != len(slugs)
    ):
        raise InstallError("Catalog model entries are invalid or duplicated; no files were written.")

    luna_matches = [model for model in models if model.get("slug") == "gpt-6-luna"]
    if len(luna_matches) != 1:
        raise InstallError("Catalog must contain exactly one gpt-6-luna model; no files were written.")
    luna = luna_matches[0]
    if luna.get("multi_agent_version") != "v2":
        raise InstallError("This Codex catalog does not advertise Luna multi-agent v2; no files were written.")

    levels = luna.get("supported_reasoning_levels")
    if not isinstance(levels, list):
        raise InstallError("Luna reasoning levels are missing; no files were written.")
    efforts = [level.get("effort") for level in levels if isinstance(level, dict)]
    if (
        len(efforts) != len(levels)
        or any(not isinstance(effort, str) or not effort for effort in efforts)
        or len(set(efforts)) != len(efforts)
        or "max" not in efforts
    ):
        raise InstallError("Luna reasoning levels are invalid or do not advertise max; no files were written.")

    ultra = next((level for level in levels if level.get("effort") == "ultra"), None)
    created_ultra = ultra is None
    if ultra is None:
        ultra = {"effort": "ultra", "description": ULTRA_DESCRIPTION}
    else:
        levels.remove(ultra)
    max_index = next(index for index, level in enumerate(levels) if level["effort"] == "max")
    levels.insert(max_index + 1, ultra)

    if created_ultra:
        luna["multi_agent_reasoning_effort"] = "max"
    else:
        luna.setdefault("multi_agent_reasoning_effort", "max")
    return catalog


def verify_profile(profile_text: str, catalog_text: str, codex: str) -> None:
    with tempfile.TemporaryDirectory(prefix="codex-luna-ultra-verify-") as temp:
        home = Path(temp) / "codex-home"
        home.mkdir(mode=0o700)
        (home / CATALOG_NAME).write_text(catalog_text, encoding="utf-8")
        (home / PROFILE_NAME).write_text(profile_text, encoding="utf-8")
        os.chmod(home / CATALOG_NAME, 0o600)
        os.chmod(home / PROFILE_NAME, 0o600)
        try:
            result = subprocess.run(
                [codex, "--profile", "luna-ultra", "debug", "prompt-input", "catalog profile validation"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=clean_cli_environment(home),
                timeout=180,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise InstallError("Profile validation timed out; no files were written.") from exc
        except OSError as exc:
            raise InstallError(f"Could not run Codex profile validation: {exc}; no files were written.") from exc
        if result.returncode != 0:
            raise InstallError(
                f"Codex rejected the generated profile (exit {result.returncode}); no files were written."
            ) from None
        try:
            json.loads(result.stdout)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise InstallError("Profile validation returned unexpected output; no files were written.") from exc


def merge_desktop_config(config_text: str) -> str:
    """Add the local catalog and multi-agent flag without rewriting other settings."""
    newline = "\r\n" if "\r\n" in config_text else "\n"
    had_trailing_newline = config_text.endswith(("\n", "\r"))
    lines = config_text.splitlines()

    def section_end(start: int) -> int:
        for index in range(start + 1, len(lines)):
            stripped = lines[index].strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                return index
        return len(lines)

    root_end = len(lines)
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            root_end = index
            break

    catalog_setting = f'model_catalog_json = "{CATALOG_NAME}"'
    catalog_matches = [
        index
        for index in range(root_end)
        if re.match(r"^\s*model_catalog_json\s*=", lines[index])
    ]
    if len(catalog_matches) > 1:
        raise InstallError("config.toml has duplicate root model_catalog_json settings; no files were written.")
    if catalog_matches:
        lines[catalog_matches[0]] = catalog_setting
    else:
        lines.insert(root_end, catalog_setting)

    feature_header = next(
        (index for index, line in enumerate(lines) if line.strip() == "[features]"),
        None,
    )
    if feature_header is None:
        if lines and lines[-1].strip():
            lines.append("")
        lines.extend(["[features]", "multi_agent = true"])
    else:
        feature_end = section_end(feature_header)
        feature_matches = [
            index
            for index in range(feature_header + 1, feature_end)
            if re.match(r"^\s*multi_agent\s*=", lines[index])
        ]
        if len(feature_matches) > 1:
            raise InstallError("config.toml has duplicate features.multi_agent settings; no files were written.")
        if feature_matches:
            lines[feature_matches[0]] = "multi_agent = true"
        else:
            lines.insert(feature_header + 1, "multi_agent = true")

    merged = newline.join(lines)
    if had_trailing_newline or not config_text:
        merged += newline
    return merged


def stage_file(path: Path, content: bytes) -> Path:
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as stream:
            fd = -1
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        return temp_path
    except BaseException:
        if fd >= 0:
            try:
                os.close(fd)
            except OSError:
                pass
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def transactional_write(files: dict[Path, bytes], force: bool) -> list[tuple[Path, Path]]:
    staged: dict[Path, Path] = {}
    replaced: list[Path] = []
    backups: list[tuple[Path, Path]] = []
    try:
        for target, content in files.items():
            staged[target] = stage_file(target, content)
        if force:
            backups = backup_existing(list(files))
        for target, temp_path in staged.items():
            if target.exists() and not force:
                raise InstallError(f"Target appeared during installation: {target}")
            if target.is_symlink():
                raise InstallError(f"Refusing to replace a symbolic-link target: {target}")
            os.replace(temp_path, target)
            replaced.append(target)
            os.chmod(target, 0o600)
        return backups
    except BaseException:
        rollback_errors = []
        for target in reversed(replaced):
            backup = dict(backups).get(target)
            try:
                if backup is not None:
                    restore_temp = stage_file(target, backup.read_bytes())
                    os.replace(restore_temp, target)
                    os.chmod(target, 0o600)
                else:
                    target.unlink(missing_ok=True)
            except OSError as exc:
                rollback_errors.append(f"{target}: {exc}")
        if rollback_errors:
            backup_paths = ", ".join(str(path) for _, path in backups)
            raise InstallError(
                "Installation failed and rollback was incomplete. "
                f"Recovery backups are at: {backup_paths}. Errors: {'; '.join(rollback_errors)}"
            )
        raise
    finally:
        for temp_path in staged.values():
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass


def backup_existing(paths: list[Path]) -> list[tuple[Path, Path]]:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    prepared: list[tuple[Path, Path]] = []
    for path in paths:
        if not path.exists() and not path.is_symlink():
            continue
        if path.is_symlink() or not path.is_file():
            raise InstallError(f"Refusing to replace a non-regular target: {path}")
        backup = path.with_name(f"{path.name}.{stamp}-{secrets.token_hex(4)}.bak")
        prepared.append((path, backup))

    backups = []
    try:
        for path, backup in prepared:
            source_flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0)
            source_flags |= getattr(os, "O_NOFOLLOW", 0)
            source_fd = -1
            backup_fd = -1
            try:
                source_fd = os.open(path, source_flags)
                if not stat.S_ISREG(os.fstat(source_fd).st_mode):
                    raise InstallError(f"Refusing to back up a non-regular target: {path}")
                backup_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
                backup_flags |= getattr(os, "O_NOFOLLOW", 0)
                backup_fd = os.open(backup, backup_flags, 0o600)
                backups.append((path, backup))
                source = os.fdopen(source_fd, "rb")
                source_fd = -1
                destination = os.fdopen(backup_fd, "wb")
                backup_fd = -1
                with source, destination:
                    shutil.copyfileobj(source, destination)
                    destination.flush()
                    os.fsync(destination.fileno())
                os.chmod(backup, 0o600)
            finally:
                if source_fd >= 0:
                    os.close(source_fd)
                if backup_fd >= 0:
                    os.close(backup_fd)
    except BaseException:
        for _, backup in backups:
            try:
                backup.unlink(missing_ok=True)
            except OSError:
                pass
        raise
    return backups


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write profile and generated catalog")
    parser.add_argument("--force", action="store_true", help="back up and replace existing targets")
    parser.add_argument("--code-home", help="absolute Codex home (defaults to CODEX_HOME or ~/.codex)")
    parser.add_argument(
        "--desktop",
        action="store_true",
        help="also wire the generated catalog into the Windows Codex desktop config",
    )
    args = parser.parse_args()

    if args.force and not args.apply:
        parser.error("--force requires --apply")
    os.umask(0o077)
    codex = shutil.which("codex")
    if not codex:
        raise InstallError("codex was not found on PATH.")
    if not PROFILE_TEMPLATE.is_file():
        raise InstallError("The profile template is missing from this repository.")

    if args.code_home is not None and not args.code_home.strip():
        raise InstallError("--code-home must not be empty.")
    env_home = os.environ.get("CODEX_HOME")
    if args.code_home is None and env_home == "":
        raise InstallError("CODEX_HOME is set to an empty value; unset it or provide --code-home.")
    configured_home = Path(args.code_home) if args.code_home is not None else Path(env_home or (Path.home() / ".codex"))
    home = configured_home.expanduser()
    if not home.is_absolute():
        raise InstallError("Codex home must be an absolute path; relative paths are refused.")
    if home.is_symlink():
        raise InstallError("Refusing to install into a symbolic-link CODEX_HOME.")
    catalog_path = home / CATALOG_NAME
    profile_path = home / PROFILE_NAME
    config_path = home / CONFIG_NAME
    targets = [catalog_path, profile_path]
    if args.desktop:
        targets.append(config_path)
    existing = [path for path in targets if path.exists() or path.is_symlink()]
    if existing and args.apply and not args.force:
        listed = ", ".join(str(path) for path in existing)
        raise InstallError(f"Target already exists; nothing was changed: {listed}. Use --apply --force to back up and replace.")
    if any(path.is_symlink() for path in existing):
        raise InstallError("Refusing to replace a symbolic-link target.")
    if any(path.exists() and not path.is_file() for path in existing):
        raise InstallError("Refusing to replace a non-regular installation target.")

    desktop_config_text = ""
    if args.desktop and config_path.exists():
        try:
            desktop_config_text = merge_desktop_config(config_path.read_text(encoding="utf-8"))
        except UnicodeDecodeError as exc:
            raise InstallError("config.toml is not valid UTF-8; no files were written.") from exc
    elif args.desktop:
        desktop_config_text = merge_desktop_config("")

    catalog = add_luna_ultra(read_catalog(codex))
    catalog_text = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
    profile_text = PROFILE_TEMPLATE.read_text(encoding="utf-8")
    verify_profile(profile_text, catalog_text, codex)

    if not args.apply:
        print("Validated the current Codex catalog and Luna Ultra profile.")
        if existing:
            print("Would replace existing targets only with --apply --force (backups are created first):")
        else:
            print("Would write (mode 0600):")
        for path in targets:
            print(f"  {path}")
        if args.desktop:
            print("Desktop mode would add model_catalog_json and features.multi_agent to config.toml.")
        print("No files were changed. Re-run with --apply to install.")
        return 0

    home.mkdir(parents=True, exist_ok=True, mode=0o700)
    if home.is_symlink():
        raise InstallError("Refusing to install into a symbolic-link CODEX_HOME.")
    files = {
        catalog_path: catalog_text.encode("utf-8"),
        profile_path: profile_text.encode("utf-8"),
    }
    if args.desktop:
        files[config_path] = desktop_config_text.encode("utf-8")
    backups = transactional_write(files, force=args.force)
    if backups:
        print("Backups created:")
        for original, backup in backups:
            print(f"  {original.name} -> {backup.name}")
    print(f"Installed Luna Ultra profile and catalog under {home}.")
    if args.desktop:
        print(f"Updated desktop Codex config: {config_path}")
        print("Restart the Codex desktop app before using the Luna Ultra menu.")
    else:
        print("Start with: codex -p luna-ultra")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except InstallError as exc:
        print(f"install: {exc}", file=sys.stderr)
        raise SystemExit(1)
    except OSError as exc:
        print(f"install: filesystem or process error: {exc}", file=sys.stderr)
        raise SystemExit(1)
