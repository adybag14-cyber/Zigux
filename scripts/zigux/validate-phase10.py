#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent
HEX40 = re.compile(r"^[0-9a-f]{40}$")

FILES = [
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase10-virtio-ring-slice.md",
    "Documentation/zigux/phase10-virtio-ring-survey.md",
    "Documentation/zigux/phase10-virtio-input-slice.md",
    "Documentation/zigux/phase10-virtio-input-module-slice.md",
    "Documentation/zigux/phase10-virtio-input-survey.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "drivers/virtio/virtio_ring.zig",
    "drivers/virtio/virtio_input.zig",
    "zigux/tests/README.md",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_virtio_ring.zig",
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "zigux/tests/phase10_virtio_ring_survey.zig",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_input.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "Documentation/zigux/phase10-virtio-mmio-slice.md",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
    "drivers/virtio/virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
]

MAKE_MARKERS = [
    "PHONY += phase10-validate phase10-test phase10",
    "phase10-validate:",
    "scripts/zigux/validate-phase10.py --self-test",
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py",
    "phase10-test:",
    "$(ZIG) build test --build-file zigux/tests/phase10_build.zig --summary all",
    "phase10: phase10-validate phase10-test",
]

WORKFLOW_MARKERS = [
    "Self-test Phase 10 shared validator",
    "python3 scripts/zigux/validate-phase10.py --self-test",
    "Validate Phase 10 closure evidence",
    "make -C zigux phase10-validate",
    "Run Phase 10 virtio helper tests",
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
]

SCRIPT_README_MARKERS = [
    "validate-phase10.py",
    "Phase 10 flow",
    "make -C zigux phase10-validate",
    "Phase 10 ring-plus-input-plus-MMIO lab packet",
    "phase10_build.zig",
    "phase10_virtio_ring_manifest.json",
    "phase10_virtio_ring_reset_reuse.zig",
    "phase10_virtio_input_manifest.json",
    "phase10_virtio_mmio_manifest.json",
    "phase10-virtio-ring-slice.md",
    "phase10-virtio-input-slice.md",
    "phase10-virtio-input-survey.md",
    "ring manifest-backed packet",
    "ring reset-reuse replay",
    "blocked registration-lifecycle contract",
    "shared validation surface",
    "bounded MMIO interrupt-ack rung",
    "probe-preflight helper",
    "eleven shared test entrypoints",
]

FORBIDDEN_SCRIPT_README_MARKERS = [
    "ABS_MT_SLOT remains the single ready-next helper step",
]

TESTS_README_MARKERS = [
    "scripts/zigux/validate-phase10.py",
    "zigux/tests/phase10_virtio_core_survey.zig",
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "registration-preflight helper",
    "queue-callback preflight helper",
    "registration-lifecycle blocker",
    "four lane survey manifests plus the shared `zigux/tests/phase10_closure_manifest.json`",
]

FORBIDDEN_TESTS_README_MARKERS = [
    "three lane survey manifests plus the shared `zigux/tests/phase10_closure_manifest.json`",
    "three manifest-backed survey records",
]

DOC_README_MARKERS = [
    "python3 scripts/zigux/validate-phase10.py",
    "python3 scripts/zigux/check-phase10-harness-coverage.py",
    "make -C zigux phase10-validate",
    "phase10-closure-evidence.md",
    "same nine published Phase 10 docs named by the shared closure packet",
    "phase10-virtio-core-survey.md",
    "phase10-virtio-ring-slice.md",
    "phase10-virtio-mmio-slice.md",
    "phase10-virtio-input-slice.md",
    "phase10-virtio-input-survey.md",
    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
    "focused harness replays",
    "queue-handling and ready-state gate",
    "registration-preflight helper",
    "queue-callback preflight helper",
    "landed probe-preflight helper",
    "registration-lifecycle plus MMIO lifecycle blockers",
]

RING_SLICE_MARKERS = [
    "notify-prepare accounting with rollover flushing",
    "queue-reset guard and drained-queue reset bookkeeping",
    "Do not reopen `virtio_ring.zig` for more speculative in-memory queue work",
]

