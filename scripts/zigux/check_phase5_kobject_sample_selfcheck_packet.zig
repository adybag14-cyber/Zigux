const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE5_KOBJECT_SAMPLE_SELFCHECK_PACKET=pass";
pub const self_test_pass_marker = "PHASE5_KOBJECT_SAMPLE_SELFCHECK_PACKET_SELF_TEST=pass";

const LANE_NOTE_MARKERS = [_][]const u8{
    "Keep `phase5-kobject-example-sample-selfcheck` explicit too as the named shared `zigux/tests/phase5_build.zig` step that reruns the sample-owned `zig test samples/zigux/kobject_example.zig` self-check, so contributor guidance does not leave that owner-side rerun handle buried in the build wiring alone.",
};

const BUILD_MARKERS = [_][]const u8{
    "\"phase5-kobject-example-sample-selfcheck\",",
    "\"Run the Phase 5 kobject example sample-owned self-checks\",",
    "phase5_kobject_example_sample_selfcheck_step.dependOn(",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_lane_note_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-sample-lane-sequencing.md");
    defer allocator.free(text_lane_note_markers_path);
    const text_lane_note_markers = try guard.readUtf8File(io, allocator, text_lane_note_markers_path);
    defer allocator.free(text_lane_note_markers);
    for (LANE_NOTE_MARKERS) |marker| try guard.requireMarker(text_lane_note_markers, marker);
    const text_build_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-sample-lane-sequencing.md");
    defer allocator.free(text_build_markers_path);
    const text_build_markers = try guard.readUtf8File(io, allocator, text_build_markers_path);
    defer allocator.free(text_build_markers);
    for (BUILD_MARKERS) |marker| try guard.requireMarker(text_build_markers, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
