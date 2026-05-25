#!/usr/bin/env python3
"""Guard the current Phase 1 bench self-test-only workflow posture."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

REQUIRED_FILES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase1-closure.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    ".github/workflows/zigux-bootstrap.yml",
)

FORBIDDEN_PRESENT_FILES = (
    "zigux/tests/fixtures/phase1_bench_expectations.json",
)

EXACT_LINE_MARKERS = {
    "Documentation/zigux/README.md": (
        "* `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.",
    ),
    "Documentation/zigux/phase1-closure.md": (
        "The current bootstrap workflow also keeps the adjacent Phase 1 route-summary guard wired beside that same live reminder packet: `.github/workflows/zigux-bootstrap.yml` self-tests the directly readable Phase 1 direct-owner, string-review, route-summary, bench, shared-reminder, and closure-validator checks, replays the route-summary, direct-owner, string-review, shared-reminder, closure-validator, and shared tests-root smoke steps on current `master`, and currently keeps the bench checker at self-test coverage only.",
    ),
    "scripts/zigux/README.md": (
        "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence",
        "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
    ),
    "zigux/tests/README.md": (
        "  * broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
    ),
    ".github/workflows/zigux-bootstrap.yml": (
        "- name: Self-test current Phase 1 bench checker",
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    ),
}

FORBIDDEN_EXACT_LINES = {
    ".github/workflows/zigux-bootstrap.yml": (
        "- name: Check current Phase 1 bench packet",
        "run: python3 scripts/zigux/check-phase1-bench.py",
        "run: zig build bench --build-file zigux/tests/build.zig",
        "run: make -C zigux phase1-bench",
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def count_exact_line_matches(text: str, marker: str) -> int:
    stripped_marker = marker.strip()
    return sum(1 for line in text.splitlines() if line.strip() == stripped_marker)


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path}")
    if failures:
        return failures

    for relative_path in FORBIDDEN_PRESENT_FILES:
        if (root / relative_path).exists():
            failures.append(f"unexpected_file:{relative_path}")

    for relative_path, markers in EXACT_LINE_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            count = count_exact_line_matches(text, marker)
            if count != 1:
                failures.append(
                    f"{relative_path}:marker_count:{marker}:expected=1:actual={count}"
                )

    for relative_path, markers in FORBIDDEN_EXACT_LINES.items():
        text = read_text(root, relative_path)
        for marker in markers:
            count = count_exact_line_matches(text, marker)
            if count != 0:
                failures.append(
                    f"{relative_path}:forbidden:{marker}:expected=0:actual={count}"
                )

    return failures


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        lines = list(EXACT_LINE_MARKERS.get(relative_path, ()))
        write_text(root, relative_path, "\n".join(lines) + ("\n" if lines else ""))


def remove_marker(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def duplicate_marker(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker, f"{marker}\n{marker}", 1), encoding="utf-8")


def add_forbidden_line(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text + marker + "\n", encoding="utf-8")


def add_forbidden_file(root: Path, relative_path: str) -> None:
    write_text(root, relative_path, "{}\n")


def run_self_test() -> int:
    cases: list[tuple[str, tuple[str, ...] | None]] = [("success", None)]

    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path}", ("missing_file", relative_path)))
    for relative_path, markers in EXACT_LINE_MARKERS.items():
        for marker in markers:
            cases.append((f"missing_marker:{relative_path}", ("remove", relative_path, marker)))
            cases.append(
                (f"duplicate_marker:{relative_path}", ("duplicate", relative_path, marker))
            )
    for relative_path, markers in FORBIDDEN_EXACT_LINES.items():
        for marker in markers:
            cases.append(
                (f"forbidden_marker:{relative_path}", ("forbidden_line", relative_path, marker))
            )
    for relative_path in FORBIDDEN_PRESENT_FILES:
        cases.append((f"forbidden_file:{relative_path}", ("forbidden_file", relative_path)))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-bench-workflow-posture-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if mutation:
                kind = mutation[0]
                if kind == "missing_file":
                    (root / mutation[1]).unlink()
                elif kind == "remove":
                    remove_marker(root, mutation[1], mutation[2])
                elif kind == "duplicate":
                    duplicate_marker(root, mutation[1], mutation[2])
                elif kind == "forbidden_line":
                    add_forbidden_line(root, mutation[1], mutation[2])
                elif kind == "forbidden_file":
                    add_forbidden_file(root, mutation[1])

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("PHASE1_BENCH_WORKFLOW_POSTURE_SELF_TEST=fail")
                    print("case=success")
                    print(f"actual={failures!r}")
                    return 1
            elif not failures:
                print("PHASE1_BENCH_WORKFLOW_POSTURE_SELF_TEST=fail")
                print(f"case={name}")
                print("actual=[]")
                return 1

    print("PHASE1_BENCH_WORKFLOW_POSTURE_SELF_TEST=pass")
    print(f"PHASE1_BENCH_WORKFLOW_POSTURE_SELF_TEST_CASE_COUNT={len(cases)}")
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
        print("PHASE1_BENCH_WORKFLOW_POSTURE=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_BENCH_WORKFLOW_POSTURE=pass")
    print(f"PHASE1_BENCH_WORKFLOW_POSTURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_BENCH_WORKFLOW_POSTURE_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in EXACT_LINE_MARKERS.values())}"
    )
    print(
        "PHASE1_BENCH_WORKFLOW_POSTURE_FORBIDDEN_FILE_COUNT="
        f"{len(FORBIDDEN_PRESENT_FILES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
