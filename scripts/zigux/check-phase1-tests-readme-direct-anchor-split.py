#!/usr/bin/env python3
"""Guard the current Phase 1 tests-root direct-anchor split in zigux/tests/README.md."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


README_PATH = Path("zigux/tests/README.md")
PHASE1_HEADING = "## Phase 1 host-tools review packet"
PHASE2_HEADING = "## Phase 2 review packet"

REQUIRED_MARKERS = (
    "  * current direct-readback Phase 1 reminder packet:",
    "- `Documentation/zigux/phase1-closure.md`",
    "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
    "- `Documentation/zigux/README.md`",
    "- `Documentation/zigux/review-checklist.md`",
    "- `scripts/zigux/README.md`",
    "- `scripts/zigux/check-phase1-string-review-packet.py`",
    "- `scripts/zigux/check-phase1-direct-owner-markers.py`",
    "- `scripts/zigux/check-phase1-bench.py`",
    "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
    "- `scripts/zigux/validate-phase1-closure.py`",
    "- `zigux/tests/build.zig`",
    "- `zigux/tests/phase1_host_tools_smoke.zig`",
    "- `.github/workflows/zigux-bootstrap.yml`",
    "- `zigux/tests/fixtures/phase1_helper_manifest.json`",
    "- `zigux/tests/README.md`",
    "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "  * current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof",
    "  * broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
    "  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    "Tests-root reviewer prompt:",
    "- Does the bounded Phase 1 reminder keep the restored closure note, the workflow-backed closure-validator and shipped checker packet, the shared tests-root smoke route, the manifest-backed owner map, the broader-companion wording for the validator-first, parity, bench-replay, and helper-replay family, and the historical-gap wording for the missing Phase 1 Makefile routes aligned without widening back into the older full closure stack?",
)

FORBIDDEN_FRAGMENTS = (
    "current shared Phase 1 workflow gates:",
    "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
)

SAMPLE_TEXT = """# zigux/tests

This directory is the home of reusable Zigux parity and differential validation harnesses.

Purpose

  * hold shared harness logic before subsystem-specific tests spread through the tree
  * keep product-facing validation code separate from ad hoc experiments
  * provide the checks for helper parity, ABI assertions, and rollback readiness

## Phase 1 host-tools review packet

  * current direct-readback Phase 1 reminder packet:
