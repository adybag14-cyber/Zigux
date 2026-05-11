#!/usr/bin/env python3
"""Fail-close the focused Phase 3 ABI replay route."""

from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


REQUIRED_FILES = (
    Path("Documentation/zigux/phase3-abi-slice.md"),
    Path("Documentation/zigux/phase3-abi-header-family-survey.md"),
    Path("Documentation/zigux/phase3-abi-h-boundary-next-step.md"),
    Path("include/linux/zigux.h"),
    Path("include/zigux/abi.h"),
    Path("zigux/bindings/abi.zig"),
    Path("zigux/kernel/export_shim.zig"),
    Path("zigux/uapi/version.zig"),
    Path("zigux/uapi/dev_t.zig"),
    Path("zigux/tests/phase3_abi.zig"),
    Path("zigux/tests/phase3_low_level_wrappers.zig"),
    Path("zigux/tests/phase3_export_uapi.zig"),
    Path("zigux/tests/phase3_abi_dump.zig"),
    Path("zigux/tests/phase3_export_uapi_layout.zig"),
    Path("zigux/tests/fixtures/phase3_abi/expected.json"),
    Path("zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c"),
    Path("scripts/zigux/validate-phase3.py"),
    Path("scripts/zigux/validate_phase3_selftest.py"),
    Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py"),
    Path("scripts/zigux/check-phase3-policy-byte-guards.py"),
    Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    Path("scripts/zigux/validate-phase3-export-uapi-survey.py"),
    Path("scripts/zigux/validate-phase3-abi-header-family-survey.py"),
    Path("scripts/zigux/validate-phase3-abi-bindings-syntax.py"),
    Path("scripts/zigux/survey-phase3-abi-constant-parity.py"),
)

MAKEFILE_PATH = Path("zigux/Makefile")
MAKE_MARKERS = (
    "phase3-abi:",
    "$(PYTHON) scripts/zigux/check-phase3-abi.py",
    "$(ZIG) build phase3-test --build-file zigux/tests/build.zig",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (repo_root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")

    makefile_path = repo_root / MAKEFILE_PATH
    if not makefile_path.is_file():
        issues.append(f"missing repo file: {MAKEFILE_PATH.as_posix()}")
    else:
        makefile_text = _read(makefile_path)
        for marker in MAKE_MARKERS:
            if marker not in makefile_text:
                issues.append(f"missing make marker: {marker}")

    return issues


def _write(path: Path, text: str = "# stub\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _populate_repo(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        _write(root / rel_path)
    _write(root / MAKEFILE_PATH, "\n".join(MAKE_MARKERS) + "\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_gate_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        case_count += 1

        missing_rel = REQUIRED_FILES[0]
        (root / missing_rel).unlink()
        issues = validate_repo(root)
        expected_missing = f"missing repo file: {missing_rel.as_posix()}"
        if expected_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing repo file was not reported")
            return 1
        case_count += 1

        _write(root / missing_rel)
        _write(
            root / MAKEFILE_PATH,
            "phase3-abi:\n\t$(ZIG) build phase3-test --build-file zigux/tests/build.zig\n",
        )
        issues = validate_repo(root)
        expected_marker = "missing make marker: $(PYTHON) scripts/zigux/check-phase3-abi.py"
        if expected_marker not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing make marker was not reported")
            return 1
        case_count += 1

    print("PHASE3_ABI_SELF_TEST=pass")
    print(f"PHASE3_ABI_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the focused Phase 3 ABI replay route and its core packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 ABI packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_ABI=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / MAKEFILE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
