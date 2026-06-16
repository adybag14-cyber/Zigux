const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_DIRECT_ANCHOR_PACKET=pass";
pub const self_test_pass_marker = "PHASE7_DIRECT_ANCHOR_PACKET_SELF_TEST=pass";

const DIRECT_ANCHOR = [_][]const u8{
    "zigux/tests/phase7_rbtree_survey.zig",
};

const TESTS_README_MARKERS = [_][]const u8{
    "Phase 7 review packet",
    "repo-reality warning for the broader Phase 7 rbtree packet:",
    "treat those paths plus the older `make -C zigux phase7-validate` and `make -C zigux phase7` route names as last-known packet members that need fresh reread or re-materialization before they are presented here as shipped direct evidence again",
    "keep the narrower current Phase 7 reminder surface tied to the directly readable `zigux/tests/phase7_rbtree_survey.zig` anchor instead of reconstructing the broader helper packet from older route names alone",
    "leave `string_helpers`, `cmdline`, and `argv_split` follow-through parked until a fresh same-lane reread justifies widening beyond rbtree",
};

const DIRECT_NOTE_MARKERS = [_][]const u8{
    "Broader Phase 7 rbtree packet currently missing on `master`:",
    "Treat those paths plus the older `make -C zigux phase7-validate` and `make -C zigux phase7` route names as last-known packet members that need fresh reread or re-materialization before they are presented as shipped direct evidence.",
    "Leave `string_helpers`, `cmdline`, and `argv_split` follow-through parked until a fresh same-lane reread justifies widening beyond the surviving rbtree anchor.",
};

const SURVEY_MARKERS = [_][]const u8{
    "const active_lane_key = \"P7-L13\";",
    "try std.testing.expectEqualStrings(\"P7-L13\", active_lane_key);",
    "\"repo-reality warning for the broader Phase 7 rbtree packet:\"",
    "\"treat those paths plus the older `make -C zigux phase7-validate` and `make -C zigux phase7` route names as last-known packet members that need fresh reread or re-materialization before they are presented here as shipped direct evidence again\"",
    "\"keep the narrower current Phase 7 reminder surface tied to the directly readable `zigux/tests/phase7_rbtree_survey.zig` anchor instead of reconstructing the broader helper packet from older route names alone\"",
    "\"leave `string_helpers`, `cmdline`, and `argv_split` follow-through parked until a fresh same-lane reread justifies widening beyond rbtree\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_direct_anchor_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_rbtree_survey.zig");
    defer allocator.free(text_direct_anchor_path);
    const text_direct_anchor = try guard.readUtf8File(io, allocator, text_direct_anchor_path);
    defer allocator.free(text_direct_anchor);
    for (DIRECT_ANCHOR) |marker| try guard.requireMarker(text_direct_anchor, marker);
    const text_tests_readme_markers_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_rbtree_survey.zig");
    defer allocator.free(text_tests_readme_markers_path);
    const text_tests_readme_markers = try guard.readUtf8File(io, allocator, text_tests_readme_markers_path);
    defer allocator.free(text_tests_readme_markers);
    for (TESTS_README_MARKERS) |marker| try guard.requireMarker(text_tests_readme_markers, marker);
    const text_direct_note_markers_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_rbtree_survey.zig");
    defer allocator.free(text_direct_note_markers_path);
    const text_direct_note_markers = try guard.readUtf8File(io, allocator, text_direct_note_markers_path);
    defer allocator.free(text_direct_note_markers);
    for (DIRECT_NOTE_MARKERS) |marker| try guard.requireMarker(text_direct_note_markers, marker);
    const text_survey_markers_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_rbtree_survey.zig");
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
