#!/usr/bin/env python3
"""Guard the current Phase 1 closure-validator contract on current master."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]

VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase1-closure.md")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
MAKEFILE_REL = Path("zigux/Makefile")
DIRECT_OWNER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
STRING_REVIEW_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
ROUTE_SUMMARY_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")
BENCH_REL = Path("scripts/zigux/check-phase1-bench.py")
SHARED_REMINDER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")

REQUIRED_FILES = (
    VALIDATOR_REL,
    CLOSURE_NOTE_REL,
    LANE_NOTE_REL,
    MANIFEST_REL,
    MAKEFILE_REL,
    DIRECT_OWNER_REL,
    STRING_REVIEW_REL,
    ROUTE_SUMMARY_REL,
    BENCH_REL,
    SHARED_REMINDER_REL,
)

EXPECTED_VALIDATOR_MARKERS = (
    '"""Validate the current Phase 1 closure note against the live reminder packet."""',
    "PHASE1_CLOSURE_REL = Path(\"Documentation/zigux/phase1-closure.md\")",
    "PHASE1_LANE_NOTE_REL = Path(\"Documentation/zigux/phase1-host-helper-lane-sequencing.md\")",
    "ROUTE_SUMMARY_CHECKER_REL = Path(\"scripts/zigux/check-phase1-route-summary-counts.py\")",
    "BENCH_CHECKER_REL = Path(\"scripts/zigux/check-phase1-bench.py\")",
    "SHARED_REMINDER_CHECKER_REL = Path(\"scripts/zigux/check-phase1-shared-reminder-packet.py\")",
    "ZIGUX_MAKEFILE_REL = Path(\"zigux/Makefile\")",
    "\"`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`\"",
    "\"`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`\"",
    "\"`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`\"",
    "\"`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`\"",
    "\"`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`\"",
    "\"phase2-toolchain:\"",
    "\"phase14-validate:\"",
    "\"phase1-validate:\"",
    "\"phase1-test:\"",
    "\"phase1-bench:\"",
    "\"phase1:\"",
    "(STRING_REVIEW_CHECKER_REL, \"phase1-string-review-packet\")",
    "(DIRECT_OWNER_CHECKER_REL, \"phase1-direct-owner-markers\")",
    "(ROUTE_SUMMARY_CHECKER_REL, \"phase1-route-summary-counts\")",
    "(BENCH_CHECKER_REL, \"phase1-bench\")",
    "(SHARED_REMINDER_CHECKER_REL, \"phase1-shared-reminder-packet\")",
    "print(\"PHASE1_CLOSURE_SELF_TEST=pass\")",
    "print(\"PHASE1_CLOSURE_VALIDATION=pass\")",
    "print(\"PHASE1_CLOSURE_MODE=current-master-safe\")",
)

EXPECTED_CLOSURE_NOTE_MARKERS = (
    "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
    "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
)

EXPECTED_LANE_NOTE_MARKERS = (
    "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py`",
    "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=leave the shared bench-checker wording and shared-reminder checker packet parked unless a fresh reread finds drift across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, scripts/zigux/README.md, Documentation/zigux/phase1-closure.md, scripts/zigux/validate-phase1-closure.py, scripts/zigux/check-phase1-bench.py, or scripts/zigux/check-phase1-shared-reminder-packet.py; otherwise prefer the smaller helper-specific next-safe-step markers below before reopening any shared reminder surface`",
)

EXPECTED_MANIFEST_PATHS = {
    ("phase",): "Phase 1",
    ("status",): "closed",
    ("helper_count",): 13,
    (
        "lane_sequencing",
        "rule_summary",
    ): "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.",
    (
        "lane_sequencing",
        "anti_overlap_rule",
    ): "Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.",
    (
        "review_anchors",
        "tools/lib/bitmap.zig",
        "next_safe_step_note",
    ): "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, cross-word scnprintf, exact-word-boundary equality fast-path masking, caller-window xor and or clamp, weighted tail-count clamp, empty-buffer, allocator-reset, zero-bit logical short-circuit, and Linux-style alias mirror anchors here, and if the separate bitmap closure-validator anchor-sync repair is still outstanding, treat that as the only other bitmap follow-through.",
    (
        "review_anchors",
        "tools/lib/find_bit.zig",
        "next_safe_step_note",
    ): "If this helper lane reopens, keep find_bit parked unless a fresh reread finds direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families.",
    (
        "review_anchors",
        "tools/lib/rbtree.zig",
        "cached_leftmost_fixture_keys",
    ): ["cached_leftmost_return_serials"],
    (
        "review_anchors",
        "tools/lib/string.zig",
        "sysfs_review_summary",
    ): "helper-local sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests because the shared Phase 1 replay still carries no dedicated sysfs fixture keys, so sysfsStreq and sysfs_streq plus sysfsMatchString and sysfs_match_string remain review-visible at the helper surface",
}


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative: Path) -> str:
    return (root / relative).read_text(encoding="utf-8")


def read_json(root: Path, relative: Path) -> object:
    return json.loads(read_text(root, relative))


def require_once(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected_once:actual={count}:{marker}"]


def nested_get(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    validator_text = read_text(root, VALIDATOR_REL)
    for marker in EXPECTED_VALIDATOR_MARKERS:
        failures.extend(require_once(validator_text, VALIDATOR_REL.as_posix(), marker))

    closure_text = read_text(root, CLOSURE_NOTE_REL)
    for marker in EXPECTED_CLOSURE_NOTE_MARKERS:
        failures.extend(require_once(closure_text, CLOSURE_NOTE_REL.as_posix(), marker))

    lane_text = read_text(root, LANE_NOTE_REL)
    for marker in EXPECTED_LANE_NOTE_MARKERS:
        failures.extend(require_once(lane_text, LANE_NOTE_REL.as_posix(), marker))

    manifest = read_json(root, MANIFEST_REL)
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]
    for path, expected in EXPECTED_MANIFEST_PATHS.items():
        actual = nested_get(manifest, path)
        if actual != expected:
            failures.append(
                f"{MANIFEST_REL.as_posix()}:{'.'.join(path)}:expected={expected!r}:actual={actual!r}"
            )

    return failures


def write_text(root: Path, relative: Path, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative in REQUIRED_FILES:
        write_text(root, relative, "")

    validator_text = "\n".join(EXPECTED_VALIDATOR_MARKERS) + "\n"
    write_text(root, VALIDATOR_REL, validator_text)
    write_text(root, CLOSURE_NOTE_REL, "\n".join(EXPECTED_CLOSURE_NOTE_MARKERS) + "\n")
    write_text(root, LANE_NOTE_REL, "\n".join(EXPECTED_LANE_NOTE_MARKERS) + "\n")
    write_text(root, MAKEFILE_REL, "phase2-toolchain:\nphase14-validate:\n")
    for relative in (DIRECT_OWNER_REL, STRING_REVIEW_REL, ROUTE_SUMMARY_REL, BENCH_REL, SHARED_REMINDER_REL):
        write_text(root, relative, "# helper\n")
    manifest_data = {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": 13,
        "lane_sequencing": {
            "rule_summary": EXPECTED_MANIFEST_PATHS[("lane_sequencing", "rule_summary")],
            "anti_overlap_rule": EXPECTED_MANIFEST_PATHS[("lane_sequencing", "anti_overlap_rule")],
        },
        "review_anchors": {
            "tools/lib/bitmap.zig": {
                "next_safe_step_note": EXPECTED_MANIFEST_PATHS[
                    ("review_anchors", "tools/lib/bitmap.zig", "next_safe_step_note")
                ],
            },
            "tools/lib/find_bit.zig": {
                "next_safe_step_note": EXPECTED_MANIFEST_PATHS[
                    ("review_anchors", "tools/lib/find_bit.zig", "next_safe_step_note")
                ],
            },
            "tools/lib/rbtree.zig": {
                "cached_leftmost_fixture_keys": ["cached_leftmost_return_serials"],
            },
            "tools/lib/string.zig": {
                "sysfs_review_summary": EXPECTED_MANIFEST_PATHS[
                    ("review_anchors", "tools/lib/string.zig", "sysfs_review_summary")
                ],
            },
        },
    }
    write_text(root, MANIFEST_REL, json.dumps(manifest_data, indent=2) + "\n")


def mutate_text(root: Path, relative: Path, old: str, new: str) -> None:
    path = root / relative
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_manifest(root: Path, path: tuple[str, ...], new_value: object) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    current = manifest
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = new_value
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, callable[[Path], None] | None]] = [
        ("baseline", None),
        (
            "missing_validator_marker",
            lambda root: mutate_text(
                root,
                VALIDATOR_REL,
                "print(\"PHASE1_CLOSURE_VALIDATION=pass\")",
                "print(\"PHASE1_CLOSURE_VALIDATION=drift\")",
            ),
        ),
        (
            "missing_delegated_checker",
            lambda root: mutate_text(
                root,
                VALIDATOR_REL,
                "(BENCH_CHECKER_REL, \"phase1-bench\")",
                "(BENCH_CHECKER_REL, \"phase1-bench-drift\")",
            ),
        ),
        (
            "missing_closure_marker",
            lambda root: mutate_text(
                root,
                CLOSURE_NOTE_REL,
                "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
                "`PHASE1_SHARED_TESTS_ROUTE=drift`",
            ),
        ),
        (
            "missing_lane_marker",
            lambda root: mutate_text(
                root,
                LANE_NOTE_REL,
                "scripts/zigux/check-phase1-bench.py",
                "scripts/zigux/check-phase1-bench-drift.py",
            ),
        ),
        (
            "manifest_helper_count_drift",
            lambda root: mutate_manifest(root, ("helper_count",), 99),
        ),
        (
            "manifest_bitmap_note_drift",
            lambda root: mutate_manifest(
                root,
                ("review_anchors", "tools/lib/bitmap.zig", "next_safe_step_note"),
                "drift",
            ),
        ),
        (
            "missing_required_file",
            lambda root: (root / SHARED_REMINDER_REL).unlink(),
        ),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-closure-validator-contract-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_CLOSURE_VALIDATOR_CONTRACT_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_CONTRACT_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    parser.add_argument(
        "--write-sample-root",
        help="write a current-like sample tree for replay",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        sample_root = Path(args.write_sample_root).resolve()
        build_sample_repo(sample_root)
        print(f"PHASE1_CLOSURE_VALIDATOR_CONTRACT_SAMPLE_ROOT={sample_root}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_CLOSURE_VALIDATOR_CONTRACT=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_VALIDATOR_CONTRACT=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_CONTRACT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_CLOSURE_VALIDATOR_CONTRACT_REQUIRED_MARKER_COUNT="
        f"{len(EXPECTED_VALIDATOR_MARKERS) + len(EXPECTED_CLOSURE_NOTE_MARKERS) + len(EXPECTED_LANE_NOTE_MARKERS) + len(EXPECTED_MANIFEST_PATHS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
