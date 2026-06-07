const std = @import("std");

const max_file_size = 1024 * 1024;

const required_validator_markers = [_][]const u8{
    "class DuplicateTrackingDict(dict[str, object]):",
    "self.duplicate_keys: list[str] = []",
    "object_pairs_hook=DuplicateTrackingDict",
    "collect_duplicate_json_key_paths(manifest)",
    "duplicate_json_key",
    "\"duplicate_manifest_helper_count\"",
    "\"duplicate_manifest_lane_rule_summary\"",
    "insert_duplicate_manifest_line(root, '  \"helper_count\": 13,', '  \"helper_count\": 99,')",
    "insert_duplicate_manifest_line(root, f'    \"rule_summary\": \"{EXPECTED_LANE_RULE_SUMMARY}\",', '    \"rule_summary\": \"drifted rule summary\",')",
};

const required_manifest_markers = [_][]const u8{
    "\"phase\": \"Phase 1\"",
    "\"status\": \"closed\"",
    "\"helper_count\": 13",
    "\"lane_sequencing\": {",
    "\"shared_replay_parked_helpers\": [",
    "\"direct_anchor_followup_helpers\": [",
    "\"review_anchors\": {",
    "\"tools/lib/bitmap.zig\": {",
    "\"tools/lib/find_bit.zig\": {",
    "\"tools/lib/rbtree.zig\": {",
    "\"tools/lib/string.zig\": {",
};

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "phase1 closure validator keeps manifest duplicate key detection wired" {
    const allocator = std.testing.allocator;
    const validator = try readFile(allocator, "scripts/zigux/validate-phase1-closure.py");
    defer allocator.free(validator);

    for (required_validator_markers) |marker| {
        try expectContains(validator, marker);
    }

    try expectBefore(
        validator,
        "load_json_with_duplicate_tracking(load_text(root, MANIFEST_REL))",
        "collect_duplicate_json_key_paths(manifest)",
    );
    try expectBefore(
        validator,
        "duplicate_manifest_helper_count",
        "duplicate_manifest_lane_rule_summary",
    );
}

test "phase1 helper manifest remains the closure duplicate key target" {
    const allocator = std.testing.allocator;
    const manifest = try readFile(allocator, "zigux/tests/fixtures/phase1_helper_manifest.json");
    defer allocator.free(manifest);

    for (required_manifest_markers) |marker| {
        try expectContains(manifest, marker);
    }

    try expectBefore(manifest, "\"lane_sequencing\": {", "\"review_anchors\": {");
    try expectBefore(manifest, "\"shared_replay_parked_helpers\": [", "\"direct_anchor_followup_helpers\": [");
}

test "closure validator self test reports duplicate manifest guard coverage" {
    const allocator = std.testing.allocator;
    const validator = try readFile(allocator, "scripts/zigux/validate-phase1-closure.py");
    defer allocator.free(validator);

    try expectContains(validator, "PHASE1_CLOSURE_SELF_TEST=pass");
    try expectContains(validator, "PHASE1_CLOSURE_SELF_TEST_CASE_COUNT=");
    try expectContains(validator, "duplicate_manifest_helper_count");
    try expectContains(validator, "duplicate_manifest_lane_rule_summary");
}
