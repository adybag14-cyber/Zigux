#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

REQUIRED_FILES = [
    "Documentation/zigux/phase13-libfs-slice.md",
    "Documentation/zigux/phase13-libfs-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "fs/libfs.zig",
    "zigux/tests/phase13_build.zig",
    "zigux/tests/phase13_libfs.zig",
    "zigux/tests/phase13_libfs_addressability.zig",
    "zigux/tests/phase13_libfs_reviewability.zig",
    "zigux/tests/phase13_libfs_manifest.json",
    "zigux/Makefile",
]

SLICE_MARKERS = [
    "simple_statfs()",
    "simple_lookup()",
    "simple_read_from_buffer()",
    "simple_write_to_buffer()",
    "memory_read_from_buffer()",
    "dcache_readdir()-adjacent emit planner",
    "dcache_dir_open() setup helper surface",
    "dcache_dir_close() cursor-release helper surface",
    "dcache_dir_lseek() cursor-reposition helper surface",
    "simple_transaction_release()",
    "generic_check_addressable() planner",
    "simple_open() planner",
    "cursor-backed directory iteration",
]

SURVEY_MARKERS = [
    "PHASE13_SLICE=libfs-helper-reviewability-packet",
    "landed `phase13-libfs-dcache-dir-open-helper`",
    "landed `phase13-libfs-dcache-dir-close-helper`",
    "landed `phase13-libfs-cursor-reposition-helper`",
    "landed `phase13-libfs-transaction-release-helper`",
    "landed `phase13-libfs-addressability-helper`",
    "landed `phase13-libfs-simple-open-helper`",
    "blocked `phase13-libfs-dcache-cursor-helpers`",
    "focused `zigux/tests/phase13_libfs_addressability.zig` file",
    "dedicated helper-local evidence rather than a ninth shared replay step",
    "shared eight-test `phase13_build.zig` route",
]

LIBFS_MARKERS = [
    "pub fn simpleStatFs(",
    "pub fn simpleLookup(",
    "pub fn simpleReadFromBuffer(",
    "pub fn simpleWriteToBuffer(",
    "pub fn memoryReadFromBuffer(",
    "pub fn dcacheDirSeekPlan(",
    "pub fn offsetDirSeekPlan(",
    "pub fn offsetReaddirPlan(",
    "pub fn dcacheReaddirEmitPlan(",
    "pub fn dcacheDirOpenPlan(",
    "pub fn dcacheDirClosePlan(",
    "pub fn dcacheCursorRepositionPlan(",
    "pub fn simpleTransactionGetPlan(",
    "pub fn simpleTransactionSetPlan(",
    "pub fn simpleTransactionReleasePlan(",
    "pub fn genericCheckAddressablePlan(",
    "pub fn simpleOpenPlan(",
    "pub fn simpleDirOperationsPlan(",
    ".provides_directory_cursor_open_planning = true,",
    ".provides_directory_cursor_close_planning = true,",
    ".provides_directory_cursor_reposition_planning = true,",
    ".provides_transaction_release_planning = true,",
    ".provides_addressability_planning = true,",
    ".provides_simple_open_planning = true,",
    ".provides_simple_dir_operations_wrapper = true,",
    ".touches_live_dcache = false,",
]

BUILD_MARKERS = [
    'b.path("../../fs/libfs.zig")',
    'b.path("phase13_libfs.zig")',
    'b.path("phase13_libfs_reviewability.zig")',
    'const phase13_libfs_tests = b.addTest(.{',
    'const phase13_libfs_reviewability_tests = b.addTest(.{',
    "test_step.dependOn(&run_phase13_libfs_tests.step);",
    "test_step.dependOn(&run_phase13_libfs_reviewability_tests.step);",
]

ADDRESSABILITY_MARKERS = [
    "provides_addressability_planning",
    "genericCheckAddressablePlan(4, 0",
    "genericCheckAddressablePlan(8, 4",
    "genericCheckAddressablePlan(63, 2",
    "genericCheckAddressablePlan(12, 1 << 21",
    "genericCheckAddressablePlan(12, 128",
    "genericCheckAddressablePlan(12, 131_072",
]

