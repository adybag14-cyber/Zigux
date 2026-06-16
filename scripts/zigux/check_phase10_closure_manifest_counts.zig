const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_CLOSURE_MANIFEST_COUNTS_SELF_TEST=pass";

const REQUIRED_EXACT_CHECKS = [_][]const u8{
    "zig run scripts/zigux/check_phase10_bootstrap_route.zig --",
    "zig run scripts/zigux/check_phase10_core_packet.zig --",
    "zig run scripts/zigux/check_phase10_shared_freeze_boundary.zig --",
    "zig run scripts/zigux/check_phase10_ring_packet.zig --",
    "zig run scripts/zigux/check_phase10_input_packet.zig --",
    "zig run scripts/zigux/check_phase10_mmio_packet.zig --",
    "zig run scripts/zigux/check_phase10_harness_coverage.zig --",
    "zig run scripts/zigux/check_phase10_tests_readme_core_surfaces.zig --",
    "zig run scripts/zigux/check_phase10_closure_manifest_counts.zig --",
    "zig run validate_phase10.zig",
    "zig run validate_phase10_closure.zig",
    "make -C zigux phase10-validate",
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
};

const REQUIRED_RING_SCOREBOARD_EVIDENCE = [_][]const u8{
    "drivers/virtio/virtio_ring.zig",
    "drivers/virtio/virtio_ring_publish_readiness.zig",
    "drivers/virtio/virtio_ring_registration_summary.zig",
    "drivers/virtio/virtio_ring_used_buffer_poll.zig",
    "zigux/tests/phase10_virtio_ring.zig",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "Documentation/zigux/phase10-virtio-ring-survey.md",
};

const REQUIRED_MMIO_SCOREBOARD_EVIDENCE = [_][]const u8{
    "drivers/virtio/virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "drivers/virtio/virtio_mmio_verify.zig",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
};

const REQUIRED_LAB_VALIDATION_EVIDENCE = [_][]const u8{
    "scripts/zigux/check_phase10_core_packet.zig",
    "scripts/zigux/check_phase10_closure_manifest_counts.zig",
    "scripts\zigux/validate_phase10.zig",
    "scripts\zigux/validate_phase10_closure.zig",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/phase10_virtio_ring_queue_build.zig",
    "zigux/tests/phase10_virtio_ring_queue_build_survey.zig",
    "drivers/virtio/virtio_ring_verify.zig",
    "drivers/virtio/virtio_ring_registration_summary.zig",
    "drivers/virtio/virtio_ring_used_buffer_poll.zig",
    "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig",
    "zigux/tests/phase10_virtio_ring_registration_replay.zig",
    "zigux/tests/phase10_virtio_ring_reset_readiness.zig",
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
};

const REQUIRED_INPUT_LAB_VALIDATION_EVIDENCE = [_][]const u8{
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
};

const REQUIRED_MMIO_LAB_VALIDATION_EVIDENCE = [_][]const u8{
    "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig",
};

const REQUIRED_REFERENCE_SAMPLE_SCOREBOARD_EVIDENCE = [_][]const u8{
    "samples/zigux",
    "zigux/tests/phase5_build.zig",
    "Documentation/zigux/review-checklist.md",
};

const REQUIRED_RUNTIME_STARTER_SCOREBOARD_EVIDENCE = [_][]const u8{
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
    "Documentation/zigux/phase9-runtime-trace-events-survey.md",
    "samples/zigux/runtime_bitmap_loader.zig",
    "samples/zigux/runtime_trace_events.zig",
    "zigux/tests/phase9_build.zig",
    "zigux/kernel/runtime_loader.zig",
    "zigux/tests/runtime_trace_events_manifest.json",
    "zigux/tests/runtime_trace_events_survey.zig",
};

const REQUIRED_CORE_LAB_VALIDATION_EVIDENCE = [_][]const u8{
    "Documentation/zigux/phase10-virtio-core-survey.md",
    "drivers/virtio/virtio_driver_id.zig",
    "zigux/tests/phase10_virtio_driver_id.zig",
    "zigux/tests/phase10_virtio_core.zig",
    "zigux/tests/phase10_virtio_core_reset_queue.zig",
    "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
    "zigux/tests/phase10_virtio_core_survey.zig",
};

const REQUIRED_DUAL_IMPLEMENTATION_SCOREBOARD_EVIDENCE = [_][]const u8{
    "Documentation/zigux/phase10-closure-evidence.md",
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
};

const COUNT_FIELDS = [_][]const u8{
    "doc_count",
    "docs",
    "manifest_count",
    "manifests",
    "driver_count",
    "drivers",
    "test_count",
    "tests",
};

const REQUIRED_SURVEY_LANE_KEYS = [_][]const u8{
    "core",
    "P10-L01",
    "ring",
    "P10-L10",
    "input",
    "P10-L22",
    "mmio",
    "P10-L11",
};

