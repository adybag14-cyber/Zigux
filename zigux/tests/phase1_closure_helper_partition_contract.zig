const std = @import("std");
const testing = std.testing;

const closure_partition_packet =
    \\## Helper-Local Direct Anchor Reminder
    \\
    \\For `tools/lib/bitmap.zig`, current `master` still justifies a parked helper-local follow-up rather than a reopened closure pass.
    \\
    \\For `tools/lib/find_bit.zig`, current `master` still justifies a parked helper-local follow-up rather than a reopened closure pass.
    \\
    \\For `tools/lib/rbtree.zig`, current `master` still justifies a parked helper-local follow-up rather than a reopened closure pass.
    \\
    \\For `tools/lib/string.zig`, current `master` still justifies a parked helper-local follow-up rather than a reopened closure pass.
    \\
    \\## Shared Replay Parked Helpers
    \\
    \\- `tools/lib/argv_split.zig`
    \\- `tools/lib/cmdline.zig`
    \\- `tools/lib/ctype.zig`
    \\- `tools/lib/hweight.zig`
    \\- `tools/lib/list_sort.zig`
    \\- `tools/lib/slab.zig`
    \\- `tools/lib/str_error_r.zig`
    \\- `tools/lib/vsprintf.zig`
    \\- `tools/lib/zalloc.zig`
    \\
    \\These helpers should only reopen for drift in the committed shared replay packet, the committed helper manifest, or the current reminder surfaces. Do not widen shared-replay helper follow-up into direct-anchor helper work by default.
;

const validator_partition_packet =
    \\EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [
    \\    "tools/lib/argv_split.zig",
    \\    "tools/lib/cmdline.zig",
    \\    "tools/lib/ctype.zig",
    \\    "tools/lib/hweight.zig",
    \\    "tools/lib/list_sort.zig",
    \\    "tools/lib/slab.zig",
    \\    "tools/lib/str_error_r.zig",
    \\    "tools/lib/vsprintf.zig",
    \\    "tools/lib/zalloc.zig",
    \\]
    \\
    \\EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [
    \\    "tools/lib/bitmap.zig",
    \\    "tools/lib/find_bit.zig",
    \\    "tools/lib/rbtree.zig",
    \\    "tools/lib/string.zig",
    \\]
    \\
    \\EXPECTED_LANE_RULE_SUMMARY = (
    \\    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, "
    \\    "while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local "
    \\    "follow-up anchors on current master."
    \\)
    \\
    \\EXPECTED_ANTI_OVERLAP_RULE = (
    \\    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    \\    "shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers "
    \\    "reopen only for their existing helper-local anchors or already-committed shared fixture keys."
    \\)
;

const shared_replay_helpers = [_][]const u8{
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

const direct_anchor_helpers = [_][]const u8{
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, left: []const u8, right: []const u8) !void {
    const left_index = std.mem.indexOf(u8, haystack, left) orelse return error.MissingLeftNeedle;
    const right_index = std.mem.indexOf(u8, haystack, right) orelse return error.MissingRightNeedle;
    try testing.expect(left_index < right_index);
}

test "closure note keeps direct-anchor helpers in the helper-local follow-up bucket" {
    try expectContains(closure_partition_packet, "## Helper-Local Direct Anchor Reminder");

    inline for (direct_anchor_helpers) |helper| {
        try expectContains(closure_partition_packet, helper);
    }

    try expectContains(closure_partition_packet, "current `master` still justifies a parked helper-local follow-up");
    try expectContains(closure_partition_packet, "rather than a reopened closure pass");
    try expectBefore(closure_partition_packet, "tools/lib/bitmap.zig", "tools/lib/find_bit.zig");
    try expectBefore(closure_partition_packet, "tools/lib/find_bit.zig", "tools/lib/rbtree.zig");
    try expectBefore(closure_partition_packet, "tools/lib/rbtree.zig", "tools/lib/string.zig");
}

test "closure note keeps shared-replay helpers parked outside direct-anchor work" {
    try expectContains(closure_partition_packet, "## Shared Replay Parked Helpers");

    inline for (shared_replay_helpers) |helper| {
        try expectContains(closure_partition_packet, helper);
        try expectAbsent(validator_partition_packet, helper ++ " direct-anchor");
    }

    try testing.expectEqual(@as(usize, 9), shared_replay_helpers.len);
    try expectContains(closure_partition_packet, "only reopen for drift in the committed shared replay packet");
    try expectContains(closure_partition_packet, "Do not widen shared-replay helper follow-up into direct-anchor helper work by default");
    try expectBefore(closure_partition_packet, "## Helper-Local Direct Anchor Reminder", "## Shared Replay Parked Helpers");
}

test "closure validator mirrors the same helper partition and anti-overlap rule" {
    try expectContains(validator_partition_packet, "EXPECTED_SHARED_REPLAY_PARKED_HELPERS");
    try expectContains(validator_partition_packet, "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS");

    inline for (shared_replay_helpers) |helper| {
        try expectContains(validator_partition_packet, helper);
    }
    inline for (direct_anchor_helpers) |helper| {
        try expectContains(validator_partition_packet, helper);
    }

    try testing.expectEqual(@as(usize, 13), shared_replay_helpers.len + direct_anchor_helpers.len);
    try expectContains(validator_partition_packet, "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above");
    try expectContains(validator_partition_packet, "bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local");
    try expectContains(validator_partition_packet, "Do not reopen Phase 1 by batching helpers across those two sets in one lane");
    try expectContains(validator_partition_packet, "shared-replay parked helpers reopen only for packet drift");
    try expectContains(validator_partition_packet, "reopen only for their existing helper-local anchors");
    try expectBefore(validator_partition_packet, "EXPECTED_SHARED_REPLAY_PARKED_HELPERS", "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS");
    try expectBefore(validator_partition_packet, "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS", "EXPECTED_LANE_RULE_SUMMARY");
    try expectBefore(validator_partition_packet, "EXPECTED_LANE_RULE_SUMMARY", "EXPECTED_ANTI_OVERLAP_RULE");
}
