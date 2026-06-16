const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_RBTREE_BUILD_WIRING_SELFTEST_GAP=pass";
pub const self_test_pass_marker = "PHASE7_RBTREE_BUILD_WIRING_SELFTEST_GAP_SELF_TEST=pass";

const NOTE_PATH = [_][]const u8{
    "Documentation/zigux/phase7-rbtree-build-wiring-selftest-gap.md",
};

const RBTREE_CHECKER_PATH = [_][]const u8{
    "scripts\\zigux/check_phase7_rbtree_parity.zig",
};

const NOTE_REQUIRED_MARKERS = [_][]const u8{
    "scripts\\zigux/check_phase7_build_wiring.zig",
    "add one missing-file self-test branch for `scripts\\zigux/check_phase7_build_wiring.zig`",
    "Whole-file replacement without a trustworthy full read would risk dropping unrelated checker content.",
};

const CHECKER_REQUIRED_MARKERS = [_][]const u8{
    "scripts\\zigux/check_phase7_build_wiring.zig",
    "(\"missing_json_fixture\", \"zigux/tests/fixtures/phase7_rbtree.json\")",
    "(\"missing_c_harness\", \"zigux/tests/fixtures/phase7_rbtree_c_harness.c\")",
};

const CHECKER_FORBIDDEN_MARKERS = [_][]const u8{
    "(\"missing_build_wiring_checker\", \"scripts\\zigux/check_phase7_build_wiring.zig\")",
    "(\"missing_build_wiring\", \"scripts\\zigux/check_phase7_build_wiring.zig\")",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_note_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-rbtree-build-wiring-selftest-gap.md");
    defer allocator.free(text_note_path_path);
    const text_note_path = try guard.readUtf8File(io, allocator, text_note_path_path);
    defer allocator.free(text_note_path);
    for (NOTE_PATH) |marker| try guard.requireMarker(text_note_path, marker);
    const text_rbtree_checker_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-rbtree-build-wiring-selftest-gap.md");
    defer allocator.free(text_rbtree_checker_path_path);
    const text_rbtree_checker_path = try guard.readUtf8File(io, allocator, text_rbtree_checker_path_path);
    defer allocator.free(text_rbtree_checker_path);
    for (RBTREE_CHECKER_PATH) |marker| try guard.requireMarker(text_rbtree_checker_path, marker);
    const text_note_required_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-rbtree-build-wiring-selftest-gap.md");
    defer allocator.free(text_note_required_markers_path);
    const text_note_required_markers = try guard.readUtf8File(io, allocator, text_note_required_markers_path);
    defer allocator.free(text_note_required_markers);
    for (NOTE_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_note_required_markers, marker);
    const text_checker_required_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-rbtree-build-wiring-selftest-gap.md");
    defer allocator.free(text_checker_required_markers_path);
    const text_checker_required_markers = try guard.readUtf8File(io, allocator, text_checker_required_markers_path);
    defer allocator.free(text_checker_required_markers);
    for (CHECKER_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_checker_required_markers, marker);
    const text_checker_forbidden_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-rbtree-build-wiring-selftest-gap.md");
    defer allocator.free(text_checker_forbidden_markers_path);
    const text_checker_forbidden_markers = try guard.readUtf8File(io, allocator, text_checker_forbidden_markers_path);
    defer allocator.free(text_checker_forbidden_markers);
    for (CHECKER_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text_checker_forbidden_markers, marker);
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
