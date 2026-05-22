#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=productization_roadmap_basis

Fail-closed checker for the shared Phase 14 productization-gap note.

This guard keeps the roadmap-backed expectations for Phase 14 aligned with the
current shared-smoke packet, the returned `phase14-validate` route split, and
the study-only versus freeze-in-C posture of the four core-adjacent anchors.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


MARKER = "PHASE14_CHECK_PACKET=productization_roadmap_basis"
PRODUCTIZATION_GAP_PATH = Path("Documentation/zigux/phase14-productization-gap-survey.md")
SMOKE_SURVEY_PATH = Path("Documentation/zigux/phase14-end-to-end-smoke-survey.md")
FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
STUDY_ONLY_ACCOUNTING_PATH = Path("Documentation/zigux/phase15-study-only-anchor-accounting.md")
ROUTE_CHECKER_PATH = Path("scripts/zigux/check-phase14-shared-smoke-route.py")
TESTS_README_CHECKER_PATH = Path("scripts/zigux/check-phase14-tests-readme-smoke-summary.py")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase14.py")
MAKEFILE_PATH = Path("zigux/Makefile")
MANIFEST_PATH = Path("zigux/tests/phase14_end_to_end_smoke_manifest.json")
WORKQUEUE_MANIFEST_PATH = Path("zigux/tests/phase14_workqueue_bridge_manifest.json")
RING_BUFFER_SURVEY_PATH = Path("zigux/tests/phase14_ring_buffer_survey.zig")

REQUIRED_FILES = (
    PRODUCTIZATION_GAP_PATH,
    SMOKE_SURVEY_PATH,
    FREEZE_MAP_PATH,
    STUDY_ONLY_ACCOUNTING_PATH,
    ROUTE_CHECKER_PATH,
    TESTS_README_CHECKER_PATH,
    VALIDATOR_PATH,
    MAKEFILE_PATH,
    MANIFEST_PATH,
    WORKQUEUE_MANIFEST_PATH,
    RING_BUFFER_SURVEY_PATH,
)

PRODUCTIZATION_MARKERS = (
    "Phase 14 in `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md` is the `Core-Adjacent Bounded Internals` lane.",
    "- boundary maps",
    "- concurrency audits",
    "- explicit stay-in-C decisions where warranted",
    "- wrapper-first or study-only posture",
    "- `kernel/workqueue.c`",
    "- `kernel/trace/ring_buffer.c`",
    "- `net/core/skbuff.c`",
    "- `kernel/rcu/tree.c`",
    "`zigux/Makefile` is readable again on current `master`, and its live body currently exposes the Phase 2 toolchain and kbuild routes together with the bounded Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes plus `phase14-validate`, but no `phase14-smoke`, `phase14-test`, or `phase14` targets",
    "`scripts/zigux/check-phase14-shared-smoke-route.py` now returns through the current contents path",
    "`scripts/zigux/check-phase14-tests-readme-smoke-summary.py` now returns through the current contents path",
    "`scripts/zigux/validate-phase14.py` now returns through the current contents path",
    "`scripts/zigux/check-phase14-release-boundary-exact-counts.py` now returns through the current contents path",
    "`zigux/tests/phase14_end_to_end_smoke_manifest.json` now returns through the current contents path",
    "`kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json` are directly readable again as the workqueue-local reviewability shard",
    "`zigux/tests/phase14_ring_buffer_survey.zig` now returns through the current contents path as a directly readable ring-buffer survey companion",
    "- `zigux/tests/phase14_build.zig`",
    "- `zigux/tests/phase14_end_to_end_smoke_survey.zig`",
    "- `zigux/tests/phase14_skbuff_bridge.zig`",
    "- `zigux/tests/phase14_rcu_tree_survey.zig`",
    "- `net/core/skbuff_bridge.zig`",
    "Given the roadmap, the correct Phase 14 posture remains study-only and wrapper-first.",
    "the directly readable shared-smoke route checker",
    "the directly readable tests-root reminder checker",
    "the directly readable validator body",
    "the directly readable release-boundary exact-count guard",
)

