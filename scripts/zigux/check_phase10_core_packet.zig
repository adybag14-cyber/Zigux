const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_CORE_PACKET_SELF_TEST=pass";

const EXPECTED_MANIFEST_FIELDS = [_][]const u8{
    "lane_key",
    "P10-L01",
    "phase",
    "Phase 10",
    "anchor",
    "drivers/virtio/virtio.c",
    "roadmap_destinations",
    "drivers/virtio/*.zig",
    "zigux/kernel/",
    "zigux/helpers/",
    "freeze_map",
    "Documentation/zigux/freeze-map.md",
    "freeze_boundary_status",
    "aligned",
    "freeze_status_change_claimed",
    "risky_transport_posture",
    "blocked_on_risky_transport",
    "allowed_evidence_kinds",
    "driver_local_lab_slices",
    "survey_manifests",
    "shared_validation_gates",
    "forbidden_transport_claims",
    "queue_setup_reset_paths",
    "irq_parity",
    "dma_paths",
    "input_registration_lifecycle",
    "probe_remove_lifecycle",
    "architecture_council_reopen_required",
    "architecture_council_reopen_attached",
};

const EXPECTED_SUMMARY_VALUES = [_][]const u8{
    "preexisting_phase10_test_files",
    "preexisting_phase10_build_present",
    "preexisting_virtio_core_zig_present",
    "preexisting_virtio_core_test_present",
    "preexisting_virtio_core_reset_queue_test_present",
    "preexisting_virtio_driver_id_zig_present",
    "preexisting_virtio_driver_id_test_present",
    "preexisting_virtio_core_slice_note_present",
    "preexisting_virtio_ring_survey_present",
    "preexisting_virtio_input_survey_present",
    "preexisting_virtio_mmio_survey_present",
};

const EXPECTED_GAP_FIELDS = [_][]const u8{
    "phase10-build-gate",
    "kind",
    "validation",
    "status",
    "starter_landed",
    "zigux_destination",
    "zigux/tests/phase10_build.zig",
    "phase10-virtio-core-lab-starter",
    "kind",
    "lab_driver_starter",
    "status",
    "starter_landed",
    "zigux_destination",
    "drivers/virtio/virtio.zig",
    "phase10-virtio-core-lab-gate",
    "kind",
    "validation",
    "status",
    "starter_landed",
    "zigux_destination",
    "zigux/tests/phase10_virtio_core.zig",
    "phase10-virtio-core-reset-queue-gate",
    "kind",
    "validation",
    "status",
    "starter_landed",
    "zigux_destination",
    "zigux/tests/phase10_virtio_core_reset_queue.zig",
    "phase10-virtio-core-slice-note",
    "kind",
    "documentation",
    "status",
    "starter_landed",
    "zigux_destination",
    "Documentation/zigux/phase10-virtio-core-slice.md",
    "phase10-virtio-core-survey-gate",
    "kind",
    "validation",
    "status",
    "starter_landed",
    "zigux_destination",
    "zigux/tests/phase10_virtio_core_survey.zig",
    "phase10-virtio-core-survey-note",
    "kind",
    "documentation",
    "status",
    "starter_landed",
    "zigux_destination",
    "phase10-virtio-core-verify-replay",
    "kind",
    "validation",
    "status",
    "starter_landed",
    "zigux_destination",
    "drivers/virtio/virtio_verify.zig",
    "phase10-queue-shape-bookkeeping-helper",
    "kind",
    "lab_driver_starter",
    "status",
    "starter_landed",
    "zigux_destination",
    "drivers/virtio/virtio.zig",
    "phase10-config-generation-bookkeeping-helper",
    "kind",
    "lab_driver_starter",
    "status",
    "starter_landed",
    "zigux_destination",
    "drivers/virtio/virtio.zig",
    "phase10-interrupt-ack-bookkeeping-helper",
    "kind",
    "lab_driver_starter",
    "status",
    "starter_landed",
    "zigux_destination",
    "drivers/virtio/virtio.zig",
    "phase10-lifecycle-guard-bookkeeping-helper",
    "kind",
    "lab_driver_starter",
    "status",
    "starter_landed",
    "zigux_destination",
    "drivers/virtio/virtio.zig",
    "phase10-driver-validation-narrowing-helper",
    "kind",
    "lab_driver_starter",
    "status",
    "starter_landed",
    "zigux_destination",
    "drivers/virtio/virtio.zig",
    "phase10-core-attribute-summary-helper",
    "kind",
    "lab_driver_starter",
    "status",
    "starter_landed",
    "zigux_destination",
    "drivers/virtio/virtio.zig",
    "phase10-reset-replay-bookkeeping-helper",
    "kind",
    "lab_driver_starter",
    "status",
    "starter_landed",
    "zigux_destination",
    "drivers/virtio/virtio.zig",
    "phase10-core-lab-validation-evidence",
    "kind",
    "validation",
    "status",
    "starter_landed",
    "zigux_destination",
    "phase10-driver-id-helper",
    "kind",
    "lab_driver_starter",
    "status",
    "starter_landed",
    "zigux_destination",
    "drivers/virtio/virtio_driver_id.zig",
    "phase10-driver-id-coverage-disposition-helper",
    "kind",
    "lab_driver_starter",
    "status",
    "starter_landed",
    "zigux_destination",
    "drivers/virtio/virtio_driver_id.zig",
    "phase10-driver-id-review-gate",
    "kind",
    "validation",
    "status",
    "starter_landed",
    "zigux_destination",
    "zigux/tests/phase10_virtio_driver_id.zig",
    "phase10-interrupt-compound-ack-gate",
    "kind",
    "validation",
    "status",
    "starter_landed",
    "zigux_destination",
    "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
    "phase10-core-dual-implementation-bridge",
    "kind",
    "dual_implementation_boundary",
    "status",
    "blocked_on_risky_transport",
    "zigux_destination",
    "drivers/virtio/virtio.zig",
    "phase10-core-probe-remove-lifecycle",
    "kind",
    "lab_driver_starter",
    "status",
    "blocked_on_risky_transport",
    "zigux_destination",
    "drivers/virtio/virtio.zig",
};

