#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=release_boundary_exact_counts

Fail-closed checker for the current Phase 14 release-boundary count posture.

This guard keeps the PMO release-boundary packet honest while exact contents
readback still leaves the compile-shard counts unknown. It validates that the
shared Phase 14 reminder notes continue to record the same unknown-count
posture, the same executable-layer gap packet, and the same readable-but-no
`phase14-*` Makefile split.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


MARKER = "PHASE14_CHECK_PACKET=release_boundary_exact_counts"

RELEASE_BOUNDARY_PATH = Path("Documentation/zigux/phase14-release-boundary-survey.md")
SMOKE_SURVEY_PATH = Path("Documentation/zigux/phase14-end-to-end-smoke-survey.md")
PRODUCTIZATION_GAP_PATH = Path("Documentation/zigux/phase14-productization-gap-survey.md")
DOCS_README_PATH = Path("Documentation/zigux/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
MAKEFILE_PATH = Path("zigux/Makefile")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase14.py")

UNKNOWN_COUNT_MARKERS = [
    "- `PHASE14_COMPILE_SHARD_TOTAL=unknown_in_current_contents_readback`",
    "- `PHASE14_COMPILE_SHARD_FOCUSED_COUNT=unknown_in_current_contents_readback`",
    "- `PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=unknown_in_current_contents_readback`",
]

EXECUTABLE_GAP_MARKERS = [
    "- `scripts/zigux/check-phase14-release-boundary-exact-counts.py`",
    "- `zigux/tests/phase14_build.zig`",
    "- `zigux/tests/phase14_end_to_end_smoke_manifest.json`",
    "- `zigux/tests/phase14_end_to_end_smoke_survey.zig`",
    "- `zigux/tests/phase14_skbuff_bridge.zig`",
    "- `zigux/tests/phase14_ring_buffer_survey.zig`",
    "- `zigux/tests/phase14_rcu_tree_survey.zig`",
    "- `net/core/skbuff_bridge.zig`",
]

MAKEFILE_PRESENT_MARKERS = [
    "phase3-validate:",
    "phase4-validate:",
    "phase4-test:",
    "phase4: phase4-validate phase4-test",
    "phase6-base64-test:",
    "phase8-validate:",
    "phase10-validate:",
    "phase12-smoke:",
]

MAKEFILE_ABSENT_MARKERS = [
    "phase14-validate:",
    "phase14-smoke:",
    "phase14-test:",
    "phase14: phase14-validate phase14-smoke phase14-test",
]

RELEASE_BOUNDARY_TEXT_MARKERS = [
    "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`",
    "- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`",
    "Do not present the compile-shard matrix, manifest-backed full-bundle replay, wrapper-backed `phase14-test`, wrapper-backed `phase14`, or dedicated `phase14-smoke` route as current release-facing proof",
]

SHARED_REMINDER_MARKERS = {
    DOCS_README_PATH: [
        "- `Documentation/zigux/phase14-productization-gap-survey.md`",
        "- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
        "while `net/core/skbuff.c` and `kernel/rcu/tree.c` remain freeze-in-C anchors",
    ],
    SCRIPTS_README_PATH: [
        "- Phase 14 flow - the current scripts-root shared smoke packet stays reviewable",
        "- `zigux/Makefile` is directly readable on current `master`, and its live body currently exposes shipped Phase 2 toolchain and kbuild routes together with bounded Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 route families, but still no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets",
    ],
    TESTS_README_PATH: [
        "Keep the current bounded Phase 14 reminder packet explicit through `Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
        "Current `master` still does not materialize `scripts/zigux/check-phase14-release-boundary-exact-counts.py`",
    ],
    PRODUCTIZATION_GAP_PATH: [
        "- `scripts/zigux/check-phase14-release-boundary-exact-counts.py`",
        "The higher-value same-lane task is reminder-surface truthfulness",
    ],
    SMOKE_SURVEY_PATH: [
        "If a future same-lane reread restores current direct readback for `phase14-validate`, `phase14-smoke`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, or `zigux/tests/phase14_end_to_end_smoke_survey.zig`, reconcile this note with those files",
    ],
    VALIDATOR_PATH: [
        "ROLLBACK_CHECKER_PATH = \"scripts/zigux/check-phase14-rollback-threshold-sequencing.py\"",
        "PHASE14_VALIDATOR_SELF_TEST=pass",
    ],
}


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


def require_absent(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            errors.append(f"forbidden_marker:{rel.as_posix()}:{marker}")


def check(root: Path) -> list[str]:
    errors: list[str] = []

    if MARKER not in Path(__file__).read_text(encoding="utf-8"):
        errors.append("missing_checker_marker:self")

    required_paths = [
        RELEASE_BOUNDARY_PATH,
        SMOKE_SURVEY_PATH,
        PRODUCTIZATION_GAP_PATH,
        DOCS_README_PATH,
        SCRIPTS_README_PATH,
        TESTS_README_PATH,
        MAKEFILE_PATH,
        VALIDATOR_PATH,
    ]
    for rel in required_paths:
        if not (root / rel).exists():
            errors.append(f"missing_file:{rel.as_posix()}")
    if errors:
        return errors

    release_boundary = read_text(root, RELEASE_BOUNDARY_PATH)
    require_markers(errors, RELEASE_BOUNDARY_PATH, release_boundary, UNKNOWN_COUNT_MARKERS)
    require_markers(errors, RELEASE_BOUNDARY_PATH, release_boundary, EXECUTABLE_GAP_MARKERS)
    require_markers(errors, RELEASE_BOUNDARY_PATH, release_boundary, RELEASE_BOUNDARY_TEXT_MARKERS)

    for rel, markers in SHARED_REMINDER_MARKERS.items():
        require_markers(errors, rel, read_text(root, rel), markers)

    makefile = read_text(root, MAKEFILE_PATH)
    require_markers(errors, MAKEFILE_PATH, makefile, MAKEFILE_PRESENT_MARKERS)
    require_absent(errors, MAKEFILE_PATH, makefile, MAKEFILE_ABSENT_MARKERS)

    return errors


def fixture_release_boundary() -> str:
    return "\n".join(
        [
            "# Phase 14 Release Boundary Survey",
            *UNKNOWN_COUNT_MARKERS,
            "- executable packet members that still do not return through this lane's exact contents readback:",
            *EXECUTABLE_GAP_MARKERS,
            "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`",
            "- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`",
            "Do not present the compile-shard matrix, manifest-backed full-bundle replay, wrapper-backed `phase14-test`, wrapper-backed `phase14`, or dedicated `phase14-smoke` route as current release-facing proof while the readable Makefile still lacks those targets and the dedicated build and manifest files are still missing in this lane's exact contents path.",
            "",
        ]
    )


def fixture_smoke_survey() -> str:
    return "\n".join(
        [
            "# Phase 14 End-to-End Smoke Survey",
            "If a future same-lane reread restores current direct readback for `phase14-validate`, `phase14-smoke`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, or `zigux/tests/phase14_end_to_end_smoke_survey.zig`, reconcile this note with those files and with `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md` before restoring any stronger validator-first wording.",
            "",
        ]
    )


def fixture_productization_gap() -> str:
    return "\n".join(
        [
            "# Phase 14 Productization Gap Survey",
            "- `scripts/zigux/check-phase14-release-boundary-exact-counts.py`",
            "The higher-value same-lane task is reminder-surface truthfulness: keep shared notes aligned with the recovered documentation packet, the blob-readable validator surface, the directly readable workqueue reviewability shard, and the current Makefile posture instead of repeating the older story that the broader shared smoke packet is simply unreadable or that the Makefile still ships the old `phase14-*` routes.",
            "",
        ]
    )


def fixture_docs_readme() -> str:
    return "\n".join(
        [
            "# Zigux Documentation",
            "- `Documentation/zigux/phase14-productization-gap-survey.md`",
            "- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
            "while `net/core/skbuff.c` and `kernel/rcu/tree.c` remain freeze-in-C anchors",
            "",
        ]
    )


def fixture_scripts_readme() -> str:
    return "\n".join(
        [
            "# scripts/zigux",
            "- Phase 14 flow - the current scripts-root shared smoke packet stays reviewable",
            "- `zigux/Makefile` is directly readable on current `master`, and its live body currently exposes shipped Phase 2 toolchain and kbuild routes together with bounded Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 route families, but still no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets",
            "",
        ]
    )


def fixture_tests_readme() -> str:
    return "\n".join(
        [
            "# zigux/tests",
            "Keep the current bounded Phase 14 reminder packet explicit through `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-productization-gap-survey.md`, and `Documentation/zigux/review-checklist.md`.",
            "Current `master` still does not materialize `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_ring_buffer_survey.zig`, `zigux/tests/phase14_rcu_tree_survey.zig`, or `net/core/skbuff_bridge.zig`, so keep that executable-layer packet framed as a repo-reality gap rather than shipped tests-root evidence until fresh current-tree reads restore it.",
            "",
        ]
    )


def fixture_makefile() -> str:
    return "\n".join(MAKEFILE_PRESENT_MARKERS) + "\n"


def fixture_validator() -> str:
    return "\n".join(
        [
            'ROLLBACK_CHECKER_PATH = "scripts/zigux/check-phase14-rollback-threshold-sequencing.py"',
            "PHASE14_VALIDATOR_SELF_TEST=pass",
            "",
        ]
    )


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root, RELEASE_BOUNDARY_PATH, fixture_release_boundary())
    write_text(root, SMOKE_SURVEY_PATH, fixture_smoke_survey())
    write_text(root, PRODUCTIZATION_GAP_PATH, fixture_productization_gap())
    write_text(root, DOCS_README_PATH, fixture_docs_readme())
    write_text(root, SCRIPTS_README_PATH, fixture_scripts_readme())
    write_text(root, TESTS_README_PATH, fixture_tests_readme())
    write_text(root, MAKEFILE_PATH, fixture_makefile())
    write_text(root, VALIDATOR_PATH, fixture_validator())


def remove_line(root: Path, rel: Path, marker: str) -> None:
    text = read_text(root, rel)
    updated = text.replace(marker + "\n", "", 1)
    if updated == text:
        updated = text.replace(marker, "", 1)
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
        write_text(base, MAKEFILE_PATH, fixture_makefile() + "phase14-validate:\n")
        if not any("phase14-validate:" in error for error in check(base)):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected stale phase14 make route to fail")
            return 1

        write_fixture_tree(base)
        remove_line(base, TESTS_README_PATH, "Current `master` still does not materialize `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_ring_buffer_survey.zig`, `zigux/tests/phase14_rcu_tree_survey.zig`, or `net/core/skbuff_bridge.zig`, so keep that executable-layer packet framed as a repo-reality gap rather than shipped tests-root evidence until fresh current-tree reads restore it.")
        if not any("Current `master` still does not materialize `scripts/zigux/check-phase14-release-boundary-exact-counts.py`" in error for error in check(base)):
            print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
            print("expected tests-root reminder drift to fail")
            return 1

        print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=pass")
        print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST_CASE_COUNT=4")
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
    print(f"PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SHARED_REMINDER_COUNT={len(SHARED_REMINDER_MARKERS)}")
    print(f"PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_EXECUTABLE_GAP_COUNT={len(EXECUTABLE_GAP_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
