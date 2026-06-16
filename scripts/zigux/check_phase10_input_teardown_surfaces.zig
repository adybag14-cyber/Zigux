const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_INPUT_TEARDOWN_SURFACES_SELF_TEST=pass";

const FILES = [_][]const u8{
    "Documentation/zigux/phase10-virtio-input-survey.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "scripts/zigux/check_phase10_input_packet.zig",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux/tests/phase10_build.zig",
};

const INPUT_SURVEY_MARKERS = [_][]const u8{
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "the dedicated teardown-preflight helper and replay",
};

const CLOSURE_NOTE_MARKERS = [_][]const u8{
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "scripts/zigux/check_phase10_input_packet.zig",
};

const COMPANION_MARKERS = [_][]const u8{
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "scripts/zigux/check_phase10_input_packet.zig",
    "scripts/zigux/check_phase10_closure_manifest_counts.zig",
};

const INPUT_CHECKER_MARKERS = [_][]const u8{
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "\"phase10-virtio-input-teardown-preflight-tests\"",
};

const BUILD_MARKERS = [_][]const u8{
    "phase10_virtio_input_teardown_preflight_module",
    "\"phase10-virtio-input-teardown-preflight-tests\"",
};

const EVIDENCE_DRIVER = [_][]const u8{
    "drivers/virtio/virtio_input_teardown_preflight.zig",
};

const EVIDENCE_REPLAY = [_][]const u8{
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (FILES) |marker| try guard.requireMarker(text, marker);
    for (INPUT_SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (CLOSURE_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (COMPANION_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (INPUT_CHECKER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EVIDENCE_DRIVER) |marker| try guard.requireMarker(text, marker);
    for (EVIDENCE_REPLAY) |marker| try guard.requireMarker(text, marker);
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
