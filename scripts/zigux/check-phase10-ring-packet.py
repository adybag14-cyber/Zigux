#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path(__file__).resolve().parent

FILES = [
    "scripts/zigux/check-phase10-ring-packet.py",
    "zigux/Makefile",
    "zigux/tests/phase10_build.zig",
    "drivers/virtio/virtio_ring.zig",
    "zigux/tests/phase10_virtio_ring.zig",
    "zigux/tests/phase10_virtio_ring_survey.zig",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "Documentation/zigux/phase10-virtio-ring-slice.md",
    "Documentation/zigux/phase10-virtio-ring-survey.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
]

EXPECTED_BUILD_MARKERS = [
    "phase10_virtio_ring_module",
    "phase10_virtio_ring_survey_module",
    '\"phase10-virtio-ring-tests\"',
    '\"phase10-virtio-ring-survey-tests\"',
]

EXPECTED_MAKEFILE_MARKERS = [
    "phase10-test:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-ring-packet.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-ring-packet.py\n",
    "$(ZIG) build test --build-file zigux/tests/phase10_build.zig",
]

EXPECTED_HELPER_MARKERS = [
    "pub const QueueResetReadinessSummary = struct {",
    "pub fn queueResetReadinessSummary(self: *const Self, queue_index: u16) !QueueResetReadinessSummary {",
    "pub fn resetQueue(self: *Self, queue_index: u16) !QueueResetSummary {",
    "pub fn markBroken(self: *Self, queue_index: u16) !BrokenQueueSummary {",
]

EXPECTED_TEST_MARKERS = [
    'test \"phase10 virtio ring reset-readiness preflight reports the current queue blocker\" {',
    'test \"phase10 virtio ring broken summary keeps queue-local debt reviewable while blocking queue work\" {',
    'test \"phase10 virtio ring delayed callback pacing reports both thresholded and immediate poll cases\" {',
    'test \"phase10 virtio ring callback re-enable reports pending used work and settles after poll\" {',
]

EXPECTED_SURVEY_TEST_MARKERS = [
    'test \"phase10 virtio ring survey manifest records the live queue-wrapper gap and freeze boundary\" {',
    'try std.testing.expectEqualStrings(\"P10-L07\", manifest.lane_key);',
    'try std.testing.expectEqual(@as(usize, 0), ready_next_count);',
    'try std.testing.expectEqual(@as(usize, 1), blocked_count);',
    "var saw_broken_queue_poll_guard = false;",
    "var saw_mmio_probe_preflight_helper = false;",
    "var saw_ring_slice_note = false;",
]

EXPECTED_SLICE_MARKERS = [
    "dedicated ring packet review guard",
    "scripts/zigux/check-phase10-ring-packet.py",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zig test zigux/tests/phase10_virtio_ring_survey.zig",
]

EXPECTED_SURVEY_NOTE_MARKERS = [
    "dedicated ring packet review guard",
    "scripts/zigux/check-phase10-ring-packet.py",
    "phase10-virtio-ring-survey-note",
    "phase10-queue-reset-readiness-helper",
    "phase10-mmio-probe-preflight-helper",
    "make -C zigux phase10-test",
]

EXPECTED_COMPANION_MARKERS = [
    "scripts/zigux/check-phase10-ring-packet.py",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_ring_survey.zig",
    "make -C zigux phase10-test",
]

EXPECTED_GAPS = {
    "phase10-build-gate": "starter_landed",
    "phase10-virtio-ring-survey-gate": "starter_landed",
    "phase10-virtio-ring-survey-note": "starter_landed",
    "phase10-virtqueue-shape-helper": "starter_landed",
    "phase10-used-buffer-polling-helper": "starter_landed",
    "phase10-callback-enable-helper": "starter_landed",
    "phase10-callback-delay-helper": "starter_landed",
    "phase10-notify-prepare-helper": "starter_landed",
    "phase10-broken-queue-poll-guard": "starter_landed",
    "phase10-queue-reset-readiness-helper": "starter_landed",
    "phase10-mmio-probe-preflight-helper": "starter_landed",
    "phase10-mmio-lifecycle-and-irq-paths": "blocked_on_risky_transport",
    "phase10-virtio-ring-slice-note": "starter_landed",
}

