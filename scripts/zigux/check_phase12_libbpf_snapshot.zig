const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_LIBBPF_SNAPSHOT_SELF_TEST=pass";

const EXPECTED_SNAPSHOT_TRACKED_PATHS = [_][]const u8{
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "Documentation/zigux/phase12-libbpf-verify-shard-note.md",
    "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md",
    "Documentation/zigux/phase12-release-coordination-matrix.md",
};

const EXPECTED_DETERMINISM_TRACKED_PATHS = [_][]const u8{
    "tools/lib/bpf/zigux_segments/pin_path.zig",
};

const REVIEWABILITY_SNAPSHOT_MARKERS = [_][]const u8{
    "test_name",
    "test \"phase12 libbpf reviewability gate keeps the current snapshot anchor exact\"",
    "tracked_file_count_assertion",
    "try std.testing.expectEqual(expected_paths.len, fixture.tracked_file_count);",
    "per_path_assertion",
    "try std.testing.expectEqualStrings(expected_path, file_entry.path);",
    "snapshot_fixture_path",
    "snapshot_determinism_fixture_path",
    "survey_note_path",
    "verify_note_path",
    "heavy_consumer_note_path",
    "release_coordination_note_path",
    "legacy_segment_catalog_path",
    "tools/lib/bpf/zigux_segments/manifest.json",
};

const EXPECTED_READBACK_MODE = [_][]const u8{
    "github-contents-readback",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (EXPECTED_SNAPSHOT_TRACKED_PATHS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_DETERMINISM_TRACKED_PATHS) |marker| try guard.requireMarker(text, marker);
    for (REVIEWABILITY_SNAPSHOT_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_READBACK_MODE) |marker| try guard.requireMarker(text, marker);
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
