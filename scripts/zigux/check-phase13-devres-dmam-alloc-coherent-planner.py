#!/usr/bin/env python3
"""Fail-closed checker for the Phase 13 devres dmam_alloc_coherent planner packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HELPER_PATH = Path("lib/devres.zig")
NOTE_PATH = Path("Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md")
MANIFEST_PATH = Path("zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json")
REPLAY_PATH = Path("zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig")

HELPER_MARKERS = [
    ".provides_dmam_alloc_coherent_planning = true",
    ".provides_release_record_lifetime_planning = true",
    ".provides_release_call_planning = true",
    ".provides_dmam_free_coherent_cleanup_planning = true",
    "pub fn planManagedReleaseRecordLifetime(retain: bool) ReleaseRecordLifetimePlan",
    "pub fn planManagedReleaseCall(requested_size: u64, release_record_matches: bool) ManagedReleaseCallPlan",
    "pub fn planManagedDmamAllocCoherent(input: ManagedDmamAllocCoherentInput) !ManagedDmamAllocCoherentPlan",
    "pub fn planManagedDmamFreeCoherent(requested_size: u64, release_record_matches: bool) ManagedDmamFreeCoherentPlan",
    ".release_record_consumed = release_record_matches",
    ".warns_on_release_miss = !release_record_matches",
    ".destroys_release_record_before_free = true",
]

NOTE_MARKERS = [
    "lands one pure `dmam_alloc_coherent()` planning surface in `lib/devres.zig`",
    "routes `planManagedDmamAllocCoherent(...)` through `planManagedReleaseRecordLifetime(...)`",
    "promotes the coherent-free release-call shape into explicit shared helper planning through `planManagedReleaseCall(...)`",
    "routes `planManagedDmamFreeCoherent(...)` through that shared release-call helper",
    "records that the planned coherent free destroys the release record before freeing the allocation",
    "zero-sized requests free the release record and avoid retaining detach-time cleanup ownership",
    "`scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py` is the packet-local fail-closed checker",
    "python3 scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py",
]

MANIFEST_MARKERS = [
    "\"packet\": \"phase13-devres-dmam-alloc-coherent-planner\"",
    "\"status\": \"starter_landed\"",
    "scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py",
    "\"validation_guard\": \"scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py\"",
    "provides_release_record_lifetime_planning",
    "provides_release_call_planning",
    "provides_dmam_free_coherent_cleanup_planning",
    "planManagedReleaseRecordLifetime",
    "planManagedReleaseCall",
    "planManagedDmamFreeCoherent",
    "release_record_consumed",
    "warns_on_release_miss",
    "destroys_release_record_before_free",
]

REPLAY_MARKERS = [
    'test "phase13 devres descriptor records helper-first dmam_alloc_coherent planning" {',
    'test "phase13 devres exposes shared release-record lifetime planning" {',
    'test "phase13 devres exposes shared release-call planning" {',
    'test "phase13 devres turns successful coherent-allocation planning into explicit detach cleanup planning" {',
    'test "phase13 devres warns when planned coherent free cannot find the devres record" {',
    'test "phase13 devres dmam_alloc_coherent planner manifest records the landed helper-first dma scope" {',
    'test "phase13 devres dmam_alloc_coherent planner note preserves standalone replay handles" {',
    'test "phase13 devres dmam_alloc_coherent checker stays packet-local" {',
    'try requireContains(note, "python3 scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py");',
    'try requireContains(checker, "PHASE13_DEVRES_DMAM_ALLOC_COHERENT_PLANNER_SELF_TEST=pass");',
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_markers(text: str, label: str, markers: list[str], errors: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"{label}:missing_marker:{marker}")


def validate(root: Path) -> list[str]:
    errors: list[str] = []

    helper = root / HELPER_PATH
    note = root / NOTE_PATH
    manifest = root / MANIFEST_PATH
    replay = root / REPLAY_PATH

    expected_paths = (
        ("helper", HELPER_PATH, helper),
        ("note", NOTE_PATH, note),
        ("manifest", MANIFEST_PATH, manifest),
        ("replay", REPLAY_PATH, replay),
    )
    for _, relative_path, full_path in expected_paths:
        if not full_path.exists():
            errors.append(f"missing:{relative_path.as_posix()}")

    if errors:
        return errors

    helper_text = read_text(helper)
    note_text = read_text(note)
    manifest_text = read_text(manifest)
    replay_text = read_text(replay)

    require_markers(helper_text, "helper", HELPER_MARKERS, errors)
    require_markers(note_text, "note", NOTE_MARKERS, errors)
    require_markers(manifest_text, "manifest", MANIFEST_MARKERS, errors)
    require_markers(replay_text, "replay", REPLAY_MARKERS, errors)

    return errors


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def seed_fixture_tree(root: Path) -> None:
    write_text(root / HELPER_PATH, "\n".join(HELPER_MARKERS) + "\n")
    write_text(root / NOTE_PATH, "\n".join(NOTE_MARKERS) + "\n")
    write_text(root / MANIFEST_PATH, "\n".join(MANIFEST_MARKERS) + "\n")
    write_text(root / REPLAY_PATH, "\n".join(REPLAY_MARKERS) + "\n")


def assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="zigux_phase13_devres_dmam_alloc_checker_") as temp_dir:
        root = Path(temp_dir)

        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        seed_fixture_tree(root)
        (root / REPLAY_PATH).unlink()
        assert_only(
            validate(root),
            [f"missing:{REPLAY_PATH.as_posix()}"],
            "missing_replay_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / HELPER_PATH, "broken\n")
        assert_only(
            validate(root),
            [f"helper:missing_marker:{marker}" for marker in HELPER_MARKERS],
            "helper_missing_markers_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / NOTE_PATH, "broken\n")
        assert_only(
            validate(root),
            [f"note:missing_marker:{marker}" for marker in NOTE_MARKERS],
            "note_missing_markers_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / MANIFEST_PATH,
            "\n".join(
                marker
                for marker in MANIFEST_MARKERS
                if marker != "\"validation_guard\": \"scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py\""
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "manifest:missing_marker:\"validation_guard\": \"scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py\""
            ],
            "manifest_missing_validation_guard_failed",
        )
        case_count += 1

    print("PHASE13_DEVRES_DMAM_ALLOC_COHERENT_PLANNER_SELF_TEST=pass")
    print(f"PHASE13_DEVRES_DMAM_ALLOC_COHERENT_PLANNER_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = validate(args.root)
    if errors:
        for error in errors:
            print(error)
        return 1

    print("PHASE13_DEVRES_DMAM_ALLOC_COHERENT_PLANNER=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
