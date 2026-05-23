#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()

SURVEY_PATH = Path("Documentation/zigux/phase14-ring-buffer-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase14_ring_buffer_manifest.json")
SURVEY_TEST_PATH = Path("zigux/tests/phase14_ring_buffer_survey.zig")
PRODUCTIZATION_GAP_PATH = Path("Documentation/zigux/phase14-productization-gap-survey.md")
SHARED_SMOKE_GAP_PATH = Path("Documentation/zigux/phase14-shared-smoke-current-master-gap.md")
SMOKE_SURVEY_PATH = Path("Documentation/zigux/phase14-end-to-end-smoke-survey.md")
CORE_BOUNDARY_TRACEABILITY_PATH = Path("Documentation/zigux/phase14-core-boundary-traceability.md")

REQUIRED_FILES = [
    SURVEY_PATH,
    MANIFEST_PATH,
    SURVEY_TEST_PATH,
    PRODUCTIZATION_GAP_PATH,
    SHARED_SMOKE_GAP_PATH,
    SMOKE_SURVEY_PATH,
    CORE_BOUNDARY_TRACEABILITY_PATH,
]

REQUIRED_MARKERS = {
    SURVEY_PATH: [
        "`PHASE14_STATUS=study_only`",
        "`phase14-ring-buffer-maintenance-handoff`",
        "`phase14-ring-buffer-tracefs-reader-serialization-followup`",
        "`zig test zigux/tests/phase14_ring_buffer_survey.zig`",
        "`zig build test --build-file zigux/tests/phase14_build.zig --summary all`",
        "current public raw-file readback now recovers both `zigux/tests/phase14_ring_buffer_survey.zig` and `zigux/tests/phase14_build.zig`",
        "keep those two routes as ring-buffer-local replay vocabulary only",
        "returned survey companion and shared build shard framed as public-raw-backed ring-buffer-local evidence",
        "reader-page import, consume-or-extract serialization, `reader_page` handoff, or mapped-reader lifetime teardown wording",
    ],
    MANIFEST_PATH: [
        '"lane_key": "P14-L08"',
        '"current_lane_posture": "maintenance_mode"',
        '"phase14-ring-buffer-maintenance-handoff"',
        '"phase14-ring-buffer-zig-port-blocker"',
        '"zig test zigux/tests/phase14_ring_buffer_survey.zig"',
        '"zig build test --build-file zigux/tests/phase14_build.zig --summary all"',
        '"head-page-reader-handoff"',
        '"remote-reader-metadata"',
        '"tracefs-mapping-limitations"',
        '"read-page-extraction-boundary"',
    ],
    SURVEY_TEST_PATH: [
        'try std.testing.expectEqualStrings("P14-L08", manifest.lane_key);',
        'try std.testing.expectEqualStrings("maintenance_mode", manifest.maintenance_handoff.current_lane_posture);',
        'try std.testing.expect(std.mem.indexOf(u8, note, "phase14-ring-buffer-maintenance-handoff") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, note, "public raw-file readback now recovers both `zigux/tests/phase14_ring_buffer_survey.zig` and `zigux/tests/phase14_build.zig`") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, note, "returned survey companion and shared build shard framed as public-raw-backed ring-buffer-local evidence") != null);',
        'try std.testing.expect(hasDecisionChecklist(manifest, "head-page-reader-handoff", "stay_in_c", "reader-page extraction", "rb_set_head_page", "page handoff semantics"));',
        'try std.testing.expect(hasDecisionChecklist(manifest, "remote-reader-metadata", "stay_in_c", "remote-reader metadata", "__rb_get_reader_page_from_remote", "reader-page import rules"));',
        'try std.testing.expect(hasDecisionChecklist(manifest, "tracefs-mapping-limitations", "stay_in_c", "shared tracefs lockout boundary", "ring_buffer_map_get_reader", "mapped reader pins `resize_disabled`"));',
    ],
    PRODUCTIZATION_GAP_PATH: [
        "`zigux/tests/phase14_ring_buffer_survey.zig` now returns through the current contents path as a directly readable ring-buffer survey companion",
        "the directly readable ring-buffer survey companion",
    ],
    SHARED_SMOKE_GAP_PATH: [
        "`PHASE14_LANE_KEY=P14-L05`",
        "recover the dedicated ring-buffer survey companion again through the current contents path",
        "`zigux/tests/phase14_ring_buffer_survey.zig` is directly readable again through the current contents path as a ring-buffer-local survey companion",
        "the returned ring-buffer survey companion",
    ],
    SMOKE_SURVEY_PATH: [
        "  * directly readable ring-buffer survey companion in this lane's current evidence split:",
        "    * `zigux/tests/phase14_ring_buffer_survey.zig`",
        "    * ring-buffer-survey drift",
    ],
    CORE_BOUNDARY_TRACEABILITY_PATH: [
        "`kernel/trace/ring_buffer.c`: `Study / Boundary Only`",
        "the dedicated `P14-L08` survey note and manifest remain ring-buffer-local study evidence",
        "the focused `zigux/tests/phase14_ring_buffer_survey.zig` companion is directly readable again through the shared smoke packet",
        "`cmpxchg()`-guarded `reader_page` handoff",
        "`ring_buffer_alloc_read_page()` import and guarded remote-reader metadata setup",
        "`ring_buffer_read_page()` consume or extract serialization",
        "`rb_remove_pages()` mapped-reader lifetime teardown",
    ],
}


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / SURVEY_PATH).exists() and (candidate / MANIFEST_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        target = root / rel_path
        if not target.exists():
            failures.append(f"missing_file:{rel_path.as_posix()}")
            continue
        text = target.read_text(encoding="utf-8")
        for marker in REQUIRED_MARKERS[rel_path]:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path.as_posix()}:{marker}")
    return failures


