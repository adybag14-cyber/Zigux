#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent
HEX40 = re.compile(r"^[0-9a-f]{40}$")

TRANSPORT_MANIFEST_FILES = {
    "ring_manifest": "zigux/tests/phase10_virtio_ring_manifest.json",
    "input_manifest": "zigux/tests/phase10_virtio_input_manifest.json",
    "mmio_manifest": "zigux/tests/phase10_virtio_mmio_manifest.json",
}

FILES = [
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py",
    "Documentation/zigux/phase10-virtio-input-survey.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    TRANSPORT_MANIFEST_FILES["ring_manifest"],
    TRANSPORT_MANIFEST_FILES["input_manifest"],
    TRANSPORT_MANIFEST_FILES["mmio_manifest"],
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
    "keep the current `virtio_input` packet fail-closed around the landed lab-only driver validation evidence while risky transport remains blocked and the adjacent shared build-graph follow-through stays parked in `P10-L15`",
    "drivers/virtio/virtio_input.zig",
    "drivers/virtio/virtio_input_probe_preflight.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input.zig",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "`phase10-virtio-input-queue-callback-preflight-helper` keeps the queue-callback preflight summary explicit",
    "`phase10-virtio-input-status-drain-helper` keeps the bounded status-drain helper explicit",
    "`phase10-virtio-input-teardown-observation-helper` keeps the teardown-observation summary explicit",
    "`phase10-virtio-input-registration-lifecycle` remains blocked",
    "Documentation/zigux/phase10-virtio-input-slice.md",
    "Documentation/zigux/phase10-virtio-input-module-slice.md",
]

LANE_NOTE_MARKERS = [
    "`P10-L13`",
    "`Documentation/zigux/phase10-virtio-input-survey.md`",
    "`zigux/tests/phase10_virtio_input_manifest.json`",
    "`drivers/virtio/virtio_input.zig`",
    "`drivers/virtio/virtio_input_probe_preflight.zig`",
    "`drivers/virtio/virtio_input_verify.zig`",
    "`zigux/tests/phase10_virtio_input.zig`",
    "`zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_registration_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_status_drain.zig`",
    "`zigux/tests/phase10_virtio_input_teardown_observation.zig`",
    "`zigux/tests/phase10_virtio_input_survey.zig`",
    "`Documentation/zigux/phase10-virtio-input-slice.md`",
    "`Documentation/zigux/phase10-virtio-input-module-slice.md`",
    "`scripts/zigux/check-phase10-input-packet.py`",
]

TEARDOWN_MARKERS = [
    'test "phase10 virtio input teardown observation keeps identity while resettable runtime state stays explicit" {',
    'try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);',
    "summary.preserves_identity",
    "summary.clears_runtime_state",
    "device.reset();",
]

EXPECTED_INPUT_SUMMARY_TRUE_FIELDS = [
    "preexisting_phase10_build_present",
    "preexisting_virtio_core_zig_present",
    "preexisting_virtio_ring_zig_present",
    "preexisting_virtio_mmio_survey_present",
    "preexisting_virtio_input_zig_present",
    "preexisting_virtio_input_test_present",
    "preexisting_virtio_input_slice_note_present",
    "preexisting_virtio_input_module_note_present",
]

