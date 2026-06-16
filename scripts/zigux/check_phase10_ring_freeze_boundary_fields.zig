const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_RING_FREEZE_BOUNDARY_FIELDS_SELF_TEST=pass";

const EXPECTED_FREEZE_FIELDS = [_][]const u8{
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

const DRIFT_CASES = [_][]const u8{
    "freeze_status_change_claimed",
    "risky_transport_posture",
    "transport_ready",
    "allowed_evidence_kinds",
    "driver_local_lab_slices",
    "survey_manifests",
    "transport_claims",
    "forbidden_transport_claims",
    "queue_setup_reset_paths",
    "irq_parity",
    "input_registration_lifecycle",
    "probe_remove_lifecycle",
    "architecture_council_reopen_required",
    "architecture_council_reopen_attached",
};

const MANIFEST_PATH = [_][]const u8{
    "zigux/tests/phase10_virtio_ring_manifest.json",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (EXPECTED_FREEZE_FIELDS) |marker| try guard.requireMarker(text, marker);
    for (DRIFT_CASES) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
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
