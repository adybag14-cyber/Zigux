#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

FILES = [
    "scripts/zigux/check-phase10-mmio-packet.py",
    "Documentation/zigux/phase10-virtio-mmio-slice.md",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
    "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md",
    "drivers/virtio/virtio_mmio.zig",
    "drivers/virtio/virtio_mmio_verify.zig",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
    "zigux/tests/phase10_build.zig",
    "zigux/Makefile",
]

SLICE_MARKERS = [
    "# Phase 10 Virtio MMIO Slice",
    "drivers/virtio/virtio_mmio.zig",
    "drivers/virtio/virtio_mmio_verify.zig",
    "config-write disposition summary",
    "selected-queue readiness summary",
    "zig test drivers/virtio/virtio_mmio_verify.zig",
]

SURVEY_NOTE_MARKERS = [
    "# Phase 10 Virtio MMIO Survey",
    "PHASE10_STATUS=parked",
    "drivers/virtio/virtio_mmio.zig",
    "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md",
    "config-write disposition reporting",
    "feature-negotiation deltas",
    "transport identity readback",
    "zigux/tests/phase10_build.zig",
    "zig test zigux/tests/phase10_virtio_mmio_survey.zig",
]

COMPANION_MARKERS = [
    "config-write disposition",
    "changed-byte mask",
]

HELPER_MARKERS = [
    "pub const ConfigWriteDispositionSummary = struct {",
    "pub const FeatureNegotiationSummary = struct {",
    "pub const TransportIdentitySummary = struct {",
    "pub const ProbePreflightSummary = struct {",
    "pub const SelectedQueueReadinessSummary = struct {",
    "pending_config_write: ?ConfigWritePlanSummary = null,",
    "pub fn bumpConfigGeneration(self: *Self) void {",
    "self.pending_config_write = null;",
    "pub fn configWriteDispositionSummary(self: *const Self) !ConfigWriteDispositionSummary {",
    "pub fn featureNegotiationSummary(self: *const Self) FeatureNegotiationSummary {",
    "pub fn transportIdentitySummary(self: *const Self) TransportIdentitySummary {",
    "pub fn probePreflightSummary(self: *const Self) ProbePreflightSummary {",
    "pub fn selectedQueueReadinessSummary(self: *const Self) !SelectedQueueReadinessSummary {",
]

VERIFY_MARKERS = [
    "pub const TransportIdentitySummary = virtio_mmio.TransportIdentitySummary;",
    "pub const ProbePreflightSummary = virtio_mmio.ProbePreflightSummary;",
    "pub const SelectedQueueReadinessSummary = virtio_mmio.SelectedQueueReadinessSummary;",
    "pub const ConfigWriteDispositionSummary = virtio_mmio.ConfigWriteDispositionSummary;",
    "pub const FeatureNegotiationSummary = virtio_mmio.FeatureNegotiationSummary;",
    "pub fn summarizeFeatureNegotiation(device: *const virtio_mmio.VirtioMmioLab) FeatureNegotiationSummary {",
    "pub fn summarizeConfigWriteDisposition(device: *const virtio_mmio.VirtioMmioLab) !ConfigWriteDispositionSummary {",
    "pub fn changedByteCount(summary: ConfigWriteDispositionSummary) u3 {",
    'test "phase10 virtio mmio verify keeps probe wrapper transitions explicit" {',
    'test "phase10 virtio mmio verify keeps queue readiness wrapper below transport claims" {',
    'test "phase10 virtio mmio verify counts changed config bytes without mutating staged data" {',
]

SURVEY_GATE_MARKERS = [
    'test "phase10 virtio mmio survey manifest records the landed identity-backed packet" {',
    'try std.testing.expectEqualStrings("P10-L10", manifest.lane_key);',
    'try std.testing.expectEqualStrings("Phase 10", manifest.phase);',
    'try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", manifest.anchor);',
    'try std.testing.expectEqualStrings("blocked_on_risky_transport", manifest.risky_transport_posture);',
    'try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/virtio/virtio_mmio_verify.zig") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, survey_note, "config-write disposition summary") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, survey_note, "selected-queue readiness summary") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, build_file, "../../drivers/virtio/virtio_mmio_verify.zig") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, build_file, "phase10-virtio-mmio-verify-tests") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, build_file, "run_phase10_virtio_mmio_verify_tests.step") != null);',
]

