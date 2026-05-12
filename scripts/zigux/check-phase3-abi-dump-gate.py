#!/usr/bin/env python3
"""Fail-close the focused Phase 3 ABI dump and interop-gate reminder surface."""

from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


SLICE_NOTE_PATH = Path("Documentation/zigux/phase3-abi-slice.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
VALIDATE_PHASE3_PATH = Path("scripts/zigux/validate-phase3.py")
SELFTEST_DRIVER_PATH = Path("scripts/zigux/validate_phase3_selftest.py")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_PACKET_FILES = (
    Path("zigux/tests/phase3_abi_dump.zig"),
    Path("zigux/tests/fixtures/phase3_abi/expected.json"),
    Path("zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c"),
)

SLICE_NOTE_MARKERS = (
    "scripts/zigux/check-phase3-abi-dump-gate.py",
    "python3 scripts/zigux/check-phase3-abi-dump-gate.py --self-test",
    "python3 scripts/zigux/check-phase3-abi-dump-gate.py",
    "zigux/tests/phase3_abi_dump.zig",
    "zigux/tests/fixtures/phase3_abi/expected.json",
    "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c",
    "zig build phase3-dump --build-file zigux/tests/build.zig",
    "PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig",
)

TESTS_README_MARKERS = (
    "scripts/zigux/check-phase3-abi-dump-gate.py",
    "zigux/tests/phase3_abi_dump.zig",
    "zigux/tests/fixtures/phase3_abi/expected.json",
    "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c",
)

SCRIPTS_README_MARKERS = (
    "check-phase3-abi-dump-gate.py",
    "zig build phase3-dump --build-file zigux/tests/build.zig",
    "make -C zigux phase3-validate",
    "make -C zigux phase3",
)

VALIDATE_PHASE3_MARKERS = (
    'Path("zigux/tests/phase3_abi_dump.zig")',
    'Path("zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c")',
    'Path("zigux/tests/fixtures/phase3_abi/expected.json")',
    'Path("scripts/zigux/check-phase3-abi-dump-gate.py")',
)

SELFTEST_DRIVER_MARKERS = (
    'Path("scripts/zigux/check-phase3-abi-dump-gate.py"), ("--self-test",)',
)

MAKEFILE_MARKERS = (
    "phase3-validate:",
    "$(PYTHON) scripts/zigux/check-phase3-abi-dump-gate.py --self-test",
    "$(PYTHON) scripts/zigux/check-phase3-abi-dump-gate.py",
    "phase3-interop:",
    "$(PYTHON) scripts/zigux/run-phase3-checks.py",
    "$(ZIG) build phase3-dump --build-file zigux/tests/build.zig",
)

WORKFLOW_MARKERS = (
    "run: python3 scripts/zigux/run-phase3-checks.py",
    "run: zig build phase3-dump --build-file zigux/tests/build.zig",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _check_markers(path: Path, markers: tuple[str, ...], label: str) -> list[str]:
    try:
        text = _read(path)
    except FileNotFoundError:
        return [f"missing repo file: {path.as_posix()}"]
    return [f"missing {label} marker: {marker}" for marker in markers if marker not in text]


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    issues.extend(_check_markers(repo_root / SLICE_NOTE_PATH, SLICE_NOTE_MARKERS, "slice note"))
    issues.extend(_check_markers(repo_root / TESTS_README_PATH, TESTS_README_MARKERS, "tests README"))
    issues.extend(
        _check_markers(repo_root / SCRIPTS_README_PATH, SCRIPTS_README_MARKERS, "scripts README")
    )
    issues.extend(
        _check_markers(repo_root / VALIDATE_PHASE3_PATH, VALIDATE_PHASE3_MARKERS, "phase3 validator")
    )
    issues.extend(
        _check_markers(
            repo_root / SELFTEST_DRIVER_PATH,
            SELFTEST_DRIVER_MARKERS,
            "phase3 selftest driver",
        )
    )
    issues.extend(_check_markers(repo_root / MAKEFILE_PATH, MAKEFILE_MARKERS, "makefile"))
    issues.extend(_check_markers(repo_root / WORKFLOW_PATH, WORKFLOW_MARKERS, "workflow"))
    for rel_path in REQUIRED_PACKET_FILES:
        if not (repo_root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")
    return issues


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _populate_repo(root: Path) -> None:
    _write(root / SLICE_NOTE_PATH, "\n".join(SLICE_NOTE_MARKERS) + "\n")
    _write(root / TESTS_README_PATH, "\n".join(TESTS_README_MARKERS) + "\n")
    _write(root / SCRIPTS_README_PATH, "\n".join(SCRIPTS_README_MARKERS) + "\n")
    _write(root / VALIDATE_PHASE3_PATH, "\n".join(VALIDATE_PHASE3_MARKERS) + "\n")
    _write(root / SELFTEST_DRIVER_PATH, "\n".join(SELFTEST_DRIVER_MARKERS) + "\n")
    _write(root / MAKEFILE_PATH, "\n".join(MAKEFILE_MARKERS) + "\n")
    _write(root / WORKFLOW_PATH, "\n".join(WORKFLOW_MARKERS) + "\n")
    for rel_path in REQUIRED_PACKET_FILES:
        _write(root / rel_path, "# stub\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_dump_gate_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        case_count += 1

        broken = root / SLICE_NOTE_PATH
        broken.write_text(
            _read(broken).replace(
                "python3 scripts/zigux/check-phase3-abi-dump-gate.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "missing slice note marker: "
            "python3 scripts/zigux/check-phase3-abi-dump-gate.py --self-test"
        )
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing slice-note dump-gate marker was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        broken = root / TESTS_README_PATH
        broken.write_text(
            _read(broken).replace("zigux/tests/phase3_abi_dump.zig\n", "", 1),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = "missing tests README marker: zigux/tests/phase3_abi_dump.zig"
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing tests README dump marker was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        broken = root / VALIDATE_PHASE3_PATH
        broken.write_text(
            _read(broken).replace('Path("scripts/zigux/check-phase3-abi-dump-gate.py")\n', "", 1),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = 'missing phase3 validator marker: Path("scripts/zigux/check-phase3-abi-dump-gate.py")'
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing validator dump-gate marker was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        broken = root / SELFTEST_DRIVER_PATH
        broken.write_text(
            _read(broken).replace(
                'Path("scripts/zigux/check-phase3-abi-dump-gate.py"), ("--self-test",)\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            'missing phase3 selftest driver marker: '
            'Path("scripts/zigux/check-phase3-abi-dump-gate.py"), ("--self-test",)'
        )
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing selftest-driver dump-gate marker was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        broken = root / MAKEFILE_PATH
        broken.write_text(
            _read(broken).replace(
                "$(PYTHON) scripts/zigux/check-phase3-abi-dump-gate.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "missing makefile marker: "
            "$(PYTHON) scripts/zigux/check-phase3-abi-dump-gate.py --self-test"
        )
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing makefile dump-gate self-test marker was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        broken = root / MAKEFILE_PATH
        broken.write_text(
            _read(broken).replace("phase3-interop:\n", "", 1),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = "missing makefile marker: phase3-interop:"
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing makefile interop target was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        broken = root / WORKFLOW_PATH
        broken.write_text(
            _read(broken).replace("run: python3 scripts/zigux/run-phase3-checks.py\n", "", 1),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = "missing workflow marker: run: python3 scripts/zigux/run-phase3-checks.py"
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing workflow interop replay marker was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        missing_packet_file = REQUIRED_PACKET_FILES[0]
        (root / missing_packet_file).unlink()
        issues = validate_repo(root)
        expected = f"missing repo file: {missing_packet_file.as_posix()}"
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing dump packet file was not reported")
            return 1
        case_count += 1

    print("PHASE3_ABI_DUMP_GATE_SELF_TEST=pass")
    print(f"PHASE3_ABI_DUMP_GATE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the focused Phase 3 ABI dump-gate reminder surface."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the shared Phase 3 ABI dump packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_ABI_DUMP_GATE=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / SLICE_NOTE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())