RING_SURVEY_MARKERS = [
    "phase10-mmio-config-write-helper",
    "no smaller ready transport follow-up remains ahead of the still-blocked lifecycle and IRQ packet",
]

SLICE_MARKERS = [
    "python3 scripts/zigux/validate-phase10.py",
    "make -C zigux phase10-validate",
    "queue-callback preflight helper",
    "input-device registration work",
]

SURVEY_MARKERS = [
    "python3 scripts/zigux/validate-phase10.py",
    "make -C zigux phase10-validate",
    "phase10-virtio-input-registration-preflight-helper",
    "phase10-virtio-input-queue-callback-preflight-helper",
    "phase10-virtio-input-probe-preflight-helper",
    "phase10-virtio-input-registration-lifecycle",
]

MODULE_SLICE_MARKERS = [
    "queue-callback preflight helper",
    "input core capability registration",
]

MMIO_SLICE_MARKERS = [
    "PHASE10_SLICE=virtio-mmio-interrupt-ack-helper",
    "in-memory config-write planning",
    "phase10-mmio-lifecycle-and-irq-paths",
]

MMIO_SURVEY_MARKERS = [
    "phase10-mmio-config-write-helper",
    "phase10-mmio-lifecycle-and-irq-paths",
    "config-write planning helper",
]

RING_HELPER_MARKERS = [
    "pub fn pollUsedBuffers(",
    "pub fn enableCallbackDelayed(",
    "pub fn resetGuardSummary(",
    "pub fn resetQueue(",
    "pub fn recoverBrokenQueue(",
]

MMIO_HELPER_MARKERS = [
    "pub const ConfigWritePlanSummary = struct {",
    "pub fn planConfigWrite(",
    "pub fn snapshotConfigWindow(",
    "pub fn acknowledgeInterrupt(self: *Self, bits: u32) !InterruptAckSummary {",
]

RING_TEST_MARKERS = [
    'test "phase10 virtio ring delays callbacks until most outstanding buffers are consumed" {',
    'test "phase10 virtio ring reset rejects queues with unpublished or unpolled work" {',
    'test "phase10 virtio ring reset clears drained queue bookkeeping without dropping queue shape" {',
]

RING_RESET_REUSE_TEST_MARKERS = [
    'test "phase10 virtio ring drained reset clears the broken flag so the queue can be reused" {',
]

RING_SURVEY_TEST_MARKERS = [
    'test "phase10 virtio ring survey manifest records the live queue-discipline packet and parked MMIO blocker after landed interrupt-ack" {',
    'try std.testing.expectEqual(@as(usize, 40), manifest.surveyed_commit.len);',
    'try std.testing.expectEqual(@as(usize, 0), ready_next_count);',
    'if (std.mem.eql(u8, gap.id, "phase10-mmio-config-write-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-mmio-lifecycle-and-irq-paths")) {',
]

HELPER_MARKERS = [
    "pub const MultitouchSlotPlanSummary = struct {",
    "pub const TeardownPlanSummary = struct {",
    "pub const RegistrationPreflightSummary = struct {",
    "pub const QueueCallbackPreflightSummary = struct {",
    "pub fn capabilitySetupSummary(self: *const Self) !CapabilitySetupSummary {",
    "pub fn multitouchSlotPlanSummary(self: *const Self) !MultitouchSlotPlanSummary {",
    "pub fn teardownPlanSummary(self: *const Self) TeardownPlanSummary {",
    "pub fn registrationPreflightSummary(self: *const Self) !RegistrationPreflightSummary {",
    "pub fn queueCallbackPreflightSummary(self: *const Self) !QueueCallbackPreflightSummary {",
    "pub fn sendStatus(self: *Self, event_type: u16, code: u16, value: i32) !StatusSendSummary {",
    "pub fn reset(self: *Self) void {",
]

TEST_MARKERS = [
    'test "phase10 virtio input stages capability setup from config bitmaps and ABS metadata" {',
    'test "phase10 virtio input plans multitouch slots from ABS_MT_SLOT metadata" {',
    'test "phase10 virtio input teardown summary keeps reset cleanup and identity preservation explicit" {',
    'test "phase10 virtio input records registration preflight once identity and capability intent are staged" {',
    'test "phase10 virtio input registration preflight infers multitouch slot intent from staged ABS_MT_SLOT metadata" {',
    'test "phase10 virtio input records queue-callback preflight once registration and queue intent are staged" {',
    'test "phase10 virtio input records probe preflight once registration and queue provisioning converge" {',
    'test "phase10 virtio input reset clears queue plan and returns to default bus identity" {',
]

