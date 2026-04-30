#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[2]


required_files = [
    ROOT / "Documentation" / "zigux" / "phase10-closure-evidence.md",
    ROOT / "Documentation" / "zigux" / "freeze-map.md",
    ROOT / "Documentation" / "zigux" / "phase10-virtio-core-slice.md",
    ROOT / "Documentation" / "zigux" / "phase10-virtio-core-survey.md",
    ROOT / "Documentation" / "zigux" / "phase10-virtio-ring-slice.md",
    ROOT / "Documentation" / "zigux" / "phase10-virtio-ring-survey.md",
    ROOT / "Documentation" / "zigux" / "phase10-virtio-input-slice.md",
    ROOT / "Documentation" / "zigux" / "phase10-virtio-input-module-slice.md",
    ROOT / "Documentation" / "zigux" / "phase10-virtio-input-survey.md",
    ROOT / "Documentation" / "zigux" / "phase10-virtio-mmio-slice.md",
    ROOT / "Documentation" / "zigux" / "phase10-virtio-mmio-survey.md",
    ROOT / "Documentation" / "zigux" / "review-checklist.md",
    ROOT / "Documentation" / "zigux" / "README.md",
    ROOT / "scripts" / "zigux" / "validate-phase10-closure.py",
    ROOT / "zigux" / "Makefile",
    ROOT / ".github" / "workflows" / "zigux-bootstrap.yml",
    ROOT / "zigux-alpha" / "BOOTSTRAP_COMMIT_LEDGER.md",
    ROOT / "zigux-alpha" / "PHASE10_CLOSURE_LEDGER.md",
    ROOT / "drivers" / "virtio" / "virtio.zig",
    ROOT / "drivers" / "virtio" / "virtio_ring.zig",
    ROOT / "drivers" / "virtio" / "virtio_input.zig",
    ROOT / "drivers" / "virtio" / "virtio_mmio.zig",
    ROOT / "zigux" / "tests" / "phase10_build.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_core.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_core_manifest.json",
    ROOT / "zigux" / "tests" / "phase10_virtio_core_survey.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_ring.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_ring_reset_reuse.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_ring_survey.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_input.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_input_survey.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_mmio.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_mmio_survey.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_ring_manifest.json",
    ROOT / "zigux" / "tests" / "phase10_virtio_input_manifest.json",
    ROOT / "zigux" / "tests" / "phase10_virtio_mmio_manifest.json",
    ROOT / "zigux" / "tests" / "phase10_closure_manifest.json",
]


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print("PHASE10_CLOSURE_VALIDATION=fail")
    print("MISSING_PHASE10_CLOSURE_FILES_START")
    for item in missing:
        print(item)
    print("MISSING_PHASE10_CLOSURE_FILES_END")
    sys.exit(1)

closure = (ROOT / "Documentation" / "zigux" / "phase10-closure-evidence.md").read_text(encoding="utf-8")
freeze_map = (ROOT / "Documentation" / "zigux" / "freeze-map.md").read_text(encoding="utf-8")
review_checklist = (ROOT / "Documentation" / "zigux" / "review-checklist.md").read_text(encoding="utf-8")
docs_readme = (ROOT / "Documentation" / "zigux" / "README.md").read_text(encoding="utf-8")
core_survey_test = (ROOT / "zigux" / "tests" / "phase10_virtio_core_survey.zig").read_text(encoding="utf-8")
ring_survey = (ROOT / "Documentation" / "zigux" / "phase10-virtio-ring-survey.md").read_text(encoding="utf-8")
ring_survey_test = (ROOT / "zigux" / "tests" / "phase10_virtio_ring_survey.zig").read_text(encoding="utf-8")
input_survey_test = (ROOT / "zigux" / "tests" / "phase10_virtio_input_survey.zig").read_text(encoding="utf-8")
mmio_helper = (ROOT / "drivers" / "virtio" / "virtio_mmio.zig").read_text(encoding="utf-8")
mmio_test = (ROOT / "zigux" / "tests" / "phase10_virtio_mmio.zig").read_text(encoding="utf-8")
mmio_slice = (ROOT / "Documentation" / "zigux" / "phase10-virtio-mmio-slice.md").read_text(encoding="utf-8")
mmio_survey_test = (ROOT / "zigux" / "tests" / "phase10_virtio_mmio_survey.zig").read_text(encoding="utf-8")
phase10_build = (ROOT / "zigux" / "tests" / "phase10_build.zig").read_text(encoding="utf-8")
makefile = (ROOT / "zigux" / "Makefile").read_text(encoding="utf-8")
workflow = (ROOT / ".github" / "workflows" / "zigux-bootstrap.yml").read_text(encoding="utf-8")
phase10_ledger = (ROOT / "zigux-alpha" / "PHASE10_CLOSURE_LEDGER.md").read_text(encoding="utf-8")
manifest = load_json(ROOT / "zigux" / "tests" / "phase10_closure_manifest.json")
core_manifest = load_json(ROOT / "zigux" / "tests" / "phase10_virtio_core_manifest.json")
ring_manifest = load_json(ROOT / "zigux" / "tests" / "phase10_virtio_ring_manifest.json")
input_manifest = load_json(ROOT / "zigux" / "tests" / "phase10_virtio_input_manifest.json")
mmio_manifest = load_json(ROOT / "zigux" / "tests" / "phase10_virtio_mmio_manifest.json")

