#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


_HERE = Path(__file__).resolve()
ROOT = _HERE.parents[2] if len(_HERE.parents) >= 3 and _HERE.parent.name == "zigux" else _HERE.parent
SCRIPT_PATH = Path("scripts/zigux/check-phase11-header-boundary-packet.py")
SURVEY_NOTE_PATH = Path("Documentation/zigux/phase11-uapi-header-parity-survey.md")
SURVEY_ZIG_PATH = Path("zigux/tests/phase11_uapi_header_parity_survey.zig")
MANIFEST_PATH = Path("zigux/tests/phase11_uapi_header_parity_manifest.json")
HVC_MATRIX_PATH = Path("Documentation/zigux/phase11-hvc-console-validation-matrix.md")
SHARED_REPLAY_NOTE_PATH = Path("Documentation/zigux/phase11-shared-replay-contract.md")
REVIEW_GUIDE_PATH = Path("Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
TESTS_COMPANION_PATH = Path("Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

SURVEY_NOTE_MARKERS = [
    "# Phase 11 UAPI And Driver-Header Parity Survey",
    "include/uapi/linux/watchdog.h",
    "struct watchdog_info",
    "include/uapi/asm-generic/termios.h",
    "struct winsize",
    "shared-versus-dedicated replay",
    "Phase 3 interop substrate",
    "shared struct layouts",
    "add one driver-local checkpoint",
]

SURVEY_ZIG_MARKERS = [
    "phase11 shared header parity manifest records the bounded layout checkpoints",
    "phase11 shared header parity survey keeps the header boundary explicit",
    "phase11 shared header parity survey keeps a bounded watchdog_info layout proof",
    "phase11 shared header parity survey keeps a bounded winsize layout proof",
]

HVC_MATRIX_MARKERS = [
    "dedicated survey replay still passes separately from the shared Phase 11 replay",
    "shared-versus-dedicated replay",
]

SHARED_REPLAY_NOTE_MARKERS = [
    "The paired UAPI and driver-header parity boundary also stays explicit in the same pre-replay gate stack:",
    "`python3 scripts/zigux/check-phase11-header-boundary-packet.py`",
    "`zigux/tests/phase11_uapi_header_parity_survey.zig`",
]

REVIEW_GUIDE_MARKERS = [
    "- `python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test`",
    "- `python3 scripts/zigux/check-phase11-header-boundary-packet.py`",
    "- `Documentation/zigux/phase11-uapi-header-parity-survey.md`",
    "- `scripts/zigux/check-phase11-header-boundary-packet.py`",
    "- Do the pre-replay checkers still describe the same delivery contract that the shared build inventory, the shared header-boundary packet, and the Phase 11 manifests claim?",
]

REVIEW_CHECKLIST_MARKERS = [
    "- if the change touches the active Phase 11 contributor packet, do `Documentation/zigux/phase11-shared-replay-contract.md`, `scripts/zigux/check-phase11-build-inventory.py`, `scripts/zigux/check-phase11-layout-assert-surface.py`, `scripts/zigux/check-phase11-hvc-validation-flow.py`, `scripts/zigux/check-phase11-hvc-cleanup-alignment.py`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, and `zigux/tests/phase11_uapi_header_parity_manifest.json` still keep the pre-replay stack, the shared-versus-dedicated `hvc_console` split, and the shared header-boundary packet aligned?",
]

TESTS_COMPANION_MARKERS = [
    "- `scripts/zigux/check-phase11-header-boundary-packet.py`",
    "- Does `zigux/tests/phase11_hvc_console_survey.zig` still stay separate as the dedicated archival replay while the shared starter packet remains under `zigux/tests/phase11_build.zig` and the shared header-boundary packet stays explicit through `scripts/zigux/check-phase11-header-boundary-packet.py`?",
]

MAKEFILE_MARKERS = [
    "scripts/zigux/check-phase11-header-boundary-packet.py --self-test",
    "scripts/zigux/check-phase11-header-boundary-packet.py",
]

WORKFLOW_MARKERS = [
    "Validate Phase 11 header boundary packet",
    "python3 scripts/zigux/check-phase11-header-boundary-packet.py",
    "Validate Phase 11 simple-driver bundle",
    "make -C zigux phase11-validate",
]


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_packet(root: Path) -> int:
    missing: list[str] = []
    workflow_text = text(root / WORKFLOW_PATH)

    for label, path, markers in [
        ("survey_note", root / SURVEY_NOTE_PATH, SURVEY_NOTE_MARKERS),
        ("survey_zig", root / SURVEY_ZIG_PATH, SURVEY_ZIG_MARKERS),
        ("hvc_matrix", root / HVC_MATRIX_PATH, HVC_MATRIX_MARKERS),
        ("shared_replay_note", root / SHARED_REPLAY_NOTE_PATH, SHARED_REPLAY_NOTE_MARKERS),
        ("review_guide", root / REVIEW_GUIDE_PATH, REVIEW_GUIDE_MARKERS),
        ("review_checklist", root / REVIEW_CHECKLIST_PATH, REVIEW_CHECKLIST_MARKERS),
        ("tests_companion", root / TESTS_COMPANION_PATH, TESTS_COMPANION_MARKERS),
        ("makefile", root / MAKEFILE_PATH, MAKEFILE_MARKERS),
        ("workflow", root / WORKFLOW_PATH, WORKFLOW_MARKERS),
    ]:
        source = workflow_text if label == "workflow" else text(path)
        for marker in markers:
            if marker not in source:
                missing.append(f"{label}:{marker}")

    header_boundary_index = workflow_text.find("Validate Phase 11 header boundary packet")
    bundle_index = workflow_text.find("Validate Phase 11 simple-driver bundle")
    if (
        header_boundary_index != -1
        and bundle_index != -1
        and header_boundary_index > bundle_index
    ):
        missing.append("workflow_order:header_boundary_before_simple_driver_bundle")

    manifest = json.loads(text(root / MANIFEST_PATH))
    if manifest.get("lane_key") != "P11-L17":
        missing.append("manifest:lane_key")
    if manifest.get("phase") != "Phase 11":
        missing.append("manifest:phase")
    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        missing.append("manifest:gaps")
    else:
        by_id = {gap.get("id"): gap for gap in gaps if isinstance(gap, dict)}
        followup = by_id.get("phase11-phase3-interop-followup")
        if not isinstance(followup, dict):
            missing.append("manifest:phase11-phase3-interop-followup")
        else:
            if followup.get("status") != "ready_next":
                missing.append("manifest:phase11-phase3-interop-followup:status")
            if followup.get("zigux_destination") != "Documentation/zigux/phase11-uapi-header-parity-survey.md":
                missing.append("manifest:phase11-phase3-interop-followup:destination")
            why_now = str(followup.get("why_now", ""))
            if "Phase 3 interop substrate" not in why_now:
                missing.append("manifest:phase11-phase3-interop-followup:why_now")

        note_gap = by_id.get("phase11-shared-header-parity-note")
        if not isinstance(note_gap, dict) or note_gap.get("status") != "starter_landed":
            missing.append("manifest:phase11-shared-header-parity-note")

        gate_gap = by_id.get("phase11-shared-header-parity-gate")
        if not isinstance(gate_gap, dict) or gate_gap.get("status") != "starter_landed":
            missing.append("manifest:phase11-shared-header-parity-gate")

    if missing:
        print("PHASE11_HEADER_BOUNDARY_PACKET=fail")
        print("PHASE11_HEADER_BOUNDARY_PACKET_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE11_HEADER_BOUNDARY_PACKET_MISSING_END")
        return 1

    print("PHASE11_HEADER_BOUNDARY_PACKET=pass")
    print(f"PHASE11_HEADER_BOUNDARY_SURVEY_MARKER_COUNT={len(SURVEY_NOTE_MARKERS)}")
    print(f"PHASE11_HEADER_BOUNDARY_ZIG_MARKER_COUNT={len(SURVEY_ZIG_MARKERS)}")
    print(f"PHASE11_HEADER_BOUNDARY_SHARED_REPLAY_NOTE_MARKER_COUNT={len(SHARED_REPLAY_NOTE_MARKERS)}")
    print(f"PHASE11_HEADER_BOUNDARY_REVIEW_GUIDE_MARKER_COUNT={len(REVIEW_GUIDE_MARKERS)}")
    print(f"PHASE11_HEADER_BOUNDARY_REVIEW_CHECKLIST_MARKER_COUNT={len(REVIEW_CHECKLIST_MARKERS)}")
    print(f"PHASE11_HEADER_BOUNDARY_TESTS_COMPANION_MARKER_COUNT={len(TESTS_COMPANION_MARKERS)}")
    print(f"PHASE11_HEADER_BOUNDARY_MAKEFILE_MARKER_COUNT={len(MAKEFILE_MARKERS)}")
    print(f"PHASE11_HEADER_BOUNDARY_WORKFLOW_MARKER_COUNT={len(WORKFLOW_MARKERS)}")
    return 0


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / SCRIPT_PATH)],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )


def expect_missing(label: str, result: subprocess.CompletedProcess[str], marker: str) -> None:
    if result.returncode == 0:
        raise SystemExit(f"phase11-header-boundary-self-test:{label}:unexpected_pass")
    if marker not in result.stdout:
        actual = result.stdout.strip() or result.stderr.strip() or "no_output"
        raise SystemExit(
            f"phase11-header-boundary-self-test:{label}:expected:{marker}:actual:{actual}"
        )


def write_fixture_tree(root: Path) -> None:
    write_text(root / SURVEY_NOTE_PATH, "\n".join(SURVEY_NOTE_MARKERS) + "\n")
    write_text(root / SURVEY_ZIG_PATH, "\n".join(SURVEY_ZIG_MARKERS) + "\n")
    write_text(root / HVC_MATRIX_PATH, "\n".join(HVC_MATRIX_MARKERS) + "\n")
    write_text(root / SHARED_REPLAY_NOTE_PATH, "\n".join(SHARED_REPLAY_NOTE_MARKERS) + "\n")
    write_text(root / REVIEW_GUIDE_PATH, "\n".join(REVIEW_GUIDE_MARKERS) + "\n")
    write_text(root / REVIEW_CHECKLIST_PATH, "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(root / TESTS_COMPANION_PATH, "\n".join(TESTS_COMPANION_MARKERS) + "\n")
    write_text(
        root / MAKEFILE_PATH,
        "\n".join(MAKEFILE_MARKERS) + "\n",
    )
    write_text(
        root / WORKFLOW_PATH,
        "\n".join(WORKFLOW_MARKERS) + "\n",
    )
    write_text(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "lane_key": "P11-L17",
                "phase": "Phase 11",
                "gaps": [
                    {
                        "id": "phase11-shared-header-parity-note",
                        "status": "starter_landed",
                        "zigux_destination": "Documentation/zigux/phase11-uapi-header-parity-survey.md",
                    },
                    {
                        "id": "phase11-shared-header-parity-gate",
                        "status": "starter_landed",
                        "zigux_destination": "zigux/tests/phase11_uapi_header_parity_survey.zig",
                    },
                    {
                        "id": "phase11-phase3-interop-followup",
                        "status": "ready_next",
                        "zigux_destination": "Documentation/zigux/phase11-uapi-header-parity-survey.md",
                        "why_now": "Phase 3 interop substrate shared struct layouts",
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write_text(root / SCRIPT_PATH, Path(__file__).read_text(encoding="utf-8"))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase11_header_boundary_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_tree(tmp_root)

        baseline = run_checker(tmp_root)
        if baseline.returncode != 0:
            raise SystemExit(
                "phase11-header-boundary-self-test:baseline_failed:"
                f"{baseline.stdout.strip() or baseline.stderr.strip() or 'no_output'}"
            )

        survey_note_path = tmp_root / SURVEY_NOTE_PATH
        survey_note_backup = text(survey_note_path)
        write_text(
            survey_note_path,
            survey_note_backup.replace("Phase 3 interop substrate\n", "", 1),
        )
        expect_missing(
            "missing_phase3_handoff",
            run_checker(tmp_root),
            "survey_note:Phase 3 interop substrate",
        )
        write_text(survey_note_path, survey_note_backup)

        manifest_path = tmp_root / MANIFEST_PATH
        manifest_backup = json.loads(text(manifest_path))
        broken = dict(manifest_backup)
        broken["lane_key"] = "P11-LXX"
        write_text(manifest_path, json.dumps(broken, indent=2) + "\n")
        expect_missing("wrong_lane_key", run_checker(tmp_root), "manifest:lane_key")
        write_text(manifest_path, json.dumps(manifest_backup, indent=2) + "\n")

        broken = json.loads(text(manifest_path))
        for gap in broken["gaps"]:
            if gap["id"] == "phase11-phase3-interop-followup":
                gap["status"] = "starter_landed"
        write_text(manifest_path, json.dumps(broken, indent=2) + "\n")
        expect_missing(
            "wrong_followup_status",
            run_checker(tmp_root),
            "manifest:phase11-phase3-interop-followup:status",
        )
        write_text(manifest_path, json.dumps(manifest_backup, indent=2) + "\n")

        broken = json.loads(text(manifest_path))
        for gap in broken["gaps"]:
            if gap["id"] == "phase11-shared-header-parity-note":
                gap["status"] = "ready_next"
        write_text(manifest_path, json.dumps(broken, indent=2) + "\n")
        expect_missing(
            "wrong_note_gap_status",
            run_checker(tmp_root),
            "manifest:phase11-shared-header-parity-note",
        )
        write_text(manifest_path, json.dumps(manifest_backup, indent=2) + "\n")

        broken = json.loads(text(manifest_path))
        for gap in broken["gaps"]:
            if gap["id"] == "phase11-shared-header-parity-gate":
                gap["status"] = "ready_next"
        write_text(manifest_path, json.dumps(broken, indent=2) + "\n")
        expect_missing(
            "wrong_gate_gap_status",
            run_checker(tmp_root),
            "manifest:phase11-shared-header-parity-gate",
        )
        write_text(manifest_path, json.dumps(manifest_backup, indent=2) + "\n")

        makefile_path = tmp_root / MAKEFILE_PATH
        makefile_backup = text(makefile_path)
        write_text(
            makefile_path,
            makefile_backup.replace(
                "scripts/zigux/check-phase11-header-boundary-packet.py --self-test\n",
                "",
                1,
            ),
        )
        expect_missing(
            "missing_makefile_self_test_marker",
            run_checker(tmp_root),
            "makefile:scripts/zigux/check-phase11-header-boundary-packet.py --self-test",
        )
        write_text(makefile_path, makefile_backup)

        workflow_path = tmp_root / WORKFLOW_PATH
        workflow_backup = text(workflow_path)
        write_text(
            workflow_path,
            workflow_backup.replace(
                "Validate Phase 11 simple-driver bundle\n",
                "",
                1,
            ),
        )
        expect_missing(
            "missing_workflow_phase11_validate_route",
            run_checker(tmp_root),
            "workflow:Validate Phase 11 simple-driver bundle",
        )
        write_text(workflow_path, workflow_backup)

        write_text(
            workflow_path,
            "\n".join(
                [
                    "Validate Phase 11 simple-driver bundle",
                    "make -C zigux phase11-validate",
                    "Validate Phase 11 header boundary packet",
                    "python3 scripts/zigux/check-phase11-header-boundary-packet.py",
                ]
            )
            + "\n",
        )
        expect_missing(
            "workflow_order_drift",
            run_checker(tmp_root),
            "workflow_order:header_boundary_before_simple_driver_bundle",
        )
        write_text(workflow_path, workflow_backup)

        shared_replay_note_path = tmp_root / SHARED_REPLAY_NOTE_PATH
        shared_replay_note_backup = text(shared_replay_note_path)
        write_text(
            shared_replay_note_path,
            shared_replay_note_backup.replace(SHARED_REPLAY_NOTE_MARKERS[0] + "\n", "", 1),
        )
        expect_missing(
            "missing_shared_replay_note_header_boundary_section",
            run_checker(tmp_root),
            f"shared_replay_note:{SHARED_REPLAY_NOTE_MARKERS[0]}",
        )
        write_text(shared_replay_note_path, shared_replay_note_backup)

        review_guide_path = tmp_root / REVIEW_GUIDE_PATH
        review_guide_backup = text(review_guide_path)
        write_text(
            review_guide_path,
            review_guide_backup.replace(REVIEW_GUIDE_MARKERS[0] + "\n", "", 1),
        )
        expect_missing(
            "missing_review_guide_header_boundary_self_test",
            run_checker(tmp_root),
            f"review_guide:{REVIEW_GUIDE_MARKERS[0]}",
        )
        write_text(review_guide_path, review_guide_backup)

        review_checklist_path = tmp_root / REVIEW_CHECKLIST_PATH
        review_checklist_backup = text(review_checklist_path)
        write_text(
            review_checklist_path,
            review_checklist_backup.replace(REVIEW_CHECKLIST_MARKERS[0] + "\n", "", 1),
        )
        expect_missing(
            "missing_review_checklist_header_boundary_marker",
            run_checker(tmp_root),
            f"review_checklist:{REVIEW_CHECKLIST_MARKERS[0]}",
        )
        write_text(review_checklist_path, review_checklist_backup)

        tests_companion_path = tmp_root / TESTS_COMPANION_PATH
        tests_companion_backup = text(tests_companion_path)
        write_text(
            tests_companion_path,
            tests_companion_backup.replace(TESTS_COMPANION_MARKERS[0] + "\n", "", 1),
        )
        expect_missing(
            "missing_tests_companion_header_boundary_marker",
            run_checker(tmp_root),
            f"tests_companion:{TESTS_COMPANION_MARKERS[0]}",
        )
        write_text(tests_companion_path, tests_companion_backup)

    print("PHASE11_HEADER_BOUNDARY_PACKET_SELF_TEST=pass")
    print("PHASE11_HEADER_BOUNDARY_PACKET_SELF_TEST_CASE_COUNT=12")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(run_self_test())
    raise SystemExit(validate_packet(ROOT))
