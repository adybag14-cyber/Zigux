#!/usr/bin/env python3
"""Guard the Lane 17 Phase 1 workflow step pair against drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
CHECKER_REL = Path("scripts/zigux/check-phase1-lane-sequencing-packet.py")

SELF_TEST_STEP = "      - name: Self-test current Phase 1 lane sequencing packet checker"
SELF_TEST_RUN = (
    "        run: python3 scripts/zigux/check-phase1-lane-sequencing-packet.py --self-test"
)
CHECK_STEP = "      - name: Check current Phase 1 lane sequencing packet"
CHECK_RUN = "        run: python3 scripts/zigux/check-phase1-lane-sequencing-packet.py"

BEFORE_STEP = "      - name: Check current Phase 1 shared reminder packet"
BEFORE_RUN = "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py"
AFTER_STEP = "      - name: Self-test current Phase 1 closure validator"
AFTER_RUN = "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test"

REQUIRED_LINES = (
    BEFORE_STEP,
    BEFORE_RUN,
    SELF_TEST_STEP,
    SELF_TEST_RUN,
    CHECK_STEP,
    CHECK_RUN,
    AFTER_STEP,
    AFTER_RUN,
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_line(text: str, label: str, line: str) -> list[str]:
    count = sum(1 for current in text.splitlines() if current == line)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    if not (root / WORKFLOW_REL).is_file():
        failures.append(f"missing_file:{WORKFLOW_REL.as_posix()}")
        return failures
    if not (root / CHECKER_REL).is_file():
        failures.append(f"missing_file:{CHECKER_REL.as_posix()}")
        return failures

    workflow_text = load_text(root, WORKFLOW_REL)
    for index, line in enumerate(REQUIRED_LINES):
        failures.extend(
            require_exact_line(workflow_text, f"{WORKFLOW_REL.as_posix()}:line_{index}", line)
        )
    if failures:
        return failures

    workflow_lines = workflow_text.splitlines()
    positions = {line: workflow_lines.index(line) for line in REQUIRED_LINES}
    if not (
        positions[BEFORE_STEP]
        < positions[BEFORE_RUN]
        < positions[SELF_TEST_STEP]
        < positions[SELF_TEST_RUN]
        < positions[CHECK_STEP]
        < positions[CHECK_RUN]
        < positions[AFTER_STEP]
        < positions[AFTER_RUN]
    ):
        failures.append(
            f"{WORKFLOW_REL.as_posix()}:lane17_phase1_packet_order_invalid"
        )
    if positions[BEFORE_RUN] != positions[BEFORE_STEP] + 1:
        failures.append(
            f"{WORKFLOW_REL.as_posix()}:shared_reminder_run_not_after_shared_reminder_step"
        )
    if positions[SELF_TEST_STEP] != positions[BEFORE_RUN] + 1:
        failures.append(
            f"{WORKFLOW_REL.as_posix()}:selftest_step_not_after_shared_reminder_run"
        )
    if positions[CHECK_STEP] != positions[SELF_TEST_RUN] + 1:
        failures.append(
            f"{WORKFLOW_REL.as_posix()}:check_step_not_adjacent_to_selftest_run"
        )
    if positions[CHECK_RUN] != positions[CHECK_STEP] + 1:
        failures.append(
            f"{WORKFLOW_REL.as_posix()}:check_run_not_adjacent_to_check_step"
        )
    if positions[AFTER_STEP] != positions[CHECK_RUN] + 1:
        failures.append(
            f"{WORKFLOW_REL.as_posix()}:closure_validator_step_not_after_lane17_packet"
        )
    if positions[AFTER_RUN] != positions[AFTER_STEP] + 1:
        failures.append(
            f"{WORKFLOW_REL.as_posix()}:closure_validator_run_not_after_closure_validator_step"
        )
    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_workflow() -> str:
    return "\n".join(
        (
            "name: zigux-bootstrap",
            "jobs:",
            "  bootstrap:",
            "    steps:",
            "      - name: Self-test current Phase 1 shared reminder checker",
            "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
            BEFORE_STEP,
            BEFORE_RUN,
            SELF_TEST_STEP,
            SELF_TEST_RUN,
            CHECK_STEP,
            CHECK_RUN,
            AFTER_STEP,
            AFTER_RUN,
        )
    ) + "\n"


def build_sample_repo(root: Path) -> None:
    write_text(root / WORKFLOW_REL, sample_workflow())
    write_text(root / CHECKER_REL, "#!/usr/bin/env python3\nprint('stub')\n")


def mutate_remove_line(root: Path, target_line: str) -> None:
    workflow_path = root / WORKFLOW_REL
    lines = workflow_path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line == target_line:
            del lines[index]
            workflow_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return


def mutate_duplicate_line(root: Path, target_line: str) -> None:
    workflow_path = root / WORKFLOW_REL
    lines = workflow_path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line == target_line:
            lines.insert(index + 1, line)
            workflow_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return


def mutate_replace_line(root: Path, old: str, new: str) -> None:
    workflow_path = root / WORKFLOW_REL
    workflow_path.write_text(
        workflow_path.read_text(encoding="utf-8").replace(old, new, 1),
        encoding="utf-8",
    )


def mutate_swap_step_order(root: Path) -> None:
    mutate_replace_line(
        root,
        "\n".join((SELF_TEST_STEP, SELF_TEST_RUN, CHECK_STEP, CHECK_RUN)),
        "\n".join((CHECK_STEP, CHECK_RUN, SELF_TEST_STEP, SELF_TEST_RUN)),
    )


def mutate_insert_gap_before_selftest(root: Path) -> None:
    mutate_replace_line(
        root,
        "\n".join((BEFORE_RUN, SELF_TEST_STEP)),
        "\n".join((
            BEFORE_RUN,
            "      - name: Drifted gap step",
            "        run: echo drift",
            SELF_TEST_STEP,
        )),
    )


def mutate_insert_gap_before_closure(root: Path) -> None:
    mutate_replace_line(
        root,
        "\n".join((CHECK_RUN, AFTER_STEP)),
        "\n".join((
            CHECK_RUN,
            "      - name: Drifted gap step",
            "        run: echo drift",
            AFTER_STEP,
        )),
    )


def run_self_test() -> int:
    cases: list[tuple[str, str, str | tuple[str, str] | None]] = [
        ("success", "noop", None),
        ("missing_checker", "remove_file", CHECKER_REL.as_posix()),
        ("missing_before_step", "remove_line", BEFORE_STEP),
        ("duplicate_before_step", "duplicate_line", BEFORE_STEP),
        ("missing_before_run", "remove_line", BEFORE_RUN),
        ("duplicate_before_run", "duplicate_line", BEFORE_RUN),
        (
            "stale_before_run",
            "replace_line",
            (BEFORE_RUN, "        run: python3 scripts/zigux/check-phase1-lane-sequencing-packet.py"),
        ),
        ("missing_self_test_step", "remove_line", SELF_TEST_STEP),
        ("duplicate_self_test_step", "duplicate_line", SELF_TEST_STEP),
        ("missing_self_test_run", "remove_line", SELF_TEST_RUN),
        ("stale_self_test_run", "replace_line", (SELF_TEST_RUN, "        run: python3 scripts/zigux/check-phase1-lane-sequencing-packet.py")),
        ("missing_check_step", "remove_line", CHECK_STEP),
        ("duplicate_check_step", "duplicate_line", CHECK_STEP),
        ("missing_check_run", "remove_line", CHECK_RUN),
        ("stale_check_run", "replace_line", (CHECK_RUN, "        run: python3 scripts/zigux/check-phase1-lane-sequencing-packet.py --self-test")),
        ("missing_after_step", "remove_line", AFTER_STEP),
        ("duplicate_after_step", "duplicate_line", AFTER_STEP),
        ("missing_after_run", "remove_line", AFTER_RUN),
        ("duplicate_after_run", "duplicate_line", AFTER_RUN),
        (
            "stale_after_run",
            "replace_line",
            (AFTER_RUN, "        run: python3 scripts/zigux/check-phase1-lane-sequencing-packet.py"),
        ),
        ("swapped_order", "swap_order", None),
        ("gap_before_selftest", "insert_gap_before_selftest", None),
        ("gap_before_closure", "insert_gap_before_closure", None),
    ]

    for name, mode, payload in cases:
        with tempfile.TemporaryDirectory(prefix="lane17-phase1-workflow-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if mode == "remove_file" and isinstance(payload, str):
                (root / payload).unlink()
            elif mode == "remove_line" and isinstance(payload, str):
                mutate_remove_line(root, payload)
            elif mode == "duplicate_line" and isinstance(payload, str):
                mutate_duplicate_line(root, payload)
            elif mode == "replace_line" and isinstance(payload, tuple):
                old, new = payload
                mutate_replace_line(root, old, new)
            elif mode == "swap_order":
                mutate_swap_step_order(root)
            elif mode == "insert_gap_before_selftest":
                mutate_insert_gap_before_selftest(root)
            elif mode == "insert_gap_before_closure":
                mutate_insert_gap_before_closure(root)

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("self-test:success:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_LANE_SEQUENCING_WORKFLOW_SELF_TEST=pass")
    print(f"PHASE1_LANE_SEQUENCING_WORKFLOW_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_LANE_SEQUENCING_WORKFLOW=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_LANE_SEQUENCING_WORKFLOW=pass")
    print("PHASE1_LANE_SEQUENCING_WORKFLOW_REQUIRED_STEP_PAIR_COUNT=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
