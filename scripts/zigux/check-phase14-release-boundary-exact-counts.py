#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=release_boundary_exact_counts

Fail-closed checker for the current Phase 14 release-boundary count posture.

This guard keeps the release-boundary packet honest around the exact unknown
compile-shard counts and the currently unreadable executable-layer gap while
cross-reading the shared smoke survey markers that define the returned
Phase 14 route split and exact-readback gap list.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


MARKER = "PHASE14_CHECK_PACKET=release_boundary_exact_counts"
RELEASE_BOUNDARY_PATH = Path("Documentation/zigux/phase14-release-boundary-survey.md")
SURVEY_PATH = Path("Documentation/zigux/phase14-end-to-end-smoke-survey.md")

UNKNOWN_COUNT_MARKERS = [
    "- `PHASE14_COMPILE_SHARD_TOTAL=unknown_in_current_contents_readback`",
    "- `PHASE14_COMPILE_SHARD_FOCUSED_COUNT=unknown_in_current_contents_readback`",
    "- `PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=unknown_in_current_contents_readback`",
]

EXECUTABLE_GAP_MARKERS = [
    "- `zigux/tests/phase14_build.zig`",
    "- `zigux/tests/phase14_end_to_end_smoke_manifest.json`",
    "- `zigux/tests/phase14_end_to_end_smoke_survey.zig`",
    "- `zigux/tests/phase14_skbuff_bridge.zig`",
    "- `zigux/tests/phase14_rcu_tree_survey.zig`",
    "- `net/core/skbuff_bridge.zig`",
]

RELEASE_BOUNDARY_TEXT_MARKERS = [
    "- `scripts/zigux/check-phase14-release-boundary-exact-counts.py` now returns through the current contents path and keeps the release-facing exact-count posture aligned with the current shared reminder packet",
    "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`",
    "- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`",
]

SURVEY_EXACT_LINE_SNIPPETS = [
    "  * exact-readback gaps that still belong to this shared note:",
    "    * `zigux/tests/phase14_build.zig`",
    "    * `zigux/tests/phase14_end_to_end_smoke_manifest.json`",
    "    * `zigux/tests/phase14_end_to_end_smoke_survey.zig`",
    "    * broad reminder text should therefore frame that build-side and executable layer as exact-readback gaps rather than as directly recovered shared-smoke proof",
    "    * the current readable route layer still stops at `make -C zigux phase14-validate`; no current attached-toolchain `make -C zigux phase14-smoke`, `make -C zigux phase14-test`, or `make -C zigux phase14` fallback is usable from this note because the readable `zigux/Makefile` body still omits those targets",
]


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    if not path.exists():
        raise FileNotFoundError(rel.as_posix())
    return path.read_text(encoding="utf-8")



def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")



def require_markers(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"missing_marker:{rel.as_posix()}:{marker}")



