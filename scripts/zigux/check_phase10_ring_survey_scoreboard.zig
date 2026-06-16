const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_RING_SURVEY_SCOREBOARD_SELF_TEST=pass";

const MANIFEST_TEST_MARKERS = [_][]const u8{
    "RING_SURVEY_REPLAY",
    "RING_MANIFEST",
    "RING_SURVEY_NOTE",
};

const CLOSURE_NOTE_MARKERS = [_][]const u8{
    "RING_SURVEY_REPLAY",
    "RING_MANIFEST",
    "RING_SURVEY_NOTE",
    "virtqueue_wrappers=starter_landed",
};

const RING_PACKET_MARKERS = [_][]const u8{
    "RING_SURVEY_GAP_ID",
    "RING_SURVEY_REPLAY",
    "starter_landed",
    "validation",
};

const RING_SURVEY_REPLAY = [_][]const u8{
    "zigux/tests/phase10_virtio_ring_survey.zig",
};

const RING_SURVEY_GAP_ID = [_][]const u8{
    "phase10-virtio-ring-survey-gate",
};

const RING_SURVEY_NOTE = [_][]const u8{
    "Documentation/zigux/phase10-virtio-ring-survey.md",
};

const RING_MANIFEST = [_][]const u8{
    "zigux/tests/phase10_virtio_ring_manifest.json",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (MANIFEST_TEST_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (CLOSURE_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (RING_PACKET_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (RING_SURVEY_REPLAY) |marker| try guard.requireMarker(text, marker);
    for (RING_SURVEY_GAP_ID) |marker| try guard.requireMarker(text, marker);
    for (RING_SURVEY_NOTE) |marker| try guard.requireMarker(text, marker);
    for (RING_MANIFEST) |marker| try guard.requireMarker(text, marker);
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
