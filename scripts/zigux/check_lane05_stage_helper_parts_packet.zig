const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "LANE05_STAGE_HELPER_PARTS_PACKET=pass";
pub const self_test_pass_marker = "LANE05_STAGE_HELPER_PARTS_PACKET_SELF_TEST=pass";

const HELPER_MARKERS = [_][]const u8{
    "parser.add_argument(",
    "\"--parts-dir\"",
    "reconstruct_archive_from_parts(",
    "parts_dir=parts_dir,",
    "input_mode == \"parts_dir\"",
    "STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR=",
    "STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=",
};

const README_MARKERS = [_][]const u8{
    ".tar.xz.parts",
    "scripts/zigux/stage_pinned_zig_archive.zig",
    "If the exact archive file is absent but",
};

const WORKFLOW_STEP_MARKERS = [_][]const u8{
    "- name: Check current pinned Zig archive packet",
    "- name: Self-test current staged pinned Zig archive helper",
    "- name: Self-test current Lane 05 stage helper contract checker",
};

const WORKFLOW_LINE_MARKERS = [_][]const u8{
    "run: zig run scripts\\zigux/check_zig_toolchain.zig -- --archive-only --allow-missing",
    "run: zig run scripts/zigux/stage_pinned_zig_archive.zig -- --self-test",
    "run: zig run scripts\\zigux/check_lane05_stage_helper_contract.zig -- --self-test",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_helper_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/stage_pinned_zig_archive.zig");
    defer allocator.free(text_helper_markers_path);
    const text_helper_markers = try guard.readUtf8File(io, allocator, text_helper_markers_path);
    defer allocator.free(text_helper_markers);
    for (HELPER_MARKERS) |marker| try guard.requireMarker(text_helper_markers, marker);
    const text_readme_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/stage_pinned_zig_archive.zig");
    defer allocator.free(text_readme_markers_path);
    const text_readme_markers = try guard.readUtf8File(io, allocator, text_readme_markers_path);
    defer allocator.free(text_readme_markers);
    for (README_MARKERS) |marker| try guard.requireMarker(text_readme_markers, marker);
    const text_workflow_step_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/stage_pinned_zig_archive.zig");
    defer allocator.free(text_workflow_step_markers_path);
    const text_workflow_step_markers = try guard.readUtf8File(io, allocator, text_workflow_step_markers_path);
    defer allocator.free(text_workflow_step_markers);
    for (WORKFLOW_STEP_MARKERS) |marker| try guard.requireMarker(text_workflow_step_markers, marker);
    const text_workflow_line_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/stage_pinned_zig_archive.zig");
    defer allocator.free(text_workflow_line_markers_path);
    const text_workflow_line_markers = try guard.readUtf8File(io, allocator, text_workflow_line_markers_path);
    defer allocator.free(text_workflow_line_markers);
    for (WORKFLOW_LINE_MARKERS) |marker| try guard.requireMarker(text_workflow_line_markers, marker);
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
