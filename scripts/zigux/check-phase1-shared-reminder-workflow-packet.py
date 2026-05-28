#!/usr/bin/env python3
"""Guard the live Phase 1 shared-reminder workflow packet against drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

REQUIRED_FILES = (
    "Documentation/zigux/phase1-closure.md",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "scripts/zigux/validate-phase1-closure.py",
    ".github/workflows/zigux-bootstrap.yml",
)

EXACT_MARKERS = {
    "Documentation/zigux/phase1-closure.md": (
        "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "- `scripts/zigux/validate-phase1-closure.py`",
        "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    ),
    "scripts/zigux/check-phase1-shared-reminder-packet.py": (
        "\"\"\"Guard the current shared Phase 1 reminder packet across docs, tests, scripts, and workflow.\"\"\"",
        'print("PHASE1_SHARED_REMINDER_PACKET=pass")',
        'print("PHASE1_SHARED_REMINDER_PACKET_SELF_TEST=pass")',
    ),
    "scripts/zigux/validate-phase1-closure.py": (
        '(SHARED_REMINDER_CHECKER_REL, "phase1-shared-reminder-packet"),',
        'print("PHASE1_CLOSURE_SELF_TEST=pass")',
        'print("PHASE1_CLOSURE_VALIDATION=pass")',
    ),
}

REQUIRED_WORKFLOW_RUN_LINES = (
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
)

FORBIDDEN_WORKFLOW_FRAGMENTS = (
    "run: python3 scripts/zigux/check-phase1-shared-reminder-workflow-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-workflow-packet.py",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --write-sample-root",
    "run: python3 scripts/zigux/validate-phase1-closure.py --write-sample-root",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [relative_path for relative_path in REQUIRED_FILES if not (root / relative_path).is_file()]


def collect_exact_markers(text: str, label: str, markers: tuple[str, ...]) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append(f"{label}:marker_count:{count}:{marker}")
    return issues


def collect_workflow_issues(text: str) -> list[str]:
    issues: list[str] = []
    lines = text.splitlines()
    positions: list[int] = []
    for marker in REQUIRED_WORKFLOW_RUN_LINES:
        matching_positions = [index for index, line in enumerate(lines) if line.strip() == marker]
        if len(matching_positions) != 1:
            issues.append(
                ".github/workflows/zigux-bootstrap.yml:"
                f"workflow_marker_count:{len(matching_positions)}:{marker}"
            )
            continue
        positions.append(matching_positions[0])

    if len(positions) == len(REQUIRED_WORKFLOW_RUN_LINES):
        if positions != sorted(positions):
            issues.append(".github/workflows/zigux-bootstrap.yml:workflow_order:out_of_order")

    for fragment in FORBIDDEN_WORKFLOW_FRAGMENTS:
        count = text.count(fragment)
        if count != 0:
            issues.append(
                ".github/workflows/zigux-bootstrap.yml:"
                f"forbidden_fragment:{count}:{fragment}"
            )
    return issues


def collect_issues(root: Path) -> list[str]:
    issues = [f"missing_file:{relative_path}" for relative_path in collect_missing_files(root)]
    if issues:
        return issues

    for relative_path, markers in EXACT_MARKERS.items():
        issues.extend(collect_exact_markers(read_text(root, relative_path), relative_path, markers))
    issues.extend(collect_workflow_issues(read_text(root, ".github/workflows/zigux-bootstrap.yml")))
    return issues


def build_sample_root(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root, relative_path, "")

    for relative_path, markers in EXACT_MARKERS.items():
        write_text(root, relative_path, "\n".join(markers) + "\n")

    write_text(
        root,
        ".github/workflows/zigux-bootstrap.yml",
        "\n".join(REQUIRED_WORKFLOW_RUN_LINES) + "\n",
    )


def remove_first_line(root: Path, relative_path: str, needle: str) -> None:
    text = read_text(root, relative_path)
    updated = text.replace(needle + "\n", "", 1)
    write_text(root, relative_path, updated)


def duplicate_line(root: Path, relative_path: str, needle: str) -> None:
    text = read_text(root, relative_path)
    updated = text.replace(needle, needle + "\n" + needle, 1)
    write_text(root, relative_path, updated)


def append_line(root: Path, relative_path: str, line: str) -> None:
    write_text(root, relative_path, read_text(root, relative_path) + line + "\n")


def reverse_workflow_packet(root: Path) -> None:
    reversed_lines = "\n".join(reversed(REQUIRED_WORKFLOW_RUN_LINES)) + "\n"
    write_text(root, ".github/workflows/zigux-bootstrap.yml", reversed_lines)


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [("baseline", None)]

    for relative_path in REQUIRED_FILES:
        cases.append(
            (
                f"missing_file:{relative_path}",
                lambda root, relative_path=relative_path: (root / relative_path).unlink(),
            )
        )

    for relative_path, markers in EXACT_MARKERS.items():
        for marker in markers:
            cases.append(
                (
                    f"remove:{relative_path}:{marker}",
                    lambda root, relative_path=relative_path, marker=marker: remove_first_line(
                        root, relative_path, marker
                    ),
                )
            )
            cases.append(
                (
                    f"duplicate:{relative_path}:{marker}",
                    lambda root, relative_path=relative_path, marker=marker: duplicate_line(
                        root, relative_path, marker
                    ),
                )
            )

    for marker in REQUIRED_WORKFLOW_RUN_LINES:
        cases.append(
            (
                f"remove_workflow:{marker}",
                lambda root, marker=marker: remove_first_line(
                    root, ".github/workflows/zigux-bootstrap.yml", marker
                ),
            )
        )
        cases.append(
            (
                f"duplicate_workflow:{marker}",
                lambda root, marker=marker: duplicate_line(
                    root, ".github/workflows/zigux-bootstrap.yml", marker
                ),
            )
        )

    cases.append(("reversed_workflow_packet", reverse_workflow_packet))

    for fragment in FORBIDDEN_WORKFLOW_FRAGMENTS:
        cases.append(
            (
                f"forbidden:{fragment}",
                lambda root, fragment=fragment: append_line(
                    root, ".github/workflows/zigux-bootstrap.yml", fragment
                ),
            )
        )

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-shared-reminder-workflow-") as tmpdir:
            root = Path(tmpdir)
            build_sample_root(root)
            if mutate is not None:
                mutate(root)
            issues = collect_issues(root)
            if name == "baseline":
                if issues:
                    print(f"self-test:{name}:unexpected={issues}")
                    return 1
            elif not issues:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_SHARED_REMINDER_WORKFLOW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_SHARED_REMINDER_WORKFLOW_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root used for checks")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    parser.add_argument(
        "--write-sample-root",
        help="write a synthetic current-like tree for local replay",
    )
    args = parser.parse_args()

    if args.write_sample_root:
        build_sample_root(Path(args.write_sample_root).resolve())
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(repo_root(args.root))
    if issues:
        print("PHASE1_SHARED_REMINDER_WORKFLOW_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE1_SHARED_REMINDER_WORKFLOW_PACKET=pass")
    print(f"PHASE1_SHARED_REMINDER_WORKFLOW_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_SHARED_REMINDER_WORKFLOW_PACKET_REQUIRED_STEP_COUNT="
        f"{len(REQUIRED_WORKFLOW_RUN_LINES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
