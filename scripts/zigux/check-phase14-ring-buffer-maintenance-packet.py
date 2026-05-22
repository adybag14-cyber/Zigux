#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

RING_BUFFER_SURVEY_PATH = "Documentation/zigux/phase14-ring-buffer-survey.md"
RING_BUFFER_MANIFEST_PATH = "zigux/tests/phase14_ring_buffer_manifest.json"
RING_BUFFER_SURVEY_TEST_PATH = "zigux/tests/phase14_ring_buffer_survey.zig"
PRODUCTIZATION_GAP_PATH = "Documentation/zigux/phase14-productization-gap-survey.md"
SHARED_SMOKE_GAP_PATH = "Documentation/zigux/phase14-shared-smoke-current-master-gap.md"
SMOKE_SURVEY_PATH = "Documentation/zigux/phase14-end-to-end-smoke-survey.md"
CORE_TRACEABILITY_PATH = "Documentation/zigux/phase14-core-boundary-traceability.md"

REQUIRED_FILES = [
    RING_BUFFER_SURVEY_PATH,
    RING_BUFFER_MANIFEST_PATH,
    RING_BUFFER_SURVEY_TEST_PATH,
    PRODUCTIZATION_GAP_PATH,
    SHARED_SMOKE_GAP_PATH,
    SMOKE_SURVEY_PATH,
    CORE_TRACEABILITY_PATH,
]

REQUIRED_MARKERS = {
    RING_BUFFER_SURVEY_PATH: [
        "`PHASE14_STATUS=study_only`",
        "current ring-buffer packet replay vocabulary",
        "`zig test zigux/tests/phase14_ring_buffer_survey.zig`",
        "`zig build test --build-file zigux/tests/phase14_build.zig --summary all`",
        "keep those two routes as ring-buffer-local replay vocabulary only",
        "missing dedicated `make -C zigux phase14` route",
        "returned survey companion and shared build shard framed as public-raw-backed ring-buffer-local evidence",
        "phase14-ring-buffer-maintenance-handoff",
        "phase14-ring-buffer-zig-port-blocker",
    ],
    RING_BUFFER_MANIFEST_PATH: [
        '"lane_key": "P14-L08"',
        '"status_bucket": "study_only"',
        '"last_closed_followup": "phase14-ring-buffer-maintenance-handoff"',
        '"blocked_gap": "phase14-ring-buffer-zig-port-blocker"',
        '"current_lane_posture": "maintenance_mode"',
        '"replay_vocabulary_only_until_paths_return": false',
        '"zig test zigux/tests/phase14_ring_buffer_survey.zig"',
        '"zig build test --build-file zigux/tests/phase14_build.zig --summary all"',
        '"phase14-build-gate-current-master-gap"',
        '"restored_via_public_raw_readback"',
    ],
    RING_BUFFER_SURVEY_TEST_PATH: [
        'try std.testing.expectEqualStrings("P14-L08", manifest.lane_key);',
        'try std.testing.expectEqualStrings("phase14-ring-buffer-maintenance-handoff", manifest.study_only_governance.last_closed_followup);',
        'try std.testing.expectEqualStrings("phase14-ring-buffer-zig-port-blocker", manifest.study_only_governance.blocked_gap);',
        'try std.testing.expectEqualStrings("maintenance_mode", manifest.maintenance_handoff.current_lane_posture);',
        'try std.testing.expectEqual(false, manifest.maintenance_handoff.replay_vocabulary_only_until_paths_return);',
        'try std.testing.expect(std.mem.indexOf(u8, note, "keep those two routes as ring-buffer-local replay vocabulary only") != null);',
    ],
    PRODUCTIZATION_GAP_PATH: [
        "`zigux/tests/phase14_ring_buffer_survey.zig` now returns through the current contents path as a directly readable ring-buffer survey companion",
        "the directly readable ring-buffer survey companion",
        "without promoting the missing executable-layer paths or the absent `phase14-smoke`, `phase14-test`, and `phase14` wrappers",
    ],
    SHARED_SMOKE_GAP_PATH: [
        "- `PHASE14_LANE_KEY=P14-L05`",
        "recover the dedicated ring-buffer survey companion again through the current contents path",
        "returned ring-buffer survey companion",
        "the aligned manifest posture",
        "continued absence of the broader `phase14-smoke`, `phase14-test`, and `phase14` wrappers on current `master`",
    ],
    SMOKE_SURVEY_PATH: [
        "* directly readable ring-buffer survey companion in this lane's current evidence split:",
        "* `zigux/tests/phase14_ring_buffer_survey.zig`",
        "the directly readable ring-buffer survey foothold explicit",
        "ring-buffer-survey drift",
        "directly readable ring-buffer survey companion",
    ],
    CORE_TRACEABILITY_PATH: [
        "ring buffer routes through `P14-L08`",
        "the dedicated `P14-L08` survey note and manifest remain ring-buffer-local study evidence",
        "workqueue and ring buffer as study-only anchors",
    ],
}


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")
    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fixture_text(rel_path: str) -> str:
    if rel_path == RING_BUFFER_SURVEY_TEST_PATH:
        return "\n".join(
            [
                "const std = @import(\"std\");",
                "",
                *REQUIRED_MARKERS[rel_path],
                "",
            ]
        )
    return "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, fixture_text(rel_path))


