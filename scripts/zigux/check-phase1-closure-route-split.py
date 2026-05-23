#!/usr/bin/env python3
"""Guard the current Phase 1 closure route-split packet on current master."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
DOCS_README_REL = Path("Documentation/zigux/README.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    PHASE1_LANE_NOTE_REL,
    DOCS_README_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    VALIDATOR_REL,
)

EXPECTED_MARKERS = {
    PHASE1_CLOSURE_REL: (
        "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
        "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
    ),
    PHASE1_LANE_NOTE_REL: (
        "`PHASE1_DIRECT_OWNER_SHARED_REMINDER_ROUTE_SPLIT=Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md now all carry the shipped bench-checker wording, while Documentation/zigux/phase1-closure.md plus scripts/zigux/validate-phase1-closure.py keep the restored closure-side packet explicit and the broader installer-backed, validator-first, bench-route, and replay names remain historical packet members until direct current-master rereads restore them`",
    ),
    DOCS_README_REL: (
        "`scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks",
    ),
    SCRIPTS_README_REL: (
        "`scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
        "`scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `.github/workflows/zigux-bootstrap.yml` keep the adjacent Phase 1 route-summary guard explicit beside the narrower reminder packet, so scripts-root follow-through can verify the returned non-Phase-1 Makefile route inventory without promoting the older Phase 1 wrappers back into shipped proof",
    ),
    TESTS_README_REL: (
        "* keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
        "* current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    ),
    VALIDATOR_REL: (
        "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
        "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
    ),
}


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{needle}"]


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    for relative_path, markers in EXPECTED_MARKERS.items():
        text = load_text(root, relative_path)
        for marker in markers:
            failures.extend(
                require_exact_occurrence(
                    text,
                    f"{relative_path.as_posix()}:required",
                    marker,
                )
            )

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture_tree(root: Path) -> None:
    for relative_path, markers in EXPECTED_MARKERS.items():
        write_text(root / relative_path, "\n".join(markers) + "\n")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [
        ("baseline", None),
        (
            "missing_route_split",
            lambda root: write_text(
                root / PHASE1_LANE_NOTE_REL,
                load_text(root, PHASE1_LANE_NOTE_REL).replace(
                    EXPECTED_MARKERS[PHASE1_LANE_NOTE_REL][0] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "stale_route_split",
            lambda root: write_text(
                root / PHASE1_LANE_NOTE_REL,
                load_text(root, PHASE1_LANE_NOTE_REL).replace(
                    EXPECTED_MARKERS[PHASE1_LANE_NOTE_REL][0],
                    "`PHASE1_DIRECT_OWNER_SHARED_REMINDER_ROUTE_SPLIT=drifted route split`",
                    1,
                ),
            ),
        ),
        (
            "missing_closure_validator_marker",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL).replace(
                    EXPECTED_MARKERS[PHASE1_CLOSURE_REL][0] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "missing_shared_tests_route_marker",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL).replace(
                    EXPECTED_MARKERS[PHASE1_CLOSURE_REL][1] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "missing_docs_bench_line",
            lambda root: write_text(
                root / DOCS_README_REL,
                load_text(root, DOCS_README_REL).replace(
                    EXPECTED_MARKERS[DOCS_README_REL][0] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "missing_scripts_route_summary_line",
            lambda root: write_text(
                root / SCRIPTS_README_REL,
                load_text(root, SCRIPTS_README_REL).replace(
                    EXPECTED_MARKERS[SCRIPTS_README_REL][1] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "missing_tests_truthful_line",
            lambda root: write_text(
                root / TESTS_README_REL,
                load_text(root, TESTS_README_REL).replace(
                    EXPECTED_MARKERS[TESTS_README_REL][0] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "missing_validator_state_literal",
            lambda root: write_text(
                root / VALIDATOR_REL,
                load_text(root, VALIDATOR_REL).replace(
                    EXPECTED_MARKERS[VALIDATOR_REL][2] + "\n",
                    "",
                    1,
                ),
            ),
        ),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-route-split-selftest-") as tmp:
            root = Path(tmp)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-closure-route-split-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-closure-route-split-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_CLOSURE_ROUTE_SPLIT_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_ROUTE_SPLIT_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_ROUTE_SPLIT=pass")
    print("PHASE1_CLOSURE_ROUTE_SPLIT_MODE=current-master-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
