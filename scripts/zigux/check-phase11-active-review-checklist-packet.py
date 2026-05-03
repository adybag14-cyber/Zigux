#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


_HERE = Path(__file__).resolve()
ROOT = _HERE.parents[2] if len(_HERE.parents) >= 3 and _HERE.parent.name == "zigux" else _HERE.parent
SCRIPT_PATH = Path("scripts/zigux/check-phase11-active-review-checklist-packet.py")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
SHARED_REPLAY_NOTE_PATH = Path("Documentation/zigux/phase11-shared-replay-contract.md")
REVIEW_GUIDE_PATH = Path("Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md")
TESTS_COMPANION_PATH = Path("Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md")
MANIFEST_PATH = Path("zigux/tests/phase11_uapi_header_parity_manifest.json")

ACTIVE_PHASE11_PROMPT = (
    "- if the change touches the active Phase 11 contributor packet, do "
    "`Documentation/zigux/phase11-shared-replay-contract.md`, "
    "`scripts/zigux/check-phase11-build-inventory.py`, "
    "`scripts/zigux/check-phase11-layout-assert-surface.py`, "
    "`scripts/zigux/check-phase11-hvc-validation-flow.py`, "
    "`scripts/zigux/check-phase11-hvc-cleanup-alignment.py`, "
    "`scripts/zigux/check-phase11-shared-replay-contract.py`, "
    "`scripts/zigux/check-phase11-header-boundary-packet.py`, "
    "`zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, "
    "and `zigux/tests/phase11_uapi_header_parity_manifest.json` still keep the "
    "pre-replay stack, the shared-versus-dedicated `hvc_console` split, and the "
    "shared header-boundary packet aligned?"
)

SHARED_REPLAY_NOTE_MARKERS = [
    "The paired UAPI and driver-header parity boundary also stays explicit in the same pre-replay gate stack:",
    "python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test",
    "python3 scripts/zigux/check-phase11-header-boundary-packet.py",
    "zigux/tests/phase11_uapi_header_parity_survey.zig",
]

REVIEW_GUIDE_MARKERS = [
    "## Phase 11: Simple-driver packet",
    "- `python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test`",
    "- `python3 scripts/zigux/check-phase11-header-boundary-packet.py`",
    "- `Documentation/zigux/phase11-uapi-header-parity-survey.md`",
]