REVIEWABILITY_MARKERS = [
    'try std.testing.expectEqualStrings("P13-L01", manifest.lane_key);',
    'try std.testing.expectEqualStrings("master-reviewability", manifest.surveyed_commit);',
    'try std.testing.expectEqual(@as(usize, 18), manifest.gaps.len);',
    'try std.testing.expect(descriptor.provides_directory_cursor_reposition_planning);',
    "var saw_cursor_reposition = false;",
    "var saw_cursor_blocker = false;",
    'if (std.mem.eql(u8, gap.id, "phase13-libfs-cursor-reposition-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase13-libfs-dcache-cursor-helpers")) {',
    'try std.testing.expectEqual(@as(usize, 17), starter_landed_count);',
    'try std.testing.expectEqual(@as(usize, 1), blocked_count);',
    'try std.testing.expectEqual(@as(usize, 12), helper_surface_count);',
    'try std.testing.expect(saw_cursor_reposition);',
    'try std.testing.expect(saw_cursor_blocker);',
    'contains(survey_note, "landed `phase13-libfs-cursor-reposition-helper`")',
    'contains(traceability_note, "cursor-reposition bookkeeping")',
    'contains(traceability_note, "transaction acquire, publish, and release helpers")',
    'contains(traceability_note, "`generic_check_addressable()` planner")',
    'contains(traceability_note, "`simple_open()` private-data handoff")',
    'contains(traceability_note, "deeper `dcache_readdir()` cursor-resume packet")',
]

MAKE_REQUIRED_LINES = [
    "phase13-validate:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-landlock-ruleset-packet.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-notifier-packet.py",
    "phase13: phase13-validate phase13-test",
]

SUMMARY_KEYS = [
    "preexisting_phase13_build_present",
    "preexisting_phase13_make_target_present",
    "preexisting_fs_libfs_zig_present",
    "preexisting_phase13_libfs_test_present",
    "preexisting_phase13_libfs_addressability_test_present",
    "preexisting_phase13_slice_note_present",
    "preexisting_phase13_reviewability_present",
    "preexisting_phase13_survey_note_present",
]

