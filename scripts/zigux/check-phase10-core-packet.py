#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
HEX40 = re.compile(r"^[0-9a-f]{40}$")

FILES = [
    "scripts/zigux/check-phase10-core-packet.py",
    "zigux/Makefile",
    "drivers/virtio/virtio.zig",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_virtio_core.zig",
    "zigux/tests/phase10_virtio_core_survey.zig",
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_closure_manifest.json",
    "Documentation/zigux/phase10-virtio-core-survey.md",
]

MAKE_MARKERS = [
    "scripts/zigux/check-phase10-core-packet.py --self-test",
    "scripts/zigux/check-phase10-core-packet.py",
]

BUILD_MARKERS = [
    "phase10-virtio-core-tests",
    "phase10-virtio-core-survey-tests",
]

CORE_DOC_MARKERS = [
    "phase10-config-generation-summary-helper",
    "phase10-config-delivery-disposition-helper",
    "phase10-config-driver-toggle-guard-helper",
    "phase10-core-probe-remove-lifecycle",
]

CORE_HELPER_MARKERS = [
    "pub const ConfigGenerationSummary = struct {",
    "pub const DriverBindingSummary = struct {",
    "pub const DriverRemoveSummary = struct {",
    "if (self.config_driver_disabled) return error.ConfigDriverAlreadyDisabled;",
    "if (!self.config_driver_disabled) return error.ConfigDriverAlreadyEnabled;",
    "pub fn configGenerationSummary(self: *const Self) ConfigGenerationSummary {",
    "pub fn driverBindingSummary(self: *const Self) DriverBindingSummary {",
    "pub fn removeDriver(self: *Self) !DriverRemoveSummary {",
]

CORE_TEST_MARKERS = [
    'test "phase10 virtio core rejects nested driver config toggles and only flushes pending change after a valid enable" {',
    'test "phase10 virtio core records bounded driver binding around config_changed" {',
    'test "phase10 virtio core models bounded driver remove bookkeeping without transport reset" {',
    'test "phase10 virtio core records config generation while change delivery is deferred" {',
]

CORE_SURVEY_TEST_MARKERS = [
    'test "phase10 virtio core survey manifest records the live core validation bundle" {',
    'try std.testing.expectEqualStrings("P10-L01", manifest.lane_key);',
    'const expected_landed_core_helpers = [_][]const u8{',
    'if (std.mem.eql(u8, gap.id, "phase10-config-driver-toggle-guard-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-core-probe-remove-lifecycle")) {',
]

