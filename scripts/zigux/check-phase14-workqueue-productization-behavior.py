#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=workqueue_productization_behavior

Fail-closed checker for the bounded Phase 14 workqueue productization-behavior
packet.

This guard verifies that the current blocked-maintenance workqueue packet keeps
the exact shared-packet productization checks aligned across the bridge survey,
the bridge manifest, the bridge-local reviewability test, the slice note, and
the current `phase14-validate` Makefile route without promoting those shared
checks into a bridge-local trust gate.
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


SURVEY_PATH = Path("Documentation/zigux/phase14-workqueue-bridge-survey.md")
SLICE_PATH = Path("Documentation/zigux/phase14-workqueue-bridge-slice.md")
MANIFEST_PATH = Path("zigux/tests/phase14_workqueue_bridge_manifest.json")
REVIEWABILITY_PATH = Path("zigux/tests/phase14_workqueue_reviewability.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

DIRECT_TRUST_GATE = "zig test zigux/tests/phase14_workqueue_reviewability.zig"
PRODUCTIZATION_POSTURE = "shared_packet_local_only"
PRODUCTIZATION_BEHAVIOR_NOTE = (
    "These checks verify shared packet-local productization behavior around "
    "the current phase14-validate route and its reminder surfaces. They do "
    "not replace the direct workqueue reviewability replay as the bridge-local "
    "trust gate."
)

PRODUCTIZATION_EXACT_CHECKS = [
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

MAKEFILE_ROUTE_MARKERS = [
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

FORBIDDEN_BRIDGE_LOCAL_PROMOTION_MARKERS = [
    "zig build test --build-file zigux/tests/phase14_build.zig --summary all",
    "make -C zigux phase14-smoke",
    "make -C zigux phase14-test",
    "make -C zigux phase14",
]


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


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
    for rel in [SURVEY_PATH, SLICE_PATH, MANIFEST_PATH, REVIEWABILITY_PATH, MAKEFILE_PATH]:
        if not (root / rel).exists():
            errors.append(f"missing_file:{rel.as_posix()}")
    if errors:
        return errors

    survey_text = read_text(root, SURVEY_PATH)
    require_markers(
        errors,
        SURVEY_PATH,
        survey_text,
        [
            "## Exact productization checks",
            DIRECT_TRUST_GATE,
            PRODUCTIZATION_BEHAVIOR_NOTE,
            "shared packet-local productization checks:",
        ],
    )
    require_markers(errors, SURVEY_PATH, survey_text, PRODUCTIZATION_EXACT_CHECKS)
    require_absent(errors, SURVEY_PATH, survey_text, FORBIDDEN_BRIDGE_LOCAL_PROMOTION_MARKERS[:-1])

    slice_text = read_text(root, SLICE_PATH)
    require_markers(
        errors,
        SLICE_PATH,
        slice_text,
        [
            "the next same-lane step is still a packet-local reread",
            "phase14_build",
            "shared-packet evidence rather than a bridge-local trust promotion signal",
        ],
    )

    reviewability_text = read_text(root, REVIEWABILITY_PATH)
    require_markers(
        errors,
        REVIEWABILITY_PATH,
        reviewability_text,
        [
            f"try std.testing.expectEqualStrings(\"{PRODUCTIZATION_POSTURE}\", manifest.maintenance_handoff.productization_posture);",
            f"\"{DIRECT_TRUST_GATE}\"",
            PRODUCTIZATION_BEHAVIOR_NOTE,
            "shared packet-local validation rather than direct bridge-local trust gates",
            "missing `phase14-smoke`, `phase14-test`, and `phase14` wrappers",
        ],
    )
    require_absent(
        errors,
        REVIEWABILITY_PATH,
        reviewability_text,
        ['"\tzig build test --build-file zigux/tests/phase14_build.zig --summary all"'],
    )

    makefile_text = read_text(root, MAKEFILE_PATH)
    require_markers(errors, MAKEFILE_PATH, makefile_text, MAKEFILE_ROUTE_MARKERS)

    manifest_text = read_text(root, MANIFEST_PATH)
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        errors.append(f"invalid_json:{MANIFEST_PATH.as_posix()}:{exc.msg}")
        return errors

    try:
        handoff = manifest["maintenance_handoff"]
    except KeyError:
        errors.append("missing_manifest_key:maintenance_handoff")
        return errors

    if handoff.get("current_lane_posture") != "blocked_maintenance":
        errors.append(
            "manifest_value_mismatch:maintenance_handoff.current_lane_posture:"
            f"expected='blocked_maintenance':actual={handoff.get('current_lane_posture')!r}"
        )
    if handoff.get("replay_before_trusting") != [DIRECT_TRUST_GATE]:
        errors.append(
            "manifest_value_mismatch:maintenance_handoff.replay_before_trusting:"
            f"expected={[DIRECT_TRUST_GATE]!r}:actual={handoff.get('replay_before_trusting')!r}"
        )
    if handoff.get("productization_posture") != PRODUCTIZATION_POSTURE:
        errors.append(
            "manifest_value_mismatch:maintenance_handoff.productization_posture:"
            f"expected={PRODUCTIZATION_POSTURE!r}:actual={handoff.get('productization_posture')!r}"
        )
    if handoff.get("productization_exact_checks") != PRODUCTIZATION_EXACT_CHECKS:
        errors.append(
            "manifest_value_mismatch:maintenance_handoff.productization_exact_checks:"
            f"expected={PRODUCTIZATION_EXACT_CHECKS!r}:actual={handoff.get('productization_exact_checks')!r}"
        )
    if handoff.get("productization_behavior_note") != PRODUCTIZATION_BEHAVIOR_NOTE:
        errors.append(
            "manifest_value_mismatch:maintenance_handoff.productization_behavior_note:"
            f"expected={PRODUCTIZATION_BEHAVIOR_NOTE!r}:actual={handoff.get('productization_behavior_note')!r}"
        )

    return errors


def fixture_survey_text() -> str:
    exact_checks = "\n".join(f"    * `{item}`" for item in PRODUCTIZATION_EXACT_CHECKS)
    return (
        "# Phase 14 Workqueue Bridge Survey\n\n"
        "## Exact productization checks\n\n"
        "For the current bounded step, productization behavior is only considered verified when the packet keeps these exact checks aligned with the same study-only posture:\n\n"
        "  * direct bridge-local trust gate:\n"
        f"    * `{DIRECT_TRUST_GATE}`\n"
        "  * shared packet-local productization checks:\n"
        f"{exact_checks}\n\n"
        f"{PRODUCTIZATION_BEHAVIOR_NOTE}\n"
    )


def fixture_slice_text() -> str:
    return (
        "# Phase 14 Workqueue Bridge Slice\n\n"
        "the next same-lane step is still a packet-local reread that leaves broader "
        "`phase14_build` rerun vocabulary to shared-packet evidence rather than a "
        "bridge-local trust promotion signal\n"
    )


def fixture_reviewability_text() -> str:
    lines = [
        "const expected_productization_exact_checks = [_][]const u8{",
        *[f'    "{item}",' for item in PRODUCTIZATION_EXACT_CHECKS],
        "};",
        f'try std.testing.expectEqualStrings("{PRODUCTIZATION_POSTURE}", manifest.maintenance_handoff.productization_posture);',
        f'"{DIRECT_TRUST_GATE}"',
        PRODUCTIZATION_BEHAVIOR_NOTE,
        "shared packet-local validation rather than direct bridge-local trust gates",
        "missing `phase14-smoke`, `phase14-test`, and `phase14` wrappers",
    ]
    return "\n".join(lines) + "\n"


def fixture_manifest_text() -> str:
    payload = {
        "maintenance_handoff": {
            "current_lane_posture": "blocked_maintenance",
            "replay_before_trusting": [DIRECT_TRUST_GATE],
            "productization_posture": PRODUCTIZATION_POSTURE,
            "productization_exact_checks": PRODUCTIZATION_EXACT_CHECKS,
            "productization_behavior_note": PRODUCTIZATION_BEHAVIOR_NOTE,
        }
    }
    return json.dumps(payload, indent=2) + "\n"


def fixture_makefile_text() -> str:
    body = "\n".join(
        [
            "phase14-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-shared-smoke-route.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-tests-readme-smoke-summary.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py",
        ]
    )
    return body + "\n"


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root, SURVEY_PATH, fixture_survey_text())
    write_text(root, SLICE_PATH, fixture_slice_text())
    write_text(root, REVIEWABILITY_PATH, fixture_reviewability_text())
    write_text(root, MANIFEST_PATH, fixture_manifest_text())
    write_text(root, MAKEFILE_PATH, fixture_makefile_text())


def expect_failure(root: Path, expected_fragment: str) -> None:
    errors = check(root)
    if not any(expected_fragment in error for error in errors):
        raise SystemExit(
            f"expected failure containing {expected_fragment!r}, got {errors!r}"
        )


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

        cases = 1

        write_fixture_tree(base)
        (base / MANIFEST_PATH).unlink()
        expect_failure(base, "missing_file:zigux/tests/phase14_workqueue_bridge_manifest.json")
        cases += 1

        write_fixture_tree(base)
        write_text(
            base,
            SURVEY_PATH,
            fixture_survey_text().replace(
                PRODUCTIZATION_BEHAVIOR_NOTE,
                "stale behavior note",
                1,
            ),
        )
        expect_failure(base, "missing_marker:Documentation/zigux/phase14-workqueue-bridge-survey.md:These checks verify shared packet-local")
        cases += 1

        write_fixture_tree(base)
        stale_manifest = json.loads(fixture_manifest_text())
        stale_manifest["maintenance_handoff"]["productization_posture"] = "bridge_local"
        write_text(base, MANIFEST_PATH, json.dumps(stale_manifest, indent=2) + "\n")
        expect_failure(base, "manifest_value_mismatch:maintenance_handoff.productization_posture")
        cases += 1

        write_fixture_tree(base)
        write_text(
            base,
            REVIEWABILITY_PATH,
            fixture_reviewability_text().replace(
                "shared packet-local validation rather than direct bridge-local trust gates",
                "shared packet-local validation promoted to direct trust",
                1,
            ),
        )
        expect_failure(base, "missing_marker:zigux/tests/phase14_workqueue_reviewability.zig:shared packet-local validation rather than direct bridge-local trust gates")
        cases += 1

        write_fixture_tree(base)
        write_text(
            base,
            MAKEFILE_PATH,
            fixture_makefile_text().replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py\n",
                "",
                1,
            ),
        )
        expect_failure(base, "missing_marker:zigux/Makefile:scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test")
        cases += 1

        print("PHASE14_WORKQUEUE_PRODUCTIZATION_BEHAVIOR_SELF_TEST=pass")
        print(f"PHASE14_WORKQUEUE_PRODUCTIZATION_BEHAVIOR_SELF_TEST_CASE_COUNT={cases}")
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
        print("PHASE14_WORKQUEUE_PRODUCTIZATION_BEHAVIOR_ISSUES_START")
        for error in errors:
            print(error)
        print("PHASE14_WORKQUEUE_PRODUCTIZATION_BEHAVIOR_ISSUES_END")
        return 1

    print("PHASE14_WORKQUEUE_PRODUCTIZATION_BEHAVIOR=pass")
    print(f"PHASE14_WORKQUEUE_PRODUCTIZATION_BEHAVIOR_EXACT_CHECK_COUNT={len(PRODUCTIZATION_EXACT_CHECKS)}")
    print(f"PHASE14_WORKQUEUE_PRODUCTIZATION_BEHAVIOR_MAKEFILE_MARKER_COUNT={len(MAKEFILE_ROUTE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
