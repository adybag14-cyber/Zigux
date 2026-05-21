#!/usr/bin/env python3
"""Check that the shared Phase 14 tests-root reminder stays aligned with repo reality."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path
import sys

SURVEY_PATH = Path("Documentation/zigux/phase14-end-to-end-smoke-survey.md")
ATTACHED_TOOLCHAIN_GUIDANCE_PATH = Path(
    "Documentation/zigux/phase14-attached-toolchain-guidance-gap.md"
)
TESTS_ROOT_README_PATH = Path("zigux/tests/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
SHARED_SMOKE_ROUTE_CHECKER_PATH = Path("scripts/zigux/check-phase14-shared-smoke-route.py")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase14.py")
RELEASE_BOUNDARY_CHECKER_PATH = Path("scripts/zigux/check-phase14-release-boundary-exact-counts.py")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKQUEUE_BRIDGE_PATH = Path("kernel/workqueue_bridge.zig")
WORKQUEUE_TEST_PATH = Path("zigux/tests/phase14_workqueue_bridge.zig")
WORKQUEUE_REVIEWABILITY_PATH = Path("zigux/tests/phase14_workqueue_reviewability.zig")
WORKQUEUE_MANIFEST_PATH = Path("zigux/tests/phase14_workqueue_bridge_manifest.json")

TESTS_PHASE14_START = "## Phase 14 shared smoke packet"
TESTS_PHASE14_END = "## Phase 15 shared governance packet"
SCRIPTS_PHASE14_START = "## Phase 14"
SCRIPTS_PHASE14_END = "## Phase 15"

REQUIRED_FILES = (
    SURVEY_PATH,
    ATTACHED_TOOLCHAIN_GUIDANCE_PATH,
    TESTS_ROOT_README_PATH,
    SCRIPTS_README_PATH,
    REVIEW_CHECKLIST_PATH,
    SHARED_SMOKE_ROUTE_CHECKER_PATH,
    VALIDATOR_PATH,
    RELEASE_BOUNDARY_CHECKER_PATH,
    MAKEFILE_PATH,
    WORKQUEUE_BRIDGE_PATH,
    WORKQUEUE_TEST_PATH,
    WORKQUEUE_REVIEWABILITY_PATH,
    WORKQUEUE_MANIFEST_PATH,
)

REQUIRED_SURVEY_MARKERS = (
    "some shared reminder surfaces may still lag this current route split",
    "the directly readable release-boundary exact-count guard",
    "the directly readable workqueue boundary shard",
    "the readable Makefile body with its shipped non-Phase-14 routes",
)

REQUIRED_ATTACHED_TOOLCHAIN_MARKERS = (
    "`zigux/tests/README.md` is aligned on the returned route split, but it still undercounts the broader recovered shared packet",
    "`Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`, and `zigux/tests/phase14_ring_buffer_survey.zig`",
    "`scripts/zigux/check-phase14-shared-smoke-route.py` is directly readable again through the current contents path",
    "`zigux/Makefile` is readable again, and its live body currently exposes the shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes together with the returned `phase14-validate` gate, but no `phase14-smoke`, `phase14-test`, or `phase14` targets",
)

REQUIRED_TESTS_ROOT_MARKERS = (
    "`Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
    "`Documentation/zigux/phase14-productization-gap-survey.md`",
    "`Documentation/zigux/phase14-shared-smoke-current-master-gap.md`",
    "`scripts/zigux/check-phase14-shared-smoke-route.py`",
    "`scripts/zigux/validate-phase14.py`",
    "`scripts/zigux/check-phase14-release-boundary-exact-counts.py`",
    "`zigux/Makefile`",
    "`kernel/workqueue_bridge.zig`",
    "`zigux/tests/phase14_workqueue_bridge.zig`",
    "`zigux/tests/phase14_workqueue_reviewability.zig`",
    "`zigux/tests/phase14_workqueue_bridge_manifest.json`",
    "Current `master` does materialize `zigux/Makefile`, but its live body currently exposes the Phase 2 toolchain and kbuild routes together with the bounded Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families plus `phase14-validate`, while `phase14-smoke`, `phase14-test`, and `phase14` still remain absent",
    "`zigux/tests/phase14_build.zig`",
    "`zigux/tests/phase14_end_to_end_smoke_manifest.json`",
    "`zigux/tests/phase14_end_to_end_smoke_survey.zig`",
    "`zigux/tests/phase14_skbuff_bridge.zig`",
    "`zigux/tests/phase14_rcu_tree_survey.zig`",
    "`net/core/skbuff_bridge.zig`",
)

FORBIDDEN_TESTS_ROOT_MARKERS = (
    "`Documentation/zigux/phase14-release-boundary-survey.md`",
    "`Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`",
    "`zigux/tests/phase14_ring_buffer_survey.zig`",
)

REQUIRED_SCRIPTS_README_MARKERS = (
    "Phase 14 flow - the current scripts-root shared smoke packet stays reviewable through the recovered study-only documentation packet",
    "`scripts/zigux/check-phase14-shared-smoke-route.py`, `scripts/zigux/validate-phase14.py`, and `scripts/zigux/check-phase14-release-boundary-exact-counts.py` keep the recoverable shared-smoke layer visible",
    "`kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json` keep the directly readable workqueue reviewability shard explicit",
    "current `master` does materialize `zigux/Makefile`, and its live body now exposes the shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes together with `phase14-validate`; `phase14-smoke`, `phase14-test`, and `phase14` still do not return",
    "keep same-lane follow-through narrowed to reminder-surface truthfulness",
)

REQUIRED_CHECKLIST_MARKERS = (
    "if the change touches the shared Phase 14 smoke packet",
    "`Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
    "`scripts/zigux/validate-phase14.py` and `scripts/zigux/check-phase14-release-boundary-exact-counts.py`",
    "`kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, `zigux/tests/phase14_workqueue_bridge_manifest.json`, and `zigux/tests/phase14_ring_buffer_survey.zig` explicit as the directly readable study-only workqueue-and-ring-buffer companions",
    "`zigux/Makefile` framed as readable current evidence for the shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes together with the returned `make -C zigux phase14-validate` gate while `phase14-smoke`, `phase14-test`, and `phase14` stay packet-local or repo-reality-gap vocabulary",
    "`zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_rcu_tree_survey.zig`, and `net/core/skbuff_bridge.zig` framed as exact-readback gaps",
)

REQUIRED_ROUTE_CHECKER_MARKERS = (
    "PHASE14_CHECK_PACKET=shared_smoke_route",
    "PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=pass",
    "run: make -C zigux phase14-validate",
)

FORBIDDEN_MAKEFILE_MARKERS = (
    "phase14-smoke:",
    "phase14-test:",
    "phase14: phase14-validate phase14-smoke phase14-test",
)


def section(text: str, start_marker: str, end_marker: str, label: str) -> str:
    start = text.find(start_marker)
    if start == -1:
        raise SystemExit(f"{label} missing section start marker: {start_marker}")
    end = text.find(end_marker, start)
    if end == -1:
        raise SystemExit(f"{label} missing section end marker: {end_marker}")
    return text[start:end]


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"{label} missing required markers: " + ", ".join(missing))


def require_absent_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    present = [marker for marker in markers if marker in text]
    if present:
        raise SystemExit(f"{label} found forbidden markers: " + ", ".join(present))


def check(root: Path) -> None:
    missing_files = [str(path) for path in REQUIRED_FILES if not (root / path).exists()]
    if missing_files:
        raise SystemExit("phase14 tests-root checker missing required files: " + ", ".join(missing_files))

    survey_text = (root / SURVEY_PATH).read_text(encoding="utf-8")
    require_markers(survey_text, REQUIRED_SURVEY_MARKERS, "phase14 smoke survey")

    attached_toolchain_text = (root / ATTACHED_TOOLCHAIN_GUIDANCE_PATH).read_text(encoding="utf-8")
    require_markers(
        attached_toolchain_text,
        REQUIRED_ATTACHED_TOOLCHAIN_MARKERS,
        "phase14 attached-toolchain guidance",
    )

    tests_text = (root / TESTS_ROOT_README_PATH).read_text(encoding="utf-8")
    tests_section = section(
        tests_text,
        TESTS_PHASE14_START,
        TESTS_PHASE14_END,
        "phase14 tests-root README",
    )
    require_markers(tests_section, REQUIRED_TESTS_ROOT_MARKERS, "phase14 tests-root README")
    require_absent_markers(
        tests_section,
        FORBIDDEN_TESTS_ROOT_MARKERS,
        "phase14 tests-root README",
    )

    scripts_text = (root / SCRIPTS_README_PATH).read_text(encoding="utf-8")
    scripts_section = section(
        scripts_text,
        SCRIPTS_PHASE14_START,
        SCRIPTS_PHASE14_END,
        "phase14 scripts README",
    )
    require_markers(scripts_section, REQUIRED_SCRIPTS_README_MARKERS, "phase14 scripts README")

    checklist_text = (root / REVIEW_CHECKLIST_PATH).read_text(encoding="utf-8")
    require_markers(checklist_text, REQUIRED_CHECKLIST_MARKERS, "phase14 review checklist")

    route_checker_text = (root / SHARED_SMOKE_ROUTE_CHECKER_PATH).read_text(encoding="utf-8")
    require_markers(route_checker_text, REQUIRED_ROUTE_CHECKER_MARKERS, "phase14 shared smoke route checker")

    makefile_text = (root / MAKEFILE_PATH).read_text(encoding="utf-8")
    require_absent_markers(makefile_text, FORBIDDEN_MAKEFILE_MARKERS, "phase14 makefile")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(
        root / SURVEY_PATH,
        "\n".join(("# Phase 14 End-to-End Smoke Survey", *REQUIRED_SURVEY_MARKERS)) + "\n",
    )
    write_text(
        root / ATTACHED_TOOLCHAIN_GUIDANCE_PATH,
        "# Phase 14 Attached Toolchain Guidance Gap\n"
        + "\n".join(REQUIRED_ATTACHED_TOOLCHAIN_MARKERS)
        + "\n",
    )
    write_text(
        root / TESTS_ROOT_README_PATH,
        "\n".join(
            (
                "# zigux/tests",
                TESTS_PHASE14_START,
                *REQUIRED_TESTS_ROOT_MARKERS,
                TESTS_PHASE14_END,
            )
        )
        + "\n",
    )
    write_text(
        root / SCRIPTS_README_PATH,
        "\n".join(
            (
                "# scripts/zigux",
                SCRIPTS_PHASE14_START,
                *REQUIRED_SCRIPTS_README_MARKERS,
                SCRIPTS_PHASE14_END,
            )
        )
        + "\n",
    )
    write_text(
        root / REVIEW_CHECKLIST_PATH,
        "# Zigux Review Checklist\n" + "\n".join(REQUIRED_CHECKLIST_MARKERS) + "\n",
    )
    write_text(
        root / SHARED_SMOKE_ROUTE_CHECKER_PATH,
        "# route checker\n" + "\n".join(REQUIRED_ROUTE_CHECKER_MARKERS) + "\n",
    )
    write_text(root / VALIDATOR_PATH, "# validator placeholder\n")
    write_text(root / RELEASE_BOUNDARY_CHECKER_PATH, "# release checker placeholder\n")
    write_text(
        root / MAKEFILE_PATH,
        "\n".join(
            (
                "phase3-validate:",
                "phase4-validate:",
                "phase6-base64-test:",
                "phase8-validate:",
                "phase10-validate:",
                "phase12-smoke:",
                "phase14-validate:",
            )
        )
        + "\n",
    )
    write_text(root / WORKQUEUE_BRIDGE_PATH, "// workqueue bridge\n")
    write_text(root / WORKQUEUE_TEST_PATH, "// workqueue test\n")
    write_text(root / WORKQUEUE_REVIEWABILITY_PATH, "// workqueue reviewability\n")
    write_text(root / WORKQUEUE_MANIFEST_PATH, "{}\n")


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        check(root)
    except SystemExit as exc:
        if expected_fragment not in str(exc):
            raise SystemExit(
                f"expected failure fragment {expected_fragment!r}, got {str(exc)!r}"
            ) from exc
    else:
        raise SystemExit(f"expected failure containing {expected_fragment!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-tests-readme-"))
    try:
        write_fixture_tree(base)
        check(base)

        cases = 1

        write_fixture_tree(base)
        (base / ATTACHED_TOOLCHAIN_GUIDANCE_PATH).unlink()
        expect_failure(base, "missing required files")
        cases += 1

        write_fixture_tree(base)
        attached_path = base / ATTACHED_TOOLCHAIN_GUIDANCE_PATH
        attached_path.write_text(
            attached_path.read_text(encoding="utf-8").replace(
                REQUIRED_ATTACHED_TOOLCHAIN_MARKERS[0],
                "`zigux/tests/README.md` is already aligned with the returned route split",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(base, "phase14 attached-toolchain guidance missing required markers")
        cases += 1

        write_fixture_tree(base)
        tests_path = base / TESTS_ROOT_README_PATH
        tests_path.write_text(
            tests_path.read_text(encoding="utf-8").replace(
                TESTS_PHASE14_END,
                FORBIDDEN_TESTS_ROOT_MARKERS[1] + "\n" + TESTS_PHASE14_END,
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(base, "phase14 tests-root README found forbidden markers")
        cases += 1

        write_fixture_tree(base)
        route_checker_path = base / SHARED_SMOKE_ROUTE_CHECKER_PATH
        route_checker_path.write_text(
            route_checker_path.read_text(encoding="utf-8").replace(
                REQUIRED_ROUTE_CHECKER_MARKERS[2],
                "run: make -C zigux phase14-smoke",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(base, "phase14 shared smoke route checker missing required markers")
        cases += 1

        write_fixture_tree(base)
        makefile_path = base / MAKEFILE_PATH
        makefile_path.write_text(
            makefile_path.read_text(encoding="utf-8") + "phase14-smoke:\n",
            encoding="utf-8",
        )
        expect_failure(base, "phase14 makefile found forbidden markers")
        cases += 1

        print("PHASE14_TESTS_README_SMOKE_SUMMARY_SELF_TEST=pass")
        print(f"PHASE14_TESTS_README_SMOKE_SUMMARY_SELF_TEST_CASE_COUNT={cases}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing Documentation/zigux, scripts/zigux, and zigux/tests",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    check(args.root.resolve())
    print("PHASE14_TESTS_README_SMOKE_SUMMARY=pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
