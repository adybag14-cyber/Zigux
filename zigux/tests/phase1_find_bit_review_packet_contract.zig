const std = @import("std");
const packet = @import("phase1_find_bit_review_packet_contract_options");

fn expectOnce(text: []const u8, marker: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, text, marker));
}

fn expectContains(text: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, text, marker) != null);
}

test "find_bit review checker keeps the live packet catalog and fail-closed surfaces" {
    const checker = packet.checker_text;

    try expectOnce(checker, "Guard the Phase 1 find_bit review packet against helper, fixture, and note drift.");
    try expectOnce(checker, "SOURCE_SYMBOLS = [");
    try expectOnce(checker, "HELPER_TEST_ANCHORS = [");
    try expectOnce(checker, "PARITY_FIXTURE_KEYS = [");
    try expectOnce(checker, "FIXTURE_VALUES = {");
    try expectOnce(checker, "MANIFEST_EXPECTED = {");
    try expectOnce(checker, "LANE_MARKERS = [");
    try expectOnce(checker, "CLOSURE_MARKERS = [");
    try expectOnce(checker, "SMOKE_MARKERS = [");
    try expectOnce(checker, "class DuplicateTrackingDict(dict[str, object]):");
    try expectOnce(checker, "def duplicate_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:");
    try expectOnce(checker, "print(\"PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST=pass\")");
    try expectOnce(checker, "print(\"PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST_CASE_COUNT=7\")");
}

test "find_bit review packet pins helper anchors, aliases, and fixture fields" {
    const checker = packet.checker_text;

    const helper_anchors = [_][]const u8{
        "findFirstAndNotBit",
        "findNextAndNotBit",
        "find_next_or_bit",
        "find_next_clump8",
        "findLastBit",
        "test \"single-word next scans honor start masks\"",
        "test \"head-word boundary scans keep the last in-range bit reachable from an inclusive start\"",
        "test \"tail-word boundary scans keep the last in-range bit reachable from an inclusive start\"",
        "test \"single-word tail windows keep the last in-range next matches reachable from an inclusive start\"",
        "test \"tail-word next zero and shared scans skip earlier in-range matches before clamping\"",
        "test \"low-level underscore aliases mirror the primary find helpers, including andnot\"",
        "test \"Linux-style aliases mirror the primary find helpers, including andnot\"",
    };

    for (helper_anchors) |marker| {
        try expectContains(checker, marker);
    }

    const fixture_fields = [_][]const u8{
        "\"bits_per_long\": 64",
        "\"next_after_word\": 66",
        "\"tail_word_inclusive_boundary_contract\"",
        "\"andnot_scan_entrypoint_contract\"",
        "\"tail_word_set_skip_anchor\"",
        "\"tail_word_skip_anchor\"",
        "\"review_packet_summary\"",
        "\"next_safe_step_note\"",
    };

    for (fixture_fields) |marker| {
        try expectContains(checker, marker);
    }
}

test "find_bit review packet stays aligned with closure, lane, fixture, and smoke evidence" {
    try expectOnce(packet.lane_note_text, "PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask");
    try expectOnce(packet.lane_note_text, "or for committed tail-clamped or tail-inclusive-boundary replay drift");
    try expectOnce(packet.closure_note_text, "PHASE1_FIND_BIT_REVIEW_GUARD=zig run scripts/zigux/check_phase1_find_bit_review_packet.zig");
    try expectOnce(packet.closure_note_text, "For `tools/lib/find_bit.zig`, current `master` still justifies a parked helper-local follow-up rather than a reopened closure pass.");

    const manifest_markers = [_][]const u8{
        "\"tools/lib/find_bit.zig\"",
        "\"same_word_start_masks\"",
        "\"tail_word_inclusive_boundary_anchor\"",
        "\"single_word_tail_inclusive_boundary_anchor\"",
        "\"andnot_scan_entrypoints\"",
        "\"tail_word_skip_anchor\"",
        "\"parity_fixture_keys\"",
    };
    for (manifest_markers) |marker| {
        try expectContains(packet.manifest_text, marker);
    }

    const fixture_markers = [_][]const u8{
        "\"find_bit\"",
        "\"inclusive_boundary_next\"",
        "\"tail_clamped_last\"",
    };
    for (fixture_markers) |marker| {
        try expectContains(packet.fixture_text, marker);
    }

    const smoke_markers = [_][]const u8{
        "const word_bits = find_bit.bits_per_long;",
        "find_bit.findFirstBit(&map, nbits)",
        "find_bit.findLastBit(&map, nbits)",
        "test \"phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned\" {",
        "find_bit.findFirstAndNotBit(&tail_lhs, &tail_rhs, nbits)",
        "find_bit._find_next_andnot_bit(&tail_lhs, &tail_rhs, nbits, find_bit.bits_per_long + 4)",
        "find_bit.find_next_clump8(&clump, &clump_map, nbits, find_bit.bits_per_long)",
        "find_bit._find_next_clump8(&clump, &clump_map, nbits, nbits)",
    };
    for (smoke_markers) |marker| {
        try expectContains(packet.smoke_text, marker);
    }
}

test "find_bit review checker self-test keeps drift cases explicit" {
    const checker = packet.checker_text;

    const self_test_cases = [_][]const u8{
        "expect_case(repo, \"missing_helper\"",
        "expect_case(repo, \"missing_symbol\"",
        "expect_case(repo, \"duplicate_anchor\"",
        "expect_case(repo, \"manifest_drift\"",
        "expect_case(repo, \"fixture_drift\"",
        "expect_case(repo, \"manifest_invalid_json\"",
        "expect_case(repo, \"duplicate_fixture_key\"",
        "expect_case(repo, \"missing_smoke\"",
    };

    for (self_test_cases) |marker| {
        try expectOnce(checker, marker);
    }
}