- `Documentation/zigux/phase1-closure.md`
- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `scripts/zigux/check-phase1-string-review-packet.py`
- `scripts/zigux/check-phase1-direct-owner-markers.py`
- `scripts/zigux/check-phase1-bench.py`
- `scripts/zigux/check-phase1-shared-reminder-packet.py`
- `scripts/zigux/validate-phase1-closure.py`
- `zigux/tests/build.zig`
- `zigux/tests/phase1_host_tools_smoke.zig`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `zigux/tests/README.md`

  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
  * current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof
  * broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet
  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`

Tests-root reviewer prompt:
- Does the bounded Phase 1 reminder keep the restored closure note, the workflow-backed closure-validator and shipped checker packet, the shared tests-root smoke route, the manifest-backed owner map, the broader-companion wording for the validator-first, parity, bench-replay, and helper-replay family, and the historical-gap wording for the missing Phase 1 Makefile routes aligned without widening back into the older full closure stack?

## Phase 2 review packet
"""


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(root: Path, relative_path: Path, content: str) -> None:
    target = root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def extract_phase1_section(text: str) -> str | None:
    start = text.find(PHASE1_HEADING)
    if start == -1:
        return None
    end = text.find(PHASE2_HEADING, start)
    if end == -1:
        return None
    return text[start:end]


def check_root(root: Path) -> int:
    text = read_text(root, README_PATH)
    section = extract_phase1_section(text)
    errors: list[str] = []

    if section is None:
        print(f"{README_PATH}:missing_phase_boundary:{PHASE1_HEADING}->{PHASE2_HEADING}")
        print("PHASE1_TESTS_README_DIRECT_ANCHOR_SPLIT=fail")
        return 1

    for marker in REQUIRED_MARKERS:
        count = section.count(marker)
        if count != 1:
            errors.append(f"{README_PATH}:marker-count:{marker!r}:expected=1:actual={count}")

    for fragment in FORBIDDEN_FRAGMENTS:
        count = section.count(fragment)
        if count != 0:
            errors.append(
                f"{README_PATH}:forbidden-fragment:{fragment!r}:expected=0:actual={count}"
            )

    if errors:
        for error in errors:
            print(error)
        print("PHASE1_TESTS_README_DIRECT_ANCHOR_SPLIT=fail")
        return 1

    print("PHASE1_TESTS_README_DIRECT_ANCHOR_SPLIT=pass")
    print(f"PHASE1_TESTS_README_DIRECT_ANCHOR_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE1_TESTS_README_DIRECT_ANCHOR_FORBIDDEN_FRAGMENT_COUNT={len(FORBIDDEN_FRAGMENTS)}")
    return 0


def write_sample_root(destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    write_text(destination, README_PATH, SAMPLE_TEXT)


def mutate_remove_marker(root: Path, marker: str) -> None:
    text = read_text(root, README_PATH)
    write_text(root, README_PATH, text.replace(marker, "", 1))


def mutate_duplicate_marker(root: Path, marker: str) -> None:
    text = read_text(root, README_PATH)
    write_text(root, README_PATH, text.replace(marker, marker + "\n" + marker, 1))


def mutate_append_forbidden_fragment(root: Path, fragment: str) -> None:
    text = read_text(root, README_PATH)
    insert_at = text.find(PHASE2_HEADING)
    if insert_at == -1:
        insert_at = len(text)
    updated = text[:insert_at] + fragment + "\n\n" + text[insert_at:]
    write_text(root, README_PATH, updated)


def mutate_drop_phase2_heading(root: Path) -> None:
    text = read_text(root, README_PATH)
    write_text(root, README_PATH, text.replace(PHASE2_HEADING, "", 1))


def run_self_test() -> int:
    cases = [
        ("missing_packet_header", lambda root: mutate_remove_marker(root, REQUIRED_MARKERS[0])),
        (
            "missing_shared_checker",
            lambda root: mutate_remove_marker(root, "- `scripts/zigux/check-phase1-shared-reminder-packet.py`"),
        ),
        (
            "missing_workflow_file_marker",
            lambda root: mutate_remove_marker(root, "- `.github/workflows/zigux-bootstrap.yml`"),
        ),
        ("missing_smoke_route", lambda root: mutate_remove_marker(root, REQUIRED_MARKERS[16])),
        ("missing_makefile_posture", lambda root: mutate_remove_marker(root, REQUIRED_MARKERS[17])),
        ("duplicate_makefile_posture", lambda root: mutate_duplicate_marker(root, REQUIRED_MARKERS[17])),
        (
            "missing_broader_companion_warning",
            lambda root: mutate_remove_marker(root, REQUIRED_MARKERS[18]),
        ),
        ("missing_direct_anchor_split", lambda root: mutate_remove_marker(root, REQUIRED_MARKERS[19])),
        ("duplicate_direct_anchor_split", lambda root: mutate_duplicateMarker(root, REQUIRED_MARKERS[19])),
        ("duplicate_reviewer_prompt", lambda root: mutate_duplicate_marker(root, REQUIRED_MARKERS[21])),
        ("missing_phase2_boundary", mutate_drop_phase2_heading),
        (
            "forbidden_workflow_gate_heading",
            lambda root: mutate_append_forbidden_fragment(root, FORBIDDEN_FRAGMENTS[0]),
        ),
        (
            "forbidden_shared_reminder_selftest",
            lambda root: mutate_append_forbidden_fragment(root, FORBIDDEN_FRAGMENTS[1]),
        ),
        (
            "forbidden_shared_reminder_live_check",
            lambda root: mutate_append_forbidden_fragment(root, FORBIDDEN_FRAGMENTS[2]),
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="phase1-tests-readme-direct-anchor-selftest-") as tmpdir:
        root = Path(tmpdir)
        write_sample_root(root)
        if check_root(root) != 0:
            print("PHASE1_TESTS_README_DIRECT_ANCHOR_SELF_TEST=fail")
            print("PHASE1_TESTS_README_DIRECT_ANCHOR_SELF_TEST_CASE_COUNT=0")
            return 1

        for name, mutate in cases:
            case_root = root / name
            write_sample_root(case_root)
            mutate(case_root)
            if check_root(case_root) == 0:
                print(f"self-test case unexpectedly passed: {name}")
                print("PHASE1_TESTS_README_DIRECT_ANCHOR_SELF_TEST=fail")
                print(f"PHASE1_TESTS_README_DIRECT_ANCHOR_SELF_TEST_CASE_COUNT={len(cases)}")
                return 1

    print("PHASE1_TESTS_README_DIRECT_ANCHOR_SELF_TEST=pass")
    print(f"PHASE1_TESTS_README_DIRECT_ANCHOR_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0
    if args.self_test:
        return run_self_test()
    return check_root(args.root)


if __name__ == "__main__":
    raise SystemExit(main())
