#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent
HEX40 = re.compile(r"^[0-9a-f]{40}$")

FILES = [
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py",
    "Documentation/zigux/phase10-virtio-input-survey.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/Makefile",
]

MAKE_MARKERS = [
    "PHONY += phase10-validate phase10-test phase10",
    "phase10-validate:",
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py",
    "phase10: phase10-validate phase10-test",
]

SURVEY_MARKERS = [
    "`PHASE10_STATUS=parked`",
    "`PHASE10_SLICE=virtio-input-survey`",
    "`PHASE10_LANE_KEY=P10-L13`",
    "keep the current `virtio_input` packet fail-closed against live current-`master` rereads now that the broader direct helper-facing packet is visible again through public-tree fallback while risky transport remains blocked",
    "drivers/virtio/virtio_input.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "scripts/zigux/check-phase10-input-packet.py",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "landed `phase10-virtio-input-direct-packet-restore`",
    "repo-reality gap `phase10-virtio-input-slice-companions`",
    "Documentation/zigux/phase10-virtio-input-slice.md",
    "Documentation/zigux/phase10-virtio-input-module-slice.md",
]

LANE_NOTE_MARKERS = [
    "`P10-L13`",
    "`Documentation/zigux/phase10-virtio-input-survey.md`",
    "`zigux/tests/phase10_virtio_input_manifest.json`",
    "`drivers/virtio/virtio_input.zig`",
    "`drivers/virtio/virtio_input_verify.zig`",
]

TEARDOWN_MARKERS = [
    'test "phase10 virtio input teardown observation keeps identity while resettable runtime state stays explicit" {',
    'try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);',
    "summary.preserves_identity",
    "summary.clears_runtime_state",
    "device.reset();",
]

EXPECTED_DIRECT_PACKET_FILES = [
    "zigux/tests/phase10_virtio_input_manifest.json",
    "Documentation/zigux/phase10-virtio-input-survey.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "drivers/virtio/virtio_input.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "scripts/zigux/check-phase10-input-packet.py",
    "zigux/tests/phase10_virtio_input.zig",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
]

EXPECTED_MISSING_DIRECT_INPUT_PATHS = [
    "Documentation/zigux/phase10-virtio-input-slice.md",
    "Documentation/zigux/phase10-virtio-input-module-slice.md",
]

EXPECTED_GAP_STATUSES = {
    "phase10-virtio-input-reminder-manifest": "starter_landed",
    "phase10-virtio-input-survey-note": "starter_landed",
    "phase10-virtio-input-direct-packet-restore": "starter_landed",
    "phase10-virtio-input-teardown-observation-replay": "starter_landed",
    "phase10-virtio-input-slice-companions": "repo_reality_gap",
    "phase10-virtio-input-registration-lifecycle": "blocked_on_risky_transport",
}

EXPECTED_ROADMAP_DESTINATIONS = [
    "drivers/virtio/*.zig",
    "zigux/kernel/",
    "zigux/helpers/",
]

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


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def load_manifest(root: Path) -> dict[str, object]:
    return json.loads(read_text(root, "zigux/tests/phase10_virtio_input_manifest.json"))