required_closure_markers = [
    "PHASE10_STATUS=active",
    "PHASE10_TRANCHE=virtio-lab-bundle",
    "PHASE10_CLOSURE_EVIDENCE=verified",
    "PHASE10_DOC_COUNT=9",
    "PHASE10_MANIFEST_COUNT=4",
    "PHASE10_DRIVER_COUNT=4",
    "PHASE10_TEST_COUNT=9",
    "PHASE10_HAS_VIRTIO_MMIO_ZIG=yes",
    "PHASE10_ROADMAP_PARITY_SCOREBOARD=present",
    "PHASE10_ROADMAP_SCOREBOARD_ROW_COUNT=4",
    "PHASE10_ROADMAP_VIRTQUEUE_WRAPPERS=starter_landed",
    "PHASE10_ROADMAP_MMIO_WRAPPERS=starter_landed",
    "PHASE10_ROADMAP_LAB_ONLY_DRIVER_VALIDATION=starter_landed",
    "PHASE10_ROADMAP_DUAL_IMPLEMENTATIONS_FOR_RISKY_AREAS=blocked_on_risky_transport",
    "PHASE10_REFERENCE_SAMPLE_PARITY_OUT_OF_SCOPE=yes",
    "PHASE10_RUNTIME_STARTER_PARITY_OUT_OF_SCOPE=yes",
    "PHASE10_CROSS_PHASE_SCOREBOARD_BOUNDARY=phase5_reference_samples_and_phase9_runtime_starters_do_not_count_as_phase10_virtio_driver_evidence",
    "samples/zigux/",
    "zigux/tests/phase5_build.zig",
    "Documentation/zigux/phase9-runtime-loader-gap-survey.md",
    "zigux/tests/runtime_loader_gap_manifest.json",
    "zigux/tests/runtime_loader_gap_survey.zig",
    "zigux/tests/phase9_build.zig",
    "zigux/kernel/runtime_loader.zig",
    "zigux/helpers/allocator_policy.zig",
    "samples/zigux/runtime_atomic64_loader.zig",
    "samples/zigux/runtime_bitmap_loader.zig",
    "samples/zigux/runtime_kretprobe_loader.zig",
    "PHASE10_CLOSURE_GATE=python3 scripts/zigux/validate-phase10-closure.py",
    "PHASE10_BUILD_GATE=zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "PHASE10_VALIDATE_ENTRYPOINT=make -C zigux phase10-validate",
    "PHASE10_TEST_ENTRYPOINT=make -C zigux phase10-test",
    "PHASE10_COMBINED_ENTRYPOINT=make -C zigux phase10",
    "PHASE10_FREEZE_MAP=Documentation/zigux/freeze-map.md",
    "PHASE10_FREEZE_BOUNDARY_STATUS=aligned",
    "PHASE10_FREEZE_STATUS_CHANGE_CLAIM=no",
    "PHASE10_FREEZE_IN_C_ANCHOR_COUNT=4",
    "PHASE10_STUDY_ONLY_ANCHOR_COUNT=2",
    "PHASE10_ALLOWED_ROADMAP_DESTINATIONS=drivers/virtio/*.zig,zigux/helpers/",
    "PHASE10_ALLOWED_EVIDENCE_KINDS=driver_local_lab_slices,survey_manifests,shared_validation_gates",
    "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes",
    "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_ATTACHED=no",
    "PHASE10_FORBIDDEN_TRANSPORT_CLAIMS=queue_setup_reset_paths,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle",
    "Documentation/zigux/phase10-virtio-core-survey.md",
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_core_survey.zig",
    "Documentation/zigux/phase10-virtio-mmio-slice.md",
    "drivers/virtio/virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "Documentation/zigux/review-checklist.md",
    "phase10-mmio-queue-register-helper",
    "phase10-mmio-config-window-helper",
    "phase10-mmio-config-write-helper",
    "phase10-config-delivery-disposition-helper",
    "phase10-virtqueue-shape-helper",
    "phase10-used-buffer-polling-helper",
    "phase10-callback-disable-helper",
    "phase10-callback-enable-helper",
    "phase10-callback-enable-prepare-helper",
    "phase10-callback-delay-helper",
    "phase10-notify-prepare-helper",
    "phase10-queue-reset-guard-helper",
    "phase10-queue-reset-helper",
    "phase10-virtio-input-registration-preflight-helper",
    "phase10-virtio-input-queue-callback-preflight-helper",
    "landed ring queue-discipline ladder, input preflight pair, and MMIO helper ladder directly alongside the core helper evidence",
    "phase10-virtio-input-registration-lifecycle",
    "phase10-mmio-lifecycle-and-irq-paths",
    "blocked_on_risky_transport",
]
required_freeze_map_markers = [
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
    "Architecture Council",
]
required_makefile_markers = [
    "PHONY += phase10-validate phase10-test phase10",
    "phase10-validate:",
    "scripts/zigux/validate-phase10-closure.py",
    "phase10-test:",
    "$(ZIG) build test --build-file zigux/tests/phase10_build.zig --summary all",
    "phase10: phase10-validate phase10-test",
]
required_workflow_markers = [
    "Validate Phase 10 closure evidence",
    "make -C zigux phase10-validate",
    "Run Phase 10 virtio helper tests",
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
]
required_ledger_markers = [
    "Phase 10 Closure Ledger",
    "Documentation/zigux/phase10-closure-evidence.md",
    "scripts/zigux/validate-phase10-closure.py",
    "zigux/tests/phase10_closure_manifest.json",
    "Documentation/zigux/phase10-virtio-ring-survey.md",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "PHASE10_LEDGER_STATUS=active",
    "PHASE10_LEDGER_TRANCHE=virtio-lab-bundle",
    "PHASE10_LEDGER_MAKEFILE=zigux/Makefile",
    "PHASE10_LEDGER_WORKFLOW=.github/workflows/zigux-bootstrap.yml",
    "PHASE10_LEDGER_EXACT_CHECK_1=python3 scripts/zigux/validate-phase10-closure.py",
    "PHASE10_LEDGER_EXACT_CHECK_2=zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "PHASE10_LEDGER_EXACT_CHECK_3=make -C zigux phase10-validate",
    "PHASE10_LEDGER_EXACT_CHECK_4=make -C zigux phase10-test",
    "PHASE10_LEDGER_EXACT_CHECK_5=make -C zigux phase10",
    "PHASE10_LEDGER_NEXT_STEP=leave_parked_unless_phase10-mmio-lifecycle-and-irq-paths_splits_smaller",
    "PHASE10_LEDGER_BLOCKERS=phase10-virtio-input-registration-lifecycle,phase10-mmio-lifecycle-and-irq-paths",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
]
required_checklist_markers = [
    "if the change is a Phase 10 virtio slice, do `Documentation/zigux/phase10-closure-evidence.md`, its roadmap parity scoreboard, `zigux/tests/phase10_closure_manifest.json`, the four Phase 10 survey manifests, the landed ring queue-discipline helper ladder, the landed `Documentation/zigux/phase10-virtio-mmio-slice.md` plus `zigux/tests/phase10_virtio_mmio.zig` starter pair, and the shared `zigux/tests/phase10_build.zig` entrypoint still agree on the same bounded lab-only scope, exact replay commands, and explicit MMIO blocker posture?",
    "if the change touches the Phase 10 scoreboard or closure packet, do the Phase 5 sample lane and the current Phase 9 runtime loader-gap ownership packet still stay outside the Phase 10 virtio parity readout so `samples/zigux/`, `zigux/tests/phase5_build.zig`, `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/tests/runtime_loader_gap_survey.zig`, `zigux/tests/phase9_build.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/helpers/allocator_policy.zig`, `samples/zigux/runtime_atomic64_loader.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_kretprobe_loader.zig` are not silently counted as driver-local virtio evidence?",
    "if the change widens a Phase 10 virtio transport-facing path, do `Documentation/zigux/freeze-map.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-closure-evidence.md`, and the ring/input/MMIO survey manifests still keep the risky transport posture explicit instead of silently widening MMIO, queue setup or reset, IRQ, registration, DMA, or probe/remove lifecycle claims?",
]
required_docs_readme_markers = [
    "`Documentation/zigux/README.md` now exposes the shared Phase 10 closure note plus the same nine published Phase 10 docs named by the shared closure packet, including `Documentation/zigux/phase10-virtio-core-survey.md` and `Documentation/zigux/phase10-virtio-mmio-slice.md`, so the top-level docs index does not undercount the live parity-evidence bundle.",
    "`Documentation/zigux/phase10-closure-evidence.md` now records the exact current roadmap-aligned virtio lab bundle and keeps Phase 10 explicit as active rather than prematurely closed while `drivers/virtio/virtio_mmio.zig`, its bounded MMIO starter test, and the remaining risky transport gaps stay visible together.",
    "`python3 scripts/zigux/validate-phase10-closure.py` and `make -C zigux phase10-validate` now fail fast if the shared closure note, the four Phase 10 survey manifests, the bootstrap workflow, and `zigux/tests/phase10_build.zig` drift apart.",
]
required_core_survey_test_markers = [
    'test "phase10 virtio core survey manifest records the live core validation bundle" {',
    'try std.testing.expectEqualStrings("P10-L03", manifest.lane_key);',
    'try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-config-delivery-disposition-helper") != null);',
    'const closure_manifest_json = try std.Io.Dir.cwd().readFileAlloc(',
    'const landed_core_helper_evidence = closure_manifest.object.get("landed_core_helper_evidence") orelse return error.TestUnexpectedResult;',
    'const core_helper_evidence = landed_core_helper_evidence.object.get("zigux/tests/phase10_virtio_core_manifest.json") orelse return error.TestUnexpectedResult;',
    'const expected_landed_core_helpers = [_][]const u8{',
    '"phase10-config-generation-summary-helper",',
    '"phase10-config-delivery-disposition-helper",',
    'try std.testing.expectEqual(@as(usize, 1), blocked_count);',
    'if (std.mem.eql(u8, gap.id, "phase10-config-generation-summary-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-config-delivery-disposition-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-core-probe-remove-lifecycle")) {',
]
required_ring_survey_markers = [
    "remaining blocked MMIO lifecycle-and-IRQ boundary against the roadmap",
    "no smaller ready transport follow-up remains ahead of the still-blocked lifecycle and IRQ packet",
    "phase10-mmio-queue-register-helper",
]
required_ring_survey_test_markers = [
    'test "phase10 virtio ring survey manifest records the live queue-discipline packet and parked MMIO blocker after landed config-write" {',
    'try std.testing.expect(std.mem.indexOf(u8, survey_note, "no smaller ready transport follow-up remains ahead of the still-blocked lifecycle and IRQ packet") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, survey_note, "remaining MMIO follow-up ladder against the roadmap") == null);',
]
required_input_survey_test_markers = [
    'test "phase10 virtio input survey manifest records the live starter and remaining gap" {',
    'try std.testing.expectEqualStrings("P10-L13", manifest.lane_key);',
    'try std.testing.expectEqual(@as(usize, 0), ready_next_count);',
    'try std.testing.expectEqual(@as(usize, 1), blocked_count);',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-registration-preflight-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-queue-callback-preflight-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-registration-lifecycle")) {',
]
required_mmio_slice_markers = [
    "PHASE10_SLICE=virtio-mmio-config-write-helper",
    "in-memory config-write planning",
    "phase10-mmio-lifecycle-and-irq-paths",
]
required_mmio_helper_markers = [
    "pub const supported_interrupt_bits: u32 = 0x3;",
    "pub const supported_config_window_bytes: usize = 16;",
    "pub const ConfigWritePlanSummary = struct {",
    "config_window: [supported_config_window_bytes]u8 = [_]u8{0} ** supported_config_window_bytes,",
    "pub fn planConfigWrite(",
    "try validateConfigWriteValue(width, value);",
    "pub fn acknowledgeInterrupt(self: *Self, bits: u32) !InterruptAckSummary {",
    "if ((bits & ~supported_interrupt_bits) != 0) return error.UnsupportedInterruptBits;",
    "if (end > supported_config_window_bytes) return error.ConfigWindowOutOfRange;",
    "fn validateConfigWriteValue(width: ConfigWindowWidth, value: u32) !void {",
    "if (value > max_value) return error.ConfigWriteValueTooWide;",
]
required_mmio_test_markers = [
    'const virtio_mmio = @import("virtio_mmio");',
    'test "phase10 virtio mmio snapshots a bounded config window without writes" {',
    'test "phase10 virtio mmio plans bounded config-window writes without side effects" {',
    'var plan = try window.planConfigWrite(0, .half, 0xabcd);',
    'try std.testing.expectEqual(@as(u32, 0x1234), plan.previous_value);',
    'try std.testing.expectEqual(@as(u32, 0xabcd), plan.planned_value);',
    'plan = try window.planConfigWrite(2, .word, 0x11223344);',
    'try std.testing.expectEqual(@as(u32, 0x9abc5678), plan.previous_value);',
    'try std.testing.expectEqual(@as(u32, 0x11223344), plan.planned_value);',
    'try std.testing.expectError(error.ConfigWriteValueTooWide, window.planConfigWrite(8, .byte, 0x100));',
    'try std.testing.expectError(error.ConfigWriteValueTooWide, window.planConfigWrite(8, .half, 0x1_0000));',
    'try std.testing.expectError(error.ConfigWindowOutOfRange, window.planConfigWrite(15, .half, 0xabcd));',
    'test "phase10 virtio mmio acknowledges only pending bounded interrupt bits" {',
    'try std.testing.expectError(error.UnsupportedInterruptBits, window.acknowledgeInterrupt(0x8));',
]
required_mmio_survey_test_markers = [
    'test "phase10 virtio mmio survey manifest records the landed config-write rung and remaining transport gap" {',
    'try std.testing.expectEqualStrings("P10-L18", manifest.lane_key);',
    'try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", manifest.anchor);',
    'try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-mmio-config-write-helper") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-mmio-lifecycle-and-irq-paths") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, slice_note, "PHASE10_SLICE=virtio-mmio-config-write-helper") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, slice_note, "in-memory config-write planning") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, slice_note, "phase10-mmio-lifecycle-and-irq-paths") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, slice_note, "add one small config-window write-planning helper next") == null);',
    'try std.testing.expectEqual(@as(usize, 0), ready_next_count);',
    'if (std.mem.eql(u8, gap.id, "phase10-mmio-config-write-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-mmio-lifecycle-and-irq-paths")) {',
    'try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "without claiming config writes") == null);',
]
required_phase10_build_markers = [
    'const phase10_virtio_core_module = b.createModule(.{',
    '.root_source_file = b.path("phase10_virtio_core.zig"),',
    'const phase10_virtio_core_survey_module = b.createModule(.{',
    '.root_source_file = b.path("phase10_virtio_core_survey.zig"),',
    'const phase10_virtio_ring_module = b.createModule(.{',
    '.root_source_file = b.path("phase10_virtio_ring.zig"),',
    'const phase10_virtio_ring_reset_reuse_module = b.createModule(.{',
    '.root_source_file = b.path("phase10_virtio_ring_reset_reuse.zig"),',
    'const phase10_virtio_ring_survey_module = b.createModule(.{',
    '.root_source_file = b.path("phase10_virtio_ring_survey.zig"),',
    'const phase10_virtio_input_module = b.createModule(.{',
    '.root_source_file = b.path("phase10_virtio_input.zig"),',
    'const phase10_virtio_input_survey_module = b.createModule(.{',
    '.root_source_file = b.path("phase10_virtio_input_survey.zig"),',
    'const phase10_virtio_mmio_module = b.createModule(.{',
    '.root_source_file = b.path("phase10_virtio_mmio.zig"),',
    'const phase10_virtio_mmio_survey_module = b.createModule(.{',
    '.root_source_file = b.path("phase10_virtio_mmio_survey.zig"),',
    '.name = "phase10-virtio-core-tests",',
    '.name = "phase10-virtio-core-survey-tests",',
    '.name = "phase10-virtio-ring-tests",',
    '.name = "phase10-virtio-ring-reset-reuse-tests",',
    '.name = "phase10-virtio-ring-survey-tests",',
    '.name = "phase10-virtio-input-tests",',
    '.name = "phase10-virtio-input-survey-tests",',
    '.name = "phase10-virtio-mmio-tests",',
    '.name = "phase10-virtio-mmio-survey-tests",',
    'test_step.dependOn(&run_phase10_virtio_core_tests.step);',
    'test_step.dependOn(&run_phase10_virtio_core_survey_tests.step);',
    'test_step.dependOn(&run_phase10_virtio_ring_tests.step);',
    'test_step.dependOn(&run_phase10_virtio_ring_reset_reuse_tests.step);',
    'test_step.dependOn(&run_phase10_virtio_ring_survey_tests.step);',
    'test_step.dependOn(&run_phase10_virtio_input_tests.step);',
    'test_step.dependOn(&run_phase10_virtio_input_survey_tests.step);',
    'test_step.dependOn(&run_phase10_virtio_mmio_tests.step);',
    'test_step.dependOn(&run_phase10_virtio_mmio_survey_tests.step);',
]
forbidden_stale_mmio_slice_markers = [
    "PHASE10_SLICE=virtio-mmio-config-window-helper",
    "add one small config-window write-planning helper next",
]
forbidden_stale_ring_markers = [
    "remaining MMIO follow-up ladder against the roadmap",
    "remaining queue-wrapper gap",
    "queue-wrapper gap",
]
missing_markers: list[str] = []
for marker in required_closure_markers:
    if marker not in closure:
        missing_markers.append(f"closure:{marker}")