SMOKE_SURVEY_MARKERS = (
    "Primary product goal:",
    "The Phase 14 roadmap treats `kernel/workqueue.c`, `net/core/skbuff.c`, `kernel/trace/ring_buffer.c`, and `kernel/rcu/tree.c` as boundary-study or freeze-in-C anchors.",
    "`zigux/tests/phase14_ring_buffer_survey.zig` is directly readable again on current `master`",
    "the current readable route layer still stops at `make -C zigux phase14-validate`",
)

FREEZE_MAP_MARKERS = (
    "## Freeze In C Initially",
    "- `kernel/rcu/tree.c`",
    "- `net/core/skbuff.c`",
    "## Study / Boundary Only",
    "- `kernel/workqueue.c`",
    "- `kernel/trace/ring_buffer.c`",
)

STUDY_ONLY_ACCOUNTING_MARKERS = (
    "The roadmap keeps two deep-core areas in a narrower posture than the four freeze-in-C anchors: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only",
    "### `kernel/workqueue.c`",
    "### `kernel/trace/ring_buffer.c`",
)

ROUTE_CHECKER_MARKERS = (
    "PHASE14_CHECK_PACKET=shared_smoke_route",
    "run: make -C zigux phase14-validate",
)

TESTS_README_CHECKER_MARKERS = (
    "Check that the shared Phase 14 tests-root reminder stays aligned with repo reality.",
    "PHASE14_TESTS_README_SMOKE_SUMMARY_SELF_TEST=pass",
)

VALIDATOR_MARKERS = (
    "PHASE14_VALIDATION=pass",
    "PHASE14_VALIDATOR_SELF_TEST=pass",
    "Documentation/zigux/phase14-productization-gap-survey.md",
)

MAKEFILE_MARKERS = (
    "phase14-validate:",
    "scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
    "scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test",
    "scripts/zigux/validate-phase14.py --self-test",
)

FORBIDDEN_MAKEFILE_MARKERS = (
    "phase14-smoke:",
    "phase14-test:",
    "phase14: phase14-validate",
)

MANIFEST_MARKERS = (
    '"validation_gate": "make -C zigux phase14-validate"',
    '"smoke_commands": [',
    '"make -C zigux phase14-validate"',
    '"smoke_shard_commands": []',
    '"phase14_make_smoke_target_present": false',
)

WORKQUEUE_MANIFEST_MARKERS = (
    '"lane_key": "P14-L04"',
    '"current_lane_posture": "blocked_maintenance"',
)

RING_BUFFER_SURVEY_MARKERS = (
    "phase14-ring-buffer-maintenance-handoff",
    "phase14-ring-buffer-tracefs-reader-serialization-followup",
)


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_markers(errors: list[str], rel: Path, text: str, markers: tuple[str, ...]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"missing_marker:{rel.as_posix()}:{marker}")