def find_gap(manifest: dict[str, object], gap_id: str) -> dict[str, object] | None:
    for gap in manifest.get("gaps", []):
        if isinstance(gap, dict) and gap.get("id") == gap_id:
            return gap
    return None


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing: list[str] = []

    for marker in MAKE_MARKERS:
        if marker not in read_text(root, "zigux/Makefile"):
            missing.append(f"make:{marker}")

    for marker in SURVEY_MARKERS:
        if marker not in read_text(root, "Documentation/zigux/phase10-virtio-input-survey.md"):
            missing.append(f"survey:{marker}")

    for marker in LANE_NOTE_MARKERS:
        if marker not in read_text(root, "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md"):
            missing.append(f"lane_note:{marker}")

    for marker in TEARDOWN_MARKERS:
        if marker not in read_text(root, "zigux/tests/phase10_virtio_input_teardown_observation.zig"):
            missing.append(f"teardown:{marker}")

    manifest = load_manifest(root)
    if manifest.get("lane_key") != "P10-L13":
        missing.append(f"manifest:lane_key={manifest.get('lane_key')}")
    if manifest.get("phase") != "Phase 10":
        missing.append(f"manifest:phase={manifest.get('phase')}")
    if manifest.get("anchor") != "drivers/virtio/virtio_input.c":
        missing.append(f"manifest:anchor={manifest.get('anchor')}")
    if not HEX40.fullmatch(str(manifest.get("surveyed_commit", ""))):
        missing.append("manifest:surveyed_commit")
    if manifest.get("roadmap_destinations") != EXPECTED_ROADMAP_DESTINATIONS:
        missing.append("manifest:roadmap_destinations")
    if manifest.get("freeze_map") != "Documentation/zigux/freeze-map.md":
        missing.append(f"manifest:freeze_map={manifest.get('freeze_map')}")
    if manifest.get("freeze_boundary_status") != "aligned":
        missing.append(f"manifest:freeze_boundary_status={manifest.get('freeze_boundary_status')}")
    if manifest.get("freeze_status_change_claimed") is not False:
        missing.append(
            f"manifest:freeze_status_change_claimed={manifest.get('freeze_status_change_claimed')}"
        )
    if manifest.get("risky_transport_posture") != "blocked_on_risky_transport":
        missing.append(f"manifest:risky_transport_posture={manifest.get('risky_transport_posture')}")
    if manifest.get("allowed_evidence_kinds") != EXPECTED_ALLOWED_EVIDENCE_KINDS:
        missing.append("manifest:allowed_evidence_kinds")
    if manifest.get("forbidden_transport_claims") != EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS:
        missing.append("manifest:forbidden_transport_claims")
    if manifest.get("architecture_council_reopen_required") is not True:
        missing.append(
            "manifest:architecture_council_reopen_required="
            + str(manifest.get("architecture_council_reopen_required"))
        )
    if manifest.get("architecture_council_reopen_attached") is not False:
        missing.append(
            "manifest:architecture_council_reopen_attached="
            + str(manifest.get("architecture_council_reopen_attached"))
        )

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        missing.append("manifest:survey_summary")
    else:
        if summary.get("virtio_input_c_lines") != 421:
            missing.append(f"manifest:survey_summary:virtio_input_c_lines={summary.get('virtio_input_c_lines')}")
        if summary.get("directly_readable_input_packet_files") != EXPECTED_DIRECT_PACKET_FILES:
            missing.append("manifest:survey_summary:directly_readable_input_packet_files")
        if summary.get("missing_direct_input_paths") != EXPECTED_MISSING_DIRECT_INPUT_PATHS:
            missing.append("manifest:survey_summary:missing_direct_input_paths")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list) or len(gaps) != len(EXPECTED_GAP_STATUSES):
        missing.append("manifest:gaps")
    else:
        for gap_id, expected_status in EXPECTED_GAP_STATUSES.items():
            gap = find_gap(manifest, gap_id)
            if gap is None:
                missing.append(f"manifest:gap:{gap_id}")
                continue
            if gap.get("status") != expected_status:
                missing.append(f"manifest:gap_status:{gap_id}={gap.get('status')}")

    return [], missing


