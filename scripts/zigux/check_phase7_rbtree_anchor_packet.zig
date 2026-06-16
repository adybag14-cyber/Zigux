const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_RBTREE_ANCHOR_PACKET=pass";
pub const self_test_pass_marker = "PHASE7_RBTREE_ANCHOR_PACKET_SELF_TEST=pass";

const DIRECT_PACKET = [_][]const u8{
    "zigux/tests/README.md",
    "zigux/tests/phase7_rbtree_survey.zig",
    "scripts\\zigux/check_phase7_rbtree_anchor_packet.zig",
};

const MISSING_BROADER_PACKET = [_][]const u8{
    "Documentation/zigux/phase7-helper-lane-sequencing.md",
    "Documentation/zigux/phase7-rbtree-slice.md",
    "scripts\\zigux/check_phase7_rbtree_parity.zig",
    "zigux/tests/phase7_rbtree.zig",
    "zigux/tests/phase7_rbtree_manifest.json",
    "zigux/tests/fixtures/phase7_rbtree.json",
    "zigux/tests/fixtures/phase7_rbtree_c_harness.c",
    "zigux/tests/phase7_build.zig",
};

const REQUIRED_TESTS_SNIPPETS = [_][]const u8{
    "Phase 7 review packet",
    "* current direct-readback Phase 7 anchor: `zigux/tests/phase7_rbtree_survey.zig`",
    "* repo-reality warning for the broader Phase 7 rbtree packet:",
    "* treat those paths plus the older `make -C zigux phase7-validate` and `make -C zigux phase7` route names as last-known packet members that need fresh reread or re-materialization before they are presented here as shipped direct evidence again",
    "* keep the narrower current Phase 7 reminder surface tied to the directly readable `zigux/tests/phase7_rbtree_survey.zig` anchor instead of reconstructing the broader helper packet from older route names alone",
};

const REQUIRED_SURVEY_SNIPPETS = [_][]const u8{
    "const active_lane_key = \"P7-L13\";",
    "current direct-readback Phase 7 anchor: `zigux/tests/phase7_rbtree_survey.zig`",
    "repo-reality warning for the broader Phase 7 rbtree packet:",
    "keep the narrower current Phase 7 reminder surface tied to the directly readable `zigux/tests/phase7_rbtree_survey.zig` anchor instead of reconstructing the broader helper packet from older route names alone",
    "leave `string_helpers`, `cmdline`, and `argv_split` follow-through parked until a fresh same-lane reread justifies widening beyond rbtree",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_direct_packet_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_direct_packet_path);
    const text_direct_packet = try guard.readUtf8File(io, allocator, text_direct_packet_path);
    defer allocator.free(text_direct_packet);
    for (DIRECT_PACKET) |marker| try guard.requireMarker(text_direct_packet, marker);
    const text_missing_broader_packet_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_missing_broader_packet_path);
    const text_missing_broader_packet = try guard.readUtf8File(io, allocator, text_missing_broader_packet_path);
    defer allocator.free(text_missing_broader_packet);
    for (MISSING_BROADER_PACKET) |marker| try guard.requireMarker(text_missing_broader_packet, marker);
    const text_required_tests_snippets_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_required_tests_snippets_path);
    const text_required_tests_snippets = try guard.readUtf8File(io, allocator, text_required_tests_snippets_path);
    defer allocator.free(text_required_tests_snippets);
    for (REQUIRED_TESTS_SNIPPETS) |marker| try guard.requireMarker(text_required_tests_snippets, marker);
    const text_required_survey_snippets_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_required_survey_snippets_path);
    const text_required_survey_snippets = try guard.readUtf8File(io, allocator, text_required_survey_snippets_path);
    defer allocator.free(text_required_survey_snippets);
    for (REQUIRED_SURVEY_SNIPPETS) |marker| try guard.requireMarker(text_required_survey_snippets, marker);
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
