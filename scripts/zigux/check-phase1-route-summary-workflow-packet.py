#!/usr/bin/env python3
"""Guard the current Phase 1 route-summary workflow packet against drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = "Documentation/zigux/phase1-closure.md"
SCRIPTS_README_REL = "scripts/zigux/README.md"
VALIDATOR_REL = "scripts/zigux/validate-phase1-closure.py"
ROUTE_SUMMARY_CHECKER_REL = "scripts/zigux/check-phase1-route-summary-counts.py"
MAKEFILE_REL = "zigux/Makefile"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    SCRIPTS_README_REL,
    VALIDATOR_REL,
    ROUTE_SUMMARY_CHECKER_REL,
    MAKEFILE_REL,
    WORKFLOW_REL,
)

EXACT_LINE_MARKERS = {
    PHASE1_CLOSURE_REL: (
        "- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
        "The current bootstrap workflow also keeps the adjacent Phase 1 route-summary guard wired beside that same live reminder packet: `.github/workflows/zigux-bootstrap.yml` self-tests the directly readable Phase 1 direct-owner, string-review, route-summary, bench, shared-reminder, and closure-validator checks, replays the route-summary, direct-owner, string-review, shared-reminder, closure-validator, and shared tests-root smoke steps on current `master`, and currently keeps the bench checker at self-test coverage only.",
    ),
    SCRIPTS_README_REL: (
        "- `scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `.github/workflows/zigux-bootstrap.yml` keep the adjacent Phase 1 route-summary guard explicit beside the narrower reminder packet, so scripts-root follow-through can verify the returned non-Phase-1 Makefile route inventory without promoting the older Phase 1 wrappers back into shipped proof",
    ),
    VALIDATOR_REL: (
        'ROUTE_SUMMARY_CHECKER_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")',
        '(ROUTE_SUMMARY_CHECKER_REL, "phase1-route-summary-counts"),',
    ),
    ROUTE_SUMMARY_CHECKER_REL: (
        '"""Guard the current Phase 1 route-summary packet across closure, Makefile, and workflow."""',
        'print("PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=pass")',
        'print("PHASE1_ROUTE_SUMMARY_COUNTS=pass")',
    ),
    MAKEFILE_REL: (
        "phase1-route-summary:",
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py",
    ),
    WORKFLOW_REL: (
        "      - name: Check current Phase 1 find-bit review packet",
        "        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
        "      - name: Self-test current Phase 1 route summary checker",
        "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        "      - name: Check current Phase 1 route summary packet",
        "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
        "      - name: Self-test current Phase 1 bench checker",
        "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    ),
}

FORBIDDEN_EXACT_LINES = {
    MAKEFILE_REL: (
        "phase1-validate:",
        "phase1-test:",
        "phase1-bench:",
        "phase1:",
    ),
    WORKFLOW_REL: (
        "        run: make -C zigux phase1-route-summary",
        "        run: python3 scripts/zigux/check-phase1-bench.py",
    ),
}

WORKFLOW_CHAIN = (
    "      - name: Check current Phase 1 find-bit review packet",
    "      - name: Self-test current Phase 1 route summary checker",
    "      - name: Check current Phase 1 route summary packet",
    "      - name: Self-test current Phase 1 bench checker",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_line(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker.strip())
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_absent_line(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker.strip())
    return [] if count == 0 else [f"{label}:expected=0:actual={count}"]


def require_adjacent_chain(text: str, label: str, markers: tuple[str, ...]) -> list[str]:
    lines = text.splitlines()
    indexes: list[int] = []
    for marker in markers:
        matches = [idx for idx, line in enumerate(lines) if line.strip() == marker.strip()]
        if len(matches) != 1:
            return [f"{label}:missing:{'->'.join(markers)}"]
        indexes.append(matches[0])
    for previous, current in zip(indexes, indexes[1:]):
        if current != previous + 2:
            return [f"{label}:missing:{'->'.join(markers)}"]
    return []


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path}")
    if failures:
        return failures

    for relative_path, markers in EXACT_LINE_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            failures.extend(require_exact_line(text, f"{relative_path}:{marker}", marker))

    for relative_path, markers in FORBIDDEN_EXACT_LINES.items():
        text = read_text(root, relative_path)
        for marker in markers:
            failures.extend(require_absent_line(text, f"{relative_path}:{marker}", marker))

    failures.extend(
        require_adjacent_chain(
            read_text(root, WORKFLOW_REL),
            "workflow_adjacent_chain",
            WORKFLOW_CHAIN,
        )
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


def add_line(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    text += marker + "\n"
    path.write_text(text, encoding="utf-8")


def move_route_summary_pair_after_bench(root: Path) -> None:
    path = root / WORKFLOW_REL
    lines = path.read_text(encoding="utf-8").splitlines()
    pair = [
        "      - name: Self-test current Phase 1 route summary checker",
        "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        "      - name: Check current Phase 1 route summary packet",
        "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    ]
    bench = [
        "      - name: Self-test current Phase 1 bench checker",
        "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    ]
    if pair[0] not in lines or bench[0] not in lines:
        raise ValueError("sample workflow missing route-summary or bench markers")
    pair_start = lines.index(pair[0])
    del lines[pair_start : pair_start + len(pair)]
    bench_start = lines.index(bench[0])
    insert_at = bench_start + len(bench)
    lines[insert_at:insert_at] = pair
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases = [("success", None)]
    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path}", ("missing_file", relative_path)))
    for relative_path, markers in EXACT_LINE_MARKERS.items():
        for marker in markers:
            cases.append((f"missing_marker:{relative_path}", ("remove", relative_path, marker)))
            cases.append((f"duplicate_marker:{relative_path}", ("duplicate", relative_path, marker)))
    for relative_path, markers in FORBIDDEN_EXACT_LINES.items():
        for marker in markers:
            cases.append((f"forbidden_marker:{relative_path}", ("forbidden", relative_path, marker)))
    cases.append(("workflow_chain_missing", ("workflow_chain_missing",)))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-route-summary-workflow-") as tmpdir:
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
                elif kind == "forbidden":
                    add_line(root, mutation[1], mutation[2])
                elif kind == "workflow_chain_missing":
                    move_route_summary_pair_after_bench(root)
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

    print("PHASE1_ROUTE_SUMMARY_WORKFLOW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_ROUTE_SUMMARY_WORKFLOW_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def write_sample_root(destination: Path) -> None:
    build_sample_repo(destination)
    print(f"PHASE1_ROUTE_SUMMARY_WORKFLOW_PACKET_SAMPLE_ROOT={destination}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    parser.add_argument("--write-sample-root", help="write a passing sample tree")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        destination = Path(args.write_sample_root).resolve()
        build_sample_repo(destination)
        print(f"PHASE1_ROUTE_SUMMARY_WORKFLOW_PACKET_SAMPLE_ROOT={destination}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_ROUTE_SUMMARY_WORKFLOW_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_ROUTE_SUMMARY_WORKFLOW_PACKET=pass")
    print(f"PHASE1_ROUTE_SUMMARY_WORKFLOW_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_ROUTE_SUMMARY_WORKFLOW_PACKET_REQUIRED_LINE_COUNT="
        f"{sum(len(markers) for markers in EXACT_LINE_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
