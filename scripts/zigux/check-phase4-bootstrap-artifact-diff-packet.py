#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
SURVEY = Path("Documentation/zigux/phase4-artifact-diff-tooling-survey.md")
NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")

REQUIRED_PATHS = (
    WORKFLOW,
    SURVEY,
    NOTE,
    Path("scripts/zigux/artifact_diff.py"),
    Path("scripts/zigux/check-artifact-diff-contract.py"),
    Path("scripts/zigux/check-phase4-artifact-diff-determinism.py"),
    Path("scripts/zigux/check-phase4-artifact-diff-validator-replays.py"),
)

STEP_BOUNDARY_BEFORE = "- name: Run Phase 4 rollback tests"
REQUIRED_STEP_NAMES = (
    "- name: Self-test current Phase 4 artifact-diff helper",
    "- name: Self-test current Phase 4 artifact-diff contract checker",
    "- name: Check current Phase 4 artifact-diff contract packet",
    "- name: Self-test current Phase 4 artifact-diff determinism checker",
    "- name: Check current Phase 4 artifact-diff determinism packet",
    "- name: Self-test current Phase 4 artifact-diff validator replay checker",
    "- name: Check current Phase 4 artifact-diff validator replay packet",
)
STEP_BOUNDARY_AFTER = "- name: Validate current Phase 6 helper packet"

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/artifact_diff.py --self-test",
    "run: python3 scripts/zigux/check-artifact-diff-contract.py --self-test",
    "run: python3 scripts/zigux/check-artifact-diff-contract.py",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
)

REQUIRED_SURVEY_MARKERS = (
    "* `scripts/zigux/artifact_diff.py` is directly readable on current `master`",
    "* `scripts/zigux/check-artifact-diff-contract.py` is also directly readable again on current `master`",
    "* `.github/workflows/zigux-bootstrap.yml` keeps the directly readable artifact-diff packet reviewable through separate named steps",
    "* `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test`",
    "* `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py`",
)

REQUIRED_NOTE_MARKERS = (
    "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.",
    "Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, and `scripts/zigux/check-phase4-artifact-diff-determinism.py`",
    "The remaining shared reminder follow-up from the older mixed-readback packet is now narrower:",
)


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise AssertionError(f"required file missing: {path}") from exc


