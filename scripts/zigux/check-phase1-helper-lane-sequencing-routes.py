#!/usr/bin/env python3
"""Guard the Phase 1 helper-lane-sequencing workflow and scripts-root packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

HELPER_CHECKER_REL = "scripts/zigux/check-phase1-helper-lane-sequencing.py"
SCRIPTS_README_REL = "scripts/zigux/README.md"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_FILES = (
    HELPER_CHECKER_REL,
    SCRIPTS_README_REL,
    WORKFLOW_REL,
)

EXACT_LINE_MARKERS = {
    SCRIPTS_README_REL: (
        "- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live owner-map, string-review, and helper-lane-sequencing guards instead of rebuilding the broader installer-backed closure packet from older missing routes",
        "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-helper-lane-sequencing.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
        "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-helper-lane-sequencing.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, helper-lane-sequencing, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
    ),
    WORKFLOW_REL: (
        "- name: Self-test current Phase 1 helper-lane sequencing checker",
        "run: python3 scripts/zigux/check-phase1-helper-lane-sequencing.py --self-test",
        "- name: Check current Phase 1 helper-lane sequencing packet",
        "run: python3 scripts/zigux/check-phase1-helper-lane-sequencing.py",
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_line(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker.strip())
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        path = root / relative_path
        if path.is_dir():
            failures.append(f"directory_path:{relative_path}")
            continue
        if not path.is_file():
            failures.append(f"missing_file:{relative_path}")
    if failures:
        return failures

    for relative_path, markers in EXACT_LINE_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            failures.extend(
                require_exact_line(text, f"{relative_path}:{marker}", marker)
            )

    return failures


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_text(root, HELPER_CHECKER_REL, "# sample helper checker\n")
    for relative_path, markers in EXACT_LINE_MARKERS.items():
        write_text(root, relative_path, "\n".join(markers) + "\n")


def remove_marker(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker.strip():
            del lines[idx]
            path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
            return
    raise ValueError(f"missing marker: {relative_path}: {marker}")


def duplicate_marker(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker.strip():
            lines.insert(idx + 1, line)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(f"missing marker: {relative_path}: {marker}")


def replace_with_directory(root: Path, relative_path: str) -> None:
    path = root / relative_path
    if path.is_file():
        path.unlink()
    path.mkdir(parents=True, exist_ok=True)


def run_self_test() -> int:
    cases = [("success", None)]
    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path}", ("missing_file", relative_path)))
        cases.append((f"directory_path:{relative_path}", ("directory_path", relative_path)))
    for relative_path, markers in EXACT_LINE_MARKERS.items():
        for marker in markers:
            cases.append((f"missing_marker:{relative_path}", ("remove", relative_path, marker)))
            cases.append(
                (f"duplicate_marker:{relative_path}", ("duplicate", relative_path, marker))
            )

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-helper-lane-routes-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutation:
                kind = mutation[0]
                if kind == "missing_file":
                    (root / mutation[1]).unlink()
                elif kind == "directory_path":
                    replace_with_directory(root, mutation[1])
                elif kind == "remove":
                    remove_marker(root, mutation[1], mutation[2])
                elif kind == "duplicate":
                    duplicate_marker(root, mutation[1], mutation[2])
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

    print("PHASE1_HELPER_LANE_SEQUENCING_ROUTES_SELF_TEST=pass")
    print(f"PHASE1_HELPER_LANE_SEQUENCING_ROUTES_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_HELPER_LANE_SEQUENCING_ROUTES=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_HELPER_LANE_SEQUENCING_ROUTES=pass")
    print(f"PHASE1_HELPER_LANE_SEQUENCING_ROUTES_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_HELPER_LANE_SEQUENCING_ROUTES_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in EXACT_LINE_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