const REQUIRED_PATHS = [_][]const u8{
    "lane: `P10-L01`",
    "c11221dc7a68d7511ae1c69d64b3f08528287ed8",
    "## Roadmap helper parity scoreboard",
    "That scoreboard now mirrors the live manifest IDs directly",
    "`drivers/virtio/virtio.zig`",
    "`drivers/virtio/virtio_driver_id.zig`",
    "`drivers/virtio/virtio_verify.zig`",
    "`zigux/tests/phase10_virtio_core.zig`",
    "`zigux/tests/phase10_virtio_core_reset_queue.zig`",
    "`zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`",
    "`zigux/tests/phase10_virtio_driver_id.zig`",
    "`zigux/tests/phase10_virtio_core_survey.zig`",
    "`zigux/tests/phase10_build.zig`",
    "`scripts\zigux/validate_phase10.zig`",
    "`scripts/zigux/check_phase10_core_packet.zig`",
    "phase10-driver-id-helper",
    "phase10-driver-id-coverage-disposition-helper",
    "phase10-core-probe-remove-lifecycle",
    "drivers/virtio/virtio_driver_id.zig",
    "pub fn reviewDriverIdMatch(",
    "pub fn reviewDevice(",
    "test \"phase10 virtio driver id review keeps exact matches explicit\" {",
    "test \"phase10 virtio driver id review keeps wildcard matches and misses distinct\" {",
    "drivers/virtio/virtio_verify.zig",
    "pub fn summarizeDriverModel(",
    "pub fn resetReplayPreservesQueueShape(",
    "test \"phase10 virtio core verify keeps lifecycle checkpoints explicit\" {",
    "test \"phase10 virtio core verify keeps reset replay below transport lifecycle claims\" {",
    "zigux/tests/phase10_build.zig",
    ".name = \"phase10-virtio-core-tests\"",
    ".name = \"phase10-virtio-core-interrupt-compound-ack-tests\"",
    ".name = \"phase10-virtio-core-reset-queue-tests\"",
    ".name = \"phase10-virtio-core-verify-tests\"",
    ".name = \"phase10-virtio-core-survey-tests\"",
    ".name = \"phase10-virtio-driver-id-tests\"",
    "test_step.dependOn(&run_phase10_virtio_core_tests.step);",
    "test_step.dependOn(&run_phase10_virtio_core_interrupt_compound_ack_tests.step);",
    "test_step.dependOn(&run_phase10_virtio_core_reset_queue_tests.step);",
    "test_step.dependOn(&run_phase10_virtio_core_verify_tests.step);",
    "test_step.dependOn(&run_phase10_virtio_core_survey_tests.step);",
    "test_step.dependOn(&run_phase10_virtio_driver_id_tests.step);",
    "zigux/tests/phase10_virtio_core.zig",
    "test \"phase10 virtio core summary replay keeps status and feature bookkeeping reviewable\" {",
    "test \"phase10 virtio core reset replay clears interrupt debt and drops driver readiness\" {",
    "test \"phase10 virtio core driver id replay keeps exact wildcard and unmatched rules reviewable\" {",
    "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
    "test \"phase10 virtio core interrupt compound ack replay keeps queue-used and config-change bits isolated\" {",
    "zigux/tests/phase10_virtio_core_reset_queue.zig",
    "test \"phase10 virtio core reset queue replay drops ready state until queue and status are replayed\" {",
    "test \"phase10 virtio core reset queue replay clears reset-required state\" {",
    "zigux/tests/phase10_virtio_driver_id.zig",
    "test \"phase10 virtio driver id replay keeps exact and wildcard dispositions reviewable\" {",
    "test \"phase10 virtio driver id replay keeps vendor wildcard and no-match paths separate\" {",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "stale guardrail reference drift",
    "can still return `404`",
    "mixed-source verification path",
};

const MANIFEST_PATH = [_][]const u8{
    "zigux/tests/phase10_virtio_core_manifest.json",
};

const SURVEY_NOTE_PATH = [_][]const u8{
    "Documentation/zigux/phase10-virtio-core-survey.md",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (EXPECTED_MANIFEST_FIELDS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_SUMMARY_VALUES) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_GAP_FIELDS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_PATHS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_NOTE_PATH) |marker| try guard.requireMarker(text, marker);
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
