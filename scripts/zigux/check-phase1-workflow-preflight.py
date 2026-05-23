#!/usr/bin/env python3
"""Guard the current Lane 17 Phase 1 workflow preflight insertion slot."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
SHARED_REMINDER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")

PREFLIGHT_INSERTION_CHAIN = (
    "Setup Python",
    "Self-test current Phase 1 workflow preflight checker",
    "Preflight current Phase 1 workflow viability",
    "Setup pinned Zig toolchain",
)
PHASE1_CHAIN = (
    "Check current Phase 1 shared reminder packet",
    "Self-test current Phase 1 closure validator",
    "Check current Phase 1 closure packet",
    "Self-test current Phase 3 interop packet",
)

REQUIRED_FILES = (
    WORKFLOW_REL,
    SHARED_REMINDER_REL,
    CLOSURE_VALIDATOR_REL,
)

REQUIRED_WORKFLOW_LINES = (
    "      - name: Self-test current Phase 1 workflow preflight checker",
    "        run: python3 scripts/zigux/check-phase1-workflow-preflight.py --self-test",
    "      - name: Preflight current Phase 1 workflow viability",
    "        run: python3 scripts/zigux/check-phase1-workflow-preflight.py",
)

REQUIRED_SHARED_REMINDER_MARKERS = (
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
)

REQUIRED_CLOSURE_VALIDATOR_MARKERS = (
    "PHASE1_CLOSURE_VALIDATION=pass",
    "PHASE1_CLOSURE_SELF_TEST=pass",
)


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(root: Path, relative_path: Path, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def count_exact_line(text: str, line: str) -> int:
    return sum(1 for current in text.splitlines() if current == line)


def require_exact_line(text: str, label: str, line: str) -> list[str]:
    count = count_exact_line(text, line)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_order(workflow_text: str, label: str, chain: tuple[str, ...]) -> list[str]:
    positions: list[int] = []
    failures: list[str] = []
    for step_name in chain:
        step_line = f"      - name: {step_name}"
        position = workflow_text.find(step_line)
        if position == -1:
            failures.append(f"{label}:missing:{step_name}")
        positions.append(position)
    if failures:
        return failures
    if any(earlier >= later for earlier, later in zip(positions, positions[1:])):
        failures.append(f"{label}:out_of_order:{','.join(chain)}")
    return failures


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    workflow_text = load_text(root, WORKFLOW_REL)
    failures.extend(require_order(workflow_text, "workflow_preflight_insertion_order", PREFLIGHT_INSERTION_CHAIN))
    failures.extend(require_order(workflow_text, "workflow_phase1_tail_order", PHASE1_CHAIN))
    for line in REQUIRED_WORKFLOW_LINES:
        failures.extend(require_exact_line(workflow_text, f"{WORKFLOW_REL.as_posix()}:{line}", line))

    shared_reminder_text = load_text(root, SHARED_REMINDER_REL)
    for marker in REQUIRED_SHARED_REMINDER_MARKERS:
        failures.extend(require_exact_line(shared_reminder_text, f"{SHARED_REMINDER_REL.as_posix()}:{marker}", marker))

    closure_validator_text = load_text(root, CLOSURE_VALIDATOR_REL)
    for marker in REQUIRED_CLOSURE_VALIDATOR_MARKERS:
        count = closure_validator_text.count(marker)
        if count != 1:
            failures.append(
                f"{CLOSURE_VALIDATOR_REL.as_posix()}:{marker}:expected=1:actual={count}"
            )

    return failures


def build_sample_root(root: Path) -> None:
    workflow_lines = [
        "name: zigux-bootstrap",
        "jobs:",
        "  bootstrap:",
        "    runs-on: ubuntu-latest",
        "    steps:",
        "      - name: Setup Python",
        "        uses: actions/setup-python@v6.2.0",
        "      - name: Self-test current Phase 1 workflow preflight checker",
        "        run: python3 scripts/zigux/check-phase1-workflow-preflight.py --self-test",
        "      - name: Preflight current Phase 1 workflow viability",
        "        run: python3 scripts/zigux/check-phase1-workflow-preflight.py",
        "      - name: Setup pinned Zig toolchain",
        "        run: echo setup-zig",
        "      - name: Check current Phase 1 shared reminder packet",
        "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        "      - name: Self-test current Phase 1 closure validator",
        "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
        "      - name: Check current Phase 1 closure packet",
        "        run: python3 scripts/zigux/validate-phase1-closure.py",
        "      - name: Self-test current Phase 3 interop packet",
        "        run: python3 scripts/zigux/validate_phase3_selftest.py",
    ]
    write_text(root, WORKFLOW_REL, "\n".join(workflow_lines) + "\n")
    write_text(
        root,
        SHARED_REMINDER_REL,
        "\n".join(REQUIRED_SHARED_REMINDER_MARKERS)
        + "\nprint(\"PHASE1_SHARED_REMINDER_PACKET=pass\")\n",
    )
    write_text(
        root,
        CLOSURE_VALIDATOR_REL,
        "\n".join(REQUIRED_CLOSURE_VALIDATOR_MARKERS) + "\n",
    )


def rewrite_once(text: str, needle: str, replacement: str) -> str:
    if needle not in text:
        raise ValueError(f"missing needle: {needle}")
    return text.replace(needle, replacement, 1)


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [
        ("baseline", None),
        (
            "missing_selftest_step",
            lambda root: write_text(
                root,
                WORKFLOW_REL,
                rewrite_once(
                    load_text(root, WORKFLOW_REL),
                    "      - name: Self-test current Phase 1 workflow preflight checker\n"
                    "        run: python3 scripts/zigux/check-phase1-workflow-preflight.py --self-test\n",
                    "",
                ),
            ),
        ),
        (
            "duplicate_preflight_step",
            lambda root: write_text(
                root,
                WORKFLOW_REL,
                load_text(root, WORKFLOW_REL)
                + "      - name: Preflight current Phase 1 workflow viability\n"
                + "        run: python3 scripts/zigux/check-phase1-workflow-preflight.py\n",
            ),
        ),
        (
            "wrong_preflight_to_zig_order",
            lambda root: write_text(
                root,
                WORKFLOW_REL,
                rewrite_once(
                    load_text(root, WORKFLOW_REL),
                    "      - name: Preflight current Phase 1 workflow viability\n"
                    "        run: python3 scripts/zigux/check-phase1-workflow-preflight.py\n"
                    "      - name: Setup pinned Zig toolchain\n"
                    "        run: echo setup-zig\n",
                    "      - name: Setup pinned Zig toolchain\n"
                    "        run: echo setup-zig\n"
                    "      - name: Preflight current Phase 1 workflow viability\n"
                    "        run: python3 scripts/zigux/check-phase1-workflow-preflight.py\n",
                ),
            ),
        ),
        (
            "missing_phase1_tail_anchor",
            lambda root: write_text(
                root,
                WORKFLOW_REL,
                rewrite_once(
                    load_text(root, WORKFLOW_REL),
                    "      - name: Check current Phase 1 closure packet\n"
                    "        run: python3 scripts/zigux/validate-phase1-closure.py\n",
                    "",
                ),
            ),
        ),
        ("missing_shared_reminder_file", lambda root: (root / SHARED_REMINDER_REL).unlink()),
        (
            "stale_closure_validator_marker",
            lambda root: write_text(root, CLOSURE_VALIDATOR_REL, "PHASE1_CLOSURE_VALIDATION=drift\n"),
        ),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-workflow-preflight-") as tmpdir:
            root = Path(tmpdir)
            build_sample_root(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-workflow-preflight-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-workflow-preflight-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_WORKFLOW_PREFLIGHT_SELF_TEST=pass")
    print(f"PHASE1_WORKFLOW_PREFLIGHT_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root used for validation")
    parser.add_argument("--self-test", action="store_true", help="run synthetic guard self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_WORKFLOW_PREFLIGHT_READY=pass")
    print(
        "PHASE1_WORKFLOW_PREFLIGHT_INSERTION_POINT=Setup Python,Self-test current Phase 1 workflow preflight checker,Preflight current Phase 1 workflow viability,Setup pinned Zig toolchain"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