def marker_fixture(title: str, markers: list[str]) -> str:
    return f"{title}\n\n" + "\n".join(f"- {marker}" for marker in markers) + "\n"


def fixture_text(rel_path: Path) -> str:
    titles = {
        SURVEY_PATH: "# Phase 14 Ring Buffer Survey",
        MANIFEST_PATH: "{",
        SURVEY_TEST_PATH: 'const std = @import("std");',
        PRODUCTIZATION_GAP_PATH: "# Phase 14 Productization Gap Survey",
        SHARED_SMOKE_GAP_PATH: "# Phase 14 Shared Smoke Current-Master Gap",
        SMOKE_SURVEY_PATH: "# Phase 14 End-to-End Smoke Survey",
        CORE_BOUNDARY_TRACEABILITY_PATH: "# Phase 14 Core Boundary Traceability",
    }
    title = titles[rel_path]
    if rel_path == MANIFEST_PATH:
        body = ",\n".join(f'  "{i}": "{marker}"' for i, marker in enumerate(REQUIRED_MARKERS[rel_path], start=1))
        return "{\n" + body + "\n}\n"
    if rel_path == SURVEY_TEST_PATH:
        return title + "\n\n" + "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"
    return marker_fixture(title, REQUIRED_MARKERS[rel_path])


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, fixture_text(rel_path))


def remove_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(f"- {marker}\n", "", 1)
    if updated == text:
        updated = text.replace(f"{marker}\n", "", 1)
    if updated == text:
        updated = text.replace(marker, "", 1)
    path.write_text(updated, encoding="utf-8")


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-ring-buffer-maintenance-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        missing_file_cases = [
            SURVEY_PATH,
            MANIFEST_PATH,
            SURVEY_TEST_PATH,
            PRODUCTIZATION_GAP_PATH,
            SHARED_SMOKE_GAP_PATH,
            SMOKE_SURVEY_PATH,
            CORE_BOUNDARY_TRACEABILITY_PATH,
        ]
        for rel_path in missing_file_cases:
            write_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path.as_posix()}")

        marker_cases = [
            (SURVEY_PATH, REQUIRED_MARKERS[SURVEY_PATH][8]),
            (MANIFEST_PATH, REQUIRED_MARKERS[MANIFEST_PATH][6]),
            (SHARED_SMOKE_GAP_PATH, REQUIRED_MARKERS[SHARED_SMOKE_GAP_PATH][2]),
            (CORE_BOUNDARY_TRACEABILITY_PATH, REQUIRED_MARKERS[CORE_BOUNDARY_TRACEABILITY_PATH][3]),
            (CORE_BOUNDARY_TRACEABILITY_PATH, REQUIRED_MARKERS[CORE_BOUNDARY_TRACEABILITY_PATH][6]),
        ]
        for rel_path, marker in marker_cases:
            write_fixture_tree(base)
            remove_marker(base / rel_path, marker)
            expect_failure(base, f"missing_marker:{rel_path.as_posix()}:{marker}")

        case_count = len(missing_file_cases) + len(marker_cases)
        print("PHASE14_RING_BUFFER_MAINTENANCE_PACKET_SELF_TEST=pass")
        print(f"PHASE14_RING_BUFFER_MAINTENANCE_PACKET_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the dedicated Phase 14 ring-buffer maintenance packet stays aligned "
            "across the survey note, survey manifest, survey companion, and shared reminder notes."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the inferred repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a passing sample root for fixture replay.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_fixture_tree(args.write_sample_root)
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
    print(
        "PHASE14_RING_BUFFER_MAINTENANCE_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
