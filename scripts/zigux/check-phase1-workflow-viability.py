#!/usr/bin/env python3
"""Guard the current Lane 17 Phase 1 workflow-viability packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_REL = Path("zigux/Makefile")

REQUIRED_FILES = (
    WORKFLOW_REL,
    MAKEFILE_REL,
    Path("Documentation/zigux/phase1-closure.md"),
    Path("scripts/zigux/check-phase1-direct-owner-markers.py"),
    Path("scripts/zigux/check-phase1-direct-anchor-manifest-gate.py"),
    Path("scripts/zigux/check-phase1-string-review-packet.py"),
    Path("scripts/zigux/check-phase1-find-bit-review-packet.py"),
    Path("scripts/zigux/check-phase1-route-summary-counts.py"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py"),
    Path("scripts/zigux/check-phase1-shared-reminder-packet.py"),
    Path("scripts/zigux/validate-phase1-closure.py"),
    Path("zigux/tests/build.zig"),
    Path("zigux/tests/phase1_helpers.zig"),
    Path("zigux/tests/phase1_helpers_build.zig"),
    Path("zigux/tests/phase1_host_tools_smoke.zig"),
    Path("zigux/tests/fixtures/phase1_helper_manifest.json"),
)

REQUIRED_WORKFLOW_STEPS = (
    (
        "Self-test current Phase 1 direct-owner checker",
        "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    ),
    (
        "Check current Phase 1 direct-owner markers",
        "python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    ),
    (
        "Self-test current Phase 1 direct-anchor manifest gate",
        "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
    ),
    (
        "Check current Phase 1 direct-anchor manifest gate",
        "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    ),
    (
        "Self-test current Phase 1 string review checker",
        "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    ),
    (
        "Check current Phase 1 string review packet",
        "python3 scripts/zigux/check-phase1-string-review-packet.py",
    ),
    (
        "Self-test current Phase 1 find-bit review checker",
        "python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
    ),
    (
        "Check current Phase 1 find-bit review packet",
        "python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
    ),
    (
        "Self-test current Phase 1 route summary checker",
        "python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    ),
    (
        "Check current Phase 1 route summary packet",
        "python3 scripts/zigux/check-phase1-route-summary-counts.py",
    ),
    (
        "Self-test current Phase 1 bench checker",
        "python3 scripts/zigux/check-phase1-bench.py --self-test",
    ),
    (
        "Self-test current Phase 1 find-bit bench anchor checker",
        "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
    ),
    (
        "Check current Phase 1 find-bit bench anchor packet",
        "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    ),
    (
        "Self-test current Phase 1 shared reminder checker",
        "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    ),
    (
        "Check current Phase 1 shared reminder packet",
        "python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    ),
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
        "Run current Phase 1 shared tests-root smoke",
        "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
)

REQUIRED_WORKFLOW_CHAIN = tuple(step_name for step_name, _ in REQUIRED_WORKFLOW_STEPS)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
)

REQUIRED_MAKEFILE_MARKERS = (
    "phase1-route-summary:",
    "phase2-toolchain:",
    "phase3-validate:",
    "phase14-validate:",
)

FORBIDDEN_WORKFLOW_COMMANDS = (
    "python3 scripts/zigux/check-phase1-bench.py",
    "python3 scripts/zigux/validate-phase1.py --self-test",
    "python3 scripts/zigux/validate-phase1.py",
    "make -C zigux phase1-validate",
    "make -C zigux phase1-test",
    "make -C zigux phase1-bench",
    "make -C zigux phase1",
)

FORBIDDEN_MAKEFILE_MARKERS = (
    "phase1-validate:",
    "phase1-test:",
    "phase1-bench:",
    "phase1:",
)


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_text_once(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_line_once(text: str, label: str, line: str) -> list[str]:
    count = sum(1 for current in text.splitlines() if current.strip() == line.strip())
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def workflow_step_names(workflow_text: str) -> list[str]:
    prefix = "      - name: "
    return [line[len(prefix) :] for line in workflow_text.splitlines() if line.startswith(prefix)]


def require_workflow_step(workflow_text: str, step_name: str, run_command: str) -> list[str]:
    failures: list[str] = []
    failures.extend(
        require_line_once(
            workflow_text,
            f"workflow_step:{step_name}",
            f"- name: {step_name}",
        )
    )
    pair = f"      - name: {step_name}\n        run: {run_command}"
    count = workflow_text.count(pair)
    if count != 1:
        failures.append(f"workflow_run:{step_name}:expected=1:actual={count}")
    return failures


def require_workflow_chain(workflow_text: str, step_names: tuple[str, ...]) -> list[str]:
    names = workflow_step_names(workflow_text)
    width = len(step_names)
    for index in range(len(names) - width + 1):
        if tuple(names[index : index + width]) == step_names:
            return []
    return [f"workflow_chain:missing:{'->'.join(step_names)}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    workflow_text = read_text(root, WORKFLOW_REL)
    makefile_text = read_text(root, MAKEFILE_REL)

    for step_name, run_command in REQUIRED_WORKFLOW_STEPS:
        failures.extend(require_workflow_step(workflow_text, step_name, run_command))
    failures.extend(require_workflow_chain(workflow_text, REQUIRED_WORKFLOW_CHAIN))

    for marker in REQUIRED_WORKFLOW_LINES:
        failures.extend(require_line_once(workflow_text, f"workflow_marker:{marker}", marker))

    workflow_lines = [line.strip() for line in workflow_text.splitlines()]
    for command in FORBIDDEN_WORKFLOW_COMMANDS:
        count = sum(1 for line in workflow_lines if line == f"run: {command}")
        if count:
            failures.append(f"workflow_forbidden:{command}:actual={count}")

    for marker in REQUIRED_MAKEFILE_MARKERS:
        failures.extend(require_text_once(makefile_text, f"makefile_marker:{marker}", marker))

    for marker in FORBIDDEN_MAKEFILE_MARKERS:
        count = makefile_text.count(marker)
        if count:
            failures.append(f"makefile_forbidden:{marker}:actual={count}")

    return failures


def write_file(root: Path, relative_path: Path, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        if relative_path == WORKFLOW_REL:
            continue
        if relative_path == MAKEFILE_REL:
            write_file(root, relative_path, "\n".join(REQUIRED_MAKEFILE_MARKERS) + "\n")
            continue
        write_file(root, relative_path, f"{relative_path.as_posix()}\n")

    workflow_lines = [
        "name: zigux-bootstrap",
        "",
        "jobs:",
        "  bootstrap:",
        "    runs-on: ubuntu-latest",
        "    steps:",
        "",
    ]
    for step_name, run_command in REQUIRED_WORKFLOW_STEPS:
        workflow_lines.append(f"      - name: {step_name}")
        workflow_lines.append(f"        run: {run_command}")
        workflow_lines.append("")
    write_file(root, WORKFLOW_REL, "\n".join(workflow_lines))


def mutate_remove_text(root: Path, relative_path: Path, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker + "\n", "", 1).replace(marker, "", 1), encoding="utf-8")


def mutate_duplicate_text(root: Path, relative_path: Path, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, str, Path | None, str | None]] = [("success", "none", None, None)]
    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path.as_posix()}", "missing_file", relative_path, None))
    for step_name, run_command in REQUIRED_WORKFLOW_STEPS:
        block = f"      - name: {step_name}\n        run: {run_command}\n"
        cases.append((f"missing_step:{step_name}", "remove", WORKFLOW_REL, block))
        cases.append((f"duplicate_step:{step_name}", "duplicate", WORKFLOW_REL, block))
    for marker in REQUIRED_MAKEFILE_MARKERS:
        cases.append((f"missing_makefile_marker:{marker}", "remove", MAKEFILE_REL, marker))
        cases.append((f"duplicate_makefile_marker:{marker}", "duplicate", MAKEFILE_REL, marker))
    cases.append(
        (
            "forbidden_workflow_bench_run",
            "append",
            WORKFLOW_REL,
            "      - name: Check current Phase 1 bench packet\n        run: python3 scripts/zigux/check-phase1-bench.py\n",
        )
    )
    cases.append(
        (
            "forbidden_makefile_phase1_validate",
            "append",
            MAKEFILE_REL,
            "phase1-validate:\n",
        )
    )
    cases.append(
        (
            "out_of_order_chain",
            "replace",
            WORKFLOW_REL,
            (
                "      - name: Self-test current Phase 1 shared reminder checker\n"
                "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test\n\n"
                "      - name: Check current Phase 1 closure packet\n"
                "        run: python3 scripts/zigux/validate-phase1-closure.py\n\n"
                "      - name: Check current Phase 1 shared reminder packet\n"
                "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\n"
            ),
        )
    )

    for name, operation, relative_path, payload in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-workflow-viability-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if operation == "missing_file" and relative_path is not None:
                (root / relative_path).unlink()
            elif operation == "remove" and relative_path is not None and payload is not None:
                mutate_remove_text(root, relative_path, payload)
            elif operation == "duplicate" and relative_path is not None and payload is not None:
                mutate_duplicate_text(root, relative_path, payload)
            elif operation == "append" and relative_path is not None and payload is not None:
                path = root / relative_path
                path.write_text(path.read_text(encoding="utf-8") + payload, encoding="utf-8")
            elif operation == "replace" and relative_path is not None and payload is not None:
                path = root / relative_path
                text = path.read_text(encoding="utf-8")
                old = (
                    "      - name: Self-test current Phase 1 shared reminder checker\n"
                    "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test\n\n"
                    "      - name: Check current Phase 1 shared reminder packet\n"
                    "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\n\n"
                    "      - name: Self-test current Phase 1 closure validator\n"
                    "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test\n"
                )
                text = text.replace(old, payload, 1)
                path.write_text(text, encoding="utf-8")

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("phase1-workflow-viability-self-test:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"phase1-workflow-viability-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_WORKFLOW_VIABILITY_SELF_TEST=pass")
    print(f"PHASE1_WORKFLOW_VIABILITY_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    parser.add_argument(
        "--write-sample-root",
        help="write a current-like sample root to the given path and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root:
        destination = Path(args.write_sample_root).resolve()
        build_sample_repo(destination)
        print(f"PHASE1_WORKFLOW_VIABILITY_SAMPLE_ROOT={destination}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_WORKFLOW_VIABILITY=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_WORKFLOW_VIABILITY=pass")
    print(f"PHASE1_WORKFLOW_VIABILITY_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_WORKFLOW_VIABILITY_REQUIRED_STEP_COUNT={len(REQUIRED_WORKFLOW_STEPS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
