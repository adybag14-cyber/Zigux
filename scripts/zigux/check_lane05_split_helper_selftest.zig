const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "LANE05_SPLIT_HELPER_SELFTEST=pass";
pub const self_test_pass_marker = "LANE05_SPLIT_HELPER_SELFTEST_SELF_TEST=pass";

const HELPER_MARKERS = [_][]const u8{
    "pub const toolchain_policy_rel = stage.toolchain_policy_rel;",
    "pub const default_chunk_bytes: usize = 786_432;",
    "pub const self_test_pass_marker = \"SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass\";",
    "pub const self_test_case_count_prefix = \"SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT=\";",
    "const stage = @import(\"stage_pinned_zig_archive.zig\");",
    "pub fn splitArchive(",
    "pub fn reconstructArchive(",
    "output directory must be empty",
    "chunk_bytes must be positive",
    "missing expected shard",
    "expected reconstructed archive to have sha256",
    "invalid base64 shard",
    "self_test_pass_marker",
    "self_test_case_count_prefix",
};

const EXACT_ONCE_MARKERS = [_][]const u8{
    "try printLine(io, \"{s}\", .{self_test_pass_marker});",
    "var tmp = try RuntimeTmp.init(io, allocator, \"pass\");",
};

const WORKFLOW_MARKERS = [_][]const u8{
    "zig run scripts/zigux/split_pinned_zig_archive.zig -- --self-test",
    "zig run scripts/zigux/check_lane05_split_helper_selftest.zig -- --self-test",
    "zig run scripts/zigux/check_lane05_split_helper_workflow.zig -- --self-test",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const helper_path = try guard.joinPath(allocator, root, "scripts/zigux/split_pinned_zig_archive.zig");
    defer allocator.free(helper_path);
    const helper_text = try guard.readUtf8File(io, allocator, helper_path);
    defer allocator.free(helper_text);
    for (HELPER_MARKERS) |marker| try guard.requireMarker(helper_text, marker);
    for (EXACT_ONCE_MARKERS) |marker| try guard.requireMarker(helper_text, marker);

    const workflow_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap-split-helper.yml");
    defer allocator.free(workflow_path);
    const workflow_text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(workflow_text);
    for (WORKFLOW_MARKERS) |marker| try guard.requireMarker(workflow_text, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
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