BUILD_MARKERS = [
    "../../drivers/virtio/virtio_mmio_verify.zig",
    '"phase10-virtio-mmio-verify-tests"',
    "run_phase10_virtio_mmio_verify_tests.step",
]

MAKEFILE_MARKERS = [
    "scripts/zigux/check-phase10-mmio-packet.py --self-test",
    "scripts/zigux/check-phase10-mmio-packet.py",
]

EXPECTED_GAPS = {
    "phase10-build-gate": "starter_landed",
    "phase10-virtio-mmio-survey-gate": "starter_landed",
    "phase10-virtio-mmio-survey-note": "starter_landed",
    "phase10-mmio-register-window-helper": "starter_landed",
    "phase10-mmio-queue-size-helper": "starter_landed",
    "phase10-mmio-feature-word-selector-helper": "starter_landed",
    "phase10-mmio-config-window-helper": "starter_landed",
    "phase10-mmio-config-write-plan-helper": "starter_landed",
    "phase10-mmio-transport-identity-helper": "starter_landed",
    "phase10-mmio-probe-preflight-helper": "starter_landed",
    "phase10-mmio-config-write-disposition-helper": "starter_landed",
    "phase10-mmio-selected-queue-readiness-helper": "starter_landed",
    "phase10-mmio-lifecycle-and-irq-paths": "blocked_on_risky_transport",
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def check_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []

    check_markers(
        missing_markers,
        "slice_note",
        read_text(root, "Documentation/zigux/phase10-virtio-mmio-slice.md"),
        SLICE_MARKERS,
    )
    check_markers(
        missing_markers,
        "survey_note",
        read_text(root, "Documentation/zigux/phase10-virtio-mmio-survey.md"),
        SURVEY_NOTE_MARKERS,
    )
    check_markers(
        missing_markers,
        "companion_note",
        read_text(root, "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md"),
        COMPANION_MARKERS,
    )
    check_markers(
        missing_markers,
        "helper",
        read_text(root, "drivers/virtio/virtio_mmio.zig"),
        HELPER_MARKERS,
    )
    check_markers(
        missing_markers,
        "verify_helper",
        read_text(root, "drivers/virtio/virtio_mmio_verify.zig"),
        VERIFY_MARKERS,
    )
    check_markers(
        missing_markers,
        "survey_gate",
        read_text(root, "zigux/tests/phase10_virtio_mmio_survey.zig"),
        SURVEY_GATE_MARKERS,
    )
    check_markers(
        missing_markers,
        "build_file",
        read_text(root, "zigux/tests/phase10_build.zig"),
        BUILD_MARKERS,
    )
    check_markers(
        missing_markers,
        "makefile",
        read_text(root, "zigux/Makefile"),
        MAKEFILE_MARKERS,
    )

    manifest = json.loads(read_text(root, "zigux/tests/phase10_virtio_mmio_manifest.json"))
    if manifest.get("lane_key") != "P10-L10":
        missing_markers.append("manifest:lane_key=P10-L10")
    if manifest.get("phase") != "Phase 10":
        missing_markers.append("manifest:phase=Phase 10")
    if manifest.get("anchor") != "drivers/virtio/virtio_mmio.c":
        missing_markers.append("manifest:anchor=drivers/virtio/virtio_mmio.c")
    if manifest.get("risky_transport_posture") != "blocked_on_risky_transport":
        missing_markers.append("manifest:risky_transport_posture=blocked_on_risky_transport")
    if manifest.get("freeze_boundary_status") != "aligned":
        missing_markers.append("manifest:freeze_boundary_status=aligned")

    gap_index = {
        gap.get("id"): gap
        for gap in manifest.get("gaps", [])
        if isinstance(gap, dict) and "id" in gap
    }
    for gap_id, status in EXPECTED_GAPS.items():
        gap = gap_index.get(gap_id)
        if gap is None:
            missing_markers.append(f"manifest:gap:{gap_id}")
            continue
        if gap.get("status") != status:
            missing_markers.append(f"manifest:gap_status:{gap_id}={gap.get('status')}")

    return [], missing_markers


def fixture_manifest() -> str:
    return json.dumps(
        {
            "lane_key": "P10-L10",
            "phase": "Phase 10",
            "anchor": "drivers/virtio/virtio_mmio.c",
            "risky_transport_posture": "blocked_on_risky_transport",
            "freeze_boundary_status": "aligned",
            "gaps": [{"id": gap_id, "status": status} for gap_id, status in EXPECTED_GAPS.items()],
        },
        indent=2,
    ) + "\n"


def write_fixture_files(root: Path) -> None:
    files = {
        "scripts/zigux/check-phase10-mmio-packet.py": "\n".join(MAKEFILE_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-mmio-slice.md": "\n".join(SLICE_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-mmio-survey.md": "\n".join(SURVEY_NOTE_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md": "\n".join(COMPANION_MARKERS) + "\n",
        "drivers/virtio/virtio_mmio.zig": "\n".join(HELPER_MARKERS) + "\n",
        "drivers/virtio/virtio_mmio_verify.zig": "\n".join(VERIFY_MARKERS) + "\n",
        "zigux/tests/phase10_virtio_mmio_manifest.json": fixture_manifest(),
        "zigux/tests/phase10_virtio_mmio_survey.zig": "\n".join(SURVEY_GATE_MARKERS) + "\n",
        "zigux/tests/phase10_build.zig": "\n".join(BUILD_MARKERS) + "\n",
        "zigux/Makefile": "\n".join(MAKEFILE_MARKERS) + "\n",
    }

    for rel_path, content in files.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def expect_missing_marker(root: Path, rel_path: str, old: str, new: str, expected: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(f"phase10-mmio-packet-self-test:unexpected_missing_files:{','.join(missing_files)}")
    if expected not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"phase10-mmio-packet-self-test:expected={expected}:actual={actual}")
    path.write_text(original, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_mmio_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_files(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-mmio-packet-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        expect_missing_marker(
            root,
            "drivers/virtio/virtio_mmio.zig",
            "self.pending_config_write = null;",
            "self.pending_config_write = stale_plan;",
            "helper:self.pending_config_write = null;",
        )
        expect_missing_marker(
            root,
            "drivers/virtio/virtio_mmio_verify.zig",
            "pub const FeatureNegotiationSummary = virtio_mmio.FeatureNegotiationSummary;",
            "pub const FeatureNegotiationDrift = virtio_mmio.FeatureNegotiationSummary;",
            "verify_helper:pub const FeatureNegotiationSummary = virtio_mmio.FeatureNegotiationSummary;",
        )
        expect_missing_marker(
            root,
            "zigux/tests/phase10_virtio_mmio_survey.zig",
            'try std.testing.expect(std.mem.indexOf(u8, build_file, "phase10-virtio-mmio-verify-tests") != null);',
            'try std.testing.expect(std.mem.indexOf(u8, build_file, "phase10-virtio-mmio-verify-drift") != null);',
            'survey_gate:try std.testing.expect(std.mem.indexOf(u8, build_file, "phase10-virtio-mmio-verify-tests") != null);',
        )
        expect_missing_marker(
            root,
            "zigux/tests/phase10_virtio_mmio_manifest.json",
            '"phase10-mmio-transport-identity-helper"',
            '"phase10-mmio-transport-identity-drift"',
            "manifest:gap:phase10-mmio-transport-identity-helper",
        )
        expect_missing_marker(
            root,
            "zigux/Makefile",
            "scripts/zigux/check-phase10-mmio-packet.py --self-test",
            "scripts/zigux/check-phase10-mmio-packet.py --fixture-test",
            "makefile:scripts/zigux/check-phase10-mmio-packet.py --self-test",
        )

    print("PHASE10_MMIO_PACKET_SELF_TEST=pass")
    print("PHASE10_MMIO_PACKET_SELF_TEST_CASE_COUNT=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 10 virtio MMIO packet.")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in synthetic drift tests for the packet checker.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE10_MMIO_PACKET=fail")
        print("MISSING_PHASE10_MMIO_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_MMIO_FILES_END")
        return 1

    if missing_markers:
        print("PHASE10_MMIO_PACKET=fail")
        print("MISSING_PHASE10_MMIO_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_MMIO_MARKERS_END")
        return 1

    print("PHASE10_MMIO_PACKET=pass")
    print(f"PHASE10_MMIO_REQUIRED_FILE_COUNT={len(FILES)}")
    print(
        "PHASE10_MMIO_REQUIRED_MARKER_COUNT="
        f"{len(SLICE_MARKERS) + len(SURVEY_NOTE_MARKERS) + len(COMPANION_MARKERS) + len(HELPER_MARKERS) + len(VERIFY_MARKERS) + len(SURVEY_GATE_MARKERS) + len(BUILD_MARKERS) + len(MAKEFILE_MARKERS) + len(EXPECTED_GAPS) + 5}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