for marker in required_freeze_map_markers:
    if marker not in freeze_map:
        missing_markers.append(f"freeze_map:{marker}")
for marker in required_makefile_markers:
    if marker not in makefile:
        missing_markers.append(f"make:{marker}")
for marker in required_workflow_markers:
    if marker not in workflow:
        missing_markers.append(f"workflow:{marker}")
for marker in required_ledger_markers:
    if marker not in phase10_ledger:
        missing_markers.append(f"phase10_ledger:{marker}")
for marker in required_checklist_markers:
    if marker not in review_checklist:
        missing_markers.append(f"checklist:{marker}")
for marker in required_docs_readme_markers:
    if marker not in docs_readme:
        missing_markers.append(f"docs_readme:{marker}")
for marker in required_core_survey_test_markers:
    if marker not in core_survey_test:
        missing_markers.append(f"core_survey_test:{marker}")
for marker in required_ring_survey_markers:
    if marker not in ring_survey:
        missing_markers.append(f"ring_survey:{marker}")
for marker in required_ring_survey_test_markers:
    if marker not in ring_survey_test:
        missing_markers.append(f"ring_survey_test:{marker}")
for marker in required_input_survey_test_markers:
    if marker not in input_survey_test:
        missing_markers.append(f"input_survey_test:{marker}")
