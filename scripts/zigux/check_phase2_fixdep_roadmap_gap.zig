const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_FIXDEP_ROADMAP_GAP=pass";
pub const self_test_pass_marker = "PHASE2_FIXDEP_ROADMAP_GAP_SELF_TEST=pass";

const SURVEY_MARKERS = [_][]const u8{
    "Lane: `P2-L01`",
    "`scripts/basic/fixdep.c`",
    "`scripts/zigux/fixdep.zig`",
    "`wrapper-first path for parser-heavy tooling`",
    "`selected dual implementations`",
    "commit 11",
    "commit 13",
    "`scripts\\zigux/check_fixdep_diff.zig`",
    "`scripts\\zigux/check_phase2_fixdep_gate.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "live twelve-case fixture packet",
    "`Documentation/zigux/phase2-closure.md`",
    "`zig test scripts/zigux/fixdep.zig`",
    "The current repo does not show a roadmap gap in the core dual-implementation requirement for `fixdep`",
    "The bounded remaining risk is reminder-surface drift, not missing parser work.",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_survey_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase2-fixdep-roadmap-gap-survey.md");
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
