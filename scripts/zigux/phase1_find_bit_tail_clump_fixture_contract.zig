const std = @import("std");

const fixture_path = "zigux/tests/fixtures/phase1_helpers.json";
const parity_checker_path = "scripts/zigux/check-phase1-parity.py";
const live_fixture_anchor = "\"tail_clump_first\"";
const checker_anchor = "\"tail_clamp_fixture_keys\": (";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(512 * 1024));
}

fn requireLivePhase1Fixture(fixture_json: []const u8) !void {
    if (std.mem.indexOf(u8, fixture_json, live_fixture_anchor) == null) {
        return error.SkipZigTest;
    }
}

fn requireLiveParityChecker(parity_checker: []const u8) !void {
    if (std.mem.indexOf(u8, parity_checker, checker_anchor) == null) {
        return error.SkipZigTest;
    }
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingFixtureMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingFixtureMarker;
    try std.testing.expect(before_index < after_index);
}

test "find_bit tail clump fixture values stay exact" {
    const allocator = std.testing.allocator;
    const fixture_json = try readRepoFile(allocator, fixture_path);
    defer allocator.free(fixture_json);

    try requireLivePhase1Fixture(fixture_json);

    try expectContains(fixture_json,
        \\    "tail_clump_first": 64,
        \\    "tail_clump_first_value": 8,
        \\    "tail_clump_next": 64,
        \\    "tail_clump_next_value": 8,
        \\    "tail_clump_exhausted": 69,
        \\    "tail_clump_exhausted_value": 90
    );
}

test "find_bit tail clump fixture remains inside the find_bit packet" {
    const allocator = std.testing.allocator;
    const fixture_json = try readRepoFile(allocator, fixture_path);
    defer allocator.free(fixture_json);

    try requireLivePhase1Fixture(fixture_json);

    try expectOrdered(fixture_json, "\"find_bit\": {", "\"tail_clump_first\": 64");
    try expectOrdered(fixture_json, "\"tail_clump_exhausted_value\": 90", "\"bitmap\": {");
    try expectOrdered(fixture_json, "\"tail_inclusive_boundary_and\": 68", "\"tail_clump_first\": 64");
}

test "parity checker keeps tail fixture rosters explicit" {
    const allocator = std.testing.allocator;
    const parity_checker = try readRepoFile(allocator, parity_checker_path);
    defer allocator.free(parity_checker);

    try requireLiveParityChecker(parity_checker);

    try expectContains(parity_checker, "\"tail_clamp_fixture_keys\": (");
    try expectContains(parity_checker, "\"tail_inclusive_boundary_fixture_keys\": (");
    try expectContains(parity_checker, "\"tail_clamped_first\",");
    try expectContains(parity_checker, "\"tail_inclusive_boundary_and\",");
    try expectContains(parity_checker, "\"tools/lib/find_bit.zig\"");
}