for marker in required_mmio_slice_markers:
    if marker not in mmio_slice:
        missing_markers.append(f"mmio_slice:{marker}")
for marker in required_mmio_helper_markers:
    if marker not in mmio_helper:
        missing_markers.append(f"mmio_helper:{marker}")
for marker in required_mmio_test_markers:
    if marker not in mmio_test:
        missing_markers.append(f"mmio_test:{marker}")
for marker in required_mmio_survey_test_markers:
    if marker not in mmio_survey_test:
        missing_markers.append(f"mmio_survey_test:{marker}")
for marker in required_phase10_build_markers:
    if marker not in phase10_build:
        missing_markers.append(f"phase10_build:{marker}")
for marker in forbidden_stale_ring_markers:
    if marker in ring_survey:
        missing_markers.append(f"ring_survey:stale_marker:{marker}")
    if marker in ring_survey_test:
        missing_markers.append(f"ring_survey_test:stale_marker:{marker}")
for marker in forbidden_stale_mmio_slice_markers:
    if marker in mmio_slice:
        missing_markers.append(f"mmio_slice:stale_marker:{marker}")

if manifest.get("phase") != "Phase 10":
    missing_markers.append("manifest:phase=Phase 10")
if manifest.get("status") != "active":
    missing_markers.append("manifest:status=active")
