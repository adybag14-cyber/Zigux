#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


def repo_root() -> Path:
    override = os.environ.get("ZIGUX_ROOT")
    if override:
        return Path(override).resolve()
    resolved = Path(__file__).resolve()
    return resolved.parents[2] if len(resolved.parents) > 2 else resolved.parent


ROOT = repo_root()
HEX40 = re.compile(r"^[0-9a-f]{40}$")

MANIFEST_PATH = ROOT / "zigux/tests/phase11_bcm2835_wdt_manifest.json"
SURVEY_DOC_PATH = ROOT / "Documentation/zigux/phase11-bcm2835-wdt-survey.md"
SLICE_DOC_PATH = ROOT / "Documentation/zigux/phase11-bcm2835-wdt-slice.md"
MATRIX_DOC_PATH = ROOT / "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md"
SURVEY_TEST_PATH = ROOT / "zigux/tests/phase11_bcm2835_wdt_survey.zig"
FOCUSED_TEST_PATH = ROOT / "zigux/tests/phase11_bcm2835_wdt.zig"
DRIVER_PATH = ROOT / "drivers/watchdog/bcm2835_wdt.zig"

SURVEY_DOC_MARKERS = [
    "This survey note now serves as the archival checkpoint for the original Phase 11 roadmap gap around `drivers/watchdog/bcm2835_wdt.c`.",
    "a tiny platform-registration or PM-base handoff summary",
    "a tiny remove-time teardown summary that only clears the shared callback when `pm_power_off` still matches `bcm2835_power_off`",
    "the focused replay `zig test zigux/tests/phase11_bcm2835_wdt_survey.zig` still passes for the bounded bcm2835 packet on current `master`",
    "the archival survey now carries `P11-L08` packet identity",
    "Any later move into live platform registration, PM base plumbing, or shared poweroff-handler coordination should stay blocked",
]
SLICE_DOC_MARKERS = [
    "adds a tiny watchdog metadata summary for the Linux identity string, watchdog option flags, static timeout bounds, and bounded start or stop or get_timeleft or restart ops coverage",
    "adds a tiny registration-outcome summary for register-device success versus failure, probe-error return intent, and poweroff-handler claim follow-through or blocking when registration does not complete",
    "adds a tiny platform-registration and PM-base handoff summary for parent attachment, PM base availability, drvdata handoff readiness, register-device intent, and poweroff claim-vs-conflict reviewability",
    "adds a tiny poweroff-path summary for shared system-poweroff callback ownership, Raspberry Pi halt-partition request bits, and the short restart arming sequence without claiming a live poweroff hook installation",
    "adds a tiny remove-time teardown summary for devm-managed watchdog cleanup while clearing the shared poweroff callback only when `pm_power_off` still points at `bcm2835_power_off`",
    "The next honest bounded step inside the same Phase 11 family is no longer another note-only handoff.",
]
MATRIX_DOC_MARKERS = [
    "`PHASE11_BCM2835_WDT_STATUS=platform_handoff_landed`",
    "latest focused replay: `zig test zigux/tests/phase11_bcm2835_wdt_survey.zig` still passes for the bounded bcm2835 packet on current `master`",
    "shared replay boundary: `zig build test --build-file zigux/tests/phase11_build.zig --summary all` still includes `phase11-bcm2835-wdt-tests` and `phase11-bcm2835-wdt-survey-tests`",
    "| platform registration and PM-base handoff | `platformHandoffSummary()` now records parent attachment, PM-base availability, drvdata handoff readiness, register-device intent, and poweroff claim-vs-conflict reviewability without claiming platform-driver execution or live MMIO |",
    "| remove-time teardown boundary | `removeSummary()` records that watchdog teardown stays devm-managed while the explicit remove callback only clears the shared poweroff callback when `pm_power_off` still matches `bcm2835_power_off`, leaving conflicting or unrelated callback ownership in place |",
    "current shared replay wiring on `master` includes both `phase11-bcm2835-wdt-tests` and `phase11-bcm2835-wdt-survey-tests`",
]
SURVEY_TEST_MARKERS = [
    'try std.testing.expectEqualStrings("P11-L08", manifest.lane_key);',
    'try std.testing.expectEqualStrings("Phase 11", manifest.phase);',
    'try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.c", manifest.anchor);',
    "try std.testing.expectEqual(@as(usize, 14), manifest.gaps.len);",
    "try std.testing.expectEqual(@as(usize, 13), starter_landed_count);",
    "try std.testing.expectEqual(@as(usize, 0), ready_next_count);",
    "try std.testing.expectEqual(@as(usize, 1), blocked_count);",
    'if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-platform-registration")) {',
    'if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-remove-summary")) {',
]
FOCUSED_TEST_MARKERS = [
    'test "phase11 bcm2835_wdt registration outcome summary keeps probe failure and poweroff claim blocking reviewable" {',
    "    try std.testing.expect(failed.poweroff_handler_claim_blocked_by_registration_failure);",
    'test "phase11 bcm2835_wdt platform handoff summary keeps parent and PM-base prerequisites reviewable" {',
    "    try std.testing.expect(ready.pm_base_handoff_ready);",
    "    try std.testing.expect(blocked.poweroff_handler_conflict);",
    'test "phase11 bcm2835_wdt remove summary only clears the shared poweroff handler when bcm2835 owns it" {',
    "    try std.testing.expect(conflict.poweroff_handler_left_in_place);",
    "    try std.testing.expect(absent.clear_poweroff_handler_skipped_without_handler);",
]
DRIVER_MARKERS = [
    "pub const RegistrationOutcomeSummary = struct {",
    "pub const PlatformHandoffSummary = struct {",
    "pub const RemoveSummary = struct {",
    "pub const PoweroffSummary = struct {",
    "pub fn registrationOutcomeSummary(",
    "pub fn platformHandoffSummary(",
    "pub fn removeSummary(",
    "pub fn poweroffSummary(",
]
REQUIRED_GAP_IDS = {
    "phase11-build-gate": "starter_landed",
    "phase11-bcm2835-wdt-survey-gate": "starter_landed",
    "phase11-bcm2835-wdt-survey-note": "starter_landed",
    "phase11-bcm2835-wdt-driver-starter": "starter_landed",
    "phase11-bcm2835-wdt-watchdog-metadata": "starter_landed",
    "phase11-bcm2835-wdt-driver-tests": "starter_landed",
    "phase11-bcm2835-wdt-slice-note": "starter_landed",
    "phase11-bcm2835-wdt-validation-matrix": "starter_landed",
    "phase11-bcm2835-wdt-probe-summary": "starter_landed",
    "phase11-bcm2835-wdt-registration-and-poweroff": "starter_landed",
    "phase11-bcm2835-wdt-platform-registration": "starter_landed",
    "phase11-bcm2835-wdt-poweroff-summary": "starter_landed",
    "phase11-bcm2835-wdt-remove-summary": "starter_landed",
    "phase11-bcm2835-wdt-live-platform-registration": "blocked_on_driver_scaffold",
}


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_manifest() -> dict[str, object]:
    return json.loads(text(MANIFEST_PATH))