def remove_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(marker + "\n", "", 1)
    if updated == text:
        updated = text.replace(marker, "", 1)
    path.write_text(updated, encoding="utf-8")


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    root = Path(tempfile.mkdtemp(prefix="phase14-ring-buffer-packet-"))
    try:
        write_fixture_tree(root)
        failures = validate(root)
        if failures:
            raise SystemExit(f"fixture should pass: {failures!r}")

        missing_file_cases = [
            RING_BUFFER_SURVEY_PATH,
            RING_BUFFER_MANIFEST_PATH,
            RING_BUFFER_SURVEY_TEST_PATH,
            PRODUCTIZATION_GAP_PATH,
        ]
        for rel_path in missing_file_cases:
            write_fixture_tree(root)
            (root / rel_path).unlink()
            expect_failure(root, f"missing_file:{rel_path}")

        marker_cases = [
            (RING_BUFFER_SURVEY_PATH, REQUIRED_MARKERS[RING_BUFFER_SURVEY_PATH][4]),
            (RING_BUFFER_MANIFEST_PATH, REQUIRED_MARKERS[RING_BUFFER_MANIFEST_PATH][4]),
            (RING_BUFFER_SURVEY_TEST_PATH, REQUIRED_MARKERS[RING_BUFFER_SURVEY_TEST_PATH][4]),
            (PRODUCTIZATION_GAP_PATH, REQUIRED_MARKERS[PRODUCTIZATION_GAP_PATH][0]),
            (SHARED_SMOKE_GAP_PATH, REQUIRED_MARKERS[SHARED_SMOKE_GAP_PATH][2]),
            (SMOKE_SURVEY_PATH, REQUIRED_MARKERS[SMOKE_SURVEY_PATH][0]),
            (CORE_TRACEABILITY_PATH, REQUIRED_MARKERS[CORE_TRACEABILITY_PATH][0]),
        ]
        for rel_path, marker in marker_cases:
            write_fixture_tree(root)
            remove_marker(root / rel_path, marker)
            expect_failure(root, f"missing_marker:{rel_path}:{marker}")

        case_count = len(missing_file_cases) + len(marker_cases)
        print("PHASE14_RING_BUFFER_MAINTENANCE_PACKET_SELF_TEST=pass")
        print(f"PHASE14_RING_BUFFER_MAINTENANCE_PACKET_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(root, ignore_errors=True)


def write_sample_root(root: Path) -> None:
    write_fixture_tree(root)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the parked Phase 14 ring-buffer maintenance packet stays aligned "
            "across the survey note, manifest, survey test, and shared productization notes."
        )
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE14_RING_BUFFER_MAINTENANCE_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = validate(args.root)
    if failures:
        print("PHASE14_RING_BUFFER_MAINTENANCE_PACKET=fail")
        print("PHASE14_RING_BUFFER_MAINTENANCE_PACKET_DRIFT_START")
        for failure in failures:
            print(failure)
        print("PHASE14_RING_BUFFER_MAINTENANCE_PACKET_DRIFT_END")
        return 1

    print("PHASE14_RING_BUFFER_MAINTENANCE_PACKET=pass")
    print(f"PHASE14_RING_BUFFER_MAINTENANCE_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE14_RING_BUFFER_MAINTENANCE_PACKET_REQUIRED_MARKER_COUNT={sum(len(v) for v in REQUIRED_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