TESTS_COMPANION_MARKERS = [
    "## Phase 11 tests-root packet",
    "- `scripts/zigux/check-phase11-header-boundary-packet.py`",
    "- Does `zigux/tests/phase11_hvc_console_survey.zig` still stay separate as the dedicated archival replay while the shared starter packet remains under `zigux/tests/phase11_build.zig`, explicitly includes `zigux/tests/phase11_dw_wdt_suspend_resume.zig`, `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, and `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, and keeps the shared header-boundary packet explicit through `scripts/zigux/check-phase11-header-boundary-packet.py`?",
]


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate_packet(root: Path) -> int:
    missing: list[str] = []

    checklist_text = text(root / REVIEW_CHECKLIST_PATH)
    prompt_count = checklist_text.count(ACTIVE_PHASE11_PROMPT)
    if prompt_count != 1:
        missing.append(f"review_checklist:active_phase11_prompt_count={prompt_count}")

    for label, path, markers in [
        ("shared_replay_note", root / SHARED_REPLAY_NOTE_PATH, SHARED_REPLAY_NOTE_MARKERS),
        ("review_guide", root / REVIEW_GUIDE_PATH, REVIEW_GUIDE_MARKERS),
        ("tests_companion", root / TESTS_COMPANION_PATH, TESTS_COMPANION_MARKERS),
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

    if missing:
        print("PHASE11_ACTIVE_REVIEW_CHECKLIST_PACKET=fail")
        print("PHASE11_ACTIVE_REVIEW_CHECKLIST_PACKET_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE11_ACTIVE_REVIEW_CHECKLIST_PACKET_MISSING_END")
        return 1

    print("PHASE11_ACTIVE_REVIEW_CHECKLIST_PACKET=pass")
    print("PHASE11_ACTIVE_REVIEW_CHECKLIST_PROMPT_COUNT=1")
    print(f"PHASE11_ACTIVE_REVIEW_CHECKLIST_SHARED_NOTE_MARKER_COUNT={len(SHARED_REPLAY_NOTE_MARKERS)}")
    print(f"PHASE11_ACTIVE_REVIEW_CHECKLIST_REVIEW_GUIDE_MARKER_COUNT={len(REVIEW_GUIDE_MARKERS)}")
    print(f"PHASE11_ACTIVE_REVIEW_CHECKLIST_TESTS_COMPANION_MARKER_COUNT={len(TESTS_COMPANION_MARKERS)}")
    return 0


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
        raise SystemExit(f"phase11-active-review-checklist-self-test:{label}:unexpected_pass")
    if marker not in result.stdout:
        actual = result.stdout.strip() or result.stderr.strip() or "no_output"
        raise SystemExit(
            f"phase11-active-review-checklist-self-test:{label}:expected:{marker}:actual:{actual}"
        )


def write_fixture_tree(root: Path) -> None:
    write_text(
        root / REVIEW_CHECKLIST_PATH,
        "# Zigux Review Checklist\n\n## Validation\n" + ACTIVE_PHASE11_PROMPT + "\n",
    )
    write_text(root / SHARED_REPLAY_NOTE_PATH, "\n".join(SHARED_REPLAY_NOTE_MARKERS) + "\n")
    write_text(root / REVIEW_GUIDE_PATH, "\n".join(REVIEW_GUIDE_MARKERS) + "\n")
    write_text(root / TESTS_COMPANION_PATH, "\n".join(TESTS_COMPANION_MARKERS) + "\n")
    write_text(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "lane_key": "P11-L17",
                "phase": "Phase 11",
                "gaps": [
                    {
                        "id": "phase11-phase3-interop-followup",
                        "status": "ready_next",
                        "zigux_destination": "Documentation/zigux/phase11-uapi-header-parity-survey.md",
                    }
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write_text(root / SCRIPT_PATH, Path(__file__).read_text(encoding="utf-8"))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase11_active_review_checklist_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_tree(tmp_root)

        baseline = run_checker(tmp_root)
        if baseline.returncode != 0:
            raise SystemExit(
                "phase11-active-review-checklist-self-test:baseline_failed:"
                f"{baseline.stdout.strip() or baseline.stderr.strip() or 'no_output'}"
            )

        checklist_path = tmp_root / REVIEW_CHECKLIST_PATH
        checklist_backup = text(checklist_path)
        write_text(checklist_path, "# Zigux Review Checklist\n")
        expect_missing(
            "missing_active_prompt",
            run_checker(tmp_root),
            "review_checklist:active_phase11_prompt_count=0",
        )
        write_text(checklist_path, checklist_backup)

        write_text(
            checklist_path,
            checklist_backup + ACTIVE_PHASE11_PROMPT + "\n",
        )
        expect_missing(
            "duplicate_active_prompt",
            run_checker(tmp_root),
            "review_checklist:active_phase11_prompt_count=2",
        )
        write_text(checklist_path, checklist_backup)

        shared_replay_path = tmp_root / SHARED_REPLAY_NOTE_PATH
        shared_replay_backup = text(shared_replay_path)
        write_text(
            shared_replay_path,
            shared_replay_backup.replace(SHARED_REPLAY_NOTE_MARKERS[0] + "\n", "", 1),
        )
        expect_missing(
            "missing_shared_replay_section",
            run_checker(tmp_root),
            f"shared_replay_note:{SHARED_REPLAY_NOTE_MARKERS[0]}",
        )
        write_text(shared_replay_path, shared_replay_backup)

        review_guide_path = tmp_root / REVIEW_GUIDE_PATH
        review_guide_backup = text(review_guide_path)
        write_text(
            review_guide_path,
            review_guide_backup.replace(REVIEW_GUIDE_MARKERS[1] + "\n", "", 1),
        )
        expect_missing(
            "missing_review_guide_self_test_marker",
            run_checker(tmp_root),
            f"review_guide:{REVIEW_GUIDE_MARKERS[1]}",
        )
        write_text(review_guide_path, review_guide_backup)

        tests_companion_path = tmp_root / TESTS_COMPANION_PATH
        tests_companion_backup = text(tests_companion_path)
        write_text(
            tests_companion_path,
            tests_companion_backup.replace(TESTS_COMPANION_MARKERS[-1] + "\n", "", 1),
        )
        expect_missing(
            "missing_tests_companion_boundary_prompt",
            run_checker(tmp_root),
            f"tests_companion:{TESTS_COMPANION_MARKERS[-1]}",
        )
        write_text(tests_companion_path, tests_companion_backup)

        manifest_path = tmp_root / MANIFEST_PATH
        manifest_backup = json.loads(text(manifest_path))
        broken = dict(manifest_backup)
        broken["lane_key"] = "P11-LXX"
        write_text(manifest_path, json.dumps(broken, indent=2) + "\n")
        expect_missing("wrong_lane_key", run_checker(tmp_root), "manifest:lane_key")
        write_text(manifest_path, json.dumps(manifest_backup, indent=2) + "\n")

        broken = json.loads(text(manifest_path))
        broken["gaps"][0]["status"] = "starter_landed"
        write_text(manifest_path, json.dumps(broken, indent=2) + "\n")
        expect_missing(
            "wrong_followup_status",
            run_checker(tmp_root),
            "manifest:phase11-phase3-interop-followup:status",
        )

    print("PHASE11_ACTIVE_REVIEW_CHECKLIST_PACKET_SELF_TEST=pass")
    print("PHASE11_ACTIVE_REVIEW_CHECKLIST_PACKET_SELF_TEST_CASE_COUNT=7")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(run_self_test())
    raise SystemExit(validate_packet(ROOT))
