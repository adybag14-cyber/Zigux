const std = @import("std");
const testing = std.testing;

const checker_source = @embedFile("check-phase1-parity.py");

fn contains(needle: []const u8) bool {
    return std.mem.indexOf(u8, checker_source, needle) != null;
}

fn requireCurrentOutputEnvelope() !void {
    if (!contains("PHASE1_PARITY_SECTION_COUNT")) {
        return error.SkipZigTest;
    }
}

fn indexOfRequired(needle: []const u8) !usize {
    return std.mem.indexOf(u8, checker_source, needle) orelse {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    };
}

test "phase1 parity checker emits stable pass envelope markers" {
    try requireCurrentOutputEnvelope();

    const pass = try indexOfRequired("print(\"PHASE1_PARITY=pass\")");
    const section_count = try indexOfRequired("print(f\"PHASE1_PARITY_SECTION_COUNT={len(EXPECTED_SECTIONS)}\")");
    const helper_count = try indexOfRequired("print(f\"PHASE1_PARITY_HELPER_COUNT={len(EXPECTED_HELPERS)}\")");
    const replay = try indexOfRequired("print(\"PHASE1_PARITY_REPLAY=present\")");
    const blocker_count = try indexOfRequired("print(f\"PHASE1_PARITY_BLOCKER_COUNT={len(EXPECTED_REPLAY_BLOCKER_IDS)}\")");
    const blocker_ids = try indexOfRequired("print(\"PHASE1_PARITY_BLOCKER_IDS=\" + \",\".join(EXPECTED_REPLAY_BLOCKER_IDS))");
    const direct_review_count = try indexOfRequired("print(f\"PHASE1_PARITY_DIRECT_REVIEW_HELPER_COUNT={len(EXPECTED_DIRECT_REVIEW_ANCHOR_HELPERS)}\")");

    try testing.expect(pass < section_count);
    try testing.expect(section_count < helper_count);
    try testing.expect(helper_count < replay);
    try testing.expect(replay < blocker_count);
    try testing.expect(blocker_count < blocker_ids);
    try testing.expect(blocker_ids < direct_review_count);
}

test "phase1 parity checker fail-closes with one issue line per collected issue" {
    try requireCurrentOutputEnvelope();

    const fail_marker = try indexOfRequired("print(\"PHASE1_PARITY=fail\")");
    const issue_loop = try indexOfRequired("for issue in issues:");
    const issue_marker = try indexOfRequired("print(f\"PHASE1_PARITY_ISSUE={issue}\")");

    try testing.expect(fail_marker < issue_loop);
    try testing.expect(issue_loop < issue_marker);
    try testing.expect(!contains("PHASE1_PARITY_INPUT_ISSUES_START"));
    try testing.expect(!contains("PHASE1_PARITY_OUTPUT_ISSUES_START"));
    try testing.expect(!contains("PHASE1_PARITY_KEY_ISSUES_START"));
}

test "phase1 parity output counts stay coupled to live constant rosters" {
    try requireCurrentOutputEnvelope();

    try testing.expect(contains("EXPECTED_SECTIONS = ("));
    try testing.expect(contains("EXPECTED_HELPERS = ("));
    try testing.expect(contains("EXPECTED_REPLAY_BLOCKER_IDS = ("));
    try testing.expect(contains("EXPECTED_DIRECT_REVIEW_ANCHOR_HELPERS = ("));
    try testing.expect(contains("\"phase1_helpers_zig_slab_zero_after_kmalloc\""));
    try testing.expect(contains("\"phase1_helpers_c_harness_missing_c_sources\""));
}
