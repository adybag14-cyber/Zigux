#!/usr/bin/env python3
"""Fail closed if validate-phase11.py's manifest roster drifts from its required paths."""

from __future__ import annotations

import argparse
import ast
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent
TARGET_PATH = Path("scripts/zigux/validate-phase11.py")


class CheckError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def assignment_literal(module: ast.Module, name: str) -> object:
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
    raise CheckError(f"missing assignment: {name}")


def parse_validate_phase11(validate_path: Path) -> tuple[tuple[str, ...], dict[str, str]]:
    text = read_text(validate_path)
    try:
        module = ast.parse(text, filename=str(validate_path))
    except SyntaxError as exc:
        raise CheckError(f"invalid Python in {validate_path}: {exc}") from exc

    required_paths = assignment_literal(module, "REQUIRED_PATHS")
    manifest_expectations = assignment_literal(module, "MANIFEST_EXPECTATIONS")

    if not isinstance(required_paths, tuple) or any(not isinstance(item, str) for item in required_paths):
        raise CheckError("REQUIRED_PATHS must be a tuple of strings")
    if not isinstance(manifest_expectations, dict):
        raise CheckError("MANIFEST_EXPECTATIONS must be a dict")
    if any(not isinstance(key, str) or not isinstance(value, str) for key, value in manifest_expectations.items()):
        raise CheckError("MANIFEST_EXPECTATIONS must map strings to strings")

    return required_paths, manifest_expectations


def is_phase11_manifest_path(path: str) -> bool:
    return path.startswith("zigux/tests/phase11_") and path.endswith("_manifest.json")


def run_check(root: Path) -> tuple[int, int]:
    validate_path = root / TARGET_PATH
    required_paths, manifest_expectations = parse_validate_phase11(validate_path)

    missing_manifest_paths = sorted(set(manifest_expectations) - set(required_paths))
    if missing_manifest_paths:
        raise CheckError(
            "manifest expectations missing from REQUIRED_PATHS: "
            + ", ".join(missing_manifest_paths)
        )

    missing_expectation_paths = sorted(
        path
        for path in required_paths
        if is_phase11_manifest_path(path) and path not in manifest_expectations
    )
    if missing_expectation_paths:
        raise CheckError(
            "required Phase 11 manifest paths missing from MANIFEST_EXPECTATIONS: "
            + ", ".join(missing_expectation_paths)
        )

    return len(required_paths), len(manifest_expectations)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path, *, include_drift: bool, include_orphan_required_manifest: bool = False) -> None:
    manifest_lines = [
        '    "zigux/tests/phase11_bcm2835_wdt_manifest.json": "P11-L08",',
        '    "zigux/tests/phase11_dw_wdt_manifest.json": "P11-L10",',
    ]
    required_paths = [
        '    "zigux/tests/phase11_bcm2835_wdt_manifest.json",',
        '    "zigux/tests/phase11_dw_wdt_manifest.json",',
    ]
    if include_drift:
        manifest_lines.append(
            '    "zigux/tests/phase11_hvc_console_manifest.json": "P11-L16",'
        )
    if include_orphan_required_manifest:
        required_paths.append(
            '    "zigux/tests/phase11_gpio_wdt_manifest.json",'
        )

    text = "\n".join(
        [
            "REQUIRED_PATHS = (",
            *required_paths,
            ")",
            "",
            "MANIFEST_EXPECTATIONS = {",
            *manifest_lines,
            "}",
            "",
        ]
    )
    write(root / TARGET_PATH, text)


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix="phase11_validate_manifest_roster_"))
    try:
        passing = tempdir / "passing"
        build_fixture(passing, include_drift=False)
        required_path_count, manifest_count = run_check(passing)
        if manifest_count != 2:
            raise AssertionError(f"unexpected manifest count: {manifest_count}")

        default_root_cli = tempdir / "default_root_cli"
        build_fixture(default_root_cli, include_drift=False)
        write(default_root_cli / "scripts/zigux/check-phase11-validate-manifest-roster.py", read_text(SELF_PATH))
        completed = subprocess.run(
            [sys.executable, str(default_root_cli / "scripts/zigux/check-phase11-validate-manifest-roster.py")],
            cwd=default_root_cli,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise AssertionError(
                "default-root CLI invocation failed: "
                f"stdout={completed.stdout!r} stderr={completed.stderr!r}"
            )
        if "PHASE11_VALIDATE_MANIFEST_ROSTER=pass" not in completed.stdout:
            raise AssertionError(
                "default-root CLI invocation did not report pass: "
                f"stdout={completed.stdout!r} stderr={completed.stderr!r}"
            )

        missing = tempdir / "missing"
        build_fixture(missing, include_drift=True)
        expect_failure(
            missing,
            "manifest expectations missing from REQUIRED_PATHS",
        )

        orphan_required_manifest = tempdir / "orphan_required_manifest"
        build_fixture(orphan_required_manifest, include_drift=False, include_orphan_required_manifest=True)
        expect_failure(
            orphan_required_manifest,
            "required Phase 11 manifest paths missing from MANIFEST_EXPECTATIONS",
        )

        syntax_error = tempdir / "syntax_error"
        write(syntax_error / TARGET_PATH, "REQUIRED_PATHS = (\n")
        expect_failure(syntax_error, "invalid Python")

        missing_assignment = tempdir / "missing_assignment"
        write(missing_assignment / TARGET_PATH, "REQUIRED_PATHS = ()\n")
        expect_failure(missing_assignment, "missing assignment: MANIFEST_EXPECTATIONS")

        wrong_required_type = tempdir / "wrong_required_type"
        write(
            wrong_required_type / TARGET_PATH,
            "REQUIRED_PATHS = []\nMANIFEST_EXPECTATIONS = {}\n",
        )
        expect_failure(wrong_required_type, "REQUIRED_PATHS must be a tuple of strings")

        wrong_manifest_type = tempdir / "wrong_manifest_type"
        write(
            wrong_manifest_type / TARGET_PATH,
            "REQUIRED_PATHS = ()\nMANIFEST_EXPECTATIONS = []\n",
        )
        expect_failure(wrong_manifest_type, "MANIFEST_EXPECTATIONS must be a dict")

        print("PHASE11_VALIDATE_MANIFEST_ROSTER_SELF_TEST=pass")
        print("PHASE11_VALIDATE_MANIFEST_ROSTER_SELF_TEST_CASE_COUNT=8")
        print(f"PHASE11_VALIDATE_MANIFEST_ROSTER_FIXTURE_REQUIRED_PATH_COUNT={required_path_count}")
        return 0
    finally:
        shutil.rmtree(tempdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        required_path_count, manifest_count = run_check(args.root.resolve())
    except CheckError as exc:
        print(f"PHASE11_VALIDATE_MANIFEST_ROSTER=fail: {exc}")
        return 1

    print("PHASE11_VALIDATE_MANIFEST_ROSTER=pass")
    print(f"PHASE11_VALIDATE_MANIFEST_ROSTER_REQUIRED_PATH_COUNT={required_path_count}")
    print(f"PHASE11_VALIDATE_MANIFEST_ROSTER_MANIFEST_COUNT={manifest_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