def write_fixture(root: Path) -> None:
    files = {
        "scripts/zigux/validate-phase10.py": "# fixture validator\n",
        "scripts/zigux/validate-phase10-closure.py": "# fixture closure validator\n",
        "zigux/Makefile": "\n".join(MAKE_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": "\n".join(LANE_NOTE_MARKERS)
        + "\n",
        "Documentation/zigux/phase10-virtio-input-survey.md": "\n".join(SURVEY_MARKERS) + "\n",
        "zigux/tests/phase10_virtio_input_teardown_observation.zig": "\n".join(TEARDOWN_MARKERS)
        + "\n",
        "zigux/tests/phase10_virtio_input_manifest.json": json.dumps(
            {
                "lane_key": "P10-L13",
                "phase": "Phase 10",
                "surveyed_commit": "7361ac51374149a96b7a7a2c6ea3c995d8cc1231",
                "anchor": "drivers/virtio/virtio_input.c",
                "roadmap_destinations": EXPECTED_ROADMAP_DESTINATIONS,
                "freeze_map": "Documentation/zigux/freeze-map.md",
                "freeze_boundary_status": "aligned",
                "freeze_status_change_claimed": False,
                "risky_transport_posture": "blocked_on_risky_transport",
                "allowed_evidence_kinds": EXPECTED_ALLOWED_EVIDENCE_KINDS,
                "forbidden_transport_claims": EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS,
                "architecture_council_reopen_required": True,
                "architecture_council_reopen_attached": False,
                "survey_summary": {
                    "virtio_input_c_lines": 421,
                    "directly_readable_input_packet_files": EXPECTED_DIRECT_PACKET_FILES,
                    "missing_direct_input_paths": EXPECTED_MISSING_DIRECT_INPUT_PATHS,
                },
                "gaps": [
                    {
                        "id": gap_id,
                        "status": status,
                    }
                    for gap_id, status in EXPECTED_GAP_STATUSES.items()
                ],
            },
            indent=2,
        )
        + "\n",
    }
    for rel_path, content in files.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def expect_missing_marker(root: Path, expected: str, label: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(f"{label}:unexpected_missing_files:{','.join(missing_files)}")
    if expected not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def expect_missing_file(root: Path, expected: str, label: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_markers:
        raise SystemExit(f"{label}:unexpected_missing_markers:{','.join(missing_markers)}")
    if expected not in missing_files:
        actual = ",".join(missing_files) if missing_files else "none"
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_validate_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        survey_path = root / "Documentation/zigux/phase10-virtio-input-survey.md"
        original_survey = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(
            original_survey.replace(
                "drivers/virtio/virtio_input.zig",
                "drivers/virtio/virtio_input_missing.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            "survey:drivers/virtio/virtio_input.zig",
            "phase10-self-test:survey_missing_direct_helper",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace(
                "repo-reality gap `phase10-virtio-input-slice-companions`",
                "repo-reality gap `phase10-virtio-input-slice-companions-missing`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            "survey:repo-reality gap `phase10-virtio-input-slice-companions`",
            "phase10-self-test:survey_missing_slice_gap",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        makefile_path = root / "zigux/Makefile"
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace("phase10-validate:\n", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            "make:phase10-validate:",
            "phase10-self-test:missing_make_route",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        lane_note_path = root / "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md"
        original_lane_note = lane_note_path.read_text(encoding="utf-8")
        lane_note_path.write_text(
            original_lane_note.replace(
                "`drivers/virtio/virtio_input_verify.zig`",
                "`drivers/virtio/virtio_input_verify_missing.zig`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            "lane_note:`drivers/virtio/virtio_input_verify.zig`",
            "phase10-self-test:lane_note_missing_verify_surface",
        )
        lane_note_path.write_text(original_lane_note, encoding="utf-8")

        manifest_path = root / "zigux/tests/phase10_virtio_input_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["survey_summary"]["directly_readable_input_packet_files"] = EXPECTED_DIRECT_PACKET_FILES[:-1]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            root,
            "manifest:survey_summary:directly_readable_input_packet_files",
            "phase10-self-test:direct_packet_file_list",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["survey_summary"]["missing_direct_input_paths"] = EXPECTED_MISSING_DIRECT_INPUT_PATHS + [
            "drivers/virtio/virtio_input.zig"
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            root,
            "manifest:survey_summary:missing_direct_input_paths",
            "phase10-self-test:missing_path_list",
        )
        writeFixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for gap in manifest["gaps"]:
            if gap["id"] == "phase10-virtio-input-direct-packet-restore":
                gap["status"] = "repo_reality_gap"
                break
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            root,
            "manifest:gap_status:phase10-virtio-input-direct-packet-restore=repo_reality_gap",
            "phase10-self-test:gap_status_drift",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["risky_transport_posture"] = "starter_landed"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            root,
            "manifest:risky_transport_posture=starter_landed",
            "phase10-self-test:risky_transport_posture",
        )
        write_fixture(root)

        teardown_path = root / "zigux/tests/phase10_virtio_input_teardown_observation.zig"
        original_teardown = teardown_path.read_text(encoding="utf-8")
        teardown_path.write_text(
            original_teardown.replace("summary.preserves_identity", "summary.identity_drift", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            "teardown:summary.preserves_identity",
            "phase10-self-test:teardown_marker",
        )
        teardown_path.write_text(original_teardown, encoding="utf-8")

        (root / "scripts/zigux/validate-phase10-closure.py").unlink()
        expect_missing_file(
            root,
            "scripts/zigux/validate-phase10-closure.py",
            "phase10-self-test:missing_required_file",
        )

    print("PHASE10_VALIDATION_SELF_TEST=pass")
    print("PHASE10_VALIDATION_SELF_TEST_CASE_COUNT=9")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current bounded Phase 10 virtio-input reminder packet."
    )
    parser.add_argument("--self-test", action="store_true", help="run local validator self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE10_VALIDATION=fail")
        print("MISSING_PHASE10_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_FILES_END")
        return 1
    if missing_markers:
        print("PHASE10_VALIDATION=fail")
        print("MISSING_PHASE10_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_MARKERS_END")
        return 1

    marker_count = (
        len(MAKE_MARKERS)
        + len(SURVEY_MARKERS)
        + len(LANE_NOTE_MARKERS)
        + len(TEARDOWN_MARKERS)
        + len(EXPECTED_DIRECT_PACKET_FILES)
        + len(EXPECTED_MISSING_DIRECT_INPUT_PATHS)
        + len(EXPECTED_GAP_STATUSES)
        + 12
    )
    print("PHASE10_VALIDATION=pass")
    print(f"PHASE10_REQUIRED_FILE_COUNT={len(FILES)}")
    print(f"PHASE10_REQUIRED_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