const REQUIRED_SURVEY_COMMITS = [_][]const u8{
    "core",
    "c11221dc7a68d7511ae1c69d64b3f08528287ed8",
    "ring",
    "0aa2db32bcb1c7065850ee3f66ec119b071fbf5c",
    "input",
    "ee789f026f11a0c5c70ded9a868979cdf4f55393",
    "mmio",
    "b53ec2bd507d0b3283486e76acc273b184ad5bf8",
};

const LEDGER_STATUS_FIELDS = [_][]const u8{
    "virtqueue_wrappers",
    "PHASE10_LEDGER_ROADMAP_VIRTQUEUE_WRAPPERS",
    "mmio_wrappers",
    "PHASE10_LEDGER_ROADMAP_MMIO_WRAPPERS",
    "lab_only_driver_validation",
    "PHASE10_LEDGER_ROADMAP_LAB_ONLY_DRIVER_VALIDATION",
    "dual_implementations_for_risky_areas",
    "PHASE10_LEDGER_ROADMAP_DUAL_IMPLEMENTATIONS_FOR_RISKY_AREAS",
};

const LEDGER_EVIDENCE_FIELDS = [_][]const u8{
    "virtqueue_wrappers",
    "PHASE10_LEDGER_SCOREBOARD_VIRTQUEUE_EVIDENCE",
    "mmio_wrappers",
    "PHASE10_LEDGER_SCOREBOARD_MMIO_EVIDENCE",
    "lab_only_driver_validation",
    "PHASE10_LEDGER_SCOREBOARD_LAB_ONLY_DRIVER_VALIDATION_EVIDENCE",
    "dual_implementations_for_risky_areas",
    "PHASE10_LEDGER_SCOREBOARD_DUAL_IMPLEMENTATIONS_EVIDENCE",
};

const REQUIRED_LANDED_CORE_HELPER_EVIDENCE = [_][]const u8{
    "zigux/tests/phase10_virtio_core_manifest.json",
    "phase10-queue-shape-bookkeeping-helper",
    "phase10-config-generation-bookkeeping-helper",
    "phase10-interrupt-ack-bookkeeping-helper",
    "phase10-lifecycle-guard-bookkeeping-helper",
    "phase10-driver-validation-narrowing-helper",
    "phase10-core-attribute-summary-helper",
    "phase10-reset-replay-bookkeeping-helper",
};

const REQUIRED_LANDED_RING_HELPER_EVIDENCE = [_][]const u8{
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "phase10-virtqueue-shape-helper",
    "phase10-used-buffer-polling-helper",
    "phase10-callback-enable-helper",
    "phase10-callback-delay-helper",
    "phase10-notify-prepare-helper",
    "phase10-notification-data-summary-helper",
    "phase10-broken-queue-poll-guard",
    "phase10-queue-publish-readiness-helper",
    "phase10-queue-reset-helper",
    "phase10-queue-reset-readiness-helper",
    "phase10-ring-verify-replay",
    "phase10-virtio-ring-slice-note",
};

const REQUIRED_LANDED_INPUT_HELPER_EVIDENCE = [_][]const u8{
    "zigux/tests/phase10_virtio_input_manifest.json",
    "phase10-virtio-input-capability-setup-helper",
    "phase10-virtio-input-multitouch-slot-helper",
    "phase10-virtio-input-probe-preflight-helper",
    "phase10-virtio-input-teardown-preflight-helper",
    "phase10-virtio-input-teardown-observation-helper",
    "phase10-virtio-input-registration-preflight-helper",
    "phase10-virtio-input-queue-callback-preflight-helper",
    "phase10-virtio-input-status-drain-helper",
};

const REQUIRED_LANDED_MMIO_HELPER_EVIDENCE = [_][]const u8{
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "phase10-virtio-mmio-lab-helper",
    "phase10-mmio-transport-identity-helper",
    "phase10-mmio-probe-preflight-helper",
    "phase10-mmio-selected-queue-readiness-helper",
    "phase10-mmio-interrupt-ack-disposition-helper",
    "phase10-mmio-feature-negotiation-summary-helper",
    "phase10-mmio-config-write-plan-freshness-helper",
    "phase10-mmio-config-write-disposition-helper",
    "phase10-mmio-config-write-apply-observation-helper",
};