def write_text(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def line_index(text: str, marker: str) -> int:
    for index, line in enumerate(text.splitlines()):
        if line.strip() == marker:
            return index
    raise AssertionError(f"marker line not found: {marker}")


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def insert_after_exact_line(text: str, marker: str, addition: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, addition)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel.as_posix()))

    workflow = read_text(root, WORKFLOW)
    survey = read_text(root, SURVEY)
    note = read_text(root, NOTE)

    packet_lines = (STEP_BOUNDARY_BEFORE, *REQUIRED_STEP_NAMES, STEP_BOUNDARY_AFTER)
    for marker in packet_lines:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_STEP", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_STEP", f"{marker}:count={count}"))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    if not any(code in {"MISSING_WORKFLOW_STEP", "DUPLICATE_WORKFLOW_STEP"} for code, _ in issues):
        positions = [line_index(workflow, marker) for marker in packet_lines]
        if positions != sorted(positions):
            issues.append(("MISORDERED_WORKFLOW_PACKET", "phase4 artifact-diff packet order drifted"))
        else:
            lines = workflow.splitlines()
            slice_lines = lines[positions[0] : positions[-1] + 1]
            slice_step_count = sum(1 for line in slice_lines if line.strip().startswith("- name: "))
            expected_step_count = len(packet_lines)
            if slice_step_count != expected_step_count:
                issues.append(
                    (
                        "NONCONTIGUOUS_WORKFLOW_PACKET",
                        f"expected {expected_step_count} step headers between packet boundaries, saw {slice_step_count}",
                    )
                )

    for marker in REQUIRED_SURVEY_MARKERS:
        if marker not in survey:
            issues.append(("MISSING_SURVEY_MARKER", marker))

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note:
            issues.append(("MISSING_NOTE_MARKER", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE4_BOOTSTRAP_ARTIFACT_DIFF_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    workflow_lines = [
        "name: zigux-bootstrap",
        STEP_BOUNDARY_BEFORE,
        "  run: make -C zigux phase4-test",
        REQUIRED_STEP_NAMES[0],
        "  run: python3 scripts/zigux/artifact_diff.py --self-test",
        REQUIRED_STEP_NAMES[1],
        "  run: python3 scripts/zigux/check-artifact-diff-contract.py --self-test",
        REQUIRED_STEP_NAMES[2],
        "  run: python3 scripts/zigux/check-artifact-diff-contract.py",
        REQUIRED_STEP_NAMES[3],
        "  run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
        REQUIRED_STEP_NAMES[4],
        "  run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py",
        REQUIRED_STEP_NAMES[5],
        "  run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test",
        REQUIRED_STEP_NAMES[6],
        "  run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
        STEP_BOUNDARY_AFTER,
        "  run: make -C zigux phase6-validate",
    ]
    write_text(root, WORKFLOW, "\n".join(workflow_lines) + "\n")

    survey_lines = [
        "# Phase 4 Artifact-Diff Tooling Survey",
        *REQUIRED_SURVEY_MARKERS,
    ]
    write_text(root, SURVEY, "\n".join(survey_lines) + "\n")

    note_lines = [
        "# Phase 4 Reversible Delivery Evidence",
        *REQUIRED_NOTE_MARKERS,
    ]
    write_text(root, NOTE, "\n".join(note_lines) + "\n")

    for rel in REQUIRED_PATHS:
        if rel in {WORKFLOW, SURVEY, NOTE}:
            continue
        write_text(root, rel, "present\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_bootstrap_artifact_diff_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            WORKFLOW,
            replace_exact_line(
                read_text(root, WORKFLOW),
                REQUIRED_STEP_NAMES[2],
                "- name: Check current Phase 4 artifact-diff contract packet drifted",
            ),
        )
        assert ("MISSING_WORKFLOW_STEP", REQUIRED_STEP_NAMES[2]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), REQUIRED_STEP_NAMES[5]))
        assert ("DUPLICATE_WORKFLOW_STEP", f"{REQUIRED_STEP_NAMES[5]}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            WORKFLOW,
            insert_after_exact_line(
                read_text(root, WORKFLOW),
                REQUIRED_STEP_NAMES[6],
                "- name: Unexpected Phase 4 extra bootstrap step",
            ),
        )
        assert any(code == "NONCONTIGUOUS_WORKFLOW_PACKET" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        (root / REQUIRED_PATHS[-1]).unlink()
        assert ("MISSING_REQUIRED_PATH", REQUIRED_PATHS[-1].as_posix()) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            SURVEY,
            read_text(root, SURVEY).replace(REQUIRED_SURVEY_MARKERS[2] + "\n", "", 1),
        )
        assert ("MISSING_SURVEY_MARKER", REQUIRED_SURVEY_MARKERS[2]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            NOTE,
            read_text(root, NOTE).replace(REQUIRED_NOTE_MARKERS[1] + "\n", "", 1),
        )
        assert ("MISSING_NOTE_MARKER", REQUIRED_NOTE_MARKERS[1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            WORKFLOW,
            replace_exact_line(
                read_text(root, WORKFLOW),
                REQUIRED_WORKFLOW_LINES[6],
                "run: python3 scripts/zigux/validate-phase4.py",
            ),
        )
        assert ("MISSING_WORKFLOW_LINE", REQUIRED_WORKFLOW_LINES[6]) in collect_issues(root)
        checks += 1

    print("PHASE4_BOOTSTRAP_ARTIFACT_DIFF_PACKET_SELF_TEST=pass")
    print(f"PHASE4_BOOTSTRAP_ARTIFACT_DIFF_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current bootstrap Phase 4 artifact-diff packet in the Zigux workflow."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a current-like sample root and exit",
    )
    parser.add_argument("--self-test", action="store_true", help="run built-in checker tests")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE4_BOOTSTRAP_ARTIFACT_DIFF_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE4_BOOTSTRAP_ARTIFACT_DIFF_PACKET=pass")
    print(f"PHASE4_BOOTSTRAP_ARTIFACT_DIFF_PACKET_WORKFLOW_STEP_COUNT={len(REQUIRED_STEP_NAMES)}")
    print(f"PHASE4_BOOTSTRAP_ARTIFACT_DIFF_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE4_BOOTSTRAP_ARTIFACT_DIFF_PACKET_SURVEY_MARKER_COUNT={len(REQUIRED_SURVEY_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