def require_absent(errors: list[str], rel: Path, text: str, markers: tuple[str, ...]) -> None:
    for marker in markers:
        if marker in text:
            errors.append(f"forbidden_marker:{rel.as_posix()}:{marker}")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            errors.append(f"missing_file:{rel.as_posix()}")
    if errors:
        return errors

    require_markers(errors, PRODUCTIZATION_GAP_PATH, read_text(root, PRODUCTIZATION_GAP_PATH), PRODUCTIZATION_MARKERS)
    require_markers(errors, SMOKE_SURVEY_PATH, read_text(root, SMOKE_SURVEY_PATH), SMOKE_SURVEY_MARKERS)
    require_markers(errors, FREEZE_MAP_PATH, read_text(root, FREEZE_MAP_PATH), FREEZE_MAP_MARKERS)
    require_markers(
        errors,
        STUDY_ONLY_ACCOUNTING_PATH,
        read_text(root, STUDY_ONLY_ACCOUNTING_PATH),
        STUDY_ONLY_ACCOUNTING_MARKERS,
    )
    require_markers(errors, ROUTE_CHECKER_PATH, read_text(root, ROUTE_CHECKER_PATH), ROUTE_CHECKER_MARKERS)
    require_markers(
        errors,
        TESTS_README_CHECKER_PATH,
        read_text(root, TESTS_README_CHECKER_PATH),
        TESTS_README_CHECKER_MARKERS,
    )
    require_markers(errors, VALIDATOR_PATH, read_text(root, VALIDATOR_PATH), VALIDATOR_MARKERS)

    makefile_text = read_text(root, MAKEFILE_PATH)
    require_markers(errors, MAKEFILE_PATH, makefile_text, MAKEFILE_MARKERS)
    require_absent(errors, MAKEFILE_PATH, makefile_text, FORBIDDEN_MAKEFILE_MARKERS)

    require_markers(errors, MANIFEST_PATH, read_text(root, MANIFEST_PATH), MANIFEST_MARKERS)
    require_markers(
        errors,
        WORKQUEUE_MANIFEST_PATH,
        read_text(root, WORKQUEUE_MANIFEST_PATH),
        WORKQUEUE_MANIFEST_MARKERS,
    )
    require_markers(
        errors,
        RING_BUFFER_SURVEY_PATH,
        read_text(root, RING_BUFFER_SURVEY_PATH),
        RING_BUFFER_SURVEY_MARKERS,
    )
    return errors


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)

    write_text(
        root,
        PRODUCTIZATION_GAP_PATH,
        "# Phase 14 Productization Gap Survey\n\n" + "\n".join(PRODUCTIZATION_MARKERS) + "\n",
    )
    write_text(
        root,
        SMOKE_SURVEY_PATH,
        "# Phase 14 End-to-End Smoke Survey\n\n" + "\n".join(SMOKE_SURVEY_MARKERS) + "\n",
    )
    write_text(root, FREEZE_MAP_PATH, "# Zigux Freeze Map\n\n" + "\n".join(FREEZE_MAP_MARKERS) + "\n")
    write_text(
        root,
        STUDY_ONLY_ACCOUNTING_PATH,
        "# Phase 15 Study-Only Anchor Accounting\n\n" + "\n".join(STUDY_ONLY_ACCOUNTING_MARKERS) + "\n",
    )
    write_text(
        root,
        ROUTE_CHECKER_PATH,
        "# route checker\n" + "\n".join(ROUTE_CHECKER_MARKERS) + "\n",
    )
    write_text(
        root,
        TESTS_README_CHECKER_PATH,
        "# tests checker\n" + "\n".join(TESTS_README_CHECKER_MARKERS) + "\n",
    )
    write_text(root, VALIDATOR_PATH, "# validator\n" + "\n".join(VALIDATOR_MARKERS) + "\n")
    write_text(
        root,
        MAKEFILE_PATH,
        "\n".join(
            (
                "phase12:",
                "phase14-validate:",
                "scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
                "scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test",
                "scripts/zigux/validate-phase14.py --self-test",
            )
        )
        + "\n",
    )
    write_text(
        root,
        MANIFEST_PATH,
        "{\n"
        '  "validation_gate": "make -C zigux phase14-validate",\n'
        '  "smoke_commands": [\n'
        '    "make -C zigux phase14-validate"\n'
        "  ],\n"
        '  "smoke_shard_commands": [],\n'
        '  "phase14_make_smoke_target_present": false\n'
        "}\n",
    )
    write_text(
        root,
        WORKQUEUE_MANIFEST_PATH,
        '{\n  "lane_key": "P14-L04",\n  "current_lane_posture": "blocked_maintenance"\n}\n',
    )
    write_text(
        root,
        RING_BUFFER_SURVEY_PATH,
        "// ring buffer survey\n"
        + "\n".join(RING_BUFFER_SURVEY_MARKERS)
        + "\n",
    )


