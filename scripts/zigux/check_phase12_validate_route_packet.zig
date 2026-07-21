const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_VALIDATE_ROUTE_PACKET_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "make -C zigux phase12-validate",
    "make -C zigux phase12-smoke",
    "make -C zigux phase12-test",
    "make -C zigux phase12",
    "scripts\zigux/validate_phase12.zig",
    "PHASE12_PACKET_CHECKERS = (",
    "VIRTIO_SCSI_ROLLBACK_COVERAGE_CHECKER_PATH",
    "VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_CHECKER_PATH",
    "make -C zigux phase12-validate",
    "scripts-side support packet",
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
    "- name: Validate current Phase 12 support bundle",
    "run: zig run scripts/zigux/validate_phase12.zig",
    "- name: Run current Phase 12 smoke packet",
    "run: make -C zigux phase12-smoke",
    "- name: Run current Phase 12 shared test packet",
    "run: make -C zigux phase12-test",
    "- name: Run current Phase 12 aggregate route",
    "run: make -C zigux phase12",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "phase12: phase12-smoke phase12-test",
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
