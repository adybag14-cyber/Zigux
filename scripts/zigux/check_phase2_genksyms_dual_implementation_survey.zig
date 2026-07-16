const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_GENKSYMS_SURVEY=pass";
pub const self_test_pass_marker = "PHASE2_GENKSYMS_SURVEY_SELF_TEST=pass";

const SURVEY_MARKERS = [_][]const u8{
    "# Phase 2 genksyms dual-implementation survey",
    "Lane: `P2-L07`",
    "scripts/genksyms/genksyms.c",
    "scripts/zigux/genksyms.zig",
    "selected dual implementations",
    "wrapper-first",
    "scripts/zigux/genksyms_crc.zig",
    "scripts\\zigux/check_genksyms_crc_diff.zig",
    "scripts\\zigux/check_genksyms_bridge.zig",
    "CRC-side tool-plus-checker evidence restored",
    "wrapper bridge and CRC-side dual-implementation evidence both materialized.",
    "Leave this survey parked unless a future reread finds another genksyms-local wording, inventory, or replay drift.",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_survey_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md");
    defer allocator.free(text_survey_markers_path);
    const text_survey_markers = try guard.readUtf8File(io, allocator, text_survey_markers_path);
    defer allocator.free(text_survey_markers);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text_survey_markers, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
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