if manifest.get("tranche") != "virtio-lab-bundle":
    missing_markers.append("manifest:tranche=virtio-lab-bundle")
if manifest.get("doc_count") != 9:
    missing_markers.append(f'manifest:doc_count={manifest.get("doc_count")}')
if manifest.get("manifest_count") != 4:
    missing_markers.append(f'manifest:manifest_count={manifest.get("manifest_count")}')
if manifest.get("driver_count") != 4:
    missing_markers.append(f'manifest:driver_count={manifest.get("driver_count")}')
if manifest.get("test_count") != 9:
    missing_markers.append(f'manifest:test_count={manifest.get("test_count")}')
if manifest.get("has_virtio_mmio_zig") is not True:
    missing_markers.append(f'manifest:has_virtio_mmio_zig={manifest.get("has_virtio_mmio_zig")}')
if manifest.get("freeze_map") != "Documentation/zigux/freeze-map.md":
    missing_markers.append(f'manifest:freeze_map={manifest.get("freeze_map")}')
if manifest.get("freeze_boundary_status") != "aligned":
    missing_markers.append(
        f'manifest:freeze_boundary_status={manifest.get("freeze_boundary_status")} '
    )
if manifest.get("freeze_status_change_claimed") is not False:
    missing_markers.append(
        "manifest:freeze_status_change_claimed=true"
    )
if manifest.get("review_checklist") != "Documentation/zigux/review-checklist.md":
    missing_markers.append(f'manifest:review_checklist={manifest.get("review_checklist")}')
if manifest.get("risky_transport_posture") != "blocked_on_risky_transport":
    missing_markers.append(f'manifest:risky_transport_posture={manifest.get("risky_transport_posture")}')
expected_allowed_roadmap_destinations = [
    "drivers/virtio/*.zig",
    "zigux/helpers/",
]
if manifest.get("allowed_roadmap_destinations") != expected_allowed_roadmap_destinations:
    missing_markers.append("manifest:allowed_roadmap_destinations:mismatch")
expected_allowed_evidence_kinds = [
    "driver_local_lab_slices",
    "survey_manifests",
    "shared_validation_gates",
]
if manifest.get("allowed_evidence_kinds") != expected_allowed_evidence_kinds:
    missing_markers.append("manifest:allowed_evidence_kinds:mismatch")
if manifest.get("architecture_council_reopen_required") is not True:
    missing_markers.append("manifest:architecture_council_reopen_required=false")
if manifest.get("architecture_council_reopen_attached") is not False:
    missing_markers.append("manifest:architecture_council_reopen_attached=true")
