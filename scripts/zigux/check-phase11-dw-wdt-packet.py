#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile


SCRIPT_PATH = Path(__file__).resolve()
if SCRIPT_PATH.parent.name == "zigux" and SCRIPT_PATH.parents[1].name == "scripts":
    ROOT = SCRIPT_PATH.parents[2]
else:
    ROOT = SCRIPT_PATH.parent
HEX40 = re.compile(r"^[0-9a-f]{40}$")

MANIFEST_PATH = "zigux/tests/phase11_dw_wdt_manifest.json"
SURVEY_DOC_PATH = "Documentation/zigux/phase11-dw-wdt-survey.md"
SLICE_DOC_PATH = "Documentation/zigux/phase11-dw-wdt-slice.md"
MATRIX_DOC_PATH = "Documentation/zigux/phase11-dw-wdt-validation-matrix.md"
TEST_PATH = "zigux/tests/phase11_dw_wdt.zig"
SURVEY_TEST_PATH = "zigux/tests/phase11_dw_wdt_survey.zig"
BUILD_PATH = "zigux/tests/phase11_build.zig"

MANIFEST_LANE_KEY = "P11-L11"
MANIFEST_ANCHOR = "drivers/watchdog/dw_wdt.c"
EXPECTED_GAP_COUNT = 12
EXPECTED_BLOCKED_IDS = ["phase11-dw-wdt-platform-and-pm"]

SURVEY_DOC_MARKERS = [
    "an explicit `summarizeTeardownLifecycle()` stop-and-restart helper",
    "the focused `dw_wdt` driver and survey replays for this landed starter packet remain green",
]

SLICE_DOC_MARKERS = [
    "keeps the DesignWare non-stoppable stop semantics explicit when reset control is unavailable",
    "adds a tiny platform-resource preflight plus live resource-order summary that keeps the timer-clock choice, optional APB clock presence, reset-control availability, and optional pretimeout-IRQ wiring, plus the bounded tclk, optional pclk, reset, irq, and registration sequencing reviewable before any live devm calls",
    "adds an explicit `summarizeTeardownLifecycle()` helper so reset-control-backed stop pulses, non-stoppable stop fallout, reset-mode restart forcing, and restart-from-stopped enablement stay reviewable before any live platform remove or PM teardown work",
]

MATRIX_DOC_MARKERS = [
    "| platform-resource ordering surface | `platformResourcePreflightSummary()` plus `liveResourceOrderSummary()` keep timer-clock choice, optional APB clock presence, reset-control availability, optional pretimeout-IRQ wiring, and the bounded tclk, optional pclk, reset, irq, and registration sequencing reviewable before any live devm calls |",
    "| stop and restart failure-mode boundary | `stop()`, `armRestart()`, and `summarizeTeardownLifecycle()` keep the non-stoppable stop failure-mode boundary explicit when reset control is unavailable while still recording the stoppable path, interrupt-status clearing, restart arming, reset-mode restart forcing, and restart-from-stopped enablement without claiming reboot-side effects |",
    "current shared replay wiring on `master` includes both `phase11-dw-wdt-tests` and `phase11-dw-wdt-survey-tests`",
]

TEST_MARKERS = [
    'test "phase11 dw_wdt platform resource preflight keeps clock choice and optional resources reviewable" {',
    'test "phase11 dw_wdt live resource order keeps tclk, optional pclk, reset, irq, and registration sequencing explicit" {',
    'test "phase11 dw_wdt stop and restart stay bounded to reset-control and non-stoppable semantics" {',
    "    try std.testing.expect(!unstoppable_summary.stop_uses_reset_pulse);",
    "    try std.testing.expect(stoppable_summary.stop_uses_reset_pulse);",
]

