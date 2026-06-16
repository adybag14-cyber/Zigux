const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_ARGV_SPLIT_REPO_REALITY_NOTE=pass";
pub const self_test_pass_marker = "PHASE7_ARGV_SPLIT_REPO_REALITY_NOTE_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "# Phase 7 Argv Split Repo Reality Note",
    "Lane key: `P7-L02`",
    "Current directly readable sibling anchors on `master`:",
    "`Documentation/zigux/phase7-rbtree-direct-anchor-note.md`",
    "`Documentation/zigux/phase7-string-helpers-slice.md`",
    "`lib/string_helpers.zig`",
    "`zigux/tests/phase7_string_helpers.zig`",
    "`zigux/tests/phase7_rbtree_survey.zig`",
    "Repo-reality warning for the missing dedicated `argv_split` packet on current `master`:",
    "`Documentation/zigux/phase7-argv-split-slice.md`",
    "`lib/argv_split.zig`",
    "`zigux/tests/phase7_argv_split.zig`",
    "`zigux/tests/phase7_argv_split_survey.zig`",
    "`zigux/tests/phase7_argv_split_manifest.json`",
    "`zigux/tests/fixtures/phase7_argv_split_vectors.zig`",
    "`scripts\\zigux/check_phase7_argv_split_packet.zig`",
    "`scripts\\zigux/validate_phase7.zig`",
    "`zigux/tests/phase7_build.zig`",
    "`zigux/Makefile`",
    "`string_helpers` stays the only directly readable Phase 7 helper implementation packet on current `master`",
    "`cmdline` stays parked under the current Phase 1 helper packet",
    "`rbtree` stays reviewable through the direct anchor note and survey only",
    "do not present the missing dedicated `argv_split` packet or the broader shared Phase 7 control routes as directly readable current-`master` evidence again until a fresh same-lane reread or republish materializes them",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-argv-split-repo-reality-note.md");
    defer allocator.free(text_required_markers_path);
    const text_required_markers = try guard.readUtf8File(io, allocator, text_required_markers_path);
    defer allocator.free(text_required_markers);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text_required_markers, marker);
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