expected_forbidden_transport_claims = [
    "queue_setup_reset_paths",
    "irq_parity",
    "dma_paths",
    "input_registration_lifecycle",
    "probe_remove_lifecycle",
]
if manifest.get("forbidden_transport_claims") != expected_forbidden_transport_claims:
    missing_markers.append("manifest:forbidden_transport_claims:mismatch")

expected_freeze_in_c_anchors = [
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
]
expected_study_only_anchors = [
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
]
if manifest.get("freeze_in_c_anchors") != expected_freeze_in_c_anchors:
    missing_markers.append("manifest:freeze_in_c_anchors:mismatch")
if manifest.get("study_only_anchors") != expected_study_only_anchors:
    missing_markers.append("manifest:study_only_anchors:mismatch")

for field in ("docs", "manifests", "drivers", "tests", "exact_checks"):
    value = manifest.get(field)
    if not isinstance(value, list) or not value:
        missing_markers.append(f"manifest:{field}:expected_non_empty_list")
        continue
    for rel in value:
        if not isinstance(rel, str):
            missing_markers.append(f"manifest:{field}:non_string_entry")
            continue
        if field != "exact_checks" and not (ROOT / rel).exists():
            missing_markers.append(f"manifest_file:{rel}")

expected_exact_checks = {
    "python3 scripts/zigux/validate-phase10-closure.py",
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "make -C zigux phase10"
}
if set(manifest.get("exact_checks", [])) != expected_exact_checks:
    missing_markers.append("manifest:exact_checks:mismatch")

expected_roadmap_parity_scoreboard = {
    "virtqueue_wrappers": {
        "status": "starter_landed",
        "evidence": [
            "drivers/virtio/virtio_ring.zig",
            "zigux/tests/phase10_virtio_ring.zig",
            "zigux/tests/phase10_virtio_ring_manifest.json",
            "Documentation/zigux/phase10-virtio-ring-survey.md"
        ]
    },
    "mmio_wrappers": {
        "status": "starter_landed",
        "evidence": [
            "drivers/virtio/virtio_mmio.zig",
            "zigux/tests/phase10_virtio_mmio.zig",
            "zigux/tests/phase10_virtio_mmio_manifest.json",
            "Documentation/zigux/phase10-virtio-mmio-slice.md",
            "Documentation/zigux/phase10-virtio-mmio-survey.md"
        ]
    },
    "lab_only_driver_validation": {
        "status": "starter_landed",
        "evidence": [
            "zigux/tests/phase10_build.zig",
            "scripts/zigux/validate-phase10-closure.py",
            "Documentation/zigux/phase10-closure-evidence.md"
        ]
    },
    "dual_implementations_for_risky_areas": {
        "status": "blocked_on_risky_transport",
        "evidence": [
            "Documentation/zigux/phase10-closure-evidence.md",
            "zigux/tests/phase10_virtio_ring_manifest.json",
            "zigux/tests/phase10_virtio_input_manifest.json",
            "zigux/tests/phase10_virtio_mmio_manifest.json"
        ]
    }
}
roadmap_parity_scoreboard = manifest.get("roadmap_parity_scoreboard")
if roadmap_parity_scoreboard != expected_roadmap_parity_scoreboard:
    missing_markers.append("manifest:roadmap_parity_scoreboard:mismatch")
else:
    for item in roadmap_parity_scoreboard.values():
        for rel in item.get("evidence", []):
            if not (ROOT / rel).exists():
                missing_markers.append(f"manifest:roadmap_parity_scoreboard:evidence_missing:{rel}")

expected_cross_phase_scoreboard_boundary = {
    "reference_samples": {
        "status": "out_of_scope",
        "evidence": [
            "samples/zigux",
            "zigux/tests/phase5_build.zig",
            "Documentation/zigux/review-checklist.md"
        ]
    },
    "runtime_starters": {
        "status": "out_of_scope",
        "evidence": [
            "Documentation/zigux/phase9-runtime-loader-gap-survey.md",
            "zigux/tests/runtime_loader_gap_manifest.json",
            "zigux/tests/runtime_loader_gap_survey.zig",
            "zigux/tests/phase9_build.zig",
            "zigux/kernel/runtime_loader.zig",
            "zigux/helpers/allocator_policy.zig",
            "samples/zigux/runtime_atomic64_loader.zig",
            "samples/zigux/runtime_bitmap_loader.zig",
            "samples/zigux/runtime_kretprobe_loader.zig"
        ]
    }
}
cross_phase_scoreboard_boundary = manifest.get("cross_phase_scoreboard_boundary")
if cross_phase_scoreboard_boundary != expected_cross_phase_scoreboard_boundary:
    missing_markers.append("manifest:cross_phase_scoreboard_boundary:mismatch")
else:
    for item in cross_phase_scoreboard_boundary.values():
        for rel in item.get("evidence", []):
            if not (ROOT / rel).exists():
                missing_markers.append(f"manifest:cross_phase_scoreboard_boundary:evidence_missing:{rel}")

survey_provenance = manifest.get("survey_provenance")
expected_survey_provenance = {
    "source": "manifest_derived",
    "lane_keys": {
        "core": core_manifest.get("lane_key"),
        "ring": ring_manifest.get("lane_key"),
        "input": input_manifest.get("lane_key"),
        "mmio": mmio_manifest.get("lane_key"),
    },
    "surveyed_commits": {
        "core": core_manifest.get("surveyed_commit"),
        "ring": ring_manifest.get("surveyed_commit"),
        "input": input_manifest.get("surveyed_commit"),
        "mmio": mmio_manifest.get("surveyed_commit"),
    },
}
if survey_provenance != expected_survey_provenance:
    missing_markers.append("manifest:survey_provenance:mismatch")

