#!/usr/bin/env python3
"""Synchronize a self-contained Hi3861 SDK snapshot and rebuild its indexes."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import uuid
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = SKILL_ROOT / "references" / "source"
EXCLUDED_DIRS = {"out", "build_tmp", "__pycache__", ".git", ".cache", ".pytest_cache"}
EXCLUDED_SUFFIXES = {".o", ".obj", ".pyc", ".pyo"}


def validate_source_destination(source: Path, destination: Path) -> None:
    destination_resolved = destination.resolve()
    allowed_root = SOURCE_ROOT.resolve()
    if destination_resolved == allowed_root or allowed_root not in destination_resolved.parents:
        raise ValueError(f"Unsafe mirror destination: {destination_resolved}")

    input_resolved = source.resolve(strict=True)
    if input_resolved == destination_resolved:
        raise ValueError("SDK source and bundled destination must be different directories")
    if input_resolved in destination_resolved.parents:
        raise ValueError("Bundled destination must not be nested inside the SDK source")
    if destination_resolved in input_resolved.parents:
        raise ValueError("SDK source must not be nested inside the bundled destination")


def ignore_entries(directory: str, names: list[str]) -> set[str]:
    ignored = set()
    for name in names:
        path = Path(directory) / name
        if path.is_dir() and name in EXCLUDED_DIRS:
            ignored.add(name)
        elif path.is_file() and path.suffix.lower() in EXCLUDED_SUFFIXES:
            ignored.add(name)
    return ignored


def mirror_tree(source: Path, destination: Path) -> None:
    if not source.is_dir():
        raise FileNotFoundError(source)
    validate_source_destination(source, destination)
    shutil.copytree(source, destination, ignore=ignore_entries, copy_function=shutil.copy2)


def run_script(name: str, *args: str) -> None:
    script = Path(__file__).with_name(name)
    subprocess.run([sys.executable, str(script), *args], check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk-root", required=True, type=Path)
    args = parser.parse_args()

    sdk_source = args.sdk_root.resolve(strict=True)
    sdk_destination = SOURCE_ROOT / "sdk"
    validate_source_destination(sdk_source, sdk_destination)

    SOURCE_ROOT.mkdir(parents=True, exist_ok=True)
    nonce = uuid.uuid4().hex
    staging = SOURCE_ROOT / f".sdk-staging-{nonce}"
    backup = SOURCE_ROOT / f".sdk-backup-{nonce}"
    replaced_existing = False

    try:
        mirror_tree(sdk_source, staging)
        if sdk_destination.exists():
            sdk_destination.rename(backup)
            replaced_existing = True
        staging.rename(sdk_destination)

        run_script("build_indexes.py")
        run_script("validate_hi3861_skill.py")
    except BaseException:
        if sdk_destination.exists():
            shutil.rmtree(sdk_destination)
        if replaced_existing and backup.exists():
            backup.rename(sdk_destination)
            try:
                run_script("build_indexes.py")
            except (OSError, subprocess.SubprocessError) as restore_error:
                print(f"WARNING: restored SDK snapshot but could not rebuild indexes: {restore_error}", file=sys.stderr)
        raise
    finally:
        if staging.exists():
            shutil.rmtree(staging)

    if backup.exists():
        shutil.rmtree(backup)

    print(f"Synchronized and validated SDK snapshot at {sdk_destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
