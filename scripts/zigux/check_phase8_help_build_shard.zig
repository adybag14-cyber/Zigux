const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE8_HELP_BUILD_SHARD=pass";
pub const self_test_pass_marker = "PHASE8_HELP_BUILD_SHARD_SELF_TEST=pass";

const SCRIPT_PATH = [_][]const u8{
    "scripts\\zigux/check_phase8_help_build_shard.zig",
};

const BUILD_PATH = [_][]const u8{
    "zigux/tests/phase8_help_only_build.zig",
};

const REQUIRED_MARKERS__zigux_tests_phase8_help_only_build_zig = [_][]const u8{
    "\"../../tools/lib/subcmd/help.zig\"",
    "\"phase8_help.zig\"",
    "\"phase8-help-only-tests\"",
    "const run_help_tests = b.addRunArtifact(help_tests);",
    "\"Run the focused Phase 8 help-only tests.\"",
    "test_step.dependOn(&run_help_tests.step);",
    "b.default_step.dependOn(test_step);",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_script_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_help_build_shard.zig");
    defer allocator.free(text_script_path_path);
    const text_script_path = try guard.readUtf8File(io, allocator, text_script_path_path);
    defer allocator.free(text_script_path);
    for (SCRIPT_PATH) |marker| try guard.requireMarker(text_script_path, marker);
    const text_build_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_help_build_shard.zig");
    defer allocator.free(text_build_path_path);
    const text_build_path = try guard.readUtf8File(io, allocator, text_build_path_path);
    defer allocator.free(text_build_path);
    for (BUILD_PATH) |marker| try guard.requireMarker(text_build_path, marker);
    const text_required_markers__zigux_tests_phase8_help_only_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase8/help/only/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase8_help_only_build_zig_path);
    const text_required_markers__zigux_tests_phase8_help_only_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase8_help_only_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase8_help_only_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase8_help_only_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase8_help_only_build_zig, marker);
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