ready_transport_followups = manifest.get("ready_transport_followups")
expected_ready_transport_followups = {}
if ready_transport_followups != expected_ready_transport_followups:
    missing_markers.append("manifest:ready_transport_followups:mismatch")

landed_core_helper_evidence = manifest.get("landed_core_helper_evidence")
expected_landed_core_helper_evidence = {
    "zigux/tests/phase10_virtio_core_manifest.json": [
        "phase10-config-generation-summary-helper",
        "phase10-config-delivery-disposition-helper"
    ]
}
if landed_core_helper_evidence != expected_landed_core_helper_evidence:
    missing_markers.append("manifest:landed_core_helper_evidence:mismatch")

landed_ring_helper_evidence = manifest.get("landed_ring_helper_evidence")
expected_landed_ring_helper_evidence = {
    "zigux/tests/phase10_virtio_ring_manifest.json": [
        "phase10-virtqueue-shape-helper",
        "phase10-used-buffer-polling-helper",
        "phase10-callback-disable-helper",
        "phase10-callback-enable-helper",
        "phase10-callback-enable-prepare-helper",
        "phase10-callback-delay-helper",
        "phase10-notify-prepare-helper",
        "phase10-queue-reset-guard-helper",
        "phase10-queue-reset-helper",
    ]
}
if landed_ring_helper_evidence != expected_landed_ring_helper_evidence:
    missing_markers.append("manifest:landed_ring_helper_evidence:mismatch")

landed_input_helper_evidence = manifest.get("landed_input_helper_evidence")
expected_landed_input_helper_evidence = {
    "zigux/tests/phase10_virtio_input_manifest.json": [
        "phase10-virtio-input-registration-preflight-helper",
        "phase10-virtio-input-queue-callback-preflight-helper"
    ]
}
if landed_input_helper_evidence != expected_landed_input_helper_evidence:
    missing_markers.append("manifest:landed_input_helper_evidence:mismatch")

landed_mmio_helper_evidence = manifest.get("landed_mmio_helper_evidence")
expected_landed_mmio_helper_evidence = {
    "zigux/tests/phase10_virtio_mmio_manifest.json": [
        "phase10-mmio-register-window-helper",
        "phase10-mmio-queue-register-helper",
        "phase10-mmio-queue-notify-helper",
        "phase10-mmio-queue-address-helper",
        "phase10-mmio-config-window-helper",
        "phase10-mmio-config-write-helper",
    ]
}
if landed_mmio_helper_evidence != expected_landed_mmio_helper_evidence:
    missing_markers.append("manifest:landed_mmio_helper_evidence:mismatch")

blocked_transport_gaps = manifest.get("blocked_transport_gaps")
expected_blocked_transport_gaps = {
    "zigux/tests/phase10_virtio_input_manifest.json": "phase10-virtio-input-registration-lifecycle",
    "zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-lifecycle-and-irq-paths"
}
if blocked_transport_gaps != expected_blocked_transport_gaps:
    missing_markers.append("manifest:blocked_transport_gaps:mismatch")
for gap in core_manifest.get("gaps", []):
    if isinstance(gap, dict) and gap.get("id") == "phase10-config-generation-summary-helper":
        if gap.get("status") != "starter_landed":
            missing_markers.append("phase10_virtio_core_manifest:phase10-config-generation-summary-helper:starter_landed")
for gap in ring_manifest.get("gaps", []):
    if isinstance(gap, dict):
        why_now = gap.get("why_now")
        if isinstance(why_now, str) and "queue-wrapper gap" in why_now:
            missing_markers.append("phase10_virtio_ring_manifest:stale_marker:queue-wrapper gap")


def validate_lane_manifest(phase_manifest: object, lane_name: str) -> None:
    if not isinstance(phase_manifest, dict):
        missing_markers.append(f"{lane_name}:expected_object")
        return
    if phase_manifest.get("phase") != "Phase 10":
        missing_markers.append(f"{lane_name}:phase=Phase 10")
    anchor = phase_manifest.get("anchor")
    if not isinstance(anchor, str) or not anchor.startswith("drivers/virtio/"):
        missing_markers.append(f"{lane_name}:anchor=drivers/virtio/*")
    if anchor in expected_freeze_in_c_anchors or anchor in expected_study_only_anchors:
        missing_markers.append(f"{lane_name}:anchor:freeze_map_overlap")
    if phase_manifest.get("roadmap_destinations") != expected_allowed_roadmap_destinations:
        missing_markers.append(f"{lane_name}:roadmap_destinations:mismatch")


def has_gap_status(phase_manifest: object, gap_id: str, status: str) -> bool:
    if not isinstance(phase_manifest, dict):
        return False
    gaps = phase_manifest.get("gaps")
    if not isinstance(gaps, list):
        return False
    for gap in gaps:
        if not isinstance(gap, dict):
            continue
        if gap.get("id") == gap_id and gap.get("status") == status:
            return True
    return False


if not has_gap_status(core_manifest, "phase10-config-generation-summary-helper", "starter_landed"):
    missing_markers.append("phase10_virtio_core_manifest:phase10-config-generation-summary-helper:starter_landed")
if not has_gap_status(core_manifest, "phase10-config-delivery-disposition-helper", "starter_landed"):
    missing_markers.append("phase10_virtio_core_manifest:phase10-config-delivery-disposition-helper:starter_landed")
if not has_gap_status(ring_manifest, "phase10-virtqueue-shape-helper", "starter_landed"):
    missing_markers.append("phase10_virtio_ring_manifest:phase10-virtqueue-shape-helper:starter_landed")
if not has_gap_status(ring_manifest, "phase10-used-buffer-polling-helper", "starter_landed"):
    missing_markers.append("phase10_virtio_ring_manifest:phase10-used-buffer-polling-helper:starter_landed")