REQUIRED_INPUT_GAPS = {
    "phase10-build-gate": {
        "status": "starter_landed",
        "zigux_destination": "zigux/tests/phase10_build.zig",
    },
    "phase10-virtio-core-lab-starter": {
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio.zig",
    },
    "phase10-virtio-ring-lab-helper": {
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio_ring.zig",
    },
    "phase10-virtio-input-lab-helper": {
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio_input.zig",
    },
    "phase10-virtio-input-lab-gate": {
        "status": "starter_landed",
        "zigux_destination": "zigux/tests/phase10_virtio_input.zig",
    },
    "phase10-virtio-input-verify-replay": {
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio_input_verify.zig",
    },
    "phase10-virtio-input-queue-callback-preflight-replay": {
        "status": "starter_landed",
        "zigux_destination": "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    },
    "phase10-virtio-input-registration-preflight-replay": {
        "status": "starter_landed",
        "zigux_destination": "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    },
    "phase10-virtio-input-teardown-observation-replay": {
        "status": "starter_landed",
        "zigux_destination": "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    },
    "phase10-virtio-input-slice-note": {
        "status": "starter_landed",
        "zigux_destination": "Documentation/zigux/phase10-virtio-input-slice.md",
    },
    "phase10-virtio-input-module-note": {
        "status": "starter_landed",
        "zigux_destination": "Documentation/zigux/phase10-virtio-input-module-slice.md",
    },
    "phase10-virtio-input-survey-gate": {
        "status": "starter_landed",
        "zigux_destination": "zigux/tests/phase10_virtio_input_survey.zig",
    },
    "phase10-virtio-input-survey-note": {
        "status": "starter_landed",
        "zigux_destination": "Documentation/zigux/phase10-virtio-input-survey.md",
    },
    "phase10-virtio-input-capability-setup-helper": {
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio_input.zig",
    },
    "phase10-virtio-input-multitouch-slot-helper": {
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio_input.zig",
    },
    "phase10-virtio-input-probe-preflight-helper": {
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio_input.zig",
    },
    "phase10-virtio-input-registration-preflight-helper": {
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio_input.zig",
    },
    "phase10-virtio-input-queue-callback-preflight-helper": {
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio_input.zig",
    },
    "phase10-virtio-input-status-drain-helper": {
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio_input.zig",
    },
    "phase10-virtio-input-teardown-observation-helper": {
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio_input.zig",
    },
    "phase10-virtio-input-wrapper-ownership-note": {
        "status": "starter_landed",
        "zigux_destination": "Documentation/zigux/phase10-virtio-input-survey.md",
    },
    "phase10-virtio-input-registration-lifecycle": {
        "status": "blocked_on_risky_transport",
        "zigux_destination": "zigux/tests/phase10_virtio_input.zig",
    },
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


def load_manifest(root: Path, rel_path: str) -> dict[str, object]:
    return json.loads(read_text(root, rel_path))


def find_gap(manifest: dict[str, object], gap_id: str) -> dict[str, object] | None:
    for gap in manifest.get("gaps", []):
        if isinstance(gap, dict) and gap.get("id") == gap_id:
            return gap
    return None


def validate_shared_transport_manifest(
    missing: list[str],
    label: str,
    manifest: dict[str, object],
) -> None:
    if manifest.get("freeze_map") != "Documentation/zigux/freeze-map.md":
        missing.append(f"{label}:freeze_map={manifest.get('freeze_map')}")
    if manifest.get("freeze_boundary_status") != "aligned":
        missing.append(f"{label}:freeze_boundary_status={manifest.get('freeze_boundary_status')}")
    if manifest.get("freeze_status_change_claimed") is not False:
        missing.append(
            f"{label}:freeze_status_change_claimed={manifest.get('freeze_status_change_claimed')}"
        )
    if manifest.get("risky_transport_posture") != "blocked_on_risky_transport":
        missing.append(f"{label}:risky_transport_posture={manifest.get('risky_transport_posture')}")
    if manifest.get("allowed_evidence_kinds") != EXPECTED_ALLOWED_EVIDENCE_KINDS:
        missing.append(f"{label}:allowed_evidence_kinds")
    if manifest.get("forbidden_transport_claims") != EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS:
        missing.append(f"{label}:forbidden_transport_claims")
    if manifest.get("architecture_council_reopen_required") is not True:
        missing.append(
            f"{label}:architecture_council_reopen_required="
            + str(manifest.get("architecture_council_reopen_required"))
        )
    if manifest.get("architecture_council_reopen_attached") is not False:
        missing.append(
            f"{label}:architecture_council_reopen_attached="
            + str(manifest.get("architecture_council_reopen_attached"))
        )


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

    manifest = load_manifest(root, TRANSPORT_MANIFEST_FILES["input_manifest"])
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
    validate_shared_transport_manifest(missing, "manifest", manifest)

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        missing.append("manifest:survey_summary")
    else:
        virtio_input_c_lines = summary.get("virtio_input_c_lines")
        if not isinstance(virtio_input_c_lines, int) or virtio_input_c_lines < 400:
            missing.append(
                f"manifest:survey_summary:virtio_input_c_lines={virtio_input_c_lines}"
            )
        preexisting_phase10_test_files = summary.get("preexisting_phase10_test_files")
        if not isinstance(preexisting_phase10_test_files, int) or preexisting_phase10_test_files < 6:
            missing.append(
                "manifest:survey_summary:preexisting_phase10_test_files="
                + str(preexisting_phase10_test_files)
            )
        for field in EXPECTED_INPUT_SUMMARY_TRUE_FIELDS:
            if summary.get(field) is not True:
                missing.append(f"manifest:survey_summary:{field}={summary.get(field)}")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        missing.append("manifest:gaps")
    else:
        if len(gaps) != len(REQUIRED_INPUT_GAPS):
            missing.append(f"manifest:gap_count={len(gaps)}")
        for gap_id, expected in REQUIRED_INPUT_GAPS.items():
            gap = find_gap(manifest, gap_id)
            if gap is None:
                missing.append(f"manifest:gap:{gap_id}")
                continue
            if gap.get("status") != expected["status"]:
                missing.append(f"manifest:gap_status:{gap_id}={gap.get('status')}")
            if gap.get("zigux_destination") != expected["zigux_destination"]:
                missing.append(
                    f"manifest:gap_destination:{gap_id}={gap.get('zigux_destination')}"
                )

    for label, rel_path in (
        ("ring_manifest", TRANSPORT_MANIFEST_FILES["ring_manifest"]),
        ("mmio_manifest", TRANSPORT_MANIFEST_FILES["mmio_manifest"]),
    ):
        validate_shared_transport_manifest(missing, label, load_manifest(root, rel_path))

    return [], missing


def build_transport_manifest(
    lane_key: str,
    anchor: str,
    surveyed_commit: str,
    extra: dict[str, object] | None = None,
) -> dict[str, object]:
    manifest: dict[str, object] = {
        "lane_key": lane_key,
        "phase": "Phase 10",
        "surveyed_commit": surveyed_commit,
        "anchor": anchor,
        "roadmap_destinations": EXPECTED_ROADMAP_DESTINATIONS,
        "freeze_map": "Documentation/zigux/freeze-map.md",
        "freeze_boundary_status": "aligned",
        "freeze_status_change_claimed": False,
        "risky_transport_posture": "blocked_on_risky_transport",
        "allowed_evidence_kinds": EXPECTED_ALLOWED_EVIDENCE_KINDS,
        "forbidden_transport_claims": EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS,
        "architecture_council_reopen_required": True,
        "architecture_council_reopen_attached": False,
    }
    if extra:
        manifest.update(extra)
    return manifest


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
        TRANSPORT_MANIFEST_FILES["input_manifest"]: json.dumps(
            build_transport_manifest(
                "P10-L13",
                "drivers/virtio/virtio_input.c",
                "7361ac51374149a96b7a7a2c6ea3c995d8cc1231",
                {
                    "survey_summary": {
                        "virtio_input_c_lines": 421,
                        "preexisting_phase10_test_files": 6,
                        "preexisting_phase10_build_present": True,
                        "preexisting_virtio_core_zig_present": True,
                        "preexisting_virtio_ring_zig_present": True,
                        "preexisting_virtio_mmio_survey_present": True,
                        "preexisting_virtio_input_zig_present": True,
                        "preexisting_virtio_input_test_present": True,
                        "preexisting_virtio_input_slice_note_present": True,
                        "preexisting_virtio_input_module_note_present": True,
                    },
                    "gaps": [
                        {
                            "id": gap_id,
                            "status": expected["status"],
                            "zigux_destination": expected["zigux_destination"],
                        }
                        for gap_id, expected in REQUIRED_INPUT_GAPS.items()
                    ],
                },
            ),
            indent=2,
        )
        + "\n",
        TRANSPORT_MANIFEST_FILES["ring_manifest"]: json.dumps(
            build_transport_manifest(
                "P10-L07",
                "drivers/virtio/virtio_ring.c",
                "bdfe88e865b94387b3c3bd41ca98054c452f78b9",
            ),
            indent=2,
        )
        + "\n",
        TRANSPORT_MANIFEST_FILES["mmio_manifest"]: json.dumps(
            build_transport_manifest(
                "P10-L10",
                "drivers/virtio/virtio_mmio.c",
                "84f90e23ad1c28ae345905d5293a8c5395f37d43",
            ),
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
                "drivers/virtio/virtio_input_probe_preflight.zig",
                "drivers/virtio/virtio_input_probe_preflight_missing.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            "survey:drivers/virtio/virtio_input_probe_preflight.zig",
            "phase10-self-test:survey_missing_probe_preflight_helper",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace(
                "`phase10-virtio-input-status-drain-helper` keeps the bounded status-drain helper explicit",
                "`phase10-virtio-input-status-drain-helper` is missing",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            "survey:`phase10-virtio-input-status-drain-helper` keeps the bounded status-drain helper explicit",
            "phase10-self-test:survey_missing_status_drain_marker",
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
                "`drivers/virtio/virtio_input_probe_preflight.zig`",
                "`drivers/virtio/virtio_input_probe_preflight_missing.zig`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            "lane_note:`drivers/virtio/virtio_input_probe_preflight.zig`",
            "phase10-self-test:lane_note_missing_probe_preflight_surface",
        )
        lane_note_path.write_text(original_lane_note, encoding="utf-8")

        manifest_path = root / TRANSPORT_MANIFEST_FILES["input_manifest"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["survey_summary"]["preexisting_phase10_test_files"] = 5
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            root,
            "manifest:survey_summary:preexisting_phase10_test_files=5",
            "phase10-self-test:minimum_test_count",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["survey_summary"]["preexisting_virtio_input_module_note_present"] = False
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            root,
            "manifest:survey_summary:preexisting_virtio_input_module_note_present=False",
            "phase10-self-test:module_slice_presence",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for gap in manifest["gaps"]:
            if gap["id"] == "phase10-virtio-input-module-note":
                gap["zigux_destination"] = "Documentation/zigux/phase10-virtio-input-survey.md"
                break
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            root,
            "manifest:gap_destination:phase10-virtio-input-module-note=Documentation/zigux/phase10-virtio-input-survey.md",
            "phase10-self-test:module_note_gap_destination",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for gap in manifest["gaps"]:
            if gap["id"] == "phase10-virtio-input-teardown-observation-helper":
                gap["status"] = "repo_reality_gap"
                break
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            root,
            "manifest:gap_status:phase10-virtio-input-teardown-observation-helper=repo_reality_gap",
            "phase10-self-test:gap_status_drift",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["gaps"] = manifest["gaps"][:-1]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            root,
            f"manifest:gap_count={len(REQUIRED_INPUT_GAPS) - 1}",
            "phase10-self-test:gap_count_drift",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for gap in manifest["gaps"]:
            if gap["id"] == "phase10-virtio-input-survey-gate":
                gap["zigux_destination"] = "Documentation/zigux/phase10-virtio-input-survey.md"
                break
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            root,
            "manifest:gap_destination:phase10-virtio-input-survey-gate=Documentation/zigux/phase10-virtio-input-survey.md",
            "phase10-self-test:gap_destination_drift",
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
        write_fixture(root)

        ring_manifest_path = root / TRANSPORT_MANIFEST_FILES["ring_manifest"]
        ring_manifest = json.loads(ring_manifest_path.read_text(encoding="utf-8"))
        ring_manifest["freeze_status_change_claimed"] = True
        ring_manifest_path.write_text(json.dumps(ring_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            root,
            "ring_manifest:freeze_status_change_claimed=True",
            "phase10-self-test:ring_manifest_freeze_status_change_claimed",
        )
        write_fixture(root)

        ring_manifest = json.loads(ring_manifest_path.read_text(encoding="utf-8"))
        ring_manifest["allowed_evidence_kinds"] = ["driver_local_lab_slices"]
        ring_manifest_path.write_text(json.dumps(ring_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            root,
            "ring_manifest:allowed_evidence_kinds",
            "phase10-self-test:ring_manifest_allowed_evidence_kinds",
        )
        write_fixture(root)

        mmio_manifest_path = root / TRANSPORT_MANIFEST_FILES["mmio_manifest"]
        mmio_manifest = json.loads(mmio_manifest_path.read_text(encoding="utf-8"))
        mmio_manifest["forbidden_transport_claims"] = [
            claim for claim in EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS if claim != "dma_paths"
        ]
        mmio_manifest_path.write_text(json.dumps(mmio_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            root,
            "mmio_manifest:forbidden_transport_claims",
            "phase10-self-test:mmio_manifest_forbidden_transport_claims",
        )
        write_fixture(root)

        mmio_manifest = json.loads(mmio_manifest_path.read_text(encoding="utf-8"))
        mmio_manifest["architecture_council_reopen_required"] = False
        mmio_manifest_path.write_text(json.dumps(mmio_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            root,
            "mmio_manifest:architecture_council_reopen_required=False",
            "phase10-self-test:mmio_manifest_reopen_required",
        )
        write_fixture(root)

        ring_manifest = json.loads(ring_manifest_path.read_text(encoding="utf-8"))
        ring_manifest["architecture_council_reopen_attached"] = True
        ring_manifest_path.write_text(json.dumps(ring_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            root,
            "ring_manifest:architecture_council_reopen_attached=True",
            "phase10-self-test:ring_manifest_reopen_attached",
        )

    print("PHASE10_VALIDATION_SELF_TEST=pass")
    print("PHASE10_VALIDATION_SELF_TEST_CASE_COUNT=17")
    return 0


def required_marker_count() -> int:
    specific_input_field_count = 5 + 1 + len(EXPECTED_INPUT_SUMMARY_TRUE_FIELDS) + 1 + (2 * len(REQUIRED_INPUT_GAPS))
    shared_transport_field_count = 8 * len(TRANSPORT_MANIFEST_FILES)
    return (
        len(MAKE_MARKERS)
        + len(SURVEY_MARKERS)
        + len(LANE_NOTE_MARKERS)
        + len(TEARDOWN_MARKERS)
        + specific_input_field_count
        + shared_transport_field_count
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current bounded Phase 10 input packet and shared freeze-boundary manifest guardrails."
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

    print("PHASE10_VALIDATION=pass")
    print(f"PHASE10_REQUIRED_FILE_COUNT={len(FILES)}")
    print(f"PHASE10_REQUIRED_MARKER_COUNT={required_marker_count()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())