def expect_failure(root: Path, expected_fragment: str) -> None:
    errors = check(root)
    if not errors:
        raise SystemExit(f"expected failure containing {expected_fragment!r}")
    if not any(expected_fragment in error for error in errors):
        raise SystemExit(f"expected failure fragment {expected_fragment!r}, got {errors!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-productization-roadmap-"))
    try:
        write_fixture_tree(base)
        errors = check(base)
        if errors:
            print("PHASE14_PRODUCTIZATION_ROADMAP_BASIS_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        cases = 1

        write_fixture_tree(base)
        (base / RING_BUFFER_SURVEY_PATH).unlink()
        expect_failure(base, "missing_file:zigux/tests/phase14_ring_buffer_survey.zig")
        cases += 1

        write_fixture_tree(base)
        write_text(
            base,
            PRODUCTIZATION_GAP_PATH,
            read_text(base, PRODUCTIZATION_GAP_PATH).replace(
                "- concurrency audits",
                "- concurrency guesses",
                1,
            ),
        )
        expect_failure(
            base,
            "missing_marker:Documentation/zigux/phase14-productization-gap-survey.md:- concurrency audits",
        )
        cases += 1

        write_fixture_tree(base)
        write_text(
            base,
            MAKEFILE_PATH,
            read_text(base, MAKEFILE_PATH) + "phase14-smoke:\n",
        )
        expect_failure(base, "forbidden_marker:zigux/Makefile:phase14-smoke:")
        cases += 1

        write_fixture_tree(base)
        write_text(
            base,
            MANIFEST_PATH,
            read_text(base, MANIFEST_PATH).replace(
                '"phase14_make_smoke_target_present": false',
                '"phase14_make_smoke_target_present": true',
                1,
            ),
        )
        expect_failure(base, 'missing_marker:zigux/tests/phase14_end_to_end_smoke_manifest.json:"phase14_make_smoke_target_present": false')
        cases += 1

        print("PHASE14_PRODUCTIZATION_ROADMAP_BASIS_SELF_TEST=pass")
        print(f"PHASE14_PRODUCTIZATION_ROADMAP_BASIS_SELF_TEST_CASE_COUNT={cases}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_fixture_tree(args.write_sample_root)
        print(f"PHASE14_PRODUCTIZATION_ROADMAP_BASIS_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    errors = check(args.root)
    if errors:
        print("PHASE14_PRODUCTIZATION_ROADMAP_BASIS=fail")
        print("PHASE14_PRODUCTIZATION_ROADMAP_BASIS_ISSUES_START")
        for error in errors:
            print(error)
        print("PHASE14_PRODUCTIZATION_ROADMAP_BASIS_ISSUES_END")
        return 1

    print("PHASE14_PRODUCTIZATION_ROADMAP_BASIS=pass")
    print(f"PHASE14_PRODUCTIZATION_ROADMAP_BASIS_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE14_PRODUCTIZATION_ROADMAP_BASIS_REQUIRED_MARKER_COUNT="
        f"{len(PRODUCTIZATION_MARKERS) + len(SMOKE_SURVEY_MARKERS) + len(FREEZE_MAP_MARKERS) + len(STUDY_ONLY_ACCOUNTING_MARKERS) + len(ROUTE_CHECKER_MARKERS) + len(TESTS_README_CHECKER_MARKERS) + len(VALIDATOR_MARKERS) + len(MAKEFILE_MARKERS) + len(MANIFEST_MARKERS) + len(WORKQUEUE_MANIFEST_MARKERS) + len(RING_BUFFER_SURVEY_MARKERS)}"
    )
    print(f"PHASE14_PRODUCTIZATION_ROADMAP_BASIS_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_MAKEFILE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())