BUILD_MARKERS = [
    '    .name = "phase11-dw-wdt-tests",',
    '    .name = "phase11-dw-wdt-survey-tests",',
    "    test_step.dependOn(&run_phase11_dw_wdt_tests.step);",
    "    test_step.dependOn(&run_phase11_dw_wdt_survey_tests.step);",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def load_manifest(root: Path) -> dict[str, object]:
    return json.loads(read_text(root, MANIFEST_PATH))


def count_statuses(manifest: dict[str, object], status_prefix: str) -> int:
    total = 0
    for gap in manifest.get("gaps", []):
        status = gap.get("status")
        if not isinstance(status, str):
            continue
        if status_prefix.endswith("_"):
            if status.startswith(status_prefix):
                total += 1
        elif status == status_prefix:
            total += 1
    return total


def validate(root: Path) -> list[str]:
    missing: list[str] = []
    for rel_path in [
        MANIFEST_PATH,
        SURVEY_DOC_PATH,
        SLICE_DOC_PATH,
        MATRIX_DOC_PATH,
        TEST_PATH,
        SURVEY_TEST_PATH,
        BUILD_PATH,
    ]:
        if not (root / rel_path).exists():
            missing.append(f"missing:{rel_path}")
    if missing:
        return missing

    manifest = load_manifest(root)
    if manifest.get("phase") != "Phase 11":
        missing.append("manifest:phase")
    if manifest.get("lane_key") != MANIFEST_LANE_KEY:
        missing.append("manifest:lane_key")
    if manifest.get("anchor") != MANIFEST_ANCHOR:
        missing.append("manifest:anchor")
    surveyed_commit = str(manifest.get("surveyed_commit", ""))
    if not HEX40.fullmatch(surveyed_commit):
        missing.append("manifest:surveyed_commit")
    gaps = manifest.get("gaps")
    if not isinstance(gaps, list) or len(gaps) != EXPECTED_GAP_COUNT:
        missing.append("manifest:gap_count")
    else:
        seen_ids: set[str] = set()
        for gap in gaps:
            gap_id = gap.get("id")
            if not isinstance(gap_id, str) or gap_id in seen_ids:
                missing.append("manifest:gap_id")
                continue
            seen_ids.add(gap_id)
        for gap_id in EXPECTED_BLOCKED_IDS:
            match = next((gap for gap in gaps if gap.get("id") == gap_id), None)
            status = "" if match is None else str(match.get("status", ""))
            if not status.startswith("blocked_on_"):
                missing.append(f"manifest:blocked:{gap_id}")

    survey_doc = read_text(root, SURVEY_DOC_PATH)
    if surveyed_commit and f"`master` `{surveyed_commit}`" not in survey_doc:
        missing.append("survey_doc:surveyed_commit")
    for marker in SURVEY_DOC_MARKERS:
        if marker not in survey_doc:
            missing.append(f"survey_doc:{marker}")

    for rel_path, label, markers in [
        (SLICE_DOC_PATH, "slice_doc", SLICE_DOC_MARKERS),
        (MATRIX_DOC_PATH, "matrix_doc", MATRIX_DOC_MARKERS),
        (TEST_PATH, "test", TEST_MARKERS),
        (BUILD_PATH, "build", BUILD_MARKERS),
    ]:
        source = read_text(root, rel_path)
        for marker in markers:
            if marker not in source:
                missing.append(f"{label}:{marker}")

    survey_test = read_text(root, SURVEY_TEST_PATH)
    if surveyed_commit and surveyed_commit not in survey_test:
        missing.append("survey_test:surveyed_commit")
    for variable_name, status_match in [
        ("starter_landed_count", "starter_landed"),
        ("ready_next_count", "ready_next"),
        ("blocked_count", "blocked_on_"),
    ]:
        expected_count = count_statuses(manifest, status_match)
        count_marker = f"expectEqual(@as(usize, {expected_count}), {variable_name});"
        if count_marker not in survey_test:
            missing.append(f"survey_test:{variable_name}={expected_count}")

    return missing


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts/zigux/check-phase11-dw-wdt-packet.py")],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )


def expect_missing(label: str, root: Path, needle: str) -> None:
    result = run_checker(root)
    if result.returncode == 0:
        raise SystemExit(f"phase11-dw-wdt-self-test:{label}:unexpected_pass")
    if needle not in result.stdout:
        actual = result.stdout.strip() or result.stderr.strip() or "no_output"
        raise SystemExit(
            f"phase11-dw-wdt-self-test:{label}:expected:{needle}:actual:{actual}"
        )


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture_tree(root: Path) -> None:
    manifest = {
        "phase": "Phase 11",
        "lane_key": MANIFEST_LANE_KEY,
        "anchor": MANIFEST_ANCHOR,
        "surveyed_commit": "a" * 40,
        "gaps": [
            {"id": "phase11-dw-wdt-core-start", "status": "starter_landed"},
            {"id": "phase11-dw-wdt-clocks", "status": "starter_landed"},
            {"id": "phase11-dw-wdt-reset-path", "status": "starter_landed"},
            {"id": "phase11-dw-wdt-restart-path", "status": "starter_landed"},
            {"id": "phase11-dw-wdt-remove-path", "status": "ready_next"},
            {"id": "phase11-dw-wdt-timeout-path", "status": "ready_next"},
            {"id": "phase11-dw-wdt-ping-path", "status": "ready_next"},
            {"id": "phase11-dw-wdt-stop-path", "status": "ready_next"},
            {"id": "phase11-dw-wdt-pretimeout-path", "status": "ready_next"},
            {"id": "phase11-dw-wdt-clk-rate-path", "status": "ready_next"},
            {"id": "phase11-dw-wdt-register-path", "status": "ready_next"},
            {"id": "phase11-dw-wdt-platform-and-pm", "status": "blocked_on_kernel_integration"},
        ],
    }
    write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
    write_text(
        root / SURVEY_DOC_PATH,
        "\n".join(
            [
                "# Phase 11 dw_wdt Survey",
                "",
                f"reviewed against live `master` `{'a' * 40}`",
                "",
                *SURVEY_DOC_MARKERS,
                "",
            ]
        ),
    )
    write_text(root / SLICE_DOC_PATH, "\n".join(SLICE_DOC_MARKERS) + "\n")
    write_text(root / MATRIX_DOC_PATH, "\n".join(MATRIX_DOC_MARKERS) + "\n")
    write_text(root / TEST_PATH, "\n".join(TEST_MARKERS) + "\n")
    write_text(
        root / SURVEY_TEST_PATH,
        "\n".join(
            [
                f"const surveyed_commit = \"{'a' * 40}\";",
                "try std.testing.expectEqual(@as(usize, 4), starter_landed_count);",
                "try std.testing.expectEqual(@as(usize, 7), ready_next_count);",
                "try std.testing.expectEqual(@as(usize, 1), blocked_count);",
                "",
            ]
        ),
    )
    write_text(root / BUILD_PATH, "\n".join(BUILD_MARKERS) + "\n")
    write_text(
        root / "scripts/zigux/check-phase11-dw-wdt-packet.py",
        Path(__file__).read_text(encoding="utf-8"),
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase11_dw_wdt_packet_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_tree(tmp_root)

        baseline = run_checker(tmp_root)
        if baseline.returncode != 0:
            raise SystemExit(
                "phase11-dw-wdt-self-test:baseline_failed:"
                f"{baseline.stdout.strip() or baseline.stderr.strip() or 'no_output'}"
            )

        survey_doc_path = tmp_root / SURVEY_DOC_PATH
        survey_doc_backup = survey_doc_path.read_text(encoding="utf-8")
        survey_doc_path.write_text(
            survey_doc_backup.replace(SURVEY_DOC_MARKERS[0] + "\n", "", 1),
            encoding="utf-8",
        )
        expect_missing("missing_survey_marker", tmp_root, f"survey_doc:{SURVEY_DOC_MARKERS[0]}")
        survey_doc_path.write_text(survey_doc_backup, encoding="utf-8")

        build_path = tmp_root / BUILD_PATH
        build_backup = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            build_backup.replace(BUILD_MARKERS[3] + "\n", "", 1),
            encoding="utf-8",
        )
        expect_missing("missing_build_dependency", tmp_root, f"build:{BUILD_MARKERS[3]}")
        build_path.write_text(build_backup, encoding="utf-8")

        manifest_path = tmp_root / MANIFEST_PATH
        manifest_backup = manifest_path.read_text(encoding="utf-8")
        manifest = json.loads(manifest_backup)
        manifest["lane_key"] = "P11-BAD"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing("bad_lane_key", tmp_root, "manifest:lane_key")
        manifest_path.write_text(manifest_backup, encoding="utf-8")

        survey_test_path = tmp_root / SURVEY_TEST_PATH
        survey_test_backup = survey_test_path.read_text(encoding="utf-8")
        survey_test_path.write_text(
            survey_test_backup.replace(
                "try std.testing.expectEqual(@as(usize, 7), ready_next_count);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing("missing_ready_next_count", tmp_root, "survey_test:ready_next_count=7")
        survey_test_path.write_text(survey_test_backup, encoding="utf-8")

        test_path = tmp_root / TEST_PATH
        test_backup = test_path.read_text(encoding="utf-8")
        test_path.write_text(
            test_backup.replace(TEST_MARKERS[4] + "\n", "", 1),
            encoding="utf-8",
        )
        expect_missing("missing_test_marker", tmp_root, f"test:{TEST_MARKERS[4]}")

    print("PHASE11_DW_WDT_PACKET_SELF_TEST=pass")
    print("PHASE11_DW_WDT_PACKET_SELF_TEST_CASE_COUNT=5")
    return 0


if "--self-test" in sys.argv[1:]:
    raise SystemExit(run_self_test())

problems = validate(ROOT)
if problems:
    print("PHASE11_DW_WDT_PACKET=fail")
    print("PHASE11_DW_WDT_PACKET_MISSING_START")
    for problem in problems:
        print(problem)
    print("PHASE11_DW_WDT_PACKET_MISSING_END")
    raise SystemExit(1)

print("PHASE11_DW_WDT_PACKET=pass")
