const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE1_CLOSURE_VALIDATION=pass";
pub const self_test_pass_marker = "PHASE1_CLOSURE_SELF_TEST=pass";

const EXPECTED_HELPERS = [_][]const u8{
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
};

const EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [_][]const u8{
    "tools/lib/argv_split.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
};

const EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [_][]const u8{
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
};

const EXPECTED_LANE_RULE_SUMMARY = [_][]const u8{
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.",
};

const EXPECTED_ANTI_OVERLAP_RULE = [_][]const u8{
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.",
};

const EXPECTED_MAKEFILE_MARKERS = [_][]const u8{
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig:",
    "phase2-cross:",
    "phase2-genksyms:",
    "phase3-validate:",
    "phase3:",
    "phase4-validate:",
    "phase6-validate:",
    "phase8-validate:",
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
    "phase14-validate:",
};

const FORBIDDEN_MAKEFILE_MARKERS = [_][]const u8{
    "phase1-validate:",
    "phase1-test:",
    "phase1-bench:",
    "phase1:",
};

const DELEGATED_CHECKERS = [_][]const u8{
    "phase1-string-review-packet",
    "phase1-find-bit-review-packet",
    "phase1-rbtree-review-packet",
    "phase1-direct-owner-markers",
    "phase1-direct-anchor-manifest-gate",
    "phase1-route-summary-counts",
    "phase1-find-bit-bench-anchors",
    "phase1-bitmap-direct-anchors",
    "phase1-shared-reminder-packet",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_helpers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(text_expected_helpers_path);
    const text_expected_helpers = try guard.readUtf8File(io, allocator, text_expected_helpers_path);
    defer allocator.free(text_expected_helpers);
    for (EXPECTED_HELPERS) |marker| try guard.requireMarker(text_expected_helpers, marker);
    const text_expected_shared_replay_parked_helpers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(text_expected_shared_replay_parked_helpers_path);
    const text_expected_shared_replay_parked_helpers = try guard.readUtf8File(io, allocator, text_expected_shared_replay_parked_helpers_path);
    defer allocator.free(text_expected_shared_replay_parked_helpers);
    for (EXPECTED_SHARED_REPLAY_PARKED_HELPERS) |marker| try guard.requireMarker(text_expected_shared_replay_parked_helpers, marker);
    const text_expected_direct_anchor_followup_helpers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(text_expected_direct_anchor_followup_helpers_path);
    const text_expected_direct_anchor_followup_helpers = try guard.readUtf8File(io, allocator, text_expected_direct_anchor_followup_helpers_path);
    defer allocator.free(text_expected_direct_anchor_followup_helpers);
    for (EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS) |marker| try guard.requireMarker(text_expected_direct_anchor_followup_helpers, marker);
    const text_expected_lane_rule_summary_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(text_expected_lane_rule_summary_path);
    const text_expected_lane_rule_summary = try guard.readUtf8File(io, allocator, text_expected_lane_rule_summary_path);
    defer allocator.free(text_expected_lane_rule_summary);
    for (EXPECTED_LANE_RULE_SUMMARY) |marker| try guard.requireMarker(text_expected_lane_rule_summary, marker);
    const text_expected_anti_overlap_rule_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(text_expected_anti_overlap_rule_path);
    const text_expected_anti_overlap_rule = try guard.readUtf8File(io, allocator, text_expected_anti_overlap_rule_path);
    defer allocator.free(text_expected_anti_overlap_rule);
    for (EXPECTED_ANTI_OVERLAP_RULE) |marker| try guard.requireMarker(text_expected_anti_overlap_rule, marker);
    const text_expected_makefile_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(text_expected_makefile_markers_path);
    const text_expected_makefile_markers = try guard.readUtf8File(io, allocator, text_expected_makefile_markers_path);
    defer allocator.free(text_expected_makefile_markers);
    for (EXPECTED_MAKEFILE_MARKERS) |marker| try guard.requireMarker(text_expected_makefile_markers, marker);
    const text_forbidden_makefile_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(text_forbidden_makefile_markers_path);
    const text_forbidden_makefile_markers = try guard.readUtf8File(io, allocator, text_forbidden_makefile_markers_path);
    defer allocator.free(text_forbidden_makefile_markers);
    for (FORBIDDEN_MAKEFILE_MARKERS) |marker| {
        if (std.mem.indexOf(u8, text_forbidden_makefile_markers, marker) != null) return guard.GuardError.MissingMarker;
    }
    const text_delegated_checkers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_delegated_checkers_path);
    const text_delegated_checkers = try guard.readUtf8File(io, allocator, text_delegated_checkers_path);
    defer allocator.free(text_delegated_checkers);
    for (DELEGATED_CHECKERS) |marker| try guard.requireMarker(text_delegated_checkers, marker);
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
