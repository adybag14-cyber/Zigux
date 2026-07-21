const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_REVIEW_GUIDE_PACKET_SELF_TEST=pass";

const REQUIRED_ROUTE_MARKERS = [_][]const u8{
    "zig run scripts/zigux/check_phase10_bootstrap_route.zig -- --self-test",
    "zig run scripts/zigux/check_phase10_docs_readme_shared_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase10_docs_readme_shared_packet.zig --",
    "zig run scripts/zigux/check_phase10_core_packet.zig --",
    "zig run scripts/zigux/check_phase10_closure_manifest_counts.zig --",
    "zig run scripts/zigux/validate_phase10.zig",
    "zig run scripts/zigux/validate_phase10_closure.zig",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
};

const REQUIRED_SURFACE_MARKERS = [_][]const u8{
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "scripts/zigux/README.md",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux/tests/phase10_build.zig",
    "zigux/Makefile",
};

const REQUIRED_BOUNDARY_MARKERS = [_][]const u8{
    "queue-local `P10-L10` freeze-boundary packet",
    "bounded `P10-L11` MMIO helper packet",
    "shared Phase 10 packet still read as one validator-first lab bundle",
};

const GUIDE_PATH = [_][]const u8{
    "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_ROUTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_SURFACE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_BOUNDARY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (GUIDE_PATH) |marker| try guard.requireMarker(text, marker);
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
