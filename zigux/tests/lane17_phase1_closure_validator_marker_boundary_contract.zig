const std = @import("std");
const config = @import("config");

const ClosureMarker = struct {
    key: []const u8,
    context: []const u8,
};

const closure_only_markers = [_]ClosureMarker{
    .{
        .key = "PHASE1_BITMAP_PARTIAL_XOR_REVIEW=",
        .context = "partial_xor_nbits and partial_xor_masked_values",
    },
    .{
        .key = "PHASE1_BITMAP_COMPLEMENT_TAIL_REVIEW=",
        .context = "complement-tail masking",
    },
    .{
        .key = "PHASE1_FIND_BIT_LINUX_ALIAS_TAIL_REVIEW=",
        .context = "find_next_or_bit tail",
    },
};

const validator_enforced_markers = [_][]const u8{
    "\"bitmap_unit_review\": \"`PHASE1_BITMAP_UNIT_REVIEW=",
    "\"bitmap_empty_unit_review\": \"`PHASE1_BITMAP_EMPTY_UNIT_REVIEW=",
    "\"bitmap_final_partial_word_review\": \"`PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW=",
    "\"bitmap_linux_alias_review\": \"`PHASE1_BITMAP_LINUX_ALIAS_REVIEW=",
    "\"find_bit_review_guard\": \"`PHASE1_FIND_BIT_REVIEW_GUARD=",
    "\"direct_anchor_manifest_gate\": \"`PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=",
};

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, haystack[cursor..], needle)) |offset| {
        count += 1;
        cursor += offset + needle.len;
    }
    return count;
}

fn expectExactlyOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(haystack, needle));
}

fn readFixture(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, std.testing.allocator, .limited(4 * 1024 * 1024));
}

test "closure note keeps helper-review marker boundary visible" {
    const closure_note = try readFixture(config.closure_note_path);
    defer std.testing.allocator.free(closure_note);

    for (closure_only_markers) |marker| {
        try expectExactlyOnce(closure_note, marker.key);
        try std.testing.expect(std.mem.indexOf(u8, closure_note, marker.context) != null);
    }

    const partial_xor_index = std.mem.indexOf(u8, closure_note, closure_only_markers[0].key).?;
    const complement_tail_index = std.mem.indexOf(u8, closure_note, closure_only_markers[1].key).?;
    const find_bit_alias_index = std.mem.indexOf(u8, closure_note, closure_only_markers[2].key).?;

    try std.testing.expect(partial_xor_index < complement_tail_index);
    try std.testing.expect(complement_tail_index < find_bit_alias_index);
}

test "closure validator still owns the core enforced marker roster" {
    const validator = try readFixture(config.validator_path);
    defer std.testing.allocator.free(validator);

    for (validator_enforced_markers) |marker| {
        try expectExactlyOnce(validator, marker);
    }

    try expectExactlyOnce(validator, "EXPECTED_CLOSURE_MARKERS = {");
    try expectExactlyOnce(validator, "FORBIDDEN_CLOSURE_MARKERS = {");
    try expectExactlyOnce(validator, "PHASE1_CLOSURE_VALIDATION=pass");
}

test "validator boundary rejects stale closure-state language" {
    const closure_note = try readFixture(config.closure_note_path);
    defer std.testing.allocator.free(closure_note);
    const validator = try readFixture(config.validator_path);
    defer std.testing.allocator.free(validator);

    try std.testing.expect(std.mem.indexOf(u8, validator, "PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master") != null);
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(closure_note, "PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master"));
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(closure_note, "PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first"));
}
