#!/usr/bin/env python3
"""Guard the Lane 17 Phase 1 workflow preflight packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
NOTE_REL = Path("Documentation/zigux/phase1-workflow-viability.md")
VIABILITY_CHECKER_REL = Path("scripts/zigux/check-phase1-workflow-viability.py")

PREFLIGHT_STEP = (
    "Preflight current Phase 1 workflow viability checker",
    "python3 scripts/zigux/check-phase1-workflow-preflight.py",
)
PREFLIGHT_ORDER = (
    "Setup Python",
    "Preflight current Phase 1 workflow viability checker",
    "Setup pinned Zig toolchain",
)

REQUIRED_FILES = (
    WORKFLOW_REL,
    NOTE_REL,
    VIABILITY_CHECKER_REL,
)

REQUIRED_NOTE_LINES = (
    "- `PHASE1_WORKFLOW_STATUS=active`",
    "- `PHASE1_WORKFLOW_SCOPE=current bootstrap Phase 1 workflow preflight guard`",
    "- `PHASE1_WORKFLOW_NOTE_OWNER=lane17-phase1-workflow-preflight`",
    "- `PHASE1_WORKFLOW_PREFLIGHT=Preflight current Phase 1 workflow viability checker after Setup Python and before Setup pinned Zig toolchain`",
    "- `PHASE1_WORKFLOW_PREFLIGHT_ORDER=Setup Python,Preflight current Phase 1 workflow viability checker,Setup pinned Zig toolchain`",
    "- `PHASE1_WORKFLOW_VIABILITY_NEXT_STEP=wire the lane-local workflow-viability self-test and packet-check pair after the current Phase 1 closure packet and before the current Phase 3 interop packet`",
)


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_line_once(text: str, label: str, line: str) -> list[str]:
    count = sum(1 for current in text.splitlines() if current.rstrip() == line.rstrip())
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
            f"      - name: {step_name}",
        )
    )
    pair = f"      - name: {step_name}\n        run: {run_command}"
    count = workflow_text.count(pair)
    if count != 1:
        failures.append(f"workflow_run:{step_name}:expected=1:actual={count}")
    return failures


def require_adjacent_chain(workflow_text: str, step_names: tuple[str, ...]) -> list[str]:
    names = workflow_step_names(workflow_text)
    width = len(step_names)
    for index in range(len(names) - width + 1):
        if tuple(names[index : index + width]) == step_names:
            return []
    return [f"workflow_adjacent_chain:missing:{'->'.join(step_names)}"]


def require_order(workflow_text: str, step_names: tuple[str, ...], label: str) -> list[str]:
    positions: list[int] = []
    for step_name in step_names:
        needle = f"- name: {step_name}"
        position = workflow_text.find(needle)
        if position == -1:
            return [f"{label}:missing:{step_name}"]
        positions.append(position)
    return [] if positions == sorted(positions) else [f"{label}:out_of_order"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    note_text = read_text(root, NOTE_REL)
    workflow_text = read_text(root, WORKFLOW_REL)

    for note_line in REQUIRED_NOTE_LINES:
        failures.extend(require_line_once(note_text, "note", note_line))

    failures.extend(require_workflow_step(workflow_text, PREFLIGHT_STEP[0], PREFLIGHT_STEP[1]))
    failures.extend(require_order(workflow_text, PREFLIGHT_ORDER, "workflow_preflight_order"))
    return failures


def build_note_text() -> str:
    return "\n".join(
        (
            "# Phase 1 Workflow Viability",
            "",
            *REQUIRED_NOTE_LINES,
            "- keep this packet scoped to the lightweight Lane 17 workflow preflight guard.",
            "- run the preflight before pinned Zig setup so the lane still emits direct signal when the external archive path fails first.",
            "- leave the lane-local workflow-viability self-test and packet-check pair as a separate follow-up until the surrounding closure-to-Phase-3 handoff is restacked safely.",
            "",
        )
    )


def build_sample_workflow_text() -> str:
    lines = [
        "name: zigux-bootstrap",
        "",
        "jobs:",
        "  bootstrap:",
        "    runs-on: ubuntu-latest",
        "    steps:",
        "      - name: Setup Python",
        "        run: python3 --version",
        "",
        f"      - name: {PREFLIGHT_STEP[0]}",
        f"        run: {PREFLIGHT_STEP[1]}",
        "",
        "      - name: Setup pinned Zig toolchain",
        "        run: printf 'pinned-zig\\n'",
        "",
    ]
    return "\n".join(lines)


def build_sample_repo(root: Path) -> None:
    write_text(root, NOTE_REL, build_note_text())
    write_text(root, WORKFLOW_REL, build_sample_workflow_text())
    write_text(root, VIABILITY_CHECKER_REL, "# placeholder\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-workflow-preflight-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        failures = collect_failures(root)
        if failures:
            print("phase1-workflow-preflight-self-test:unexpected_failures")
            for failure in failures:
                print(failure)
            return 1
        case_count += 1

        note_text = read_text(root, NOTE_REL)
        write_text(
            root,
            NOTE_REL,
            note_text.replace(REQUIRED_NOTE_LINES[3] + "\n", "", 1),
        )
        failures = collect_failures(root)
        if "note:expected=1:actual=0" not in failures:
            print("phase1-workflow-preflight-self-test:missing_note_marker_not_detected")
            return 1
        case_count += 1
        build_sample_repo(root)

        workflow_text = read_text(root, WORKFLOW_REL)
        write_text(
            root,
            WORKFLOW_REL,
            workflow_text.replace(
                "      - name: Preflight current Phase 1 workflow viability checker\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        if (
            "workflow_step:Preflight current Phase 1 workflow viability checker:expected=1:actual=0"
            not in failures
        ):
            print("phase1-workflow-preflight-self-test:missing_preflight_step_not_detected")
            return 1
        case_count += 1
        build_sample_repo(root)

        workflow_text = read_text(root, WORKFLOW_REL)
        duplicate = (
            "      - name: Preflight current Phase 1 workflow viability checker\n"
            "        run: python3 scripts/zigux/check-phase1-workflow-preflight.py\n"
        )
        write_text(root, WORKFLOW_REL, workflow_text + "\n" + duplicate)
        failures = collect_failures(root)
        if (
            "workflow_step:Preflight current Phase 1 workflow viability checker:expected=1:actual=2"
            not in failures
        ):
            print("phase1-workflow-preflight-self-test:duplicate_preflight_step_not_detected")
            return 1
        case_count += 1
        build_sample_repo(root)

        workflow_text = read_text(root, WORKFLOW_REL)
        old = (
            "      - name: Setup Python\n"
            "        run: python3 --version\n\n"
            "      - name: Preflight current Phase 1 workflow viability checker\n"
            "        run: python3 scripts/zigux/check-phase1-workflow-preflight.py\n\n"
            "      - name: Setup pinned Zig toolchain\n"
            "        run: printf 'pinned-zig\\n'\n"
        )
        new = (
            "      - name: Setup Python\n"
            "        run: python3 --version\n\n"
            "      - name: Setup pinned Zig toolchain\n"
            "        run: printf 'pinned-zig\\n'\n\n"
            "      - name: Preflight current Phase 1 workflow viability checker\n"
            "        run: python3 scripts/zigux/check-phase1-workflow-preflight.py\n"
        )
        write_text(root, WORKFLOW_REL, workflow_text.replace(old, new, 1))
        failures = collect_failures(root)
        if "workflow_preflight_order:out_of_order" not in failures:
            print("phase1-workflow-preflight-self-test:preflight_order_not_detected")
            return 1
        case_count += 1
        build_sample_repo(root)

        workflow_text = read_text(root, WORKFLOW_REL)
    print("PHASE1_WORKFLOW_PREFLIGHT_SELF_TEST=pass")
    print(f"PHASE1_WORKFLOW_PREFLIGHT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Override the repository root.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-tests.")
    parser.add_argument(
        "--write-sample-root",
        help="Write a passing sample repository root to the given path and exit.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root:
        destination = Path(args.write_sample_root).resolve()
        build_sample_repo(destination)
        print(f"PHASE1_WORKFLOW_PREFLIGHT_SAMPLE_ROOT={destination}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_WORKFLOW_PREFLIGHT=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_WORKFLOW_PREFLIGHT=pass")
    print(f"PHASE1_WORKFLOW_PREFLIGHT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_WORKFLOW_PREFLIGHT_REQUIRED_NOTE_LINE_COUNT={len(REQUIRED_NOTE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
