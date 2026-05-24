#!/usr/bin/env python3
"""Guard the current Lane 17 Phase 1 no-old-make-route packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

MAKEFILE_REL = Path("zigux/Makefile")
CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
TESTS_README_REL = Path("zigux/tests/README.md")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
ROUTE_SUMMARY_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")
CHECKER_REL = Path("scripts/zigux/check-phase1-make-route-viability.py")

REQUIRED_FILES = (
    MAKEFILE_REL,
    CLOSURE_REL,
    TESTS_README_REL,
    WORKFLOW_REL,
    ROUTE_SUMMARY_REL,
    CHECKER_REL,
)

MARKERS = {
    MAKEFILE_REL: (
        "phase1-route-summary:",
        "phase2-toolchain:",
        "phase2-tools:",
        "phase2-kconfig:",
        "phase2-cross:",
        "phase2-genksyms:",
        "phase3-validate:",
        "phase14-validate:",
    ),
    CLOSURE_REL: (
        "- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
        "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`, so treat the returned file as current repo evidence while those older Phase 1 wrapper names remain historical packet members rather than active closure proof.",
    ),
    TESTS_README_REL: (
        "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "  * current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof",
    ),
    WORKFLOW_REL: (
        "      - name: Self-test current Phase 1 route summary checker",
        "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        "      - name: Check current Phase 1 route summary packet",
        "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
        "      - name: Run current Phase 1 shared tests-root smoke",
        "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
    ROUTE_SUMMARY_REL: (
        '"""Guard the current Phase 1 route-summary packet across closure, Makefile, and workflow."""',
        'print("PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=pass")',
        'print("PHASE1_ROUTE_SUMMARY_COUNTS=pass")',
    ),
}

FORBIDDEN_MARKERS = {
    MAKEFILE_REL: (
        "phase1-validate:",
        "phase1-test:",
        "phase1-bench:",
        "phase1:",
    ),
    WORKFLOW_REL: (
        "        run: make -C zigux phase1-validate",
        "        run: make -C zigux phase1-test",
        "        run: make -C zigux phase1-bench",
        "        run: make -C zigux phase1",
    ),
}


def load_text(root: Path, relative: Path) -> str:
    return (root / relative).read_text(encoding="utf-8")


def write_text(root: Path, relative: Path, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_once(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker.strip())
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_absent(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker.strip())
    return [] if count == 0 else [f"{label}:expected=0:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.exists():
            failures.append(f"missing_file:{relative.as_posix()}")
        elif not path.is_file():
            failures.append(f"non_file_path:{relative.as_posix()}")
    if failures:
        return failures

    for relative, markers in MARKERS.items():
        text = load_text(root, relative)
        for marker in markers:
            failures.extend(require_once(text, f"{relative.as_posix()}:{marker}", marker))

    for relative, markers in FORBIDDEN_MARKERS.items():
        text = load_text(root, relative)
        for marker in markers:
            failures.extend(require_absent(text, f"{relative.as_posix()}:{marker}", marker))

    return failures


def sample_text(relative: Path) -> str:
    lines = list(MARKERS.get(relative, ()))
    if relative == WORKFLOW_REL:
        return "name: zigux-bootstrap\n\njobs:\n  bootstrap:\n    runs-on: ubuntu-latest\n    steps:\n" + "\n".join(lines) + "\n"
    return "\n".join(lines) + ("\n" if lines else "")


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    for relative in REQUIRED_FILES:
        write_text(root, relative, sample_text(relative))


def rewrite_once(text: str, old: str, new: str = "") -> str:
    if old not in text:
        raise AssertionError(f"missing sample marker: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-make-route-viability-") as tmpdir:
        root = Path(tmpdir)

        write_sample_root(root)
        if collect_failures(root):
            print("self-test:baseline_failed")
            return 1
        case_count += 1

        sample_root = root / "sample-root"
        write_sample_root(sample_root)
        if collect_failures(sample_root):
            print("self-test:written_sample_failed")
            return 1
        case_count += 1

        broken_root = root / "missing_checker"
        write_sample_root(broken_root)
        (broken_root / CHECKER_REL).unlink()
        failures = collect_failures(broken_root)
        if f"missing_file:{CHECKER_REL.as_posix()}" not in failures:
            print("self-test:missing_checker_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing_makefile_marker"
        write_sample_root(broken_root)
        write_text(
            broken_root,
            MAKEFILE_REL,
            rewrite_once(load_text(broken_root, MAKEFILE_REL), MARKERS[MAKEFILE_REL][0] + "\n"),
        )
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{MAKEFILE_REL.as_posix()}:{MARKERS[MAKEFILE_REL][0]}") for item in failures):
            print("self-test:missing_makefile_marker_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing_closure_marker"
        write_sample_root(broken_root)
        write_text(
            broken_root,
            CLOSURE_REL,
            rewrite_once(load_text(broken_root, CLOSURE_REL), MARKERS[CLOSURE_REL][2] + "\n"),
        )
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{CLOSURE_REL.as_posix()}:{MARKERS[CLOSURE_REL][2]}") for item in failures):
            print("self-test:missing_closure_marker_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing_tests_readme_marker"
        write_sample_root(broken_root)
        write_text(
            broken_root,
            TESTS_README_REL,
            rewrite_once(load_text(broken_root, TESTS_README_REL), MARKERS[TESTS_README_REL][1] + "\n"),
        )
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{TESTS_README_REL.as_posix()}:{MARKERS[TESTS_README_REL][1]}") for item in failures):
            print("self-test:missing_tests_readme_marker_not_detected")
            return 1
        case_count += 1

        broken_root = root / "duplicate_workflow_marker"
        write_sample_root(broken_root)
        workflow_text = load_text(broken_root, WORKFLOW_REL)
        duplicate = workflow_text.replace(
            MARKERS[WORKFLOW_REL][1],
            MARKERS[WORKFLOW_REL][1] + "\n" + MARKERS[WORKFLOW_REL][1],
            1,
        )
        write_text(broken_root, WORKFLOW_REL, duplicate)
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{WORKFLOW_REL.as_posix()}:{MARKERS[WORKFLOW_REL][1]}") for item in failures):
            print("self-test:duplicate_workflow_marker_not_detected")
            return 1
        case_count += 1

        broken_root = root / "forbidden_make_route"
        write_sample_root(broken_root)
        write_text(
            broken_root,
            MAKEFILE_REL,
            load_text(broken_root, MAKEFILE_REL) + FORBIDDEN_MARKERS[MAKEFILE_REL][0] + "\n",
        )
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{MAKEFILE_REL.as_posix()}:{FORBIDDEN_MARKERS[MAKEFILE_REL][0]}") for item in failures):
            print("self-test:forbidden_make_route_not_detected")
            return 1
        case_count += 1

        broken_root = root / "forbidden_workflow_make_route"
        write_sample_root(broken_root)
        write_text(
            broken_root,
            WORKFLOW_REL,
            load_text(broken_root, WORKFLOW_REL) + FORBIDDEN_MARKERS[WORKFLOW_REL][0] + "\n",
        )
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{WORKFLOW_REL.as_posix()}:{FORBIDDEN_MARKERS[WORKFLOW_REL][0]}") for item in failures):
            print("self-test:forbidden_workflow_make_route_not_detected")
            return 1
        case_count += 1

    print("PHASE1_MAKE_ROUTE_VIABILITY_SELF_TEST=pass")
    print(f"PHASE1_MAKE_ROUTE_VIABILITY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE1_MAKE_ROUTE_VIABILITY_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = collect_failures(args.root.resolve())
    if failures:
        print("PHASE1_MAKE_ROUTE_VIABILITY=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_MAKE_ROUTE_VIABILITY=pass")
    print(f"PHASE1_MAKE_ROUTE_VIABILITY_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_MAKE_ROUTE_VIABILITY_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in MARKERS.values())}"
    )
    print(
        "PHASE1_MAKE_ROUTE_VIABILITY_FORBIDDEN_MARKER_COUNT="
        f"{sum(len(markers) for markers in FORBIDDEN_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
