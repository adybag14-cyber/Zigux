#!/usr/bin/env python3
"""Guard the current Phase 1 route-summary workflow packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[3] if len(HERE.parents) > 3 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
ROUTE_SUMMARY_CHECKER_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")
MAKEFILE_REL = Path("zigux/Makefile")

REQUIRED_FILES = (
    WORKFLOW_REL,
    CLOSURE_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    VALIDATOR_REL,
    ROUTE_SUMMARY_CHECKER_REL,
    MAKEFILE_REL,
)

WORKFLOW_STEPS = (
    "      - name: Check current Phase 1 find-bit review packet",
    "      - name: Self-test current Phase 1 route summary checker",
    "      - name: Check current Phase 1 route summary packet",
    "      - name: Self-test current Phase 1 bench checker",
)

WORKFLOW_RUN_LINES = (
    "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
)

FORBIDDEN_WORKFLOW_RUN_LINES = (
    "        run: python3 scripts/zigux/check-phase1-bench.py",
)

CLOSURE_MARKERS = (
    "- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
    "The current bootstrap workflow also keeps the adjacent Phase 1 route-summary guard wired beside that same live reminder packet: `.github/workflows/zigux-bootstrap.yml` self-tests the directly readable Phase 1 direct-owner, string-review, route-summary, bench, shared-reminder, and closure-validator checks, replays the route-summary, direct-owner, string-review, shared-reminder, closure-validator, and shared tests-root smoke steps on current `master`, and currently keeps the bench checker at self-test coverage only.",
)

SCRIPTS_README_MARKERS = (
    "- `scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `.github/workflows/zigux-bootstrap.yml` keep the adjacent Phase 1 route-summary guard explicit beside the narrower reminder packet, so scripts-root follow-through can verify the returned non-Phase-1 Makefile route inventory without promoting the older Phase 1 wrappers back into shipped proof",
)

TESTS_README_MARKERS = (
    "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "  * current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof",
)

VALIDATOR_MARKERS = (
    'ROUTE_SUMMARY_CHECKER_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")',
    '"route_summary_guard": "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",',
)

MAKEFILE_MARKERS = (
    "phase1-route-summary:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py",
)

FORBIDDEN_MAKEFILE_MARKERS = (
    "phase1-validate:",
    "phase1-test:",
    "phase1-bench:",
    "phase1:",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker.strip())
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}"]


def require_absent(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker.strip())
    return [] if count == 0 else [f"{label}:expected_absent:actual_count={count}"]


def require_ordered(text: str, label: str, markers: tuple[str, ...]) -> list[str]:
    cursor = 0
    for marker in markers:
        index = text.find(marker, cursor)
        if index == -1:
            return [f"{label}:missing_or_out_of_order:{marker}"]
        cursor = index + len(marker)
    return []


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    workflow_text = read_text(root, WORKFLOW_REL)
    for marker in WORKFLOW_STEPS:
        failures.extend(require_exact_occurrence(workflow_text, f"{WORKFLOW_REL.as_posix()}:{marker}", marker))
    failures.extend(require_ordered(workflow_text, WORKFLOW_REL.as_posix(), WORKFLOW_STEPS))
    for marker in WORKFLOW_RUN_LINES:
        failures.extend(require_exact_occurrence(workflow_text, f"{WORKFLOW_REL.as_posix()}:{marker}", marker))
    failures.extend(require_ordered(workflow_text, f"{WORKFLOW_REL.as_posix()}:run_order", WORKFLOW_RUN_LINES))
    for marker in FORBIDDEN_WORKFLOW_RUN_LINES:
        failures.extend(require_absent(workflow_text, f"{WORKFLOW_REL.as_posix()}:{marker}", marker))

    closure_text = read_text(root, CLOSURE_REL)
    for marker in CLOSURE_MARKERS:
        failures.extend(require_exact_occurrence(closure_text, f"{CLOSURE_REL.as_posix()}:{marker}", marker))

    scripts_readme_text = read_text(root, SCRIPTS_README_REL)
    for marker in SCRIPTS_README_MARKERS:
        failures.extend(require_exact_occurrence(scripts_readme_text, f"{SCRIPTS_README_REL.as_posix()}:{marker}", marker))

    tests_readme_text = read_text(root, TESTS_README_REL)
    for marker in TESTS_README_MARKERS:
        failures.extend(require_exact_occurrence(tests_readme_text, f"{TESTS_README_REL.as_posix()}:{marker}", marker))

    validator_text = read_text(root, VALIDATOR_REL)
    for marker in VALIDATOR_MARKERS:
        failures.extend(require_exact_occurrence(validator_text, f"{VALIDATOR_REL.as_posix()}:{marker}", marker))

    makefile_text = read_text(root, MAKEFILE_REL)
    for marker in MAKEFILE_MARKERS:
        failures.extend(require_exact_occurrence(makefile_text, f"{MAKEFILE_REL.as_posix()}:{marker}", marker))
    for marker in FORBIDDEN_MAKEFILE_MARKERS:
        failures.extend(require_absent(makefile_text, f"{MAKEFILE_REL.as_posix()}:{marker}", marker))

    checker_text = read_text(root, ROUTE_SUMMARY_CHECKER_REL)
    failures.extend(
        require_exact_occurrence(
            checker_text,
            f"{ROUTE_SUMMARY_CHECKER_REL.as_posix()}:summary",
            '"""Guard the current Phase 1 route-summary packet across closure, Makefile, and workflow."""',
        )
    )

    return failures


def write_text(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_sample_root(root: Path) -> None:
    write_text(
        root,
        WORKFLOW_REL,
        "\n".join(
            [
                "jobs:",
                "  bootstrap:",
                "    steps:",
                *WORKFLOW_STEPS,
                *WORKFLOW_RUN_LINES,
                "      - name: Check current Phase 1 shared reminder packet",
            ]
        )
        + "\n",
    )
    write_text(root, CLOSURE_REL, "\n".join(CLOSURE_MARKERS) + "\n")
    write_text(root, SCRIPTS_README_REL, "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(root, TESTS_README_REL, "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(root, VALIDATOR_REL, "\n".join(VALIDATOR_MARKERS) + "\n")
    write_text(root, ROUTE_SUMMARY_CHECKER_REL, '"""Guard the current Phase 1 route-summary packet across closure, Makefile, and workflow."""\n')
    write_text(root, MAKEFILE_REL, "\n".join(MAKEFILE_MARKERS) + "\n")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing text: {old}")
    return text.replace(old, new, 1)


def mutate_remove(root: Path, relative_path: Path, marker: str) -> None:
    path = root / relative_path
    path.write_text(replace_once(path.read_text(encoding="utf-8"), marker + "\n", ""), encoding="utf-8")


def mutate_duplicate(root: Path, relative_path: Path, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(replace_once(text, marker, marker + "\n" + marker), encoding="utf-8")


def mutate_swap_workflow_steps(root: Path) -> None:
    path = root / WORKFLOW_REL
    text = path.read_text(encoding="utf-8")
    swapped = text.replace(WORKFLOW_STEPS[1] + "\n" + WORKFLOW_STEPS[2], WORKFLOW_STEPS[2] + "\n" + WORKFLOW_STEPS[1], 1)
    path.write_text(swapped, encoding="utf-8")


def mutate_add_forbidden_workflow_bench_run(root: Path) -> None:
    path = root / WORKFLOW_REL
    text = path.read_text(encoding="utf-8")
    path.write_text(text + FORBIDDEN_WORKFLOW_RUN_LINES[0] + "\n", encoding="utf-8")


def mutate_add_forbidden_makefile_route(root: Path) -> None:
    path = root / MAKEFILE_REL
    text = path.read_text(encoding="utf-8")
    path.write_text(text + "phase1-bench:\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [
        ("baseline", None),
        ("missing_workflow_file", ("unlink", WORKFLOW_REL)),
        ("missing_route_summary_step", ("remove", WORKFLOW_REL, WORKFLOW_STEPS[1])),
        ("duplicate_route_summary_step", ("duplicate", WORKFLOW_REL, WORKFLOW_STEPS[1])),
        ("swapped_route_summary_order", ("swap_workflow_steps",)),
        ("missing_route_summary_run", ("remove", WORKFLOW_REL, WORKFLOW_RUN_LINES[1])),
        ("forbidden_live_bench_run", ("forbidden_bench_run",)),
        ("missing_closure_marker", ("remove", CLOSURE_REL, CLOSURE_MARKERS[0])),
        ("missing_scripts_readme_marker", ("remove", SCRIPTS_README_REL, SCRIPTS_README_MARKERS[0])),
        ("missing_tests_readme_marker", ("remove", TESTS_README_REL, TESTS_README_MARKERS[0])),
        ("missing_validator_marker", ("remove", VALIDATOR_REL, VALIDATOR_MARKERS[0])),
        ("missing_makefile_route", ("remove", MAKEFILE_REL, MAKEFILE_MARKERS[0])),
        ("forbidden_makefile_route", ("forbidden_makefile_route",)),
        ("missing_checker_summary", ("remove", ROUTE_SUMMARY_CHECKER_REL, '"""Guard the current Phase 1 route-summary packet across closure, Makefile, and workflow."""')),
    ]

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-route-summary-workflow-") as tmpdir:
            root = Path(tmpdir)
            make_sample_root(root)
            if mutation is not None:
                kind = mutation[0]
                if kind == "unlink":
                    (root / mutation[1]).unlink()
                elif kind == "remove":
                    mutate_remove(root, mutation[1], mutation[2])
                elif kind == "duplicate":
                    mutate_duplicate(root, mutation[1], mutation[2])
                elif kind == "swap_workflow_steps":
                    mutate_swap_workflow_steps(root)
                elif kind == "forbidden_bench_run":
                    mutate_add_forbidden_workflow_bench_run(root)
                elif kind == "forbidden_makefile_route":
                    mutate_add_forbidden_makefile_route(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-route-summary-workflow-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-route-summary-workflow-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_ROUTE_SUMMARY_WORKFLOW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_ROUTE_SUMMARY_WORKFLOW_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    parser.add_argument("--write-sample-root", help="write a current-like sample root")
    args = parser.parse_args()

    if args.write_sample_root:
        root = Path(args.write_sample_root).resolve()
        make_sample_root(root)
        print(f"PHASE1_ROUTE_SUMMARY_WORKFLOW_PACKET_SAMPLE_ROOT={root}")
        return 0

    if args.self_test:
        return run_self_test()

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
        f"{len(WORKFLOW_STEPS) + len(WORKFLOW_RUN_LINES) + len(CLOSURE_MARKERS) + len(SCRIPTS_README_MARKERS) + len(TESTS_README_MARKERS) + len(VALIDATOR_MARKERS) + len(MAKEFILE_MARKERS) + 1}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())