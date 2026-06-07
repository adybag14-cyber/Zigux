const std = @import("std");

const checker_source = @embedFile("check-phase1-parity.py");

fn requireContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, checker_source, needle) != null);
}

fn requireOrder(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, checker_source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, checker_source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn requireExactCount(needle: []const u8, expected_count: usize) !void {
    var count: usize = 0;
    var cursor: []const u8 = checker_source;
    while (std.mem.indexOf(u8, cursor, needle)) |index| {
        count += 1;
        cursor = cursor[index + needle.len ..];
    }
    try std.testing.expectEqual(expected_count, count);
}

test "success summary is emitted only after issue collection passes" {
    try requireOrder("issues = collect_issues(root)", "if issues:");
    try requireOrder("if issues:", "return 1");
    try requireOrder("return 1", "print(\"PHASE1_PARITY=pass\")");
    try requireOrder("print(\"PHASE1_PARITY=pass\")", "return 0");
    try requireExactCount("print(\"PHASE1_PARITY=pass\")", 1);
}

test "success summary keeps public counter names tied to live rosters" {
    try requireContains("print(f\"PHASE1_PARITY_SECTION_COUNT={len(EXPECTED_SECTIONS)}\")");
    try requireContains("print(f\"PHASE1_PARITY_HELPER_COUNT={len(EXPECTED_HELPERS)}\")");
    try requireContains("print(f\"PHASE1_PARITY_BLOCKER_COUNT={len(EXPECTED_REPLAY_BLOCKER_IDS)}\")");
    try requireContains("print(f\"PHASE1_PARITY_DIRECT_REVIEW_HELPER_COUNT={len(EXPECTED_DIRECT_REVIEW_ANCHOR_HELPERS)}\")");
    try requireOrder("EXPECTED_SECTIONS = (", "print(f\"PHASE1_PARITY_SECTION_COUNT={len(EXPECTED_SECTIONS)}\")");
    try requireOrder("EXPECTED_HELPERS = (", "print(f\"PHASE1_PARITY_HELPER_COUNT={len(EXPECTED_HELPERS)}\")");
    try requireOrder("EXPECTED_DIRECT_REVIEW_ANCHOR_HELPERS = (", "print(f\"PHASE1_PARITY_DIRECT_REVIEW_HELPER_COUNT={len(EXPECTED_DIRECT_REVIEW_ANCHOR_HELPERS)}\")");
}

test "success summary keeps replay and blocker id lines stable" {
    try requireContains("print(\"PHASE1_PARITY_REPLAY=present\")");
    try requireContains("print(\"PHASE1_PARITY_BLOCKER_IDS=\" + \",\".join(EXPECTED_REPLAY_BLOCKER_IDS))");
    try requireContains("\"phase1_helpers_zig_slab_zero_after_kmalloc\"");
    try requireContains("\"phase1_helpers_c_harness_missing_c_sources\"");
    try requireOrder("print(\"PHASE1_PARITY_REPLAY=present\")", "print(f\"PHASE1_PARITY_BLOCKER_COUNT={len(EXPECTED_REPLAY_BLOCKER_IDS)}\")");
    try requireOrder("print(f\"PHASE1_PARITY_BLOCKER_COUNT={len(EXPECTED_REPLAY_BLOCKER_IDS)}\")", "print(\"PHASE1_PARITY_BLOCKER_IDS=\" + \",\".join(EXPECTED_REPLAY_BLOCKER_IDS))");
}
