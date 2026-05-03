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


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_packet(root: Path) -> int:
    missing: list[str] = []

    for label, path, markers in [
        ("survey_note", root / SURVEY_NOTE_PATH, SURVEY_NOTE_MARKERS),
        ("survey_zig", root / SURVEY_ZIG_PATH, SURVEY_ZIG_MARKERS),
        ("hvc_matrix", root / HVC_MATRIX_PATH, HVC_MATRIX_MARKERS),
    ]:
        source = text(path)
        for marker in markers:
            if marker not in source:
                missing.append(f"{label}:{marker}")

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

    print("PHASE11_HEADER_BOUNDARY_PACKET_SELF_TEST=pass")
    print("PHASE11_HEADER_BOUNDARY_PACKET_SELF_TEST_CASE_COUNT=3")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(run_self_test())
    raise SystemExit(validate_packet(ROOT))