EXPECTED_ROADMAP_DESTINATIONS = [
    "drivers/virtio/*.zig",
    "zigux/kernel/",
    "zigux/helpers/",
]
EXPECTED_LANDED_CORE_HELPERS = [
    "phase10-config-generation-summary-helper",
    "phase10-config-delivery-disposition-helper",
    "phase10-config-driver-toggle-guard-helper",
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


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing: list[str] = []

    for name, source, markers in [
        ("make", read_text(root, "zigux/Makefile"), MAKE_MARKERS),
        ("build", read_text(root, "zigux/tests/phase10_build.zig"), BUILD_MARKERS),
        ("core_doc", read_text(root, "Documentation/zigux/phase10-virtio-core-survey.md"), CORE_DOC_MARKERS),
        ("core_helper", read_text(root, "drivers/virtio/virtio.zig"), CORE_HELPER_MARKERS),
        ("core_tests", read_text(root, "zigux/tests/phase10_virtio_core.zig"), CORE_TEST_MARKERS),
        ("core_survey_tests", read_text(root, "zigux/tests/phase10_virtio_core_survey.zig"), CORE_SURVEY_TEST_MARKERS),
    ]:
        for marker in markers:
            if marker not in source:
                missing.append(f"{name}:{marker}")

    manifest = load_manifest(root, "zigux/tests/phase10_virtio_core_manifest.json")
    if manifest.get("lane_key") != "P10-L01":
        missing.append("manifest:lane_key=P10-L01")
    if manifest.get("phase") != "Phase 10":
        missing.append("manifest:phase=Phase 10")
    if manifest.get("anchor") != "drivers/virtio/virtio.c":
        missing.append("manifest:anchor=drivers/virtio/virtio.c")
    if not HEX40.fullmatch(str(manifest.get("surveyed_commit", ""))):
        missing.append("manifest:surveyed_commit")
    if manifest.get("roadmap_destinations") != EXPECTED_ROADMAP_DESTINATIONS:
        missing.append("manifest:roadmap_destinations")

    survey_summary = manifest.get("survey_summary")
    if not isinstance(survey_summary, dict):
        missing.append("manifest:survey_summary")
    else:
        for key in [
            "preexisting_phase10_build_present",
            "preexisting_phase10_closure_validator_present",
            "preexisting_phase10_closure_note_present",
            "preexisting_virtio_core_zig_present",
            "preexisting_virtio_core_test_present",
            "preexisting_virtio_core_slice_note_present",
            "preexisting_virtio_ring_survey_present",
            "preexisting_virtio_input_survey_present",
            "preexisting_virtio_mmio_survey_present",
        ]:
            if survey_summary.get(key) is not True:
                missing.append(f"manifest:survey_summary:{key}")

        if int(survey_summary.get("virtio_c_lines", 0)) < 700:
            missing.append("manifest:survey_summary:virtio_c_lines")
        if int(survey_summary.get("preexisting_phase10_test_files", 0)) != 9:
            missing.append("manifest:survey_summary:preexisting_phase10_test_files")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list) or len(gaps) < 14:
        missing.append("manifest:gaps")
    else:
        starter_count = 0
        blocked_count = 0
        for gap in gaps:
            if not isinstance(gap, dict):
                missing.append("manifest:gap_object")
                continue
            if gap.get("status") == "starter_landed":
                starter_count += 1
            elif gap.get("status") == "blocked_on_risky_transport":
                blocked_count += 1

        if starter_count < 13:
            missing.append(f"manifest:starter_count={starter_count}")
        if blocked_count != 1:
            missing.append(f"manifest:blocked_count={blocked_count}")

        expected_statuses = {
            "phase10-build-gate": "starter_landed",
            "phase10-closure-evidence-gate": "starter_landed",
            "phase10-virtio-core-lab-starter": "starter_landed",
            "phase10-virtio-core-lab-gate": "starter_landed",
            "phase10-virtio-core-slice-note": "starter_landed",
            "phase10-virtio-core-survey-gate": "starter_landed",
            "phase10-virtio-core-survey-note": "starter_landed",
            "phase10-config-change-bookkeeping-helper": "starter_landed",
            "phase10-driver-binding-bookkeeping-helper": "starter_landed",
            "phase10-driver-remove-bookkeeping-helper": "starter_landed",
            "phase10-config-generation-summary-helper": "starter_landed",
            "phase10-config-delivery-disposition-helper": "starter_landed",
            "phase10-config-driver-toggle-guard-helper": "starter_landed",
            "phase10-core-probe-remove-lifecycle": "blocked_on_risky_transport",
        }
        for gap_id, status in expected_statuses.items():
            gap = find_gap(manifest, gap_id)
            if gap is None:
                missing.append(f"manifest:gap:{gap_id}")
                continue
            if gap.get("status") != status:
                missing.append(f"manifest:gap_status:{gap_id}={gap.get('status')}")

        remove_gap = find_gap(manifest, "phase10-driver-remove-bookkeeping-helper")
        if remove_gap is not None:
            why_now = str(remove_gap.get("why_now", ""))
            if "virtio_dev_remove()" not in why_now:
                missing.append("manifest:remove_gap:virtio_dev_remove()")
            if "ACKNOWLEDGE" not in why_now:
                missing.append("manifest:remove_gap:ACKNOWLEDGE")

        generation_gap = find_gap(manifest, "phase10-config-generation-summary-helper")
        if generation_gap is not None:
            why_now = str(generation_gap.get("why_now", ""))
            if "config-generation increments" not in why_now:
                missing.append("manifest:generation_gap:config_generation_increments")
            if "last observed generation" not in why_now:
                missing.append("manifest:generation_gap:last_observed_generation")

        delivery_gap = find_gap(manifest, "phase10-config-delivery-disposition-helper")
        if delivery_gap is not None:
            why_now = str(delivery_gap.get("why_now", ""))
            if "__virtio_config_changed()" not in why_now:
                missing.append("manifest:delivery_gap:__virtio_config_changed()")
            if "no handler was bound" not in why_now:
                missing.append("manifest:delivery_gap:no_handler_was_bound")

        toggle_gap = find_gap(manifest, "phase10-config-driver-toggle-guard-helper")
        if toggle_gap is not None:
            why_now = str(toggle_gap.get("why_now", ""))
            if "virtio_config_driver_disable()" not in why_now:
                missing.append("manifest:toggle_gap:virtio_config_driver_disable()")
            if "virtio_config_driver_enable()" not in why_now:
                missing.append("manifest:toggle_gap:virtio_config_driver_enable()")

        blocked_gap = find_gap(manifest, "phase10-core-probe-remove-lifecycle")
        if blocked_gap is not None:
            why_now = str(blocked_gap.get("why_now", ""))
            if "probe, full remove, reset" not in why_now:
                missing.append("manifest:blocked_gap:probe_full_remove_reset")
            if "risky transport state" not in why_now:
                missing.append("manifest:blocked_gap:risky_transport_state")

    closure_manifest = load_manifest(root, "zigux/tests/phase10_closure_manifest.json")
    landed_core = closure_manifest.get("landed_core_helper_evidence")
    expected_landed_core = {
        "zigux/tests/phase10_virtio_core_manifest.json": EXPECTED_LANDED_CORE_HELPERS
    }
    if landed_core != expected_landed_core:
        missing.append("closure_manifest:landed_core_helper_evidence")

    survey_provenance = closure_manifest.get("survey_provenance")
    if not isinstance(survey_provenance, dict):
        missing.append("closure_manifest:survey_provenance")
    else:
        lane_keys = survey_provenance.get("lane_keys")
        surveyed_commits = survey_provenance.get("surveyed_commits")
        if not isinstance(lane_keys, dict) or lane_keys.get("core") != "P10-L01":
            missing.append("closure_manifest:survey_provenance:core_lane_key")
        if not isinstance(surveyed_commits, dict) or not HEX40.fullmatch(str(surveyed_commits.get("core", ""))):
            missing.append("closure_manifest:survey_provenance:core_surveyed_commit")

    return [], missing


