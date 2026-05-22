#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=workqueue_packet

Fail-closed checker for the dedicated Phase 14 workqueue bridge packet.

This checker stays scoped to the review-only `kernel/workqueue.c` study packet.
It validates that the bridge, dedicated tests, manifest, slice note, survey
note, and shared traceability notes all still agree on the same blocked-
maintenance, wrapper-first posture without claiming live workqueue ownership.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


MARKER = "PHASE14_CHECK_PACKET=workqueue_packet"
WORKQUEUE_BRIDGE_PATH = Path("kernel/workqueue_bridge.zig")
WORKQUEUE_TEST_PATH = Path("zigux/tests/phase14_workqueue_bridge.zig")
WORKQUEUE_REVIEWABILITY_PATH = Path("zigux/tests/phase14_workqueue_reviewability.zig")
WORKQUEUE_MANIFEST_PATH = Path("zigux/tests/phase14_workqueue_bridge_manifest.json")
WORKQUEUE_SLICE_PATH = Path("Documentation/zigux/phase14-workqueue-bridge-slice.md")
WORKQUEUE_SURVEY_PATH = Path("Documentation/zigux/phase14-workqueue-bridge-survey.md")
TRACEABILITY_PATH = Path("Documentation/zigux/phase14-core-boundary-traceability.md")
SMOKE_SURVEY_PATH = Path("Documentation/zigux/phase14-end-to-end-smoke-survey.md")

REQUIRED_FILES = (
    WORKQUEUE_BRIDGE_PATH,
    WORKQUEUE_TEST_PATH,
    WORKQUEUE_REVIEWABILITY_PATH,
    WORKQUEUE_MANIFEST_PATH,
    WORKQUEUE_SLICE_PATH,
    WORKQUEUE_SURVEY_PATH,
    TRACEABILITY_PATH,
    SMOKE_SURVEY_PATH,
)

REQUIRED_MARKERS = {
    WORKQUEUE_BRIDGE_PATH: (
        'return "phase14-workqueue-scheduler-visible-worker-state-refinement";',
        '.posture = "blocked_maintenance",',
        "zigux/tests/phase14_workqueue_reviewability.zig",
        "__cancel_work_sync",
        "disable_work()",
        "__flush_work()",
    ),
    WORKQUEUE_TEST_PATH: (
        'try std.testing.expectEqualStrings("phase14-workqueue-scheduler-visible-worker-state-refinement", workqueue_bridge.WorkqueueBridgeLab.currentSliceId());',
        'try std.testing.expect(std.mem.indexOf(u8, handoff.next_future_target, "blocked maintenance") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, handoff.reopen_conditions[1], "shared smoke or core traceability packet") != null);',
    ),
    WORKQUEUE_REVIEWABILITY_PATH: (
        'try std.testing.expectEqualStrings("P14-L04", manifest.lane_key);',
        '"zig test zigux/tests/phase14_workqueue_reviewability.zig"',
        '"phase14-workqueue-live-execution-blocker"',
        '"blocked maintenance"',
        "Documentation/zigux/phase14-core-boundary-traceability.md",
        "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    ),
    WORKQUEUE_MANIFEST_PATH: (
        '"lane_key": "P14-L04"',
        '"anchor": "kernel/workqueue.c"',
        '"current_lane_posture": "blocked_maintenance"',
        '"zig test zigux/tests/phase14_workqueue_reviewability.zig"',
        '"phase14-workqueue-live-execution-blocker"',
        '"phase14-workqueue-scheduler-visible-worker-state-refinement"',
    ),
    WORKQUEUE_SLICE_PATH: (
        "`PHASE14_LANE_KEY=P14-L04`",
        "`PHASE14_DIRECT_ZIG_TEST=zigux/tests/phase14_workqueue_reviewability.zig`",
        "`PHASE14_ANCHOR=kernel/workqueue.c`",
        "blocked maintenance",
    ),
    WORKQUEUE_SURVEY_PATH: (
        "`PHASE14_LANE_KEY=P14-L04`",
        "`PHASE14_ANCHOR=kernel/workqueue.c`",
        "`PHASE14_BLOCKER=phase14-workqueue-live-execution-blocker`",
        "`zig test zigux/tests/phase14_workqueue_reviewability.zig`",
        "`make -C zigux phase14-validate`",
        "shared packet-local validation rather than direct bridge-local trust gates",
        "missing `phase14-smoke`, `phase14-test`, and `phase14` wrappers",
    ),
    TRACEABILITY_PATH: (
        "`kernel/workqueue.c`: `Study / Boundary Only`",
        "`kernel/workqueue_bridge.zig` remains review-only boundary evidence",
        "delayed-work requeue ownership",
    ),
    SMOKE_SURVEY_PATH: (
        "`zigux/tests/phase14_workqueue_reviewability.zig`",
        "workqueue: `zigux/tests/phase14_workqueue_bridge_manifest.json`, lane `P14-L04`",
        "boundary-map-and-reviewability foothold",
        "`make -C zigux phase14-validate`",
    ),
}


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    if MARKER not in Path(__file__).read_text(encoding="utf-8"):
        errors.append("missing_checker_marker:self")

    missing = [rel.as_posix() for rel in REQUIRED_FILES if not (root / rel).exists()]
    if missing:
        return [f"missing_file:{rel}" for rel in missing] + errors

    for rel, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel)
        for marker in markers:
            if marker not in text:
                errors.append(f"missing_marker:{rel.as_posix()}:{marker}")
    return errors


