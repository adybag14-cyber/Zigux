const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_PERF_BASELINE_VALUES_CHECK=pass";
pub const self_test_pass_marker = "PHASE4_PERF_BASELINE_VALUES_SELF_TEST=pass";

const MANIFEST_MARKERS = [_][]const u8{
    "\"acceptable_limit_iterations\": 4",
    "\"acceptable_limit_sample_count\": 7",
    "\"acceptable_limit_max_elapsed_ns\": 12288",
    "\"sample_count_note\": \"seven monotonic samples\"",
    "\"id\": \"phase4-perf-baseline-bitmap-command-evidence\"",
    "\"iterations\": 1",
    "\"checksum\": 5216946504564592253",
    "\"iterations\": 4",
    "\"checksum\": 7942141539243507472",
    "\"status\": \"shared CI perf promotion pending\"",
    "\"owner\": \"Validation and Perf Team\"",
    "\"coordination_owners\": [\n    \"ABI and Runtime Team\",\n    \"Shared Subsystems Pod\"\n  ]",
};

const SURVEY_MARKERS = [_][]const u8{
    "test \"phase4 perf baseline survey keeps exact local-only iteration and sample counts explicit\" {",
    "try requireMarkerCount(\"\\\"acceptable_limit_iterations\\\": 4\", 2);",
    "try requireMarkerCount(\"\\\"acceptable_limit_sample_count\\\": 7\", 2);",
    "try std.testing.expectEqual(@as(u64, 4), @as(u64, 4));",
    "try std.testing.expectEqual(@as(u64, 7), @as(u64, 7));",
    "\\\"acceptable_limit_max_elapsed_ns\\\": 12288",
    "\\\"checksum\\\": 5216946504564592253",
    "\\\"checksum\\\": 7942141539243507472",
    "\\\"final_first_zero\\\": 109",
    "test \"phase4 perf baseline survey keeps reversible delivery evidence explicit\" {",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_manifest_markers_path = try guard.joinPath(allocator, root, "zigux/tests/phase4_perf_baseline_manifest.json");
    defer allocator.free(text_manifest_markers_path);
    const text_manifest_markers = try guard.readUtf8File(io, allocator, text_manifest_markers_path);
    defer allocator.free(text_manifest_markers);
    for (MANIFEST_MARKERS) |marker| try guard.requireMarker(text_manifest_markers, marker);
    const text_survey_markers_path = try guard.joinPath(allocator, root, "zigux/tests/phase4_perf_baseline_manifest.json");
    defer allocator.free(text_survey_markers_path);
    const text_survey_markers = try guard.readUtf8File(io, allocator, text_survey_markers_path);
    defer allocator.free(text_survey_markers);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text_survey_markers, marker);
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
