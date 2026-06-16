const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`",
    "rollback-only split machine-checkable",
    "rollback drill: when this packet moves",
    "\"preexisting_phase12_repeated_rollback_gate_present\": false",
    "\"id\": \"phase12-virtio-scsi-repeated-rollback-gate\"",
    "\"status\": \"missing_on_master\"",
    "\"zigux_destination\": \"zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig\"",
    "\"why_now\": \"Current master no longer serves the repeated rollback gate, so post-restore readiness evidence is archival only.\"",
    "try std.testing.expect(!manifest.survey_summary.preexisting_phase12_repeated_rollback_gate_present);",
    "try std.testing.expect(!try pathExists(\"zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig\"));",
    "\"zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig\"",
    "\"expected_absent_paths\"",
    "\"Rollback-only Phase 12 virtio_scsi survey packet\"",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "current `master` now carries `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig` so the second-cycle rollback contract and post-restore readiness stay explicit",
    "\"status\": \"landed_on_master\"",
    "\"why_now\": \"The repeated-rollback gate keeps the second-cycle rollback contract and post-restore readiness explicit without claiming runtime reset execution.\"",
    "try std.testing.expect(try pathExists(\"zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig\"));",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
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