def fixture_text(rel: Path) -> str:
    title_map = {
        WORKQUEUE_SLICE_PATH: "# Phase 14 Workqueue Bridge Slice",
        WORKQUEUE_SURVEY_PATH: "# Phase 14 Workqueue Bridge Survey",
        TRACEABILITY_PATH: "# Phase 14 Core Boundary Traceability",
        SMOKE_SURVEY_PATH: "# Phase 14 End-to-End Smoke Survey",
    }
    if rel.suffix == ".py":
        return "#!/usr/bin/env python3\n"
    if rel.suffix == ".zig":
        return "\n".join(("// fixture", *REQUIRED_MARKERS.get(rel, ()))) + "\n"
    if rel.suffix == ".json":
        return "\n".join(("{", *[f"  {marker}" for marker in REQUIRED_MARKERS.get(rel, ())], "}")) + "\n"
    title = title_map.get(rel, "# Fixture")
    return "\n".join((title, *REQUIRED_MARKERS.get(rel, ()))) + "\n"


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for rel in REQUIRED_FILES:
        write_text(root, rel, fixture_text(rel))


def remove_marker(root: Path, rel: Path, marker: str) -> None:
    text = read_text(root, rel)
    updated = text.replace(marker + "\n", "", 1)
    if updated == text:
        updated = text.replace(marker, "", 1)
    write_text(root, rel, updated)


def expect_failure(root: Path, expected_fragment: str) -> None:
    errors = check(root)
    if not any(expected_fragment in error for error in errors):
        raise SystemExit(f"expected failure containing {expected_fragment!r}, got {errors!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-workqueue-packet-"))
    try:
        write_fixture_tree(base)
        errors = check(base)
        if errors:
            print("PHASE14_WORKQUEUE_PACKET_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        cases = 1
        write_fixture_tree(base)
        (base / WORKQUEUE_MANIFEST_PATH).unlink()
        expect_failure(base, f"missing_file:{WORKQUEUE_MANIFEST_PATH.as_posix()}")
        cases += 1

        write_fixture_tree(base)
        remove_marker(base, WORKQUEUE_BRIDGE_PATH, REQUIRED_MARKERS[WORKQUEUE_BRIDGE_PATH][0])
        expect_failure(base, REQUIRED_MARKERS[WORKQUEUE_BRIDGE_PATH][0])
        cases += 1

        write_fixture_tree(base)
        remove_marker(base, WORKQUEUE_REVIEWABILITY_PATH, REQUIRED_MARKERS[WORKQUEUE_REVIEWABILITY_PATH][2])
        expect_failure(base, REQUIRED_MARKERS[WORKQUEUE_REVIEWABILITY_PATH][2])
        cases += 1

        write_fixture_tree(base)
        remove_marker(base, WORKQUEUE_SURVEY_PATH, REQUIRED_MARKERS[WORKQUEUE_SURVEY_PATH][4])
        expect_failure(base, REQUIRED_MARKERS[WORKQUEUE_SURVEY_PATH][4])
        cases += 1

        write_fixture_tree(base)
        remove_marker(base, TRACEABILITY_PATH, REQUIRED_MARKERS[TRACEABILITY_PATH][1])
        expect_failure(base, REQUIRED_MARKERS[TRACEABILITY_PATH][1])
        cases += 1

        write_fixture_tree(base)
        remove_marker(base, SMOKE_SURVEY_PATH, REQUIRED_MARKERS[SMOKE_SURVEY_PATH][1])
        expect_failure(base, REQUIRED_MARKERS[SMOKE_SURVEY_PATH][1])
        cases += 1

        print("PHASE14_WORKQUEUE_PACKET_SELF_TEST=pass")
        print(f"PHASE14_WORKQUEUE_PACKET_SELF_TEST_CASE_COUNT={cases}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(args.root)
    if errors:
        print("PHASE14_WORKQUEUE_PACKET=fail")
        print("PHASE14_WORKQUEUE_PACKET_ISSUES_START")
        for error in errors:
            print(error)
        print("PHASE14_WORKQUEUE_PACKET_ISSUES_END")
        return 1

    print("PHASE14_WORKQUEUE_PACKET=pass")
    print(f"PHASE14_WORKQUEUE_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE14_WORKQUEUE_PACKET_REQUIRED_MARKER_COUNT={sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())