def clone_fixture_root(destination_root: Path) -> None:
    for rel_path in FILES:
        source = ROOT / rel_path
        target = destination_root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(
            f"phase10-core-self-test:{label}:unexpected_missing_files:{','.join(missing_files)}"
        )
    if expected_marker not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(
            f"phase10-core-self-test:{label}:expected_missing_marker:{expected_marker}:actual:{actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_core_selftest_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        clone_fixture_root(tmp_root)

        missing_files, missing_markers = validate(tmp_root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-core-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        manifest_path = tmp_root / "zigux/tests/phase10_virtio_core_manifest.json"
        original_manifest = manifest_path.read_text(encoding="utf-8")
        manifest_path.write_text(
            original_manifest.replace(
                '"phase10-config-driver-toggle-guard-helper"',
                '"phase10-config-driver-toggle-guard-helper-drift"',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "core_manifest_toggle_gap_id",
            tmp_root,
            "manifest:gap:phase10-config-driver-toggle-guard-helper",
        )
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest_path.write_text(
            original_manifest.replace(
                '"phase10-core-probe-remove-lifecycle",\n      "status": "blocked_on_risky_transport"',
                '"phase10-core-probe-remove-lifecycle",\n      "status": "starter_landed"',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "core_manifest_blocked_regression",
            tmp_root,
            "manifest:gap_status:phase10-core-probe-remove-lifecycle=starter_landed",
        )
        manifest_path.write_text(original_manifest, encoding="utf-8")

        build_path = tmp_root / "zigux/tests/phase10_build.zig"
        original_build = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            original_build.replace(
                '.name = "phase10-virtio-core-survey-tests",',
                '.name = "phase10-core-survey-tests-drift",',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "build_core_survey_step",
            tmp_root,
            "build:phase10-virtio-core-survey-tests",
        )
        build_path.write_text(original_build, encoding="utf-8")

        helper_path = tmp_root / "drivers/virtio/virtio.zig"
        original_helper = helper_path.read_text(encoding="utf-8")
        helper_path.write_text(
            original_helper.replace(
                "pub fn removeDriver(self: *Self) !DriverRemoveSummary {",
                "pub fn removeDriverDrift(self: *Self) !DriverRemoveSummary {",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "helper_remove_driver_entrypoint",
            tmp_root,
            "core_helper:pub fn removeDriver(self: *Self) !DriverRemoveSummary {",
        )
        helper_path.write_text(original_helper, encoding="utf-8")

        survey_test_path = tmp_root / "zigux/tests/phase10_virtio_core_survey.zig"
        original_survey_test = survey_test_path.read_text(encoding="utf-8")
        survey_test_path.write_text(
            original_survey_test.replace(
                'if (std.mem.eql(u8, gap.id, "phase10-core-probe-remove-lifecycle")) {',
                'if (std.mem.eql(u8, gap.id, "phase10-core-probe-remove-lifecycle-drift")) {',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "survey_test_blocked_gap_guard",
            tmp_root,
            'core_survey_tests:if (std.mem.eql(u8, gap.id, "phase10-core-probe-remove-lifecycle")) {',
        )
        survey_test_path.write_text(original_survey_test, encoding="utf-8")

        closure_path = tmp_root / "zigux/tests/phase10_closure_manifest.json"
        original_closure = closure_path.read_text(encoding="utf-8")
        closure_path.write_text(
            original_closure.replace(
                '"phase10-config-driver-toggle-guard-helper"',
                '"phase10-config-driver-toggle-guard-helper-drift"',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "closure_manifest_core_helper_evidence",
            tmp_root,
            "closure_manifest:landed_core_helper_evidence",
        )
        closure_path.write_text(original_closure, encoding="utf-8")

        closure_manifest = json.loads(original_closure)
        closure_manifest["survey_provenance"]["lane_keys"]["core"] = "P10-L01-drift"
        closure_path.write_text(json.dumps(closure_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "closure_manifest_core_lane_key",
            tmp_root,
            "closure_manifest:survey_provenance:core_lane_key",
        )
        closure_path.write_text(original_closure, encoding="utf-8")

        closure_manifest = json.loads(original_closure)
        closure_manifest["survey_provenance"]["surveyed_commits"]["core"] = "deadbeef"
        closure_path.write_text(json.dumps(closure_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "closure_manifest_core_surveyed_commit",
            tmp_root,
            "closure_manifest:survey_provenance:core_surveyed_commit",
        )
        closure_path.write_text(original_closure, encoding="utf-8")

    print("PHASE10_CORE_PACKET_SELF_TEST=pass")
    print("PHASE10_CORE_PACKET_SELF_TEST_CASE_COUNT=8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Phase 10 virtio core packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in drift checks against a temporary Phase 10 core fixture tree.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE10_CORE_PACKET=fail")
        print("MISSING_PHASE10_CORE_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_CORE_FILES_END")
        return 1
    if missing_markers:
        print("PHASE10_CORE_PACKET=fail")
        print("MISSING_PHASE10_CORE_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_CORE_MARKERS_END")
        return 1

    print("PHASE10_CORE_PACKET=pass")
    print(f"PHASE10_CORE_REQUIRED_FILE_COUNT={len(FILES)}")
    print(
        "PHASE10_CORE_REQUIRED_MARKER_COUNT="
        f"{len(MAKE_MARKERS) + len(BUILD_MARKERS) + len(CORE_DOC_MARKERS) + len(CORE_HELPER_MARKERS) + len(CORE_TEST_MARKERS) + len(CORE_SURVEY_TEST_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