def validate_packet(root: Path) -> int:
    missing: list[str] = []

    manifest_path = root / MANIFEST_PATH.relative_to(ROOT)
    survey_doc_path = root / SURVEY_DOC_PATH.relative_to(ROOT)
    slice_doc_path = root / SLICE_DOC_PATH.relative_to(ROOT)
    matrix_doc_path = root / MATRIX_DOC_PATH.relative_to(ROOT)
    survey_test_path = root / SURVEY_TEST_PATH.relative_to(ROOT)
    focused_test_path = root / FOCUSED_TEST_PATH.relative_to(ROOT)
    driver_path = root / DRIVER_PATH.relative_to(ROOT)

    for label, path in [
        ("manifest", manifest_path),
        ("survey_doc", survey_doc_path),
        ("slice_doc", slice_doc_path),
        ("matrix_doc", matrix_doc_path),
        ("survey_test", survey_test_path),
        ("focused_test", focused_test_path),
        ("driver", driver_path),
    ]:
        if not path.exists():
            missing.append(f"{label}:missing:{path.as_posix()}")

    if missing:
        print("PHASE11_BCM2835_WDT_PACKET=fail")
        print("PHASE11_BCM2835_WDT_PACKET_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE11_BCM2835_WDT_PACKET_MISSING_END")
        return 1

    manifest = json.loads(text(manifest_path))
    survey_doc = text(survey_doc_path)
    slice_doc = text(slice_doc_path)
    matrix_doc = text(matrix_doc_path)
    survey_test = text(survey_test_path)
    focused_test = text(focused_test_path)
    driver_text = text(driver_path)

    if manifest.get("lane_key") != "P11-L08":
        missing.append("manifest:lane_key")
    if manifest.get("phase") != "Phase 11":
        missing.append("manifest:phase")
    if manifest.get("anchor") != "drivers/watchdog/bcm2835_wdt.c":
        missing.append("manifest:anchor")
    surveyed_commit = str(manifest.get("surveyed_commit", ""))
    if not HEX40.fullmatch(surveyed_commit):
        missing.append("manifest:surveyed_commit")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list) or len(gaps) != 14:
        missing.append("manifest:gap_count")
        gaps = []

    gap_statuses: dict[str, str] = {}
    starter_landed_count = 0
    blocked_count = 0
    ready_next_count = 0
    for gap in gaps:
        if not isinstance(gap, dict):
            missing.append("manifest:gap_shape")
            continue
        gap_id = gap.get("id")
        status = gap.get("status")
        if not isinstance(gap_id, str) or not isinstance(status, str):
            missing.append("manifest:gap_fields")
            continue
        gap_statuses[gap_id] = status
        if status == "starter_landed":
            starter_landed_count += 1
        elif status == "blocked_on_driver_scaffold":
            blocked_count += 1
        elif status == "ready_next":
            ready_next_count += 1

    if starter_landed_count != 13:
        missing.append("manifest:starter_landed_count")
    if blocked_count != 1:
        missing.append("manifest:blocked_count")
    if ready_next_count != 0:
        missing.append("manifest:ready_next_count")

    for gap_id, expected_status in REQUIRED_GAP_IDS.items():
        if gap_statuses.get(gap_id) != expected_status:
            missing.append(f"manifest:gap_status:{gap_id}")

    commit_marker = f"reviewed against live `master` `{surveyed_commit}`"
    for marker in SURVEY_DOC_MARKERS + [commit_marker]:
        if marker not in survey_doc:
            missing.append(f"survey_doc:{marker}")
    for marker in SLICE_DOC_MARKERS:
        if marker not in slice_doc:
            missing.append(f"slice_doc:{marker}")
    for marker in MATRIX_DOC_MARKERS + [commit_marker]:
        if marker not in matrix_doc:
            missing.append(f"matrix_doc:{marker}")
    for marker in SURVEY_TEST_MARKERS:
        if marker not in survey_test:
            missing.append(f"survey_test:{marker}")
    if surveyed_commit and surveyed_commit not in survey_test:
        missing.append("survey_test:surveyed_commit")
    for marker in FOCUSED_TEST_MARKERS:
        if marker not in focused_test:
            missing.append(f"focused_test:{marker}")
    for marker in DRIVER_MARKERS:
        if marker not in driver_text:
            missing.append(f"driver:{marker}")

    if missing:
        print("PHASE11_BCM2835_WDT_PACKET=fail")
        print("PHASE11_BCM2835_WDT_PACKET_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE11_BCM2835_WDT_PACKET_MISSING_END")
        return 1

    print("PHASE11_BCM2835_WDT_PACKET=pass")
    print(f"PHASE11_BCM2835_WDT_SURVEY_MARKER_COUNT={len(SURVEY_DOC_MARKERS) + 1}")
    print(f"PHASE11_BCM2835_WDT_SLICE_MARKER_COUNT={len(SLICE_DOC_MARKERS)}")
    print(f"PHASE11_BCM2835_WDT_MATRIX_MARKER_COUNT={len(MATRIX_DOC_MARKERS) + 1}")
    print(f"PHASE11_BCM2835_WDT_SURVEY_TEST_MARKER_COUNT={len(SURVEY_TEST_MARKERS) + 1}")
    print(f"PHASE11_BCM2835_WDT_FOCUSED_TEST_MARKER_COUNT={len(FOCUSED_TEST_MARKERS)}")
    print(f"PHASE11_BCM2835_WDT_DRIVER_MARKER_COUNT={len(DRIVER_MARKERS)}")
    return 0


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["ZIGUX_ROOT"] = str(root)
    return subprocess.run(
        [sys.executable, __file__],
        cwd=str(root),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def expect_stdout(label: str, result: subprocess.CompletedProcess[str], expected: str) -> None:
    if result.returncode == 0:
        raise SystemExit(f"phase11-bcm2835-wdt-packet-self-test:{label}:unexpected_pass")
    if expected not in result.stdout:
        actual = result.stdout.strip() or result.stderr.strip() or "no_output"
        raise SystemExit(
            f"phase11-bcm2835-wdt-packet-self-test:{label}:expected:{expected}:actual:{actual}"
        )


def write_self_test_fixture(root: Path) -> None:
    surveyed_commit = "f5a4d6990f701937b2a3bb9ae723bb6d0f27ba21"
    manifest = {
        "lane_key": "P11-L08",
        "phase": "Phase 11",
        "surveyed_commit": surveyed_commit,
        "anchor": "drivers/watchdog/bcm2835_wdt.c",
        "gaps": [{"id": gap_id, "status": status} for gap_id, status in REQUIRED_GAP_IDS.items()],
    }
    write_text(root / "zigux/tests/phase11_bcm2835_wdt_manifest.json", json.dumps(manifest, indent=2) + "\n")
    write_text(root / "Documentation/zigux/phase11-bcm2835-wdt-survey.md", "\n".join(SURVEY_DOC_MARKERS + [f"reviewed against live `master` `{surveyed_commit}`"]) + "\n")
    write_text(root / "Documentation/zigux/phase11-bcm2835-wdt-slice.md", "\n".join(SLICE_DOC_MARKERS) + "\n")
    write_text(root / "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md", "\n".join(MATRIX_DOC_MARKERS + [f"reviewed against live `master` `{surveyed_commit}`"]) + "\n")
    write_text(root / "zigux/tests/phase11_bcm2835_wdt_survey.zig", "\n".join(SURVEY_TEST_MARKERS + [surveyed_commit]) + "\n")
    write_text(root / "zigux/tests/phase11_bcm2835_wdt.zig", "\n".join(FOCUSED_TEST_MARKERS) + "\n")
    write_text(root / "drivers/watchdog/bcm2835_wdt.zig", "\n".join(DRIVER_MARKERS) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase11_bcm2835_wdt_packet_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_self_test_fixture(tmp_root)

        baseline = run_checker(tmp_root)
        if baseline.returncode != 0:
            raise SystemExit(
                "phase11-bcm2835-wdt-packet-self-test:baseline_failed:"
                f"{baseline.stdout.strip() or baseline.stderr.strip() or 'no_output'}"
            )

        survey_doc = tmp_root / "Documentation/zigux/phase11-bcm2835-wdt-survey.md"
        survey_doc_backup = text(survey_doc)
        write_text(survey_doc, survey_doc_backup.replace(SURVEY_DOC_MARKERS[1] + "\n", "", 1))
        expect_stdout("missing_survey_marker", run_checker(tmp_root), f"survey_doc:{SURVEY_DOC_MARKERS[1]}")
        write_text(survey_doc, survey_doc_backup)

        slice_doc = tmp_root / "Documentation/zigux/phase11-bcm2835-wdt-slice.md"
        slice_doc_backup = text(slice_doc)
        write_text(slice_doc, slice_doc_backup.replace(SLICE_DOC_MARKERS[2] + "\n", "", 1))
        expect_stdout("missing_slice_marker", run_checker(tmp_root), f"slice_doc:{SLICE_DOC_MARKERS[2]}")
        write_text(slice_doc, slice_doc_backup)

        matrix_doc = tmp_root / "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md"
        matrix_doc_backup = text(matrix_doc)
        write_text(matrix_doc, matrix_doc_backup.replace(MATRIX_DOC_MARKERS[3] + "\n", "", 1))
        expect_stdout("missing_matrix_marker", run_checker(tmp_root), f"matrix_doc:{MATRIX_DOC_MARKERS[3]}")
        write_text(matrix_doc, matrix_doc_backup)

        manifest_path = tmp_root / "zigux/tests/phase11_bcm2835_wdt_manifest.json"
        manifest_backup = text(manifest_path)
        manifest = json.loads(manifest_backup)
        manifest["lane_key"] = "P11-L10"
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_stdout("wrong_lane_key", run_checker(tmp_root), "manifest:lane_key")
        write_text(manifest_path, manifest_backup)

        survey_test = tmp_root / "zigux/tests/phase11_bcm2835_wdt_survey.zig"
        survey_test_backup = text(survey_test)
        write_text(survey_test, survey_test_backup.replace(SURVEY_TEST_MARKERS[4] + "\n", "", 1))
        expect_stdout("missing_survey_test_marker", run_checker(tmp_root), f"survey_test:{SURVEY_TEST_MARKERS[4]}")
        write_text(survey_test, survey_test_backup)

        focused_test = tmp_root / "zigux/tests/phase11_bcm2835_wdt.zig"
        focused_test_backup = text(focused_test)
        write_text(focused_test, focused_test_backup.replace(FOCUSED_TEST_MARKERS[6] + "\n", "", 1))
        expect_stdout("missing_focused_test_marker", run_checker(tmp_root), f"focused_test:{FOCUSED_TEST_MARKERS[6]}")
        write_text(focused_test, focused_test_backup)

        driver_path = tmp_root / "drivers/watchdog/bcm2835_wdt.zig"
        driver_backup = text(driver_path)
        write_text(driver_path, driver_backup.replace(DRIVER_MARKERS[5] + "\n", "", 1))
        expect_stdout("missing_driver_marker", run_checker(tmp_root), f"driver:{DRIVER_MARKERS[5]}")
        write_text(driver_path, driver_backup)

    print("PHASE11_BCM2835_WDT_PACKET_SELF_TEST=pass")
    print("PHASE11_BCM2835_WDT_PACKET_SELF_TEST_CASE_COUNT=7")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(run_self_test())
    raise SystemExit(validate_packet(ROOT))
