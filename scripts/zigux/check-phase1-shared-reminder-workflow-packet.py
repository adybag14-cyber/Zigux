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

MARKERS = {
    "Documentation/zigux/phase1-closure.md": (
        "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
        "The current bootstrap workflow also keeps the adjacent Phase 1 route-summary guard wired beside that same live reminder packet: `.github/workflows/zigux-bootstrap.yml` self-tests the directly readable Phase 1 direct-owner, string-review, route-summary, bench, shared-reminder, and closure-validator checks, replays the route-summary, direct-owner, string-review, shared-reminder, closure-validator, and shared tests-root smoke steps on current `master`, and currently keeps the bench checker at self-test coverage only.",
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
    ".github/workflows/zigux-bootstrap.yml": (
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
        "run: python3 scripts/zigux/validate-phase1-closure.py",
    ),
}

FORBIDDEN_FRAGMENTS = (
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --write-sample-root",
    "run: python3 scripts/zigux/validate-phase1-closure.py --write-sample-root",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [relative_path for relative_path in REQUIRED_FILES if not (root / relative_path).exists()]


def collect_exact_markers(text: str, label: str, markers: tuple[str, ...]) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append(f"{label}:{marker}:expected=1:actual={count}")
    return issues


def collect_stripped_line_markers(text: str, label: str, markers: tuple[str, ...]) -> list[str]:
    issues: list[str] = []
    lines = text.splitlines()
    for marker in markers:
        count = sum(1 for line in lines if line.strip() == marker)
        if count != 1:
            issues.append(f"{label}:{marker}:expected=1:actual={count}")
    return issues


def collect_forbidden_fragments(text: str, label: str) -> list[str]:
    issues: list[str] = []
    for fragment in FORBIDDEN_FRAGMENTS:
        count = text.count(fragment)
        if count:
            issues.append(f"{label}:forbidden:{fragment}:actual={count}")
    return issues


def collect_issues(root: Path) -> list[str]:
    issues = [f"missing_file:{relative_path}" for relative_path in collect_missing_files(root)]
    if issues:
        return issues

    for relative_path, markers in MARKERS.items():
        text = read_text(root, relative_path)
        if relative_path == ".github/workflows/zigux-bootstrap.yml":
            issues.extend(collect_stripped_line_markers(text, relative_path, markers))
        else:
            issues.extend(collect_exact_markers(text, relative_path, markers))
        issues.extend(collect_forbidden_fragments(text, relative_path))
    return issues


def write_text(root: Path, relative_path: str, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        markers = MARKERS.get(relative_path, ())
        write_text(root, relative_path, "\n".join(markers) + ("\n" if markers else ""))


def remove_marker(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def duplicate_marker(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def append_forbidden_fragment(root: Path, relative_path: str, fragment: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text + fragment + "\n", encoding="utf-8")


def write_sample_root(path: Path) -> None:
    build_sample_repo(path)


def run_self_test() -> int:
    cases: list[tuple[str, object]] = [("success", None)]

    for relative_path in REQUIRED_FILES:
        cases.append(
            (
                f"missing_file:{relative_path}",
                lambda root, relative_path=relative_path: (root / relative_path).unlink(),
            )
        )

    for relative_path, markers in MARKERS.items():
        for marker in markers:
            cases.append(
                (
                    f"remove:{relative_path}:{marker}",
                    lambda root, relative_path=relative_path, marker=marker: remove_marker(
                        root, relative_path, marker
                    ),
                )
            )
            cases.append(
                (
                    f"duplicate:{relative_path}:{marker}",
                    lambda root, relative_path=relative_path, marker=marker: duplicate_marker(
                        root, relative_path, marker
                    ),
                )
            )

    for fragment in FORBIDDEN_FRAGMENTS:
        cases.append(
            (
                f"forbidden:{fragment}",
                lambda root, fragment=fragment: append_forbidden_fragment(
                    root, ".github/workflows/zigux-bootstrap.yml", fragment
                ),
            )
        )

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-shared-reminder-workflow-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutate is not None:
                mutate(root)
            issues = collect_issues(root)
            if name == "success":
                if issues:
                    print("self-test:success:unexpected_failures")
                    for issue in issues:
                        print(issue)
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
        help="write a synthetic current-like tree for local validation",
    )
    args = parser.parse_args()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    if args.self_test:
        return run_self_test()

    root = repo_root(args.root)
    issues = collect_issues(root)
    if issues:
        print("PHASE1_SHARED_REMINDER_WORKFLOW_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE1_SHARED_REMINDER_WORKFLOW_PACKET=pass")
    print(f"PHASE1_SHARED_REMINDER_WORKFLOW_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_SHARED_REMINDER_WORKFLOW_PACKET_REQUIRED_LINE_COUNT="
        f"{sum(len(markers) for markers in MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