def require_exact_once(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        count = text.count(marker)
        if count == 0:
            errors.append(f"missing_marker:{rel.as_posix()}:{marker}")
        elif count != 1:
            errors.append(f"duplicate_marker:{rel.as_posix()}:{marker}:{count}")



def check(root: Path) -> list[str]:
    errors: list[str] = []

    if MARKER not in Path(__file__).read_text(encoding="utf-8"):
        errors.append("missing_checker_marker:self")

    if not (root / RELEASE_BOUNDARY_PATH).exists():
        errors.append(f"missing_file:{RELEASE_BOUNDARY_PATH.as_posix()}")
        return errors

    if not (root / SURVEY_PATH).exists():
        errors.append(f"missing_file:{SURVEY_PATH.as_posix()}")
        return errors

    release_boundary = read_text(root, RELEASE_BOUNDARY_PATH)
    require_markers(errors, RELEASE_BOUNDARY_PATH, release_boundary, UNKNOWN_COUNT_MARKERS)
    require_markers(errors, RELEASE_BOUNDARY_PATH, release_boundary, EXECUTABLE_GAP_MARKERS)
    require_markers(errors, RELEASE_BOUNDARY_PATH, release_boundary, RELEASE_BOUNDARY_TEXT_MARKERS)

    survey = read_text(root, SURVEY_PATH)
    require_exact_once(errors, SURVEY_PATH, survey, SURVEY_EXACT_LINE_SNIPPETS)
    return errors



def fixture_release_boundary() -> str:
    return "\n".join(
        [
            "# Phase 14 Release Boundary Survey",
            *UNKNOWN_COUNT_MARKERS,
            *RELEASE_BOUNDARY_TEXT_MARKERS,
            "- executable packet members that still do not return through this lane's exact contents readback:",
            *EXECUTABLE_GAP_MARKERS,
            "",
        ]
    )



def fixture_survey() -> str:
    return "\n".join(
        [
            "# Phase 14 End-to-End Smoke Survey",
            *SURVEY_EXACT_LINE_SNIPPETS,
            "",
        ]
    )



def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root, RELEASE_BOUNDARY_PATH, fixture_release_boundary())
    write_text(root, SURVEY_PATH, fixture_survey())



def remove_line(root: Path, rel: Path, marker: str) -> None:
    text = read_text(root, rel)
    updated = text.replace(marker + "\n", "", 1)
    if updated == text:
        updated = text.replace(marker, "", 1)
    write_text(root, rel, updated)



def duplicate_line(root: Path, rel: Path, marker: str) -> None:
    text = read_text(root, rel)
    if marker not in text:
        raise ValueError(f"marker not found for duplication: {marker}")
    updated = text.replace(marker, marker + "\n" + marker, 1)
    write_text(root, rel, updated)



def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-release-boundary-counts-"))
    try:
        write_fixture_tree(base)
        errors = check(base)
        if errors:
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        remove_line(base, RELEASE_BOUNDARY_PATH, UNKNOWN_COUNT_MARKERS[0])
        if not any(UNKNOWN_COUNT_MARKERS[0] in error for error in check(base)):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected unknown-count drift to fail")
            return 1

        write_fixture_tree(base)
        remove_line(base, RELEASE_BOUNDARY_PATH, EXECUTABLE_GAP_MARKERS[0])
        if not any(EXECUTABLE_GAP_MARKERS[0] in error for error in check(base)):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected executable-gap drift to fail")
            return 1

        write_fixture_tree(base)
        remove_line(base, RELEASE_BOUNDARY_PATH, RELEASE_BOUNDARY_TEXT_MARKERS[0])
        if not any(RELEASE_BOUNDARY_TEXT_MARKERS[0] in error for error in check(base)):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected shipped-checker drift to fail")
            return 1

        write_fixture_tree(base)
        remove_line(base, SURVEY_PATH, SURVEY_EXACT_LINE_SNIPPETS[0])
        if not any(SURVEY_EXACT_LINE_SNIPPETS[0] in error for error in check(base)):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected missing survey marker drift to fail")
            return 1

        write_fixture_tree(base)
        duplicate_line(base, SURVEY_PATH, SURVEY_EXACT_LINE_SNIPPETS[0])
        if not any(error.startswith(f"duplicate_marker:{SURVEY_PATH.as_posix()}:{SURVEY_EXACT_LINE_SNIPPETS[0]}") for error in check(base)):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected duplicate survey marker drift to fail")
            return 1

        print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=pass")
        print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST_CASE_COUNT=5")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)



def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(args.root)
    if errors:
        print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS=fail")
        print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_ISSUES_START")
        for error in errors:
            print(error)
        print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_ISSUES_END")
        return 1

    print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS=pass")
    print(f"PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_EXECUTABLE_GAP_COUNT={len(EXECUTABLE_GAP_MARKERS)}")
    print(f"PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SURVEY_MARKER_COUNT={len(SURVEY_EXACT_LINE_SNIPPETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())