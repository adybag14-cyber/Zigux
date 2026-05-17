#!/usr/bin/env python3
"""Fail-close the current Phase 3 scripts-root tooling inventory."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SCRIPTS_README_PATH = Path("scripts/zigux/README.md")

REQUIRED_FILES = (
    Path("Documentation/zigux/phase3-abi-slice.md"),
    Path("Documentation/zigux/phase3-errptr-xarray-slice.md"),
    Path("Documentation/zigux/phase3-policy-slice.md"),
    Path("Documentation/zigux/phase3-validator-support-surface.md"),
    Path("Documentation/zigux/phase3-boundary-lane-sequencing.md"),
    Path("scripts/zigux/check-phase3-selftest-surface.py"),
    Path("scripts/zigux/validate-phase3-validator-support-surface.py"),
    Path("scripts/zigux/validate_phase3_selftest.py"),
    Path("scripts/zigux/check-phase3-dev-t-starter-packet.py"),
    Path("scripts/zigux/check-phase3-errptr-xarray-starter-packet.py"),
    Path("scripts/zigux/check-phase3-errptr-xarray.py"),
    Path("scripts/zigux/check-phase3-policy-starter-packet.py"),
    Path("zigux/kernel/export_shim.zig"),
    Path("zigux/helpers/unsafe_policy.zig"),
    Path("zigux/tests/phase3_errptr_xarray_dump.zig"),
    Path("zigux/tests/phase3_errptr_xarray_dump_build.zig"),
    Path("zigux/tests/fixtures/phase3_errptr_xarray/phase3_errptr_xarray_c_harness.c"),
    Path("zigux/tests/fixtures/phase3_errptr_xarray/expected.json"),
    Path("zigux/tests/fixtures/phase3_errptr_xarray_manifest.json"),
    Path("zigux/tests/phase3_policy_starter_packet.zig"),
)

REQUIRED_MARKERS = (
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-errptr-xarray-slice.md",
    "Documentation/zigux/phase3-policy-slice.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "python3 scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test",
    "python3 scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "scripts/zigux/check-phase3-selftest-surface.py",
    "scripts/zigux/validate-phase3-validator-support-surface.py",
    "scripts/zigux/validate_phase3_selftest.py",
    "scripts/zigux/check-phase3-dev-t-starter-packet.py",
    "scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
    "scripts/zigux/check-phase3-errptr-xarray.py",
    "scripts/zigux/check-phase3-policy-starter-packet.py",
    "Documentation/zigux/phase3-boundary-lane-sequencing.md",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "zigux/helpers/unsafe_policy.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/tests/phase3_errptr_xarray_dump.zig",
    "zigux/tests/phase3_errptr_xarray_dump_build.zig",
    "zigux/tests/fixtures/phase3_errptr_xarray/phase3_errptr_xarray_c_harness.c",
    "zigux/tests/fixtures/phase3_errptr_xarray/expected.json",
    "zigux/tests/fixtures/phase3_errptr_xarray_manifest.json",
    "zigux/tests/phase3_policy_starter_packet.zig",
)

FORBIDDEN_MARKERS = (
    "still return missing for `zigux/kernel/export_shim.zig`",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (repo_root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")

    readme_path = repo_root / SCRIPTS_README_PATH
    try:
        readme_text = _read(readme_path)
    except FileNotFoundError:
        return issues + [f"missing repo file: {SCRIPTS_README_PATH.as_posix()}"]

    for marker in REQUIRED_MARKERS:
        if marker not in readme_text:
            issues.append(f"missing scripts README marker: {marker}")
    for marker in FORBIDDEN_MARKERS:
        if marker in readme_text:
            issues.append(f"forbidden scripts README marker: {marker}")
    return issues


def _populate_repo(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        _write(root / rel_path, rel_path.as_posix() + "\n")
    _write(root / SCRIPTS_README_PATH, "\n".join(REQUIRED_MARKERS) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_readme_tooling_inventory_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        readme = root / SCRIPTS_README_PATH
        readme.write_text(_read(readme).replace(REQUIRED_MARKERS[4], "", 1), encoding="utf-8")
        issues = validate_repo(root)
        expected = f"missing scripts README marker: {REQUIRED_MARKERS[4]}"
        if expected not in issues:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected missing README marker was not reported")
            return 1

        _populate_repo(root)
        missing_file = REQUIRED_FILES[-1]
        (root / missing_file).unlink()
        issues = validate_repo(root)
        expected = f"missing repo file: {missing_file.as_posix()}"
        if expected not in issues:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected missing repo file was not reported")
            return 1

        _populate_repo(root)
        readme.write_text(_read(readme) + FORBIDDEN_MARKERS[0] + "\n", encoding="utf-8")
        issues = validate_repo(root)
        expected = f"forbidden scripts README marker: {FORBIDDEN_MARKERS[0]}"
        if expected not in issues:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected forbidden README marker was not reported")
            return 1

    print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass")
    print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 scripts-root tooling inventory."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains scripts/zigux/README.md",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_README_TOOLING_INVENTORY=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / SCRIPTS_README_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())