SURVEY_TEST_MARKERS = [
    'test "phase10 virtio input survey manifest records the live starter and remaining gap" {',
    'try std.testing.expectEqualStrings("P10-L13", manifest.lane_key);',
    'try std.testing.expectEqual(@as(usize, 0), ready_next_count);',
    'try std.testing.expectEqual(@as(usize, 1), blocked_count);',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-teardown-observation-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-registration-preflight-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-queue-callback-preflight-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-probe-preflight-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-registration-lifecycle")) {',
]

MMIO_TEST_MARKERS = [
    'test "phase10 virtio mmio plans bounded config-window writes without side effects" {',
    'test "phase10 virtio mmio acknowledges only pending bounded interrupt bits" {',
]

MMIO_SURVEY_TEST_MARKERS = [
    'test "phase10 virtio mmio survey manifest records the landed config-write rung and remaining transport gap" {',
    'try std.testing.expectEqualStrings("P10-L18", manifest.lane_key);',
    'try std.testing.expectEqual(@as(usize, 0), ready_next_count);',
    'if (std.mem.eql(u8, gap.id, "phase10-mmio-config-write-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-mmio-lifecycle-and-irq-paths")) {',
]

ALLOWED_DESTINATIONS = ["drivers/virtio/*.zig", "zigux/kernel/", "zigux/helpers/"]

RING_EXPECTED_STATUSES = {
    "phase10-virtio-ring-survey-gate": "starter_landed",
    "phase10-virtio-ring-survey-note": "starter_landed",
    "phase10-virtqueue-shape-helper": "starter_landed",
    "phase10-used-buffer-polling-helper": "starter_landed",
    "phase10-callback-disable-helper": "starter_landed",
    "phase10-callback-enable-helper": "starter_landed",
    "phase10-callback-enable-prepare-helper": "starter_landed",
    "phase10-callback-delay-helper": "starter_landed",
    "phase10-notify-prepare-helper": "starter_landed",
    "phase10-queue-reset-guard-helper": "starter_landed",
    "phase10-queue-reset-helper": "starter_landed",
    "phase10-broken-queue-recovery-helper": "starter_landed",
    "phase10-mmio-config-write-helper": "starter_landed",
    "phase10-mmio-lifecycle-and-irq-paths": "blocked_on_risky_transport",
    "phase10-virtio-ring-slice-note": "starter_landed",
}

INPUT_EXPECTED_STATUSES = {
    "phase10-virtio-input-lab-helper": "starter_landed",
    "phase10-virtio-input-lab-gate": "starter_landed",
    "phase10-virtio-input-survey-gate": "starter_landed",
    "phase10-virtio-input-survey-note": "starter_landed",
    "phase10-virtio-input-capability-setup-helper": "starter_landed",
    "phase10-virtio-input-multitouch-slot-helper": "starter_landed",
    "phase10-virtio-input-teardown-observation-helper": "starter_landed",
    "phase10-virtio-input-registration-preflight-helper": "starter_landed",
    "phase10-virtio-input-queue-callback-preflight-helper": "starter_landed",
    "phase10-virtio-input-probe-preflight-helper": "starter_landed",
    "phase10-virtio-input-registration-lifecycle": "blocked_on_risky_transport",
}

MMIO_EXPECTED_STATUSES = {
    "phase10-virtio-mmio-survey-gate": "starter_landed",
    "phase10-virtio-mmio-survey-note": "starter_landed",
    "phase10-virtio-mmio-slice-note": "starter_landed",
    "phase10-mmio-register-window-helper": "starter_landed",
    "phase10-mmio-queue-register-helper": "starter_landed",
    "phase10-mmio-queue-notify-helper": "starter_landed",
    "phase10-mmio-queue-address-helper": "starter_landed",
    "phase10-mmio-config-window-helper": "starter_landed",
    "phase10-mmio-config-write-helper": "starter_landed",
    "phase10-mmio-interrupt-ack-helper": "starter_landed",
    "phase10-mmio-lifecycle-and-irq-paths": "blocked_on_risky_transport",
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def load_manifest(root: Path, rel_path: str) -> dict[str, object]:
    return json.loads(read_text(root, rel_path))


def find_gap(manifest: dict[str, object], gap_id: str) -> dict[str, object] | None:
    for gap in manifest.get("gaps", []):
        if isinstance(gap, dict) and gap.get("id") == gap_id:
            return gap
    return None


def require_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def forbid_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            missing.append(f"{label}:stale_marker:{marker}")


def validate_manifest(
    missing: list[str],
    label: str,
    manifest: dict[str, object],
    *,
    lane_key: str,
    anchor: str,
    expected_statuses: dict[str, str],
    minimum_gap_count: int,
    minimum_starter_count: int,
    expected_blocked_count: int = 1,
) -> None:
    if manifest.get("lane_key") != lane_key:
        missing.append(f"{label}:lane_key={lane_key}")
    if manifest.get("phase") != "Phase 10":
        missing.append(f"{label}:phase=Phase 10")
    if manifest.get("anchor") != anchor:
        missing.append(f"{label}:anchor={anchor}")
    if not HEX40.fullmatch(str(manifest.get("surveyed_commit", ""))):
        missing.append(f"{label}:surveyed_commit")
    if manifest.get("roadmap_destinations") != ALLOWED_DESTINATIONS:
        missing.append(f"{label}:roadmap_destinations")

    survey_summary = manifest.get("survey_summary")
    if not isinstance(survey_summary, dict):
        missing.append(f"{label}:survey_summary")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list) or len(gaps) < minimum_gap_count:
        missing.append(f"{label}:gaps")
        return

    starter_count = 0
    ready_count = 0
    blocked_count = 0
    for gap in gaps:
        if not isinstance(gap, dict):
            missing.append(f"{label}:gap_object")
            continue
        status = gap.get("status")
        if status == "starter_landed":
            starter_count += 1
        elif status == "ready_next":
            ready_count += 1
        elif status == "blocked_on_risky_transport":
            blocked_count += 1

    if starter_count < minimum_starter_count:
        missing.append(f"{label}:starter_count={starter_count}")
    if ready_count != 0:
        missing.append(f"{label}:ready_next_count={ready_count}")
    if blocked_count != expected_blocked_count:
        missing.append(f"{label}:blocked_count={blocked_count}")

    for gap_id, status in expected_statuses.items():
        gap = find_gap(manifest, gap_id)
        if gap is None:
            missing.append(f"{label}:gap:{gap_id}")
            continue
        if gap.get("status") != status:
            missing.append(f"{label}:gap_status:{gap_id}={gap.get('status')}")


def required_marker_count() -> int:
    return (
        len(MAKE_MARKERS)
        + len(WORKFLOW_MARKERS)
        + len(SCRIPT_README_MARKERS)
        + len(TESTS_README_MARKERS)
        + len(DOC_README_MARKERS)
        + len(RING_SLICE_MARKERS)
        + len(RING_SURVEY_MARKERS)
        + len(SLICE_MARKERS)
        + len(SURVEY_MARKERS)
        + len(MODULE_SLICE_MARKERS)
        + len(MMIO_SLICE_MARKERS)
        + len(MMIO_SURVEY_MARKERS)
        + len(RING_HELPER_MARKERS)
        + len(HELPER_MARKERS)
        + len(MMIO_HELPER_MARKERS)
        + len(RING_TEST_MARKERS)
        + len(RING_RESET_REUSE_TEST_MARKERS)
        + len(RING_SURVEY_TEST_MARKERS)
        + len(TEST_MARKERS)
        + len(MMIO_TEST_MARKERS)
        + len(SURVEY_TEST_MARKERS)
        + len(MMIO_SURVEY_TEST_MARKERS)
        + len(FORBIDDEN_SCRIPT_README_MARKERS)
        + len(FORBIDDEN_TESTS_README_MARKERS)
    )


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing: list[str] = []
    for label, rel_path, markers in [
        ("make", "zigux/Makefile", MAKE_MARKERS),
        ("workflow", ".github/workflows/zigux-bootstrap.yml", WORKFLOW_MARKERS),
        ("script_readme", "scripts/zigux/README.md", SCRIPT_README_MARKERS),
        ("tests_readme", "zigux/tests/README.md", TESTS_README_MARKERS),
        ("doc_readme", "Documentation/zigux/README.md", DOC_README_MARKERS),
        ("ring_slice_doc", "Documentation/zigux/phase10-virtio-ring-slice.md", RING_SLICE_MARKERS),
        ("ring_survey_doc", "Documentation/zigux/phase10-virtio-ring-survey.md", RING_SURVEY_MARKERS),
        ("slice_doc", "Documentation/zigux/phase10-virtio-input-slice.md", SLICE_MARKERS),
        ("survey_doc", "Documentation/zigux/phase10-virtio-input-survey.md", SURVEY_MARKERS),
        ("module_slice", "Documentation/zigux/phase10-virtio-input-module-slice.md", MODULE_SLICE_MARKERS),
        ("mmio_slice_doc", "Documentation/zigux/phase10-virtio-mmio-slice.md", MMIO_SLICE_MARKERS),
        ("mmio_survey_doc", "Documentation/zigux/phase10-virtio-mmio-survey.md", MMIO_SURVEY_MARKERS),
        ("ring_helper", "drivers/virtio/virtio_ring.zig", RING_HELPER_MARKERS),
        ("helper", "drivers/virtio/virtio_input.zig", HELPER_MARKERS),
        ("mmio_helper", "drivers/virtio/virtio_mmio.zig", MMIO_HELPER_MARKERS),
        ("ring_tests", "zigux/tests/phase10_virtio_ring.zig", RING_TEST_MARKERS),
        ("ring_reset_reuse_tests", "zigux/tests/phase10_virtio_ring_reset_reuse.zig", RING_RESET_REUSE_TEST_MARKERS),
        ("ring_survey_tests", "zigux/tests/phase10_virtio_ring_survey.zig", RING_SURVEY_TEST_MARKERS),
        ("tests", "zigux/tests/phase10_virtio_input.zig", TEST_MARKERS),
        ("survey_test", "zigux/tests/phase10_virtio_input_survey.zig", SURVEY_TEST_MARKERS),
        ("mmio_tests", "zigux/tests/phase10_virtio_mmio.zig", MMIO_TEST_MARKERS),
        ("mmio_survey_test", "zigux/tests/phase10_virtio_mmio_survey.zig", MMIO_SURVEY_TEST_MARKERS),
    ]:
        require_markers(missing, label, read_text(root, rel_path), markers)

    forbid_markers(missing, "script_readme", read_text(root, "scripts/zigux/README.md"), FORBIDDEN_SCRIPT_README_MARKERS)
    forbid_markers(missing, "tests_readme", read_text(root, "zigux/tests/README.md"), FORBIDDEN_TESTS_README_MARKERS)

    validate_manifest(
        missing,
        "ring_manifest",
        load_manifest(root, "zigux/tests/phase10_virtio_ring_manifest.json"),
        lane_key="P10-L07",
        anchor="drivers/virtio/virtio_ring.c",
        expected_statuses=RING_EXPECTED_STATUSES,
        minimum_gap_count=20,
        minimum_starter_count=20,
    )
    validate_manifest(
        missing,
        "manifest",
        load_manifest(root, "zigux/tests/phase10_virtio_input_manifest.json"),
        lane_key="P10-L13",
        anchor="drivers/virtio/virtio_input.c",
        expected_statuses=INPUT_EXPECTED_STATUSES,
        minimum_gap_count=13,
        minimum_starter_count=10,
    )
    validate_manifest(
        missing,
        "mmio_manifest",
        load_manifest(root, "zigux/tests/phase10_virtio_mmio_manifest.json"),
        lane_key="P10-L18",
        anchor="drivers/virtio/virtio_mmio.c",
        expected_statuses=MMIO_EXPECTED_STATUSES,
        minimum_gap_count=18,
        minimum_starter_count=17,
    )

    return [], missing


