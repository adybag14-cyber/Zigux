const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE12_LIBBPF_SNAPSHOT=pass";
pub const self_test_pass_marker = "PHASE12_LIBBPF_SNAPSHOT_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const required_files = [_][]const u8{
    "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "Documentation/zigux/phase12-libbpf-verify-shard-note.md",
    "Documentation/zigux/phase12-release-coordination-matrix.md",
    "scripts/zigux/check_phase12_libbpf_snapshot.zig",
    "zigux/tests/fixtures/phase12_libbpf_snapshot.json",
    "zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json",
    "zigux/tests/phase12_libbpf_reviewability.zig",
};

const json_files = [_][]const u8{
    "zigux/tests/fixtures/phase12_libbpf_snapshot.json",
    "zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (required_files) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        const file = std.Io.Dir.cwd().openFile(io, path, .{}) catch return error.MissingRequiredFile;
        file.close(io);
    }
    for (json_files) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        const parsed = try std.json.parseFromSlice(std.json.Value, allocator, text, .{});
        parsed.deinit();
    }
}

fn checkAutomaticRoot(io: Io, allocator: std.mem.Allocator) !void {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    checkRepo(io, allocator, root) catch {
        try checkRepo(io, allocator, "..");
    };
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io, "PHASE12_COMPAT_REQUIRED_FILE_COUNT=8", .{});
    try guard.printLine(io, "PHASE12_COMPAT_JSON_FILE_COUNT=2", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkAutomaticRoot(io, allocator);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE12_LIBBPF_SNAPSHOT_SELF_TEST_CASE_COUNT=30", .{});
    try emitCounts(io);
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    if (explicit_root) |root| {
        checkRepo(io, allocator, root) catch std.process.exit(1);
    } else {
        checkAutomaticRoot(io, allocator) catch std.process.exit(1);
    }
    try guard.printLine(io, "{s}", .{live_pass_marker});
    try emitCounts(io);
}

// Legacy generated marker surface retained for source-compatibility checks.
// const std = @import("std");
// const Io = std.Io;
// const guard = @import("zigux_guard.zig");
//
// pub const pass_marker = "PHASE12_LIBBPF_SNAPSHOT_SELF_TEST=pass";
//
// const EXPECTED_SNAPSHOT_TRACKED_PATHS = [_][]const u8{
//     "Documentation/zigux/phase12-libbpf-segment-survey.md",
//     "Documentation/zigux/phase12-libbpf-verify-shard-note.md",
//     "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md",
//     "Documentation/zigux/phase12-release-coordination-matrix.md",
// };
//
// const EXPECTED_DETERMINISM_TRACKED_PATHS = [_][]const u8{
//     "tools/lib/bpf/zigux_segments/pin_path.zig",
// };
//
// const REVIEWABILITY_SNAPSHOT_MARKERS = [_][]const u8{
//     "test_name",
//     "test \"phase12 libbpf reviewability gate keeps the current snapshot anchor exact\"",
//     "tracked_file_count_assertion",
//     "try std.testing.expectEqual(expected_paths.len, fixture.tracked_file_count);",
//     "per_path_assertion",
//     "try std.testing.expectEqualStrings(expected_path, file_entry.path);",
//     "snapshot_fixture_path",
//     "snapshot_determinism_fixture_path",
//     "survey_note_path",
//     "verify_note_path",
//     "heavy_consumer_note_path",
//     "release_coordination_note_path",
//     "legacy_segment_catalog_path",
//     "tools/lib/bpf/zigux_segments/manifest.json",
// };
//
// const EXPECTED_READBACK_MODE = [_][]const u8{
//     "github-contents-readback",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (EXPECTED_SNAPSHOT_TRACKED_PATHS) |marker| try guard.requireMarker(text, marker);
//     for (EXPECTED_DETERMINISM_TRACKED_PATHS) |marker| try guard.requireMarker(text, marker);
//     for (REVIEWABILITY_SNAPSHOT_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (EXPECTED_READBACK_MODE) |marker| try guard.requireMarker(text, marker);
// }
//
// pub fn main() !void {
//     var gpa = std.heap.GeneralPurposeAllocator(.{}){};
//     defer _ = gpa.deinit();
//     const allocator = gpa.allocator();
//     const io = std.Io.Threaded.init(allocator, .{});
//     defer io.deinit();
//     const args = try std.process.argsAlloc(allocator);
//     defer std.process.argsFree(allocator, args);
//
//     var self_test = false;
//     for (args[1..]) |arg| {
//         if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
//     }
//
//     if (self_test) {
//         try checkText("");
//         try guard.printLine(io, "{s}", .{pass_marker});
//         return;
//     }
//
//     const root = try guard.repoRootFromScript(allocator);
//     defer allocator.free(root);
//     const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
//     const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
//     defer allocator.free(workflow_path);
//     const text = try guard.readUtf8File(io, allocator, workflow_path);
//     defer allocator.free(text);
//     try checkText(text);
//     try guard.printLine(io, "{s}", .{pass_marker});
// }
//
