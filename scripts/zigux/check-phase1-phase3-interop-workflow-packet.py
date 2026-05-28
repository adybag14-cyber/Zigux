#!/usr/bin/env python3
"""Guard the current Phase 1 closure-to-Phase 3 interop workflow packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
PHASE3_SELFTEST_REL = Path("scripts/zigux/validate_phase3_selftest.py")
PHASE3_RUNNER_REL = Path("scripts/zigux/run-phase3-checks.py")
EXPORT_SMOKE_REL = Path("scripts/zigux/check-phase3-export-uapi-c-header-smoke.py")
BUILD_ZIG_REL = Path("zigux/tests/build.zig")

REQUIRED_FILES = (
    WORKFLOW_REL,
    CLOSURE_VALIDATOR_REL,
    PHASE3_SELFTEST_REL,
    PHASE3_RUNNER_REL,
    EXPORT_SMOKE_REL,
    BUILD_ZIG_REL,
)

WORKFLOW_PACKET_STEPS = (
    (
        "Self-test current Phase 1 closure validator",
        "python3 scripts/zigux/validate-phase1-closure.py --self-test",
    ),
    (
        "Check current Phase 1 closure packet",
        "python3 scripts/zigux/validate-phase1-closure.py",
    ),
    (
        "Self-test current Phase 3 interop packet",
        "python3 scripts/zigux/validate_phase3_selftest.py",
    ),
    (
        "Check current Phase 3 interop packet",
        "python3 scripts/zigux/run-phase3-checks.py",
    ),
    (
        "Run current Phase 3 export/UAPI C header smoke",
        "python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
    ),
    (
        "Run current Phase 3 shared tests-root packet",
        "zig build phase3-test --build-file zigux/tests/build.zig",
    ),
    (
        "Run current Phase 3 ABI dump replay",
        "zig build phase3-dump --build-file zigux/tests/build.zig",
    ),
)

EXACT_MARKERS = {
    str(CLOSURE_VALIDATOR_REL): (
        '(SHARED_REMINDER_CHECKER_REL, "phase1-shared-reminder-packet"),',
        'print("PHASE1_CLOSURE_SELF_TEST=pass")',
        'print("PHASE1_CLOSURE_VALIDATION=pass")',
    ),
    str(PHASE3_SELFTEST_REL): (
        '"""Run the current bounded Phase 3 interop self-test packet."""',
        'Path("scripts/zigux/run-phase3-checks.py"),',
        'print("PHASE3_VALIDATE_SELFTEST=pass")',
    ),
    str(PHASE3_RUNNER_REL): (
        '"""Run the current bounded Phase 3 validator packet."""',
        'Path("scripts/zigux/validate_phase3_selftest.py"),',
        'print("PHASE3_CHECK_RUNNER=pass")',
    ),
    str(EXPORT_SMOKE_REL): (
        '"""Compile and run the current Phase 3 export/UAPI C header smoke."""',
        'SMOKE_PATH = Path("zigux/tests/phase3_export_uapi_c_header_smoke.c")',
        'print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE=pass")',
    ),
    str(BUILD_ZIG_REL): (
        'const phase3_test_step = b.step(',
        'const phase3_dump_step = b.step(',
        '.name = "phase3-abi-dump",',
        '"Run the current shared Phase 3 starter packet bundle from zigux/tests",',
        '"Dump the current shared Phase 3 ABI snapshot from zigux/tests",',
    ),
}

FORBIDDEN_WORKFLOW_LINES = (
    "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    "run: python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_line_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_absent_line_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker)
    return [] if count == 0 else [f"{label}:expected=0:actual={count}"]


def workflow_step_block(step_name: str, run_command: str) -> str:
    return f"      - name: {step_name}\n        run: {run_command}"


def collect_workflow_failures(text: str) -> list[str]:
    failures: list[str] = []
    positions: list[int] = []
    step_names = [line[len("      - name: ") :] for line in text.splitlines() if line.startswith("      - name: ")]

    for step_name, run_command in WORKFLOW_PACKET_STEPS:
        block = workflow_step_block(step_name, run_command)
        count = text.count(block)
        if count != 1:
            failures.append(f"workflow_pair:{step_name}:expected=1:actual={count}")
            continue
        positions.append(text.index(block))

        name_count = sum(1 for current in step_names if current == step_name)
        if name_count != 1:
            failures.append(f"workflow_step_name:{step_name}:expected=1:actual={name_count}")

    if failures:
        return failures

    if positions != sorted(positions):
        failures.append("workflow_order:expected=strictly_increasing:actual=out_of_order")

    expected_chain = tuple(step_name for step_name, _ in WORKFLOW_PACKET_STEPS)
    width = len(expected_chain)
    if not any(tuple(step_names[idx : idx + width]) == expected_chain for idx in range(len(step_names) - width + 1)):
        failures.append("workflow_chain:expected=adjacent_phase3_interop_packet:actual=split_or_interleaved")

    for marker in FORBIDDEN_WORKFLOW_LINES:
        failures.extend(require_absent_line_occurrence(text, f"{WORKFLOW_REL.as_posix()}:{marker}", marker))

    return failures


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    workflow_text = read_text(root, WORKFLOW_REL)
    failures.extend(collect_workflow_failures(workflow_text))

    for relative_path, markers in EXACT_MARKERS.items():
        text = read_text(root, Path(relative_path))
        for marker in markers:
            failures.extend(require_exact_occurrence(text, f"{relative_path}:{marker}", marker))

    return failures


def build_sample_repo(root: Path) -> None:
    write_text(
        root,
        WORKFLOW_REL,
        "\n".join(workflow_step_block(step_name, run_command) for step_name, run_command in WORKFLOW_PACKET_STEPS) + "\n",
    )
    for relative_path, markers in EXACT_MARKERS.items():
        write_text(root, Path(relative_path), "\n".join(markers) + "\n")


def remove_marker(root: Path, relative_path: Path, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def duplicate_marker(root: Path, relative_path: Path, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def remove_workflow_step(root: Path, step_name: str, run_command: str) -> None:
    path = root / WORKFLOW_REL
    block = workflow_step_block(step_name, run_command)
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(block + "\n", "", 1), encoding="utf-8")


def duplicate_workflow_step(root: Path, step_name: str, run_command: str) -> None:
    path = root / WORKFLOW_REL
    block = workflow_step_block(step_name, run_command)
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(block, block + "\n" + block, 1), encoding="utf-8")


def reorder_workflow(root: Path) -> None:
    path = root / WORKFLOW_REL
    steps = list(WORKFLOW_PACKET_STEPS)
    steps[2], steps[3] = steps[3], steps[2]
    path.write_text(
        "\n".join(workflow_step_block(step_name, run_command) for step_name, run_command in steps) + "\n",
        encoding="utf-8",
    )


def append_forbidden_workflow_line(root: Path, marker: str) -> None:
    path = root / WORKFLOW_REL
    text = path.read_text(encoding="utf-8")
    path.write_text(text + "        " + marker + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, tuple[object, ...] | None]] = [("baseline", None)]

    for relative_path in REQUIRED_FILES:
        cases.append(("missing_file_" + relative_path.as_posix().replace("/", "_"), ("unlink", relative_path)))

    for relative_path, markers in EXACT_MARKERS.items():
        rel_path = Path(relative_path)
        for marker in markers:
            safe_marker = str(abs(hash((relative_path, marker))))
            cases.append((f"remove_marker_{safe_marker}", ("remove_marker", rel_path, marker)))
            cases.append((f"duplicate_marker_{safe_marker}", ("duplicate_marker", rel_path, marker)))

    for step_name, run_command in WORKFLOW_PACKET_STEPS:
        safe_step = step_name.lower().replace(" ", "_").replace("/", "_")
        cases.append((f"remove_step_{safe_step}", ("remove_step", step_name, run_command)))
        cases.append((f"duplicate_step_{safe_step}", ("duplicate_step", step_name, run_command)))

    cases.append(("reorder_workflow", ("reorder_workflow",)))

    for marker in FORBIDDEN_WORKFLOW_LINES:
        safe_marker = str(abs(hash(marker)))
        cases.append((f"forbidden_line_{safe_marker}", ("append_forbidden", marker)))

    for name, action in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-phase3-interop-packet-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if action is not None:
                verb = action[0]
                if verb == "unlink":
                    (root / action[1]).unlink()
                elif verb == "remove_marker":
                    remove_marker(root, action[1], action[2])
                elif verb == "duplicate_marker":
                    duplicate_marker(root, action[1], action[2])
                elif verb == "remove_step":
                    remove_workflow_step(root, action[1], action[2])
                elif verb == "duplicate_step":
                    duplicate_workflow_step(root, action[1], action[2])
                elif verb == "reorder_workflow":
                    reorder_workflow(root)
                elif verb == "append_forbidden":
                    append_forbidden_workflow_line(root, action[1])
                else:
                    raise AssertionError(f"unknown self-test action: {verb}")

            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print("self-test:baseline:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_PHASE3_INTEROP_WORKFLOW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_PHASE3_INTEROP_WORKFLOW_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def write_sample_root(sample_root: Path) -> None:
    build_sample_repo(sample_root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", "--root", dest="repo_root", help="override the repository root used for checks")
    parser.add_argument(
        "--write-sample-root",
        dest="write_sample_root",
        help="write a synthetic passing sample repo to the given directory",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic positive and negative cases",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    root = repo_root(args.repo_root)
    failures = collect_failures(root)
    if failures:
        print("PHASE1_PHASE3_INTEROP_WORKFLOW_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_PHASE3_INTEROP_WORKFLOW_PACKET=pass")
    print(f"PHASE1_PHASE3_INTEROP_WORKFLOW_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_PHASE3_INTEROP_WORKFLOW_PACKET_REQUIRED_STEP_COUNT={len(WORKFLOW_PACKET_STEPS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