def manifest_template(
    lane_key: str,
    anchor: str,
    statuses: dict[str, str],
    minimum_gap_count: int,
) -> dict[str, object]:
    gaps = []
    for gap_id, status in statuses.items():
        gaps.append(
            {
                "id": gap_id,
                "status": status,
                "kind": "validation",
                "zigux_destination": "drivers/virtio/example.zig",
                "why_now": "fixture marker for validator self-test",
            }
        )
    while len(gaps) < minimum_gap_count:
        gaps.append(
            {
                "id": f"fixture-extra-{len(gaps)}",
                "status": "starter_landed",
                "kind": "validation",
                "zigux_destination": "drivers/virtio/example.zig",
                "why_now": "fixture filler gap",
            }
        )
    return {
        "lane_key": lane_key,
        "phase": "Phase 10",
        "surveyed_commit": "0123456789abcdef0123456789abcdef01234567",
        "anchor": anchor,
        "roadmap_destinations": ALLOWED_DESTINATIONS,
        "survey_summary": {"fixture": True},
        "gaps": gaps,
    }


def write_fixture_tree(root: Path) -> None:
    text_files = {
        "zigux/Makefile": "\n".join(MAKE_MARKERS) + "\n",
        ".github/workflows/zigux-bootstrap.yml": "\n".join(WORKFLOW_MARKERS) + "\n",
        "scripts/zigux/README.md": "\n".join(SCRIPT_README_MARKERS) + "\n",
        "zigux/tests/README.md": "\n".join(TESTS_README_MARKERS) + "\n",
        "Documentation/zigux/README.md": "\n".join(DOC_README_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-ring-slice.md": "\n".join(RING_SLICE_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-ring-survey.md": "\n".join(RING_SURVEY_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-input-slice.md": "\n".join(SLICE_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-input-module-slice.md": "\n".join(MODULE_SLICE_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-input-survey.md": "\n".join(SURVEY_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-mmio-slice.md": "\n".join(MMIO_SLICE_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-mmio-survey.md": "\n".join(MMIO_SURVEY_MARKERS) + "\n",
        "drivers/virtio/virtio_ring.zig": "\n".join(RING_HELPER_MARKERS) + "\n",
        "drivers/virtio/virtio_input.zig": "\n".join(HELPER_MARKERS) + "\n",
        "drivers/virtio/virtio_mmio.zig": "\n".join(MMIO_HELPER_MARKERS) + "\n",
        "zigux/tests/phase10_build.zig": "fixture\n",
        "zigux/tests/phase10_virtio_ring.zig": "\n".join(RING_TEST_MARKERS) + "\n",
        "zigux/tests/phase10_virtio_ring_reset_reuse.zig": "\n".join(RING_RESET_REUSE_TEST_MARKERS) + "\n",
        "zigux/tests/phase10_virtio_ring_survey.zig": "\n".join(RING_SURVEY_TEST_MARKERS) + "\n",
        "zigux/tests/phase10_virtio_input.zig": "\n".join(TEST_MARKERS) + "\n",
        "zigux/tests/phase10_virtio_input_survey.zig": "\n".join(SURVEY_TEST_MARKERS) + "\n",
        "zigux/tests/phase10_virtio_mmio.zig": "\n".join(MMIO_TEST_MARKERS) + "\n",
        "zigux/tests/phase10_virtio_mmio_survey.zig": "\n".join(MMIO_SURVEY_TEST_MARKERS) + "\n",
        "scripts/zigux/validate-phase10.py": "fixture\n",
        "scripts/zigux/validate-phase10-closure.py": "fixture\n",
    }

    manifests = {
        "zigux/tests/phase10_virtio_ring_manifest.json": manifest_template(
            "P10-L07",
            "drivers/virtio/virtio_ring.c",
            RING_EXPECTED_STATUSES,
            21,
        ),
        "zigux/tests/phase10_virtio_input_manifest.json": manifest_template(
            "P10-L13",
            "drivers/virtio/virtio_input.c",
            INPUT_EXPECTED_STATUSES,
            13,
        ),
        "zigux/tests/phase10_virtio_mmio_manifest.json": manifest_template(
            "P10-L18",
            "drivers/virtio/virtio_mmio.c",
            MMIO_EXPECTED_STATUSES,
            18,
        ),
    }

    for rel_path in FILES:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel_path in manifests:
            path.write_text(json.dumps(manifests[rel_path], indent=2) + "\n", encoding="utf-8")
        else:
            path.write_text(text_files[rel_path], encoding="utf-8")


def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(f"{label}:unexpected_missing_files:{','.join(missing_files)}")
    if expected_marker not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"{label}:expected:{expected_marker}:actual:{actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_selftest_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_tree(tmp_root)

        missing_files, missing_markers = validate(tmp_root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        ring_manifest_path = tmp_root / "zigux/tests/phase10_virtio_ring_manifest.json"
        ring_manifest = json.loads(ring_manifest_path.read_text(encoding="utf-8"))
        ring_manifest["lane_key"] = "P10-L08"
        ring_manifest_path.write_text(json.dumps(ring_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("ring_lane_key_guard", tmp_root, "ring_manifest:lane_key=P10-L07")
        write_fixture_tree(tmp_root)

        ring_manifest = json.loads(ring_manifest_path.read_text(encoding="utf-8"))
        ring_manifest["roadmap_destinations"] = ["drivers/virtio/*.zig", "zigux/helpers/"]
        ring_manifest_path.write_text(json.dumps(ring_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("ring_destinations_guard", tmp_root, "ring_manifest:roadmap_destinations")
        write_fixture_tree(tmp_root)

        input_manifest_path = tmp_root / "zigux/tests/phase10_virtio_input_manifest.json"
        input_manifest = json.loads(input_manifest_path.read_text(encoding="utf-8"))
        for gap in input_manifest["gaps"]:
            if gap["id"] == "phase10-virtio-input-registration-lifecycle":
                gap["status"] = "ready_next"
                break
        input_manifest_path.write_text(json.dumps(input_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("input_blocker_guard", tmp_root, "manifest:ready_next_count=1")
        write_fixture_tree(tmp_root)

        mmio_manifest_path = tmp_root / "zigux/tests/phase10_virtio_mmio_manifest.json"
        mmio_manifest = json.loads(mmio_manifest_path.read_text(encoding="utf-8"))
        for gap in mmio_manifest["gaps"]:
            if gap["id"] == "phase10-mmio-lifecycle-and-irq-paths":
                gap["id"] = "phase10-mmio-lifecycle-and-irq-paths-drift"
                break
        mmio_manifest_path.write_text(json.dumps(mmio_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("mmio_blocker_presence_guard", tmp_root, "mmio_manifest:gap:phase10-mmio-lifecycle-and-irq-paths")
        write_fixture_tree(tmp_root)

        docs_root_path = tmp_root / "Documentation/zigux/README.md"
        docs_root_path.write_text("missing marker fixture\n", encoding="utf-8")
        expect_missing_marker("docs_root_marker_guard", tmp_root, "doc_readme:phase10-closure-evidence.md")
        write_fixture_tree(tmp_root)

        tests_readme_path = tmp_root / "zigux/tests/README.md"
        tests_readme_path.write_text(
            read_text(tmp_root, "zigux/tests/README.md") + "\nthree manifest-backed survey records\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_stale_marker_guard",
            tmp_root,
            "tests_readme:stale_marker:three manifest-backed survey records",
        )
        write_fixture_tree(tmp_root)

        script_readme_path = tmp_root / "scripts/zigux/README.md"
        script_readme_path.write_text(
            read_text(tmp_root, "scripts/zigux/README.md")
            + "\nABS_MT_SLOT remains the single ready-next helper step\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "script_readme_stale_marker_guard",
            tmp_root,
            "script_readme:stale_marker:ABS_MT_SLOT remains the single ready-next helper step",
        )

    print("PHASE10_VALIDATOR_SELF_TEST=pass")
    print("PHASE10_VALIDATOR_SELF_TEST_CASE_COUNT=7")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the shared Phase 10 virtio lab review packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in validator drift checks against a temporary Phase 10 fixture tree.",
    )
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
    sys.exit(main())
