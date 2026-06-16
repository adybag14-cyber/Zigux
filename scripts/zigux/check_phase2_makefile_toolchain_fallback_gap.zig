const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_MAKEFILE_TOOLCHAIN_FALLBACK_GAP=pass";
pub const self_test_pass_marker = "PHASE2_MAKEFILE_TOOLCHAIN_FALLBACK_GAP_SELF_TEST=pass";

const EXPECTED_FALLBACK_LINE = [_][]const u8{
    "ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))",
};

const EXPECTED_PINNED_LINE = [_][]const u8{
    "ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))",
};

const NOTE_MARKERS = [_][]const u8{
    "**Status: resolved on current `master`.**",
    "zig test scripts/zigux/toolchain_policy.zig",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-validate",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_fallback_line_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_expected_fallback_line_path);
    const text_expected_fallback_line = try guard.readUtf8File(io, allocator, text_expected_fallback_line_path);
    defer allocator.free(text_expected_fallback_line);
    for (EXPECTED_FALLBACK_LINE) |marker| try guard.requireMarker(text_expected_fallback_line, marker);
    const text_expected_pinned_line_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_expected_pinned_line_path);
    const text_expected_pinned_line = try guard.readUtf8File(io, allocator, text_expected_pinned_line_path);
    defer allocator.free(text_expected_pinned_line);
    for (EXPECTED_PINNED_LINE) |marker| try guard.requireMarker(text_expected_pinned_line, marker);
    const text_note_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase2-makefile-toolchain-fallback-gap.md");
    defer allocator.free(text_note_markers_path);
    const text_note_markers = try guard.readUtf8File(io, allocator, text_note_markers_path);
    defer allocator.free(text_note_markers);
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text_note_markers, marker);
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