EXPECTED_GAPS = {
    "phase13-build-gate": "starter_landed",
    "phase13-make-target": "starter_landed",
    "phase13-libfs-starter": "starter_landed",
    "phase13-libfs-tests": "starter_landed",
    "phase13-libfs-slice-note": "starter_landed",
    "phase13-libfs-reviewability-gate": "starter_landed",
    "phase13-libfs-survey-note": "starter_landed",
    "phase13-libfs-offset-seek-helper": "starter_landed",
    "phase13-libfs-directory-emit-helper": "starter_landed",
    "phase13-libfs-transaction-buffer-helper": "starter_landed",
    "phase13-libfs-transaction-publish-helper": "starter_landed",
    "phase13-libfs-transaction-release-helper": "starter_landed",
    "phase13-libfs-dcache-dir-open-helper": "starter_landed",
    "phase13-libfs-dcache-dir-close-helper": "starter_landed",
    "phase13-libfs-cursor-reposition-helper": "starter_landed",
    "phase13-libfs-addressability-helper": "starter_landed",
    "phase13-libfs-simple-open-helper": "starter_landed",
    "phase13-libfs-dcache-cursor-helpers": "blocked_on_vfs_state",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def missing_markers(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def validate_manifest(text: str) -> list[str]:
    try:
        manifest = json.loads(text)
    except json.JSONDecodeError as exc:
        return [f"phase13-libfs-manifest:json:{exc.msg}"]

    issues: list[str] = []
    if manifest.get("lane_key") != "P13-L01":
        issues.append("phase13-libfs-manifest:lane_key")
    if manifest.get("phase") != "Phase 13":
        issues.append("phase13-libfs-manifest:phase")
    if manifest.get("anchor") != "fs/libfs.c":
        issues.append("phase13-libfs-manifest:anchor")
    if manifest.get("surveyed_commit") != "master-reviewability":
        issues.append("phase13-libfs-manifest:surveyed_commit")

    summary = manifest.get("survey_summary", {})
    for key in SUMMARY_KEYS:
        if summary.get(key) is not True:
            issues.append(f"phase13-libfs-manifest-summary:{key}")

    gaps = {
        entry.get("id"): entry.get("status")
        for entry in manifest.get("gaps", [])
        if isinstance(entry, dict)
    }
    if len(gaps) != len(EXPECTED_GAPS):
        issues.append("phase13-libfs-manifest:gap_count")
    for gap_id, status in EXPECTED_GAPS.items():
        if gap_id not in gaps:
            issues.append(f"phase13-libfs-manifest-gap:{gap_id}")
        elif gaps[gap_id] != status:
            issues.append(f"phase13-libfs-manifest-gap-status:{gap_id}")

    return issues


def validate(root: Path) -> list[str]:
    issues = [f"missing_file:{rel}" for rel in REQUIRED_FILES if not (root / rel).exists()]
    if issues:
        return issues

    issues.extend(missing_markers(read_text(root / "Documentation/zigux/phase13-libfs-slice.md"), SLICE_MARKERS, "phase13-libfs-slice"))
    issues.extend(missing_markers(read_text(root / "Documentation/zigux/phase13-libfs-survey.md"), SURVEY_MARKERS, "phase13-libfs-survey"))
    issues.extend(missing_markers(read_text(root / "fs/libfs.zig"), LIBFS_MARKERS, "phase13-libfs-zig"))
    issues.extend(missing_markers(read_text(root / "zigux/tests/phase13_build.zig"), BUILD_MARKERS, "phase13-build"))
    issues.extend(missing_markers(read_text(root / "zigux/tests/phase13_libfs_addressability.zig"), ADDRESSABILITY_MARKERS, "phase13-libfs-addressability"))
    issues.extend(missing_markers(read_text(root / "zigux/tests/phase13_libfs_reviewability.zig"), REVIEWABILITY_MARKERS, "phase13-libfs-reviewability"))
    issues.extend(missing_markers(read_text(root / "zigux/Makefile"), MAKE_REQUIRED_LINES, "makefile"))
    issues.extend(validate_manifest(read_text(root / "zigux/tests/phase13_libfs_manifest.json")))
    return issues


def seed_fixture(root: Path) -> None:
    for rel in REQUIRED_FILES:
        write_text(root / rel, "// stub\n")

    write_text(root / "Documentation/zigux/phase13-libfs-slice.md", "\n".join(SLICE_MARKERS) + "\n")
    write_text(root / "Documentation/zigux/phase13-libfs-survey.md", "\n".join(SURVEY_MARKERS) + "\n")
    write_text(root / "Documentation/zigux/phase13-roadmap-traceability.md", "\n".join([
        "cursor-reposition bookkeeping",
        "transaction acquire, publish, and release helpers",
        "`generic_check_addressable()` planner",
        "`simple_open()` private-data handoff",
        "deeper `dcache_readdir()` cursor-resume packet",
    ]) + "\n")
    write_text(root / "fs/libfs.zig", "\n".join(LIBFS_MARKERS) + "\n")
    write_text(root / "zigux/tests/phase13_build.zig", "\n".join(BUILD_MARKERS) + "\n")
    write_text(root / "zigux/tests/phase13_libfs.zig", "// packet fixture placeholder\n")
    write_text(root / "zigux/tests/phase13_libfs_addressability.zig", "\n".join(ADDRESSABILITY_MARKERS) + "\n")
    write_text(root / "zigux/tests/phase13_libfs_reviewability.zig", "\n".join(REVIEWABILITY_MARKERS) + "\n")
    write_text(root / "zigux/Makefile", "\n".join(MAKE_REQUIRED_LINES) + "\n")
    write_text(
        root / "zigux/tests/phase13_libfs_manifest.json",
        json.dumps(
            {
                "lane_key": "P13-L01",
                "phase": "Phase 13",
                "surveyed_commit": "master-reviewability",
                "anchor": "fs/libfs.c",
                "survey_summary": {key: True for key in SUMMARY_KEYS},
                "gaps": [{"id": gap_id, "status": status} for gap_id, status in EXPECTED_GAPS.items()],
            },
            indent=2,
        )
        + "\n",
    )


def assert_only(got: list[str], want: list[str], label: str) -> None:
    if got != want:
        raise SystemExit(f"{label}:got={','.join(got) or 'none'}:want={','.join(want) or 'none'}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase13_libfs_packet_") as temp_dir:
        root = Path(temp_dir)

        seed_fixture(root)
        assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        write_text(root / "Documentation/zigux/phase13-libfs-survey.md", "blocked `phase13-libfs-dcache-cursor-helpers`\n")
        assert_only(
            validate(root),
            [
                "phase13-libfs-survey:PHASE13_SLICE=libfs-helper-reviewability-packet",
                "phase13-libfs-survey:landed `phase13-libfs-dcache-dir-open-helper`",
                "phase13-libfs-survey:landed `phase13-libfs-dcache-dir-close-helper`",
                "phase13-libfs-survey:landed `phase13-libfs-cursor-reposition-helper`",
                "phase13-libfs-survey:landed `phase13-libfs-transaction-release-helper`",
                "phase13-libfs-survey:landed `phase13-libfs-addressability-helper`",
                "phase13-libfs-survey:landed `phase13-libfs-simple-open-helper`",
                "phase13-libfs-survey:focused `zigux/tests/phase13_libfs_addressability.zig` file",
                "phase13-libfs-survey:dedicated helper-local evidence rather than a ninth shared replay step",
                "phase13-libfs-survey:shared eight-test `phase13_build.zig` route",
            ],
            "survey_guard_failed",
        )
        seed_fixture(root)
        case_count += 1

        write_text(root / "zigux/tests/phase13_libfs_manifest.json", json.dumps({"lane_key": "P13-L04"}, indent=2) + "\n")
        assert_only(
            validate(root),
            [
                "phase13-libfs-manifest:lane_key",
                "phase13-libfs-manifest:phase",
                "phase13-libfs-manifest:anchor",
                "phase13-libfs-manifest:surveyed_commit",
                "phase13-libfs-manifest-summary:preexisting_phase13_build_present",
                "phase13-libfs-manifest-summary:preexisting_phase13_make_target_present",
                "phase13-libfs-manifest-summary:preexisting_fs_libfs_zig_present",
                "phase13-libfs-manifest-summary:preexisting_phase13_libfs_test_present",
                "phase13-libfs-manifest-summary:preexisting_phase13_libfs_addressability_test_present",
                "phase13-libfs-manifest-summary:preexisting_phase13_slice_note_present",
                "phase13-libfs-manifest-summary:preexisting_phase13_reviewability_present",
                "phase13-libfs-manifest-summary:preexisting_phase13_survey_note_present",
                "phase13-libfs-manifest:gap_count",
            ]
            + [f"phase13-libfs-manifest-gap:{gap_id}" for gap_id in EXPECTED_GAPS],
            "manifest_guard_failed",
        )
        seed_fixture(root)
        case_count += 1

        write_text(root / "zigux/tests/phase13_libfs_reviewability.zig", 'try std.testing.expectEqualStrings("P13-L01", manifest.lane_key);\n')
        assert_only(
            validate(root),
            [f"phase13-libfs-reviewability:{marker}" for marker in REVIEWABILITY_MARKERS[1:]],
            "reviewability_guard_failed",
        )
        case_count += 1

    print("PHASE13_LIBFS_PACKET=pass")
    print(f"PHASE13_LIBFS_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current shipped Phase 13 libfs packet surfaces.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        for issue in issues:
            print(f"PHASE13_LIBFS_PACKET_ISSUE={issue}")
        return 1

    print("PHASE13_LIBFS_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
