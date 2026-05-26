#!/usr/bin/env python3
"""Guard the Phase 1 docs-root reminder packet on current master."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
STRING_REVIEW_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
DIRECT_OWNER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
SHARED_REMINDER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
BENCH_REL = Path("scripts/zigux/check-phase1-bench.py")
TESTS_README_REL = Path("zigux/tests/README.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
MAKEFILE_REL = Path("zigux/Makefile")

REQUIRED_FILES = (
    DOCS_ROOT_REL,
    PHASE1_CLOSURE_REL,
    PHASE1_LANE_NOTE_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    VALIDATOR_REL,
    STRING_REVIEW_REL,
    DIRECT_OWNER_REL,
    SHARED_REMINDER_REL,
    BENCH_REL,
    TESTS_README_REL,
    MANIFEST_REL,
    MAKEFILE_REL,
)

REQUIRED_MARKERS = (
    "Phase 1 notes - `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
    "`Documentation/zigux/phase1-closure.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/README.md`",
    "`zigux/tests/fixtures/phase1_helper_manifest.json`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/validate-phase1-closure.py`",
    "`scripts/zigux/check-phase1-string-review-packet.py`",
    "`scripts/zigux/check-phase1-direct-owner-markers.py`",
    "`scripts/zigux/check-phase1-shared-reminder-packet.py`",
    "`scripts/zigux/check-phase1-bench.py` keep the live owner map, the restored closure note and closure validator, the adjacent route-summary guard, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.",
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members",
    "the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards",
    "keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.",
    "`python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the bounded current reminder checks",
    "`zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14.",
)

FORBIDDEN_MARKERS = (
    "`scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`",
    "`make -C zigux phase1-route-summary`",
)


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def load_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{rel.as_posix()}" for rel in REQUIRED_FILES if not (root / rel).is_file()]
    if failures:
        return failures

    docs_root = load_text(root, DOCS_ROOT_REL)
    for marker in REQUIRED_MARKERS:
        count = docs_root.count(marker)
        if count != 1:
            failures.append(
                f"{DOCS_ROOT_REL.as_posix()}:required_marker:actual_count={count}:{marker}"
            )
    for marker in FORBIDDEN_MARKERS:
        count = docs_root.count(marker)
        if count:
            failures.append(
                f"{DOCS_ROOT_REL.as_posix()}:forbidden_marker:actual_count={count}:{marker}"
            )
    return failures


def make_fixture_tree(root: Path) -> None:
    for rel in REQUIRED_FILES:
        write_text(root / rel, f"fixture for {rel.as_posix()}\n")

    docs_root_text = (
        "# Zigux Documentation\n\n"
        "Phase 1 notes - `Documentation/zigux/phase1-host-helper-lane-sequencing.md` - `Documentation/zigux/phase1-closure.md` - `Documentation/zigux/review-checklist.md` - `zigux/tests/README.md` - `zigux/tests/fixtures/phase1_helper_manifest.json` - `scripts/zigux/README.md` - `scripts/zigux/validate-phase1-closure.py` - `scripts/zigux/check-phase1-string-review-packet.py` - `scripts/zigux/check-phase1-direct-owner-markers.py` - `scripts/zigux/check-phase1-shared-reminder-packet.py` - `scripts/zigux/check-phase1-bench.py` keep the live owner map, the restored closure note and closure validator, the adjacent route-summary guard, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.\n"
        "* repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members.\n"
        "* the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards.\n"
        "* keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.\n"
        "* `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the bounded current reminder checks.\n"
        "* `zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14.\n"
    )
    write_text(root / DOCS_ROOT_REL, docs_root_text)


def run_self_test() -> int:
    cases = (
        ("baseline", None),
        (
            "missing_bench_marker",
            lambda root: write_text(
                root / DOCS_ROOT_REL,
                load_text(root, DOCS_ROOT_REL).replace(
                    "`scripts/zigux/check-phase1-bench.py`", "", 1
                ),
            ),
        ),
        (
            "missing_gap_sentence",
            lambda root: write_text(
                root / DOCS_ROOT_REL,
                load_text(root, DOCS_ROOT_REL).replace(
                    "* repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members.\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "forbidden_direct_anchor_gate",
            lambda root: write_text(
                root / DOCS_ROOT_REL,
                load_text(root, DOCS_ROOT_REL) + "`scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`\n",
            ),
        ),
        (
            "forbidden_route_summary_wrapper",
            lambda root: write_text(
                root / DOCS_ROOT_REL,
                load_text(root, DOCS_ROOT_REL) + "`make -C zigux phase1-route-summary`\n",
            ),
        ),
        (
            "missing_required_file",
            lambda root: (root / BENCH_REL).unlink(),
        ),
    )

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-docs-root-") as tmp:
            root = Path(tmp)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-docs-root-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-docs-root-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_DOCS_ROOT_PACKET_SELF_TEST=pass")
    print(f"PHASE1_DOCS_ROOT_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def write_sample_root(root: Path) -> None:
    make_fixture_tree(root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    parser.add_argument(
        "--write-sample-root",
        help="write a current-like sample tree to the given root and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        print(f"PHASE1_DOCS_ROOT_PACKET_SAMPLE_ROOT={Path(args.write_sample_root).resolve()}")
        return 0

    root = repo_root(args.root)
    failures = collect_failures(root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_DOCS_ROOT_PACKET=pass")
    print(f"PHASE1_DOCS_ROOT_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_DOCS_ROOT_PACKET_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE1_DOCS_ROOT_PACKET_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
