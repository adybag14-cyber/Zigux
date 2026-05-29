const std = @import("std");
const testing = std.testing;

const closure_status_packet =
    \\This note restores the missing Lane 15 closure record in a current-master-safe form.
    \\
    \\## Status
    \\
    \\- `PHASE1_STATUS=parked`
    \\- `PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`
    \\- `PHASE1_HELPER_COUNT=13`
    \\- manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`
    \\- current authority: the committed helper manifest, this closure note, the narrow closure validator, the direct-anchor manifest gate, the shipped bench checker, the shipped shared reminder checker, the live owner-map reminders, and the shared tests-root smoke route remain the trustworthy current-master sources for the closed helper tranche, while the route-summary checker stays an adjacent workflow and Makefile guard.
    \\
    \\The bounded Phase 1 helper tranche is still the same thirteen helper ports named in the committed manifest, but the broader closure-side validator and replay stack is only partially promoted into the narrow current reminder packet on current `master`.
;

const manifest_inventory_packet =
    \\  "phase": "Phase 1",
    \\  "status": "closed",
    \\  "helper_count": 13,
    \\  "helpers": [
    \\    "tools/lib/argv_split.zig",
    \\    "tools/lib/bitmap.zig",
    \\    "tools/lib/cmdline.zig",
    \\    "tools/lib/ctype.zig",
    \\    "tools/lib/find_bit.zig",
    \\    "tools/lib/hweight.zig",
    \\    "tools/lib/list_sort.zig",
    \\    "tools/lib/rbtree.zig",
    \\    "tools/lib/slab.zig",
    \\    "tools/lib/str_error_r.zig",
    \\    "tools/lib/string.zig",
    \\    "tools/lib/vsprintf.zig",
    \\    "tools/lib/zalloc.zig"
    \\  ],
    \\  "lane_sequencing": {
    \\    "shared_replay_parked_helpers": [
    \\      "tools/lib/argv_split.zig",
    \\      "tools/lib/cmdline.zig",
    \\      "tools/lib/ctype.zig",
    \\      "tools/lib/hweight.zig",
    \\      "tools/lib/list_sort.zig",
    \\      "tools/lib/slab.zig",
    \\      "tools/lib/str_error_r.zig",
    \\      "tools/lib/vsprintf.zig",
    \\      "tools/lib/zalloc.zig"
    \\    ],
    \\    "direct_anchor_followup_helpers": [
    \\      "tools/lib/bitmap.zig",
    \\      "tools/lib/find_bit.zig",
    \\      "tools/lib/rbtree.zig",
    \\      "tools/lib/string.zig"
    \\    ],
    \\    "rule_summary": "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.",
    \\    "anti_overlap_rule": "Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys."
    \\  }
;

const helper_roster = [_][]const u8{
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

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, left: []const u8, right: []const u8) !void {
    const left_index = std.mem.indexOf(u8, haystack, left) orelse return error.MissingLeftNeedle;
    const right_index = std.mem.indexOf(u8, haystack, right) orelse return error.MissingRightNeedle;
    try testing.expect(left_index < right_index);
}

test "phase1 closure note status remains parked under docs plus validator authority" {
    try expectContains(closure_status_packet, "This note restores the missing Lane 15 closure record");
    try expectContains(closure_status_packet, "`PHASE1_STATUS=parked`");
    try expectContains(closure_status_packet, "`PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`");
    try expectContains(closure_status_packet, "`PHASE1_HELPER_COUNT=13`");
    try expectContains(closure_status_packet, "zigux/tests/fixtures/phase1_helper_manifest.json");
    try expectContains(closure_status_packet, "the narrow closure validator");
    try expectContains(closure_status_packet, "the shared tests-root smoke route");
    try expectContains(closure_status_packet, "the route-summary checker stays an adjacent workflow and Makefile guard");
    try expectBefore(closure_status_packet, "`PHASE1_STATUS=parked`", "`PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`");
    try expectBefore(closure_status_packet, "`PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`", "`PHASE1_HELPER_COUNT=13`");
}

test "phase1 helper manifest stays closed at the same thirteen helper ports" {
    try expectContains(manifest_inventory_packet, "\"phase\": \"Phase 1\"");
    try expectContains(manifest_inventory_packet, "\"status\": \"closed\"");
    try expectContains(manifest_inventory_packet, "\"helper_count\": 13");

    inline for (helper_roster) |helper| {
        try expectContains(manifest_inventory_packet, helper);
    }

    try testing.expectEqual(@as(usize, 13), helper_roster.len);
}

test "phase1 closure status keeps shared and direct follow-up lanes split" {
    try expectContains(manifest_inventory_packet, "\"shared_replay_parked_helpers\"");
    try expectContains(manifest_inventory_packet, "\"direct_anchor_followup_helpers\"");
    try expectContains(manifest_inventory_packet, "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above");
    try expectContains(manifest_inventory_packet, "bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors");
    try expectContains(manifest_inventory_packet, "Do not reopen Phase 1 by batching helpers across those two sets in one lane");
    try expectContains(manifest_inventory_packet, "shared-replay parked helpers reopen only for packet drift");
    try expectContains(manifest_inventory_packet, "direct-anchor helpers reopen only for their existing helper-local anchors");
    try expectBefore(manifest_inventory_packet, "\"shared_replay_parked_helpers\"", "\"direct_anchor_followup_helpers\"");
    try expectBefore(manifest_inventory_packet, "\"direct_anchor_followup_helpers\"", "\"rule_summary\"");
    try expectBefore(manifest_inventory_packet, "\"rule_summary\"", "\"anti_overlap_rule\"");
}
