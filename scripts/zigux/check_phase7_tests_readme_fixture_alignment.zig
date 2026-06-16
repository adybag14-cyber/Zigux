const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_TESTS_README_FIXTURE_ALIGNMENT=pass";
pub const self_test_pass_marker = "PHASE7_TESTS_README_FIXTURE_ALIGNMENT_SELF_TEST=pass";

const REQUIRED_TESTS_README_MARKERS = [_][]const u8{
    "## Phase 7",
    "`zigux/tests/phase7_build.zig`",
    "`zigux/tests/phase7_string_helpers.zig`",
    "`zigux/tests/phase7_cmdline.zig`",
    "`zigux/tests/phase7_argv_split.zig`",
    "`zigux/tests/phase7_argv_split_survey.zig`",
    "`zigux/tests/phase7_argv_split_manifest.json`",
    "`zigux/tests/fixtures/phase7_argv_split_vectors.zig`",
    "`zigux/tests/phase7_rbtree.zig`",
    "`zigux/tests/phase7_rbtree_survey.zig`",
    "`zigux/tests/phase7_rbtree_manifest.json`",
};

const FORBIDDEN_TESTS_README_MARKERS = [_][]const u8{
    "`zigux/tests/fixtures/phase7_string_helpers_escape_vectors.zig`",
    "`zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`",
    "`zigux/tests/fixtures/phase7_rbtree.json`",
    "`zigux/tests/fixtures/phase7_rbtree_c_harness.c`",
};

const REQUIRED_ARGV_SPLIT_SURFACES = [_][]const u8{
    "zigux/tests/phase7_argv_split.zig",
    "zigux/tests/phase7_argv_split_survey.zig",
    "zigux/tests/phase7_argv_split_manifest.json",
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_tests_readme_markers_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_required_tests_readme_markers_path);
    const text_required_tests_readme_markers = try guard.readUtf8File(io, allocator, text_required_tests_readme_markers_path);
    defer allocator.free(text_required_tests_readme_markers);
    for (REQUIRED_TESTS_README_MARKERS) |marker| try guard.requireMarker(text_required_tests_readme_markers, marker);
    const text_forbidden_tests_readme_markers_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_forbidden_tests_readme_markers_path);
    const text_forbidden_tests_readme_markers = try guard.readUtf8File(io, allocator, text_forbidden_tests_readme_markers_path);
    defer allocator.free(text_forbidden_tests_readme_markers);
    for (FORBIDDEN_TESTS_README_MARKERS) |marker| {
        if (std.mem.indexOf(u8, text_forbidden_tests_readme_markers, marker) != null) return guard.GuardError.MissingMarker;
    }
    const text_required_argv_split_surfaces_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_required_argv_split_surfaces_path);
    const text_required_argv_split_surfaces = try guard.readUtf8File(io, allocator, text_required_argv_split_surfaces_path);
    defer allocator.free(text_required_argv_split_surfaces);
    for (REQUIRED_ARGV_SPLIT_SURFACES) |marker| try guard.requireMarker(text_required_argv_split_surfaces, marker);
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
