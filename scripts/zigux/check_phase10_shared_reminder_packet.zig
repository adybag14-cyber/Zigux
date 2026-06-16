const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_SHARED_REMINDER_PACKET_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase10_closure_manifest.json",
};

const REQUIRED_MARKERS = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
    "Self-test current Phase 10 bootstrap route checker",
    "Check current Phase 10 bootstrap route",
    "Validate Phase 10 checker-backed review packet",
    "make -C zigux phase10-validate",
    "Run Phase 10 helper tests",
    "make -C zigux phase10-test",
    "Documentation/zigux/phase10-closure-evidence.md",
    "`PHASE10_STATUS=active`",
    "`PHASE10_RISKY_TRANSPORT_POSTURE=blocked_on_risky_transport`",
    "scripts/zigux/check_phase10_harness_coverage.zig",
    "scripts/zigux/check_phase10_tests_readme_core_surfaces.zig",
    "scripts/zigux/check_phase10_closure_manifest_counts.zig",
    "zigux/tests/phase10_closure_manifest.json",
    "scripts\zigux/validate_phase10.zig",
    "scripts\zigux/validate_phase10_closure.zig",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "phase10-virtio-input-registration-lifecycle",
    "phase10-mmio-lifecycle-and-irq-paths",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "scripts/zigux/check_phase10_harness_coverage.zig",
    "scripts/zigux/check_phase10_tests_readme_core_surfaces.zig",
    "scripts/zigux/check_phase10_closure_manifest_counts.zig",
    "scripts\zigux/validate_phase10.zig",
    "scripts\zigux/validate_phase10_closure.zig",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
    "phase10-virtio-input-registration-lifecycle",
    "phase10-mmio-lifecycle-and-irq-paths",
    "P10-L22",
    "P10-L11",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check_phase10_harness_coverage.zig",
    "Documentation/zigux/phase10-closure-evidence.md",
    "zigux/tests/phase10_closure_manifest.json",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
    "zigux/Makefile",
    "phase10-validate:",
    "scripts/zigux/check_phase10_bootstrap_route.zig",
    "scripts/zigux/check_phase10_shared_freeze_boundary.zig",
    "scripts/zigux/check_phase10_ring_packet.zig",
    "scripts/zigux/check_phase10_input_packet.zig",
    "scripts/zigux/check_phase10_mmio_packet.zig",
    "scripts/zigux/check_phase10_harness_coverage.zig",
    "scripts/zigux/check_phase10_tests_readme_core_surfaces.zig",
    "scripts/zigux/check_phase10_closure_manifest_counts.zig",
    "scripts\zigux/validate_phase10.zig",
    "scripts\zigux/validate_phase10_closure.zig",
    "phase10-test:",
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "phase10: phase10-validate phase10-test",
    "zigux/tests/README.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "scripts/zigux/check_phase10_tests_readme_core_surfaces.zig",
    "scripts/zigux/check_phase10_harness_coverage.zig",
    "scripts\zigux/validate_phase10_closure.zig",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux/tests/phase10_build.zig",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
    "phase10_virtio_input_queue_callback_preflight.zig",
    "phase10_virtio_input_registration_preflight.zig",
    "phase10_virtio_input_status_drain.zig",
    "phase10_virtio_input_teardown_observation.zig",
    "phase10_virtio_mmio_apply_observation_replay.zig",
    "build.phase10_virtio_mmio_apply_observation_replay.zig",
    "zigux/tests/phase10_closure_manifest.json",
    "\"phase\": \"Phase 10\"",
    "\"status\": \"active\"",
    "\"tranche\": \"virtio-lab-bundle\"",
    "\"risky_transport_posture\": \"blocked_on_risky_transport\"",
    "\"core\": \"P10-L01\"",
    "\"ring\": \"P10-L10\"",
    "\"input\": \"P10-L22\"",
    "\"mmio\": \"P10-L11\"",
    "\"zigux/tests/phase10_virtio_input_manifest.json\": \"phase10-virtio-input-registration-lifecycle\"",
    "\"zigux/tests/phase10_virtio_mmio_manifest.json\": \"phase10-mmio-lifecycle-and-irq-paths\"",
    "\"scripts/zigux/check_phase10_harness_coverage.zig\"",
    "\"scripts/zigux/check_phase10_tests_readme_core_surfaces.zig\"",
    "\"scripts/zigux/check_phase10_closure_manifest_counts.zig\"",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
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