EXPECTED_ALLOWED_EVIDENCE_KINDS = [
    "driver_local_lab_slices",
    "survey_manifests",
    "shared_validation_gates",
]

EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS = [
    "queue_setup_reset_paths",
    "irq_parity",
    "dma_paths",
    "input_registration_lifecycle",
    "probe_remove_lifecycle",
]

BASELINE_FIXTURE = {
    "scripts/zigux/check-phase10-ring-packet.py": "# synthetic fixture for self-test\n",
    "zigux/Makefile": """phase10-test:
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-core-packet.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-core-packet.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-ring-packet.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-ring-packet.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-input-packet.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-input-packet.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-mmio-packet.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-mmio-packet.py
\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase10_build.zig
""",
    "zigux/tests/phase10_build.zig": """const phase10_virtio_ring_module = b.createModule(.{});
const phase10_virtio_ring_survey_module = b.createModule(.{});
const phase10_virtio_ring_tests = b.addTest(.{ .name = \"phase10-virtio-ring-tests\" });
const phase10_virtio_ring_survey_tests = b.addTest(.{ .name = \"phase10-virtio-ring-survey-tests\" });
""",
    "drivers/virtio/virtio_ring.zig": """pub const QueueResetReadinessSummary = struct {};
pub fn queueResetReadinessSummary(self: *const Self, queue_index: u16) !QueueResetReadinessSummary { _ = self; _ = queue_index; }
pub fn resetQueue(self: *Self, queue_index: u16) !QueueResetSummary { _ = self; _ = queue_index; }
pub fn markBroken(self: *Self, queue_index: u16) !BrokenQueueSummary { _ = self; _ = queue_index; }
""",
    "zigux/tests/phase10_virtio_ring.zig": """test \"phase10 virtio ring reset-readiness preflight reports the current queue blocker\" {}
test \"phase10 virtio ring broken summary keeps queue-local debt reviewable while blocking queue work\" {}
test \"phase10 virtio ring delayed callback pacing reports both thresholded and immediate poll cases\" {}
test \"phase10 virtio ring callback re-enable reports pending used work and settles after poll\" {}
""",
    "zigux/tests/phase10_virtio_ring_survey.zig": """test \"phase10 virtio ring survey manifest records the live queue-wrapper gap and freeze boundary\" {
    try std.testing.expectEqualStrings(\"P10-L07\", manifest.lane_key);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    var saw_broken_queue_poll_guard = false;
    var saw_mmio_probe_preflight_helper = false;
    var saw_ring_slice_note = false;
}
""",
    "Documentation/zigux/phase10-virtio-ring-slice.md": """- dedicated ring packet review guard
- `scripts/zigux/check-phase10-ring-packet.py`
- `zigux/tests/phase10_virtio_ring_manifest.json`
- `zig test zigux/tests/phase10_virtio_ring_survey.zig`
""",
    "Documentation/zigux/phase10-virtio-ring-survey.md": """- dedicated ring packet review guard
- `scripts/zigux/check-phase10-ring-packet.py`
- `phase10-virtio-ring-survey-note`
- `phase10-queue-reset-readiness-helper`
- `phase10-mmio-probe-preflight-helper`
- `make -C zigux phase10-test`
""",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": """- `scripts/zigux/check-phase10-ring-packet.py`
- `zigux/tests/phase10_virtio_ring_manifest.json`
- `zigux/tests/phase10_virtio_ring_survey.zig`
- `make -C zigux phase10-test`
""",
    "zigux/tests/phase10_virtio_ring_manifest.json": json.dumps(
        {
            "lane_key": "P10-L07",
            "phase": "Phase 10",
            "surveyed_commit": "e42103fc02f544e1bd23a5ec2e5b584734f5af7d",
            "anchor": "drivers/virtio/virtio_ring.c",
            "roadmap_destinations": ["drivers/virtio/*.zig", "zigux/kernel/", "zigux/helpers/"],
            "freeze_map": "Documentation/zigux/freeze-map.md",
            "freeze_boundary_status": "aligned",
            "freeze_status_change_claimed": False,
            "risky_transport_posture": "blocked_on_risky_transport",
            "allowed_evidence_kinds": EXPECTED_ALLOWED_EVIDENCE_KINDS,
            "forbidden_transport_claims": EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS,
            "architecture_council_reopen_required": True,
            "architecture_council_reopen_attached": False,
            "survey_summary": {
                "virtio_ring_c_lines": 3940,
                "preexisting_phase10_test_files": 7,
                "preexisting_virtio_core_zig_present": True,
                "preexisting_phase10_build_present": True,
                "preexisting_phase10_core_doc_present": True,
                "preexisting_virtio_ring_zig_present": True,
                "preexisting_virtio_ring_doc_present": True,
                "preexisting_virtio_input_zig_present": True,
                "preexisting_virtio_input_test_present": True,
                "preexisting_virtio_input_survey_present": True,
                "preexisting_virtio_mmio_zig_present": True,
                "preexisting_virtio_mmio_test_present": True,
                "preexisting_virtio_mmio_survey_present": True,
            },
            "gaps": [
                {"id": "phase10-build-gate", "status": "starter_landed"},
                {"id": "phase10-virtio-ring-survey-gate", "status": "starter_landed"},
                {"id": "phase10-virtio-ring-survey-note", "status": "starter_landed"},
                {"id": "phase10-virtqueue-shape-helper", "status": "starter_landed"},
                {"id": "phase10-used-buffer-polling-helper", "status": "starter_landed"},
                {"id": "phase10-callback-enable-helper", "status": "starter_landed"},
                {"id": "phase10-callback-delay-helper", "status": "starter_landed"},
                {"id": "phase10-notify-prepare-helper", "status": "starter_landed"},
                {"id": "phase10-broken-queue-poll-guard", "status": "starter_landed"},
                {"id": "phase10-queue-reset-readiness-helper", "status": "starter_landed"},
                {"id": "phase10-mmio-probe-preflight-helper", "status": "starter_landed"},
                {"id": "phase10-mmio-lifecycle-and-irq-paths", "status": "blocked_on_risky_transport"},
                {"id": "phase10-virtio-ring-slice-note", "status": "starter_landed"},
            ],
        },
        indent=2,
    )
    + "\n",
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []

    build_text = read_text(root, "zigux/tests/phase10_build.zig")
    for marker in EXPECTED_BUILD_MARKERS:
        if marker not in build_text:
            missing_markers.append(f"build:{marker}")

    makefile_text = read_text(root, "zigux/Makefile")
    for marker in EXPECTED_MAKEFILE_MARKERS:
        if marker not in makefile_text:
            missing_markers.append(f"makefile:{marker}")

    helper_text = read_text(root, "drivers/virtio/virtio_ring.zig")
    for marker in EXPECTED_HELPER_MARKERS:
        if marker not in helper_text:
            missing_markers.append(f"helper:{marker}")

    test_text = read_text(root, "zigux/tests/phase10_virtio_ring.zig")
    for marker in EXPECTED_TEST_MARKERS:
        if marker not in test_text:
            missing_markers.append(f"tests:{marker}")

    survey_test_text = read_text(root, "zigux/tests/phase10_virtio_ring_survey.zig")
    for marker in EXPECTED_SURVEY_TEST_MARKERS:
        if marker not in survey_test_text:
            missing_markers.append(f"survey_test:{marker}")

    slice_text = read_text(root, "Documentation/zigux/phase10-virtio-ring-slice.md")
    for marker in EXPECTED_SLICE_MARKERS:
        if marker not in slice_text:
            missing_markers.append(f"slice:{marker}")

    survey_note_text = read_text(root, "Documentation/zigux/phase10-virtio-ring-survey.md")
    for marker in EXPECTED_SURVEY_NOTE_MARKERS:
        if marker not in survey_note_text:
            missing_markers.append(f"survey_note:{marker}")

    companion_text = read_text(root, "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md")
    for marker in EXPECTED_COMPANION_MARKERS:
        if marker not in companion_text:
            missing_markers.append(f"companion:{marker}")

    manifest = json.loads(read_text(root, "zigux/tests/phase10_virtio_ring_manifest.json"))
    if manifest.get("lane_key") != "P10-L07":
        missing_markers.append("manifest:lane_key=P10-L07")
    if manifest.get("phase") != "Phase 10":
        missing_markers.append("manifest:phase=Phase 10")
    if manifest.get("anchor") != "drivers/virtio/virtio_ring.c":
        missing_markers.append("manifest:anchor=drivers/virtio/virtio_ring.c")
    if manifest.get("surveyed_commit") != "e42103fc02f544e1bd23a5ec2e5b584734f5af7d":
        missing_markers.append("manifest:surveyed_commit")
    if manifest.get("roadmap_destinations") != ["drivers/virtio/*.zig", "zigux/kernel/", "zigux/helpers/"]:
        missing_markers.append("manifest:roadmap_destinations")
    if manifest.get("freeze_map") != "Documentation/zigux/freeze-map.md":
        missing_markers.append("manifest:freeze_map")
    if manifest.get("freeze_boundary_status") != "aligned":
        missing_markers.append("manifest:freeze_boundary_status=aligned")
    if manifest.get("freeze_status_change_claimed") is not False:
        missing_markers.append("manifest:freeze_status_change_claimed=false")
    if manifest.get("risky_transport_posture") != "blocked_on_risky_transport":
        missing_markers.append("manifest:risky_transport_posture=blocked_on_risky_transport")
    if manifest.get("allowed_evidence_kinds") != EXPECTED_ALLOWED_EVIDENCE_KINDS:
        missing_markers.append("manifest:allowed_evidence_kinds")
    if manifest.get("forbidden_transport_claims") != EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS:
        missing_markers.append("manifest:forbidden_transport_claims")
    if manifest.get("architecture_council_reopen_required") is not True:
        missing_markers.append("manifest:architecture_council_reopen_required=true")
    if manifest.get("architecture_council_reopen_attached") is not False:
        missing_markers.append("manifest:architecture_council_reopen_attached=false")

    summary = manifest.get("survey_summary", {})
    if summary.get("virtio_ring_c_lines") != 3940:
        missing_markers.append("manifest:virtio_ring_c_lines=3940")
    if summary.get("preexisting_phase10_test_files") != 7:
        missing_markers.append("manifest:preexisting_phase10_test_files=7")
    for key in [
        "preexisting_virtio_core_zig_present",
        "preexisting_phase10_build_present",
        "preexisting_phase10_core_doc_present",
        "preexisting_virtio_ring_zig_present",
        "preexisting_virtio_ring_doc_present",
        "preexisting_virtio_input_zig_present",
        "preexisting_virtio_input_test_present",
        "preexisting_virtio_input_survey_present",
        "preexisting_virtio_mmio_zig_present",
        "preexisting_virtio_mmio_test_present",
        "preexisting_virtio_mmio_survey_present",
    ]:
        if summary.get(key) is not True:
            missing_markers.append(f"manifest:{key}")

    gaps = manifest.get("gaps", [])
    if len(gaps) < 13:
        missing_markers.append("manifest:gaps")
    gap_index = {gap.get("id"): gap for gap in gaps if isinstance(gap, dict)}
    for gap_id, status in EXPECTED_GAPS.items():
        gap = gap_index.get(gap_id)
        if gap is None:
            missing_markers.append(f"manifest:gap:{gap_id}")
            continue
        if gap.get("status") != status:
            missing_markers.append(f"manifest:gap_status:{gap_id}={gap.get('status')}")

    return missing_files, missing_markers


def write_fixture(root: Path, rel_path: str, content: str) -> None:
    target = root / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_ring_packet_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        for rel_path, content in BASELINE_FIXTURE.items():
            write_fixture(tmp_root, rel_path, content)

        missing_files, missing_markers = validate(tmp_root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-ring-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        manifest_path = tmp_root / "zigux/tests/phase10_virtio_ring_manifest.json"
        original_manifest = manifest_path.read_text(encoding="utf-8")
        manifest_path.write_text(
            original_manifest.replace('\"lane_key\": \"P10-L07\"', '\"lane_key\": \"P10-drift\"', 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "manifest:lane_key=P10-L07" not in missing_markers:
            raise SystemExit("phase10-ring-self-test:expected_lane_key_marker_missing")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest_path.write_text(
            original_manifest.replace('\"freeze_boundary_status\": \"aligned\"', '\"freeze_boundary_status\": \"drifted\"', 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "manifest:freeze_boundary_status=aligned" not in missing_markers:
            raise SystemExit("phase10-ring-self-test:expected_freeze_boundary_marker_missing")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        makefile_path = tmp_root / "zigux/Makefile"
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-ring-packet.py --self-test\n",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-ring-drift.py --self-test\n",
                1,
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-ring-packet.py --self-test\n" not in missing_markers:
            raise SystemExit("phase10-ring-self-test:expected_makefile_marker_missing")
        makefile_path.write_text(original_makefile, encoding="utf-8")

        helper_path = tmp_root / "drivers/virtio/virtio_ring.zig"
        original_helper = helper_path.read_text(encoding="utf-8")
        helper_path.write_text(
            original_helper.replace(
                "pub fn queueResetReadinessSummary(self: *const Self, queue_index: u16) !QueueResetReadinessSummary {",
                "pub fn queueResetReadinessDrift(self: *const Self, queue_index: u16) !QueueResetReadinessSummary {",
                1,
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "helper:pub fn queueResetReadinessSummary(self: *const Self, queue_index: u16) !QueueResetReadinessSummary {" not in missing_markers:
            raise SystemExit("phase10-ring-self-test:expected_helper_marker_missing")
        helper_path.write_text(original_helper, encoding="utf-8")

        test_path = tmp_root / "zigux/tests/phase10_virtio_ring.zig"
        original_test = test_path.read_text(encoding="utf-8")
        test_path.write_text(
            original_test.replace(
                'test \"phase10 virtio ring broken summary keeps queue-local debt reviewable while blocking queue work\" {',
                'test \"phase10 virtio ring blocks publish drift while a queue is broken\" {',
                1,
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if 'tests:test \"phase10 virtio ring broken summary keeps queue-local debt reviewable while blocking queue work\" {' not in missing_markers:
            raise SystemExit("phase10-ring-self-test:expected_test_marker_missing")
        test_path.write_text(original_test, encoding="utf-8")

        slice_path = tmp_root / "Documentation/zigux/phase10-virtio-ring-slice.md"
        original_slice = slice_path.read_text(encoding="utf-8")
        slice_path.write_text(
            original_slice.replace("scripts/zigux/check-phase10-ring-packet.py", "scripts/zigux/check-phase10-ring-drift.py", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "slice:scripts/zigux/check-phase10-ring-packet.py" not in missing_markers:
            raise SystemExit("phase10-ring-self-test:expected_slice_marker_missing")
        slice_path.write_text(original_slice, encoding="utf-8")

        survey_path = tmp_root / "Documentation/zigux/phase10-virtio-ring-survey.md"
        original_survey = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(
            original_survey.replace("dedicated ring packet review guard", "dedicated ring packet drift guard", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "survey_note:dedicated ring packet review guard" not in missing_markers:
            raise SystemExit("phase10-ring-self-test:expected_survey_marker_missing")
        survey_path.write_text(original_survey, encoding="utf-8")

        companion_path = tmp_root / "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"
        original_companion = companion_path.read_text(encoding="utf-8")
        companion_path.write_text(
            original_companion.replace("scripts/zigux/check-phase10-ring-packet.py", "scripts/zigux/check-phase10-ring-drift.py", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "companion:scripts/zigux/check-phase10-ring-packet.py" not in missing_markers:
            raise SystemExit("phase10-ring-self-test:expected_companion_marker_missing")

    print("PHASE10_RING_PACKET_SELF_TEST=pass")
    print("PHASE10_RING_PACKET_SELF_TEST_CASE_COUNT=7")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 10 virtio_ring packet.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in drift checks against a synthetic fixture tree.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE10_RING_PACKET=fail")
        print("MISSING_PHASE10_RING_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_RING_FILES_END")
        return 1

    if missing_markers:
        print("PHASE10_RING_PACKET=fail")
        print("MISSING_PHASE10_RING_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_RING_MARKERS_END")
        return 1

    print("PHASE10_RING_PACKET=pass")
    print(f"PHASE10_RING_REQUIRED_FILE_COUNT={len(FILES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
