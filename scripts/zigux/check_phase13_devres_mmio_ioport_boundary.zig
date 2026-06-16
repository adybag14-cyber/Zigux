const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_DEVRES_MMIO_IOPORT_BOUNDARY_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "SLICE_PATH",
    "SURVEY_PATH",
    "HELPER_PATH",
    "CURRENT_PACKET_CHECKER_PATH",
};

const SLICE_MARKERS = [_][]const u8{
    "helper-local ioport unmap planning",
    "live ioport-unmap execution",
    "`planManagedIoportUnmap(...)` as a helper-local ioport release-match foothold",
    "still-missing live `devm_ioport_unmap()` call remains in the same blocked live-MMIO gap family",
};

const SURVEY_MARKERS = [_][]const u8{
    "helper-local ioport unmap planning",
    "still-missing non-posted wrapper, live ioport-unmap call, and arch-memtype safety gaps",
    "helper-local ioport unmap call planner in `lib/devres.zig`",
    "`.provides_ioport_unmap_call_planning = true`",
    "devm_ioport_unmap(`",
    "blocked `phase13-devres-live-ioport-unmap-call`",
};

const HELPER_REQUIRED_MARKERS = [_][]const u8{
    ".provides_ioport_unmap_call_planning = true",
    ".touches_live_mmio = false",
    "pub fn planManagedIoportUnmap(",
    "release_matches = tracked_address == candidate_address",
};

const CURRENT_PACKET_CHECKER_MARKERS = [_][]const u8{
    "devm_ioport_unmap(",
    "helper_scope:unexpected_marker:devm_ioremap_np(",
    "PHASE13_DEVRES_CURRENT_PACKET=pass",
};

const FORBIDDEN_HELPER_MARKERS = [_][]const u8{
    "devm_ioport_unmap(",
    "devm_ioremap_np(",
    "devm_of_iomap(",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (SLICE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (HELPER_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (CURRENT_PACKET_CHECKER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
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