const REQUIRED_FOCUSED_HARNESS_REPLAYS = [_][]const u8{
    "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
    "phase10 core interrupt-compound-ack replay",
    "zigux/tests/phase10_virtio_core_reset_queue.zig",
    "phase10 core reset-queue replay",
    "zigux/tests/phase10_virtio_driver_id.zig",
    "phase10 driver-id review path replay",
    "zigux/tests/phase10_virtio_ring.zig",
    "phase10 ring broader replay",
    "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig",
    "phase10 ring notification-data readiness replay",
    "zigux/tests/phase10_virtio_ring_registration_replay.zig",
    "phase10 ring queue-registration replay",
    "drivers/virtio/virtio_ring_registration_summary.zig",
    "phase10 ring registration-summary wrapper replay",
    "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig",
    "phase10 ring prepare-kick idempotence replay",
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "phase10 ring drained-reset reuse replay",
    "zigux/tests/phase10_virtio_ring_reset_readiness.zig",
    "phase10 ring reset-readiness replay",
    "zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig",
    "phase10 ring broken-queue queue-discipline replay",
    "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig",
    "phase10 ring delayed-callback budget replay",
    "zigux/tests/phase10_virtio_ring_queue_build.zig",
    "phase10 ring focused queue-build replay",
    "zigux/tests/phase10_virtio_ring_queue_build_survey.zig",
    "phase10 ring queue-build survey replay",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "phase10 input queue-callback-preflight replay",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "phase10 input status-drain replay",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "phase10 input probe-preflight replay",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "phase10 input registration-preflight replay",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "phase10 input teardown-preflight replay",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "phase10 input teardown-observation replay",
    "zigux/tests/phase10_virtio_mmio.zig",
    "phase10 mmio lab replay",
    "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig",
    "phase10 mmio apply-observation replay",
    "drivers/virtio/virtio_mmio_verify.zig",
    "phase10 mmio wrapper-facing verify replay",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
    "phase10 mmio survey replay",
    "drivers/virtio/virtio_ring_publish_readiness.zig",
    "phase10 ring publish-readiness wrapper replay",
};

const MANIFEST_PATH = [_][]const u8{
    "zigux/tests/phase10_closure_manifest.json",
};

const LEDGER_PATH = [_][]const u8{
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
};

const REQUIRED_CORE_BLOCKED_TRANSPORT_PATH = [_][]const u8{
    "zigux/tests/phase10_virtio_core_manifest.json",
};

const REQUIRED_CORE_BLOCKED_TRANSPORT_GAP = [_][]const u8{
    "phase10-core-probe-remove-lifecycle",
};

const REQUIRED_INPUT_READY_TRANSPORT_PATH = [_][]const u8{
    "zigux/tests/phase10_virtio_input_manifest.json",
};

const REQUIRED_INPUT_READY_TRANSPORT_GAP = [_][]const u8{
    "phase10-virtio-input-registration-lifecycle",
};

const REQUIRED_MMIO_READY_TRANSPORT_PATH = [_][]const u8{
    "zigux/tests/phase10_virtio_mmio_manifest.json",
};

const REQUIRED_MMIO_READY_TRANSPORT_GAP = [_][]const u8{
    "phase10-mmio-lifecycle-and-irq-paths",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_EXACT_CHECKS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_RING_SCOREBOARD_EVIDENCE) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MMIO_SCOREBOARD_EVIDENCE) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_LAB_VALIDATION_EVIDENCE) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_INPUT_LAB_VALIDATION_EVIDENCE) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MMIO_LAB_VALIDATION_EVIDENCE) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_REFERENCE_SAMPLE_SCOREBOARD_EVIDENCE) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_RUNTIME_STARTER_SCOREBOARD_EVIDENCE) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_CORE_LAB_VALIDATION_EVIDENCE) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_DUAL_IMPLEMENTATION_SCOREBOARD_EVIDENCE) |marker| try guard.requireMarker(text, marker);
    for (COUNT_FIELDS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_SURVEY_LANE_KEYS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_SURVEY_COMMITS) |marker| try guard.requireMarker(text, marker);
    for (LEDGER_STATUS_FIELDS) |marker| try guard.requireMarker(text, marker);
    for (LEDGER_EVIDENCE_FIELDS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_LANDED_CORE_HELPER_EVIDENCE) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_LANDED_RING_HELPER_EVIDENCE) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_LANDED_INPUT_HELPER_EVIDENCE) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_LANDED_MMIO_HELPER_EVIDENCE) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_FOCUSED_HARNESS_REPLAYS) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
    for (LEDGER_PATH) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_CORE_BLOCKED_TRANSPORT_PATH) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_CORE_BLOCKED_TRANSPORT_GAP) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_INPUT_READY_TRANSPORT_PATH) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_INPUT_READY_TRANSPORT_GAP) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MMIO_READY_TRANSPORT_PATH) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MMIO_READY_TRANSPORT_GAP) |marker| try guard.requireMarker(text, marker);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const io = std.Io.Threaded.init(allocator, .{});
    defer io.deinit();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        try checkText("");
        try guard.printLine(io, "{s}", .{pass_marker});
        return;
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
    const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(workflow_path);
    const text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(text);
    try checkText(text);
    try guard.printLine(io, "{s}", .{pass_marker});
}
