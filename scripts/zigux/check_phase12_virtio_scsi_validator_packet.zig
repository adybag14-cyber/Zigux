const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_VIRTIO_SCSI_VALIDATOR_PACKET_SELF_TEST=pass";

const REQUIRED_VIRTIO_SCSI_CHECKERS = [_][]const u8{
    "scripts/zigux/check_phase12_virtio_scsi_packet.zig",
    "scripts/zigux/check_phase12_virtio_scsi_libbpf_boundary.zig",
    "scripts/zigux/check_phase12_virtio_scsi_rollback_coverage.zig",
    "scripts/zigux/check_phase12_virtio_scsi_repeated_rollback_packet.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_VIRTIO_SCSI_CHECKERS) |marker| try guard.requireMarker(text, marker);
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
