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
    "fs/libfs.zig",
    "zigux/tests/phase13_build.zig",
    "zigux/tests/phase13_libfs.zig",
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
    "simple_transaction_release()",
    "cursor-backed directory iteration",
]

SURVEY_MARKERS = [
    "landed `phase13-libfs-transaction-release-helper`",
    "blocked `phase13-libfs-dcache-cursor-helpers`",
    "dcache_dir_open()",
    "deeper `dcache_readdir()` cursor preconditions",
    "real helper footing reviewable",
]

LIBFS_MARKERS = [
    "pub fn simpleStatFs(",
    "pub fn simpleLookup(",
    "pub fn simpleReadFromBuffer(",
    "pub fn simpleWriteToBuffer(",
    "pub fn memoryReadFromBuffer(",
    "pub fn dcacheDirSeekPlan(",
    "pub fn offsetDirSeekPlan(",
    "pub fn dcacheReaddirEmitPlan(",
    "pub fn simpleTransactionGetPlan(",
    "pub fn simpleTransactionSetPlan(",
    "pub fn simpleTransactionReleasePlan(",
    ".provides_transaction_release_planning = true,",
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

REVIEWABILITY_MARKERS = [
    'try std.testing.expectEqual(@as(usize, 13), manifest.gaps.len);',
    "try std.testing.expect(saw_transaction_release_helper);",
    "try std.testing.expect(saw_dcache_cursor_followup);",
    'std.mem.indexOf(u8, survey_note, "landed `phase13-libfs-transaction-release-helper`")',
    'std.mem.indexOf(u8, survey_note, "blocked `phase13-libfs-dcache-cursor-helpers`")',
    'std.mem.indexOf(u8, traceability_note, "transaction acquire, publish, and release helpers")',
    'std.mem.indexOf(u8, traceability_note, "dcache_dir_open()")',
    'std.mem.indexOf(u8, traceability_note, "deeper `dcache_readdir()` cursor-precondition packet")',
]

MAKE_REQUIRED_LINES = [
    "phase13-validate:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py",
    "phase13: phase13-validate phase13-test",
]

SUMMARY_KEYS = [
    "preexisting_phase13_build_present",
    "preexisting_phase13_make_target_present",
    "preexisting_fs_libfs_zig_present",
    "preexisting_phase13_libfs_test_present",
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
    if manifest.get("lane_key") != "P13-L04":
        issues.append("phase13-libfs-manifest:lane_key")
    if manifest.get("phase") != "Phase 13":
        issues.append("phase13-libfs-manifest:phase")
    if manifest.get("anchor") != "fs/libfs.c":
        issues.append("phase13-libfs-manifest:anchor")

    summary = manifest.get("survey_summary", {})
    for key in SUMMARY_KEYS:
        if summary.get(key) is not True:
            issues.append(f"phase13-libfs-manifest-summary:{key}")

    gaps = {
        entry.get("id"): entry.get("status")
        for entry in manifest.get("gaps", [])
        if isinstance(entry, dict)
    }
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
    issues.extend(
        missing_markers(
            read_text(root / "zigux/tests/phase13_libfs_reviewability.zig"),
            REVIEWABILITY_MARKERS,
            "phase13-libfs-reviewability",
        )
    )
    issues.extend(missing_markers(read_text(root / "zigux/Makefile"), MAKE_REQUIRED_LINES, "makefile"))
    issues.extend(validate_manifest(read_text(root / "zigux/tests/phase13_libfs_manifest.json")))
    return issues


def seed_fixture(root: Path) -> None:
    for rel in REQUIRED_FILES:
        write_text(root / rel, "// stub\n")

    write_text(root / "Documentation/zigux/phase13-libfs-slice.md", "\n".join(SLICE_MARKERS) + "\n")
    write_text(root / "Documentation/zigux/phase13-libfs-survey.md", "\n".join(SURVEY_MARKERS) + "\n")
    write_text(root / "fs/libfs.zig", "\n".join(LIBFS_MARKERS) + "\n")
    write_text(root / "zigux/tests/phase13_build.zig", "\n".join(BUILD_MARKERS) + "\n")
    write_text(root / "zigux/tests/phase13_libfs_reviewability.zig", "\n".join(REVIEWABILITY_MARKERS) + "\n")
    write_text(root / "zigux/Makefile", "\n".join(MAKE_REQUIRED_LINES) + "\n")
    write_text(
        root / "zigux/tests/phase13_libfs_manifest.json",
        json.dumps(
            {
                "lane_key": "P13-L04",
                "phase": "Phase 13",
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
        raise SystemExit(
            f"phase13-libfs-packet-self-test:{label}:got={','.join(got) or 'none'}:want={','.join(want) or 'none'}"
        )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase13_libfs_packet_") as temp_dir:
        root = Path(temp_dir)

        seed_fixture(root)
        assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        write_text(root / "Documentation/zigux/phase13-libfs-slice.md", "simple_statfs()\n")
        assert_only(
            validate(root),
            [
                "phase13-libfs-slice:simple_lookup()",
                "phase13-libfs-slice:simple_read_from_buffer()",
                "phase13-libfs-slice:simple_write_to_buffer()",
                "phase13-libfs-slice:memory_read_from_buffer()",
                "phase13-libfs-slice:dcache_readdir()-adjacent emit planner",
                "phase13-libfs-slice:simple_transaction_release()",
                "phase13-libfs-slice:cursor-backed directory iteration",
            ],
            "slice_guard_failed",
        )
        seed_fixture(root)
        case_count += 1

        write_text(root / "Documentation/zigux/phase13-libfs-survey.md", "blocked `phase13-libfs-dcache-cursor-helpers`\n")
        assert_only(
            validate(root),
            [
                "phase13-libfs-survey:landed `phase13-libfs-transaction-release-helper`",
                "phase13-libfs-survey:dcache_dir_open()",
                "phase13-libfs-survey:deeper `dcache_readdir()` cursor preconditions",
                "phase13-libfs-survey:real helper footing reviewable",
            ],
            "survey_guard_failed",
        )
        seed_fixture(root)
        case_count += 1

        write_text(root / "fs/libfs.zig", "pub fn simpleStatFs(\n")
        assert_only(
            validate(root),
            [
                "phase13-libfs-zig:pub fn simpleLookup(",
                "phase13-libfs-zig:pub fn simpleReadFromBuffer(",
                "phase13-libfs-zig:pub fn simpleWriteToBuffer(",
                "phase13-libfs-zig:pub fn memoryReadFromBuffer(",
                "phase13-libfs-zig:pub fn dcacheDirSeekPlan(",
                "phase13-libfs-zig:pub fn offsetDirSeekPlan(",
                "phase13-libfs-zig:pub fn dcacheReaddirEmitPlan(",
                "phase13-libfs-zig:pub fn simpleTransactionGetPlan(",
                "phase13-libfs-zig:pub fn simpleTransactionSetPlan(",
                "phase13-libfs-zig:pub fn simpleTransactionReleasePlan(",
                "phase13-libfs-zig:.provides_transaction_release_planning = true,",
                "phase13-libfs-zig:.touches_live_dcache = false,",
            ],
            "libfs_guard_failed",
        )
        seed_fixture(root)
        case_count += 1

        write_text(root / "zigux/tests/phase13_build.zig", 'b.path("../../fs/libfs.zig")\n')
        assert_only(
            validate(root),
            [
                'phase13-build:b.path("phase13_libfs.zig")',
                'phase13-build:b.path("phase13_libfs_reviewability.zig")',
                "phase13-build:const phase13_libfs_tests = b.addTest(.{",
                "phase13-build:const phase13_libfs_reviewability_tests = b.addTest(.{",
                "phase13-build:test_step.dependOn(&run_phase13_libfs_tests.step);",
                "phase13-build:test_step.dependOn(&run_phase13_libfs_reviewability_tests.step);",
            ],
            "build_guard_failed",
        )
        seed_fixture(root)
        case_count += 1

        write_text(
            root / "zigux/tests/phase13_libfs_manifest.json",
            json.dumps({"lane_key": "P13-L04", "phase": "Phase 13", "anchor": "fs/libfs.c", "survey_summary": {}, "gaps": []}, indent=2)
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "phase13-libfs-manifest-summary:preexisting_phase13_build_present",
                "phase13-libfs-manifest-summary:preexisting_phase13_make_target_present",
                "phase13-libfs-manifest-summary:preexisting_fs_libfs_zig_present",
                "phase13-libfs-manifest-summary:preexisting_phase13_libfs_test_present",
                "phase13-libfs-manifest-summary:preexisting_phase13_slice_note_present",
                "phase13-libfs-manifest-summary:preexisting_phase13_reviewability_present",
                "phase13-libfs-manifest-summary:preexisting_phase13_survey_note_present",
                "phase13-libfs-manifest-gap:phase13-build-gate",
                "phase13-libfs-manifest-gap:phase13-make-target",
                "phase13-libfs-manifest-gap:phase13-libfs-starter",
                "phase13-libfs-manifest-gap:phase13-libfs-tests",
                "phase13-libfs-manifest-gap:phase13-libfs-slice-note",
                "phase13-libfs-manifest-gap:phase13-libfs-reviewability-gate",
                "phase13-libfs-manifest-gap:phase13-libfs-survey-note",
                "phase13-libfs-manifest-gap:phase13-libfs-offset-seek-helper",
                "phase13-libfs-manifest-gap:phase13-libfs-directory-emit-helper",
                "phase13-libfs-manifest-gap:phase13-libfs-transaction-buffer-helper",
                "phase13-libfs-manifest-gap:phase13-libfs-transaction-publish-helper",
                "phase13-libfs-manifest-gap:phase13-libfs-transaction-release-helper",
                "phase13-libfs-manifest-gap:phase13-libfs-dcache-cursor-helpers",
            ],
            "manifest_guard_failed",
        )
        seed_fixture(root)
        case_count += 1

        write_text(root / "zigux/tests/phase13_libfs_reviewability.zig", "try std.testing.expect(saw_transaction_release_helper);\n")
        assert_only(
            validate(root),
            [
                "phase13-libfs-reviewability:try std.testing.expectEqual(@as(usize, 13), manifest.gaps.len);",
                "phase13-libfs-reviewability:try std.testing.expect(saw_dcache_cursor_followup);",
                'phase13-libfs-reviewability:std.mem.indexOf(u8, survey_note, "landed `phase13-libfs-transaction-release-helper`")',
                'phase13-libfs-reviewability:std.mem.indexOf(u8, survey_note, "blocked `phase13-libfs-dcache-cursor-helpers`")',
                'phase13-libfs-reviewability:std.mem.indexOf(u8, traceability_note, "transaction acquire, publish, and release helpers")',
                'phase13-libfs-reviewability:std.mem.indexOf(u8, traceability_note, "dcache_dir_open()")',
                'phase13-libfs-reviewability:std.mem.indexOf(u8, traceability_note, "deeper `dcache_readdir()` cursor-precondition packet")',
            ],
            "reviewability_guard_failed",
        )
        seed_fixture(root)
        case_count += 1

        write_text(root / "zigux/Makefile", "phase13-validate:\n")
        assert_only(
            validate(root),
            [
                "makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py",
                "makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py",
                "makefile:phase13: phase13-validate phase13-test",
            ],
            "makefile_guard_failed",
        )
        case_count += 1

        (root / "fs/libfs.zig").unlink()
        assert_only(validate(root), ["missing_file:fs/libfs.zig"], "required_file_guard_failed")
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
