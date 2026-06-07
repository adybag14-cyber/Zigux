const std = @import("std");

const testing = std.testing;

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        path,
        testing.allocator,
        .limited(768 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.TestExpectedEqual;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.TestExpectedEqual;
    try testing.expect(earlier_index < later_index);
}

test "closure validator keeps the direct-owner checker in the required Phase 1 packet" {
    const validator = try readRepoFile("scripts/zigux/validate-phase1-closure.py");
    defer testing.allocator.free(validator);
    const closure_note = try readRepoFile("Documentation/zigux/phase1-closure.md");
    defer testing.allocator.free(closure_note);

    try expectContains(validator, "DIRECT_OWNER_CHECKER_REL = Path(\"scripts/zigux/check-phase1-direct-owner-markers.py\")");
    try expectContains(validator, "DIRECT_OWNER_CHECKER_REL,");
    try expectContains(validator, "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py");
    try expectContains(validator, "PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker");

    try expectContains(closure_note, "scripts/zigux/check-phase1-direct-owner-markers.py");
    try expectContains(closure_note, "PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig");
    try expectContains(closure_note, "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py");
    try expectNotContains(closure_note, "PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master");
}

test "direct-owner checker hardens the same four helper families as the lane note" {
    const checker = try readRepoFile("scripts/zigux/check-phase1-direct-owner-markers.py");
    defer testing.allocator.free(checker);

    try expectContains(checker, "EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [");
    try expectContains(checker, "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [");
    try expectContains(checker, "\"tools/lib/bitmap.zig\",");
    try expectContains(checker, "\"tools/lib/find_bit.zig\",");
    try expectContains(checker, "\"tools/lib/rbtree.zig\",");
    try expectContains(checker, "\"tools/lib/string.zig\",");

    try expectContains(checker, "PHASE1_BITMAP_DIRECT_OWNER=bitmap helper-local anchors plus the committed bitmap replay keys it already owns");
    try expectContains(checker, "PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local same-word start-mask");
    try expectContains(checker, "PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias");
    try expectContains(checker, "PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics");
    try expectContains(checker, "PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=");
    try expectContains(checker, "PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=");

    try expectBefore(
        checker,
        "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [",
        "REQUIRED_EXACT_LINES = {",
    );
}

test "lane sequencing publishes exact direct-owner markers and next-safe-step tie breakers" {
    const lane_note = try readRepoFile("Documentation/zigux/phase1-host-helper-lane-sequencing.md");
    defer testing.allocator.free(lane_note);

    try expectContains(lane_note, "scripts/zigux/check-phase1-direct-owner-markers.py");
    try expectContains(lane_note, "PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig");
    try expectContains(lane_note, "PHASE1_LANE_ANTI_OVERLAP_RULE=Do not reopen Phase 1 by batching helpers across those two sets in one lane");
    try expectContains(lane_note, "PHASE1_BITMAP_DIRECT_OWNER=bitmap helper-local anchors plus the committed bitmap replay keys it already owns");
    try expectContains(lane_note, "PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local same-word start-mask");
    try expectContains(lane_note, "PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias");
    try expectContains(lane_note, "PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics");
    try expectContains(lane_note, "PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift");
    try expectContains(lane_note, "PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift");
    try expectContains(lane_note, "PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned");
    try expectContains(lane_note, "PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift");

    try expectBefore(lane_note, "## Direct-Anchor Owner Map", "## Next Bounded Step");
    try expectNotContains(lane_note, "PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/string.zig");
}

test "tests-root reminder keeps direct-owner checker visible without reviving old Phase 1 make routes" {
    const tests_readme = try readRepoFile("zigux/tests/README.md");
    defer testing.allocator.free(tests_readme);
    const manifest = try readRepoFile("zigux/tests/fixtures/phase1_helper_manifest.json");
    defer testing.allocator.free(manifest);

    try expectContains(tests_readme, "scripts/zigux/check-phase1-direct-owner-markers.py");
    try expectContains(tests_readme, "only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig`");
    try expectContains(tests_readme, "older Phase 1 wrapper names remain historical packet members rather than active tests-root proof");

    try expectContains(manifest, "\"direct_anchor_followup_helpers\"");
    try expectContains(manifest, "\"tools/lib/bitmap.zig\"");
    try expectContains(manifest, "\"tools/lib/find_bit.zig\"");
    try expectContains(manifest, "\"tools/lib/rbtree.zig\"");
    try expectContains(manifest, "\"tools/lib/string.zig\"");
    try expectContains(manifest, "\"anti_overlap_rule\"");
    try expectNotContains(tests_readme, "`make -C zigux phase1-validate` as active tests-root proof");
}
