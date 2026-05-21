#!/usr/bin/env python3
"""Guard the current Phase 1 bench workflow posture across reminder surfaces."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

REQUIRED_FILES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase1-bench.py",
    "zigux/tests/README.md",
    ".github/workflows/zigux-bootstrap.yml",
)

MARKERS = {
    "Documentation/zigux/README.md": (
        "- `scripts/zigux/check-phase1-bench.py` keep the live owner map, the restored closure note and closure validator, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.",
        "* `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.",
    ),
    "Documentation/zigux/phase1-closure.md": (
        "The current bootstrap workflow also keeps the adjacent Phase 1 route-summary guard wired beside that same live reminder packet: `.github/workflows/zigux-bootstrap.yml` self-tests the directly readable Phase 1 direct-owner, string-review, route-summary, bench, shared-reminder, and closure-validator checks, replays the route-summary, direct-owner, string-review, shared-reminder, closure-validator, and shared tests-root smoke steps on current `master`, and currently keeps the bench checker at self-test coverage only.",
        "- `PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`",
    ),
    "Documentation/zigux/review-checklist.md": (
        "`Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet",
    ),
    "scripts/zigux/README.md": (
        "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
        "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
    ),
    "scripts/zigux/check-phase1-bench.py": (
        "EXPECTATIONS = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"phase1_bench_expectations.json\"",
        'print("PHASE1_BENCH_CHECK_SELF_TEST=pass")',
        'print("PHASE1_BENCH_CHECK=pass")',
    ),
    "zigux/tests/README.md": (
        "- `scripts/zigux/check-phase1-bench.py`",
        "Tests-root reviewer prompt:",
        "- Does the bounded Phase 1 reminder keep the restored closure note, the workflow-backed closure-validator and shipped checker packet, the shared tests-root smoke route, the manifest-backed owner map, the broader-companion wording for the validator-first, parity, bench-replay, and helper-replay family, and the historical-gap wording for the missing Phase 1 Makefile routes aligned without widening back into the older full closure stack?",
    ),
}

WORKFLOW_REQUIRED_LINES = (
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
    "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
)

WORKFLOW_FORBIDDEN_LINES = (
    "run: python3 scripts/zigux/check-phase1-bench.py",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_file_failures(root: Path) -> list[str]:
    return [f"missing_file:{path}" for path in REQUIRED_FILES if not (root / path).is_file()]


def require_exact_fragment(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_line(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_absent_line(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker)
    return [] if count == 0 else [f"{label}:expected=0:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    failures = collect_file_failures(root)
    if failures:
        return failures

    for relative_path, markers in MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            failures.extend(require_exact_fragment(text, f"{relative_path}:{marker}", marker))

    workflow_text = read_text(root, ".github/workflows/zigux-bootstrap.yml")
    for marker in WORKFLOW_REQUIRED_LINES:
        failures.extend(require_exact_line(workflow_text, f"workflow:{marker}", marker))
    for marker in WORKFLOW_FORBIDDEN_LINES:
        failures.extend(require_absent_line(workflow_text, f"workflow:{marker}", marker))

    return failures


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        if relative_path == ".github/workflows/zigux-bootstrap.yml":
            write_text(root, relative_path, "\n".join(WORKFLOW_REQUIRED_LINES) + "\n")
            continue
        lines = list(MARKERS.get(relative_path, ()))
        write_text(root, relative_path, "\n".join(lines) + ("\n" if lines else ""))


def remove_fragment(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    replaced = text.replace(marker + "\n", "", 1)
    if replaced == text:
        replaced = text.replace(marker, "", 1)
    path.write_text(replaced, encoding="utf-8")


def duplicate_fragment(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def remove_line(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker:
            del lines[idx]
            path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
            return
    raise ValueError(f"missing line: {marker}")


def duplicate_line(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(idx + 1, line)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(f"missing line: {marker}")


def append_line(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text + marker + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [("success", None)]
    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path}", ("missing_file", relative_path)))
    for relative_path, markers in MARKERS.items():
        for marker in markers:
            cases.append((f"remove:{relative_path}", ("remove_fragment", relative_path, marker)))
            cases.append((f"duplicate:{relative_path}", ("duplicate_fragment", relative_path, marker)))
    for marker in WORKFLOW_REQUIRED_LINES:
        cases.append((f"remove_workflow:{marker}", ("remove_line", ".github/workflows/zigux-bootstrap.yml", marker)))
        cases.append((f"duplicate_workflow:{marker}", ("duplicate_line", ".github/workflows/zigux-bootstrap.yml", marker)))
    for marker in WORKFLOW_FORBIDDEN_LINES:
        cases.append((f"forbidden_workflow:{marker}", ("append_line", ".github/workflows/zigux-bootstrap.yml", marker)))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-bench-workflow-posture-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutation:
                kind = mutation[0]
                if kind == "missing_file":
                    (root / mutation[1]).unlink()
                elif kind == "remove_fragment":
                    remove_fragment(root, mutation[1], mutation[2])
                elif kind == "duplicate_fragment":
                    duplicate_fragment(root, mutation[1], mutation[2])
                elif kind == "remove_line":
                    remove_line(root, mutation[1], mutation[2])
                elif kind == "duplicate_line":
                    duplicate_line(root, mutation[1], mutation[2])
                elif kind == "append_line":
                    append_line(root, mutation[1], mutation[2])
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
        f"{sum(len(markers) for markers in MARKERS.values()) + len(WORKFLOW_REQUIRED_LINES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