if not has_gap_status(ring_manifest, "phase10-callback-disable-helper", "starter_landed"):
    missing_markers.append("phase10_virtio_ring_manifest:phase10-callback-disable-helper:starter_landed")
if not has_gap_status(ring_manifest, "phase10-callback-enable-helper", "starter_landed"):
    missing_markers.append("phase10_virtio_ring_manifest:phase10-callback-enable-helper:starter_landed")
if not has_gap_status(ring_manifest, "phase10-callback-enable-prepare-helper", "starter_landed"):
    missing_markers.append("phase10_virtio_ring_manifest:phase10-callback-enable-prepare-helper:starter_landed")
if not has_gap_status(ring_manifest, "phase10-callback-delay-helper", "starter_landed"):
    missing_markers.append("phase10_virtio_ring_manifest:phase10-callback-delay-helper:starter_landed")
if not has_gap_status(ring_manifest, "phase10-notify-prepare-helper", "starter_landed"):
    missing_markers.append("phase10_virtio_ring_manifest:phase10-notify-prepare-helper:starter_landed")
if not has_gap_status(ring_manifest, "phase10-queue-reset-guard-helper", "starter_landed"):
    missing_markers.append("phase10_virtio_ring_manifest:phase10-queue-reset-guard-helper:starter_landed")
if not has_gap_status(ring_manifest, "phase10-queue-reset-helper", "starter_landed"):
    missing_markers.append("phase10_virtio_ring_manifest:phase10-queue-reset-helper:starter_landed")
if not has_gap_status(ring_manifest, "phase10-mmio-register-window-helper", "starter_landed"):
    missing_markers.append("phase10_virtio_ring_manifest:phase10-mmio-register-window-helper:starter_landed")
if not has_gap_status(input_manifest, "phase10-virtio-input-registration-preflight-helper", "starter_landed"):
    missing_markers.append("phase10_virtio_input_manifest:phase10-virtio-input-registration-preflight-helper:starter_landed")
if not has_gap_status(input_manifest, "phase10-virtio-input-queue-callback-preflight-helper", "starter_landed"):
    missing_markers.append("phase10_virtio_input_manifest:phase10-virtio-input-queue-callback-preflight-helper:starter_landed")
if not has_gap_status(input_manifest, "phase10-virtio-input-registration-lifecycle", "blocked_on_risky_transport"):
    missing_markers.append("phase10_virtio_input_manifest:phase10-virtio-input-registration-lifecycle:blocked_on_risky_transport")
if not has_gap_status(mmio_manifest, "phase10-mmio-register-window-helper", "starter_landed"):
    missing_markers.append("phase10_virtio_mmio_manifest:phase10-mmio-register-window-helper:starter_landed")
if not has_gap_status(mmio_manifest, "phase10-mmio-queue-register-helper", "starter_landed"):
    missing_markers.append("phase10_virtio_mmio_manifest:phase10-mmio-queue-register-helper:starter_landed")
if not has_gap_status(mmio_manifest, "phase10-mmio-queue-notify-helper", "starter_landed"):
    missing_markers.append("phase10_virtio_mmio_manifest:phase10-mmio-queue-notify-helper:starter_landed")
if not has_gap_status(mmio_manifest, "phase10-mmio-queue-address-helper", "starter_landed"):
    missing_markers.append("phase10_virtio_mmio_manifest:phase10-mmio-queue-address-helper:starter_landed")
if not has_gap_status(mmio_manifest, "phase10-mmio-config-window-helper", "starter_landed"):
    missing_markers.append("phase10_virtio_mmio_manifest:phase10-mmio-config-window-helper:starter_landed")
if not has_gap_status(mmio_manifest, "phase10-mmio-config-write-helper", "starter_landed"):
    missing_markers.append("phase10_virtio_mmio_manifest:phase10-mmio-config-write-helper:starter_landed")
if not has_gap_status(mmio_manifest, "phase10-mmio-lifecycle-and-irq-paths", "blocked_on_risky_transport"):
    missing_markers.append("phase10_virtio_mmio_manifest:phase10-mmio-lifecycle-and-irq-paths:blocked_on_risky_transport")

validate_lane_manifest(core_manifest, "phase10_virtio_core_manifest")
validate_lane_manifest(ring_manifest, "phase10_virtio_ring_manifest")
validate_lane_manifest(input_manifest, "phase10_virtio_input_manifest")
validate_lane_manifest(mmio_manifest, "phase10_virtio_mmio_manifest")

if missing_markers:
    print("PHASE10_CLOSURE_VALIDATION=fail")
    print("MISSING_PHASE10_CLOSURE_MARKERS_START")
    for marker in missing_markers:
        print(marker)
    print("MISSING_PHASE10_CLOSURE_MARKERS_END")
    sys.exit(1)

print("PHASE10_CLOSURE_VALIDATION=pass")
print(f"PHASE10_CLOSURE_REQUIRED_FILE_COUNT={len(required_files)}")
print(
    "PHASE10_CLOSURE_REQUIRED_MARKER_COUNT="
    f"{len(required_closure_markers) + len(required_freeze_map_markers) + len(required_makefile_markers) + len(required_workflow_markers) + len(required_ledger_markers) + len(required_checklist_markers) + len(required_docs_readme_markers) + len(required_core_survey_test_markers) + len(required_ring_survey_markers) + len(required_ring_survey_test_markers) + len(required_input_survey_test_markers) + len(required_mmio_slice_markers) + len(required_mmio_helper_markers) + len(required_mmio_test_markers) + len(required_mmio_survey_test_markers) + len(required_phase10_build_markers)}"
)
