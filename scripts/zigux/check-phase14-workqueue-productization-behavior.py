#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=workqueue_productization_behavior

Fail-closed checker for the current Phase 14 workqueue productization behavior.

This guard keeps the blocked-maintenance workqueue packet honest around the
exact shared-packet checks recorded in the current survey and manifest. It does
not promote the workqueue bridge to live ownership. It only verifies that the
current productization behavior remains the same narrow study-only packet.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


MARKER = "PHASE14_CHECK_PACKET=workqueue_productization_behavior"
SURVEY_PATH = Path("Documentation/zigux/phase14-workqueue-bridge-survey.md")
SLICE_PATH = Path("Documentation/zigux/phase14-workqueue-bridge-slice.md")
MANIFEST_PATH = Path("zigux/tests/phase14_workqueue_bridge_manifest.json")
REVIEWABILITY_PATH = Path("zigux/tests/phase14_workqueue_reviewability.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

EXACT_CHECKS = [
    "python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
    "python3 scripts/zigux/check-phase14-shared-smoke-route.py",
    "python3 scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test",
    "python3 scripts/zigux/check-phase14-tests-readme-smoke-summary.py",
    "python3 scripts/zigux/validate-phase14.py --self-test",
    "python3 scripts/zigux/validate-phase14.py",
    "python3 scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test",
    "python3 scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
    "python3 scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test",
    "python3 scripts/zigux/check-phase14-release-boundary-exact-counts.py",
    "make -C zigux phase14-validate",
]

SURVEY_MARKERS = [
    "`PHASE14_STATUS=blocked_maintenance`",
    "`PHASE14_LANE_KEY=P14-L04`",
    "`PHASE14_CURRENT_SLICE=phase14-workqueue-scheduler-visible-worker-state-refinement`",
    "`PHASE14_REVIEWABILITY_TEST=zigux/tests/phase14_workqueue_reviewability.zig`",
    "## Exact productization checks",
    "productization behavior is only considered verified",
    "They do not promote the workqueue bridge to owner status",
]

SLICE_MARKERS = [
    "`PHASE14_LANE_KEY=P14-L04`",
    "`PHASE14_STATUS=blocked_maintenance`",
    "`PHASE14_REVIEWABILITY_TEST=zigux/tests/phase14_workqueue_reviewability.zig`",
    "shared-packet evidence rather than a bridge-local trust promotion signal",
]

MANIFEST_MARKERS = [
    '"lane_key": "P14-L04"',
    '"current_lane_posture": "blocked_maintenance"',
    '"productization_posture": "shared_packet_local_only"',
    '"productization_behavior_note": "These checks verify shared packet-local productization behavior around the current phase14-validate route and its reminder surfaces. They do not replace the direct workqueue reviewability replay as the bridge-local trust gate."',
]

REVIEWABILITY_MARKERS = [
    "const expected_productization_exact_checks = [_][]const u8{",
    '"python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test",',
    '"python3 scripts/zigux/check-phase14-release-boundary-exact-counts.py",',
    '"make -C zigux phase14-validate",',
]

MAKEFILE_MARKERS = [
    "phase14-validate:",
    "scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
    "scripts/zigux/check-phase14-shared-smoke-route.py",
    "scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test",
    "scripts/zigux/check-phase14-tests-readme-smoke-summary.py",
    "scripts/zigux/validate-phase14.py --self-test",
    "scripts/zigux/validate-phase14.py",
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test",
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test",
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py",
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


def require_exact_checks(errors: list[str], rel: Path, text: str) -> None:
    for marker in EXACT_CHECKS:
        if marker not in text:
            errors.append(f"missing_exact_check:{rel.as_posix()}:{marker}")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    if MARKER not in Path(__file__).read_text(encoding="utf-8"):
        errors.append("missing_checker_marker:self")

    required_paths = [
        SURVEY_PATH,
        SLICE_PATH,
        MANIFEST_PATH,
        REVIEWABILITY_PATH,
        MAKEFILE_PATH,
    ]
    for rel in required_paths:
        if not (root / rel).exists():
            errors.append(f"missing_file:{rel.as_posix()}")
    if errors:
        return errors

    survey_text = read_text(root, SURVEY_PATH)
    require_markers(errors, SURVEY_PATH, survey_text, SURVEY_MARKERS)
    require_exact_checks(errors, SURVEY_PATH, survey_text)

    slice_text = read_text(root, SLICE_PATH)
    require_markers(errors, SLICE_PATH, slice_text, SLICE_MARKERS)

    manifest_text = read_text(root, MANIFEST_PATH)
    require_markers(errors, MANIFEST_PATH, manifest_text, MANIFEST_MARKERS)
    require_exact_checks(errors, MANIFEST_PATH, manifest_text)

    reviewability_text = read_text(root, REVIEWABILITY_PATH)
    require_markers(errors, REVIEWABILITY_PATH, reviewability_text, REVIEWABILITY_MARKERS)
    require_exact_checks(errors, REVIEWABILITY_PATH, reviewability_text)

    makefile_text = read_text(root, MAKEFILE_PATH)
    require_markers(errors, MAKEFILE_PATH, makefile_text, MAKEFILE_MARKERS)

    return errors


def fixture_survey() -> str:
    bullets = "\n".join(f"    * `{item}`" for item in EXACT_CHECKS[:-1])
    return (
        "# Phase 14 Workqueue Bridge Survey\n\n"
        "* `PHASE14_STATUS=blocked_maintenance`\n"
        "* `PHASE14_LANE_KEY=P14-L04`\n"
        "* `PHASE14_CURRENT_SLICE=phase14-workqueue-scheduler-visible-worker-state-refinement`\n"
        "* `PHASE14_REVIEWABILITY_TEST=zigux/tests/phase14_workqueue_reviewability.zig`\n\n"
        "## Exact productization checks\n\n"
        "For the current bounded step, productization behavior is only considered verified when the packet keeps these exact checks aligned with the same study-only posture:\n\n"
        "  * direct bridge-local trust gate:\n"
        "    * `zig test zigux/tests/phase14_workqueue_reviewability.zig`\n"
        "  * shared packet-local productization checks:\n"
        f"{bullets}\n"
        f"    * `{EXACT_CHECKS[-1]}`\n\n"
        "Those productization-facing checks verify shared packet-local routing and reminder-surface behavior. They do not promote the workqueue bridge to owner status, and they do not replace the direct workqueue reviewability replay as the bridge-local trust gate.\n"
    )


def fixture_slice() -> str:
    return (
        "# Phase 14 Workqueue Bridge Slice\n\n"
        "* `PHASE14_LANE_KEY=P14-L04`\n"
        "* `PHASE14_STATUS=blocked_maintenance`\n"
        "* `PHASE14_REVIEWABILITY_TEST=zigux/tests/phase14_workqueue_reviewability.zig`\n\n"
        "Leave broader `phase14_build` rerun vocabulary to the shared Phase 14 smoke packet as shared-packet evidence rather than a bridge-local trust promotion signal.\n"
    )


def fixture_manifest() -> str:
    lines = ",\n".join(f'      "{item}"' for item in EXACT_CHECKS)
    return (
        "{\n"
        '  "lane_key": "P14-L04",\n'
        '  "maintenance_handoff": {\n'
        '    "current_lane_posture": "blocked_maintenance",\n'
        '    "productization_posture": "shared_packet_local_only",\n'
        '    "productization_exact_checks": [\n'
        f"{lines}\n"
        "    ],\n"
        '    "productization_behavior_note": "These checks verify shared packet-local productization behavior around the current phase14-validate route and its reminder surfaces. They do not replace the direct workqueue reviewability replay as the bridge-local trust gate."\n'
        "  }\n"
        "}\n"
    )


def fixture_reviewability() -> str:
    lines = "\n".join(f'    "{item}",' for item in EXACT_CHECKS)
    return (
        "const expected_productization_exact_checks = [_][]const u8{\n"
        f"{lines}\n"
        "};\n"
    )


def fixture_makefile() -> str:
    lines = "\n".join(f"\t$(PYTHON) {item}" for item in EXACT_CHECKS[:-1])
    return f"phase14-validate:\n{lines}\n"


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root, SURVEY_PATH, fixture_survey())
    write_text(root, SLICE_PATH, fixture_slice())
    write_text(root, MANIFEST_PATH, fixture_manifest())
    write_text(root, REVIEWABILITY_PATH, fixture_reviewability())
    write_text(root, MAKEFILE_PATH, fixture_makefile())


def remove_once(root: Path, rel: Path, marker: str) -> None:
    text = read_text(root, rel)
    updated = text.replace(marker, "", 1)
    write_text(root, rel, updated)


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-workqueue-productization-"))
    try:
        write_fixture_tree(base)
        errors = check(base)
        if errors:
            print("PHASE14_WORKQUEUE_PRODUCTIZATION_BEHAVIOR_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        cases = [
            (SURVEY_PATH, EXACT_CHECKS[0], f"missing_exact_check:{SURVEY_PATH.as_posix()}:{EXACT_CHECKS[0]}"),
            (SURVEY_PATH, SURVEY_MARKERS[4], f"missing_marker:{SURVEY_PATH.as_posix()}:{SURVEY_MARKERS[4]}"),
            (MANIFEST_PATH, EXACT_CHECKS[-1], f"missing_exact_check:{MANIFEST_PATH.as_posix()}:{EXACT_CHECKS[-1]}"),
            (MANIFEST_PATH, MANIFEST_MARKERS[2], f"missing_marker:{MANIFEST_PATH.as_posix()}:{MANIFEST_MARKERS[2]}"),
            (REVIEWABILITY_PATH, REVIEWABILITY_MARKERS[0], f"missing_marker:{REVIEWABILITY_PATH.as_posix()}:{REVIEWABILITY_MARKERS[0]}"),
            (MAKEFILE_PATH, MAKEFILE_MARKERS[-2], f"missing_marker:{MAKEFILE_PATH.as_posix()}:{MAKEFILE_MARKERS[-2]}"),
        ]
        for rel, marker, expected in cases:
            write_fixture_tree(base)
            remove_once(base, rel, marker)
            errors = check(base)
            if expected not in errors:
                print("PHASE14_WORKQUEUE_PRODUCTIZATION_BEHAVIOR_SELF_TEST=fail")
                print(f"expected {expected!r}, got {errors!r}")
                return 1

        print("PHASE14_WORKQUEUE_PRODUCTIZATION_BEHAVIOR_SELF_TEST=pass")
        print("PHASE14_WORKQUEUE_PRODUCTIZATION_BEHAVIOR_SELF_TEST_CASE_COUNT=6")
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
        print("PHASE14_WORKQUEUE_PRODUCTIZATION_BEHAVIOR=fail")
        print("PHASE14_WORKQUEUE_PRODUCTIZATION_BEHAVIOR_DRIFT_START")
        for error in errors:
            print(error)
        print("PHASE14_WORKQUEUE_PRODUCTIZATION_BEHAVIOR_DRIFT_END")
        return 1

    print("PHASE14_WORKQUEUE_PRODUCTIZATION_BEHAVIOR=pass")
    print(f"PHASE14_WORKQUEUE_PRODUCTIZATION_BEHAVIOR_EXACT_CHECK_COUNT={len(EXACT_CHECKS)}")
    print(f"PHASE14_WORKQUEUE_PRODUCTIZATION_BEHAVIOR_MAKEFILE_MARKER_COUNT={len(MAKEFILE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
