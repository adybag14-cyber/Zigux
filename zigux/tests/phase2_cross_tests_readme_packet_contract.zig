const std = @import("std");
const testing = std.testing;

const tests_readme_path = "zigux/tests/README.md";
const cross_fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

const readme_cross_markers = [_][]const u8{
    "## Phase 2 review packet",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "python3 scripts/zigux/check-phase2-cross.py --self-test",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "make -C zigux phase2-cross",
    "direct cross-route",
    "cross-target fixture packet",
};

const fixture_packet_markers = [_][]const u8{
    "\"phase\": \"Phase 2\"",
    "\"status\": \"active\"",
    "\"route\": \"make -C zigux phase2-cross\"",
    "\"archive_target_scope\"",
    "\"cross_targets\"",
    "\"target\": \"x86_64-linux\"",
    "\"review_status\": \"pinned bootstrap archive\"",
    "\"validation_mode\": \"archive_required\"",
    "\"target\": \"aarch64-linux\"",
    "\"review_status\": \"route contract only\"",
    "\"validation_mode\": \"route_contract_only\"",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, path, allocator, .limited(512 * 1024));
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    return count;
}

fn expectContains(text: []const u8, marker: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, text, marker) != null);
}

fn expectOrdered(text: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, text, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, text, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

test "phase2 tests README keeps the direct cross packet visible" {
    const readme = try readRepoFile(testing.allocator, tests_readme_path);
    defer testing.allocator.free(readme);

    for (readme_cross_markers) |marker| {
        try expectContains(readme, marker);
    }

    try testing.expect(countOccurrences(readme, "scripts/zigux/check-phase2-cross.py") >= 2);
    try expectOrdered(readme, "scripts/zigux/check-phase2-cross.py", "python3 scripts/zigux/check-phase2-cross.py --self-test");
    try expectOrdered(readme, "python3 scripts/zigux/check-phase2-cross.py --self-test", "zigux/tests/fixtures/phase2_cross_targets.json");
}

test "phase2 cross fixture keeps the current two-target archive-scope packet" {
    const fixture = try readRepoFile(testing.allocator, cross_fixture_path);
    defer testing.allocator.free(fixture);

    for (fixture_packet_markers) |marker| {
        try expectContains(fixture, marker);
    }

    try testing.expectEqual(@as(usize, 1), countOccurrences(fixture, "\"target\": \"x86_64-linux\""));
    try testing.expectEqual(@as(usize, 1), countOccurrences(fixture, "\"target\": \"aarch64-linux\""));
    try testing.expectEqual(@as(usize, 1), countOccurrences(fixture, "\"validation_mode\": \"archive_required\""));
    try testing.expectEqual(@as(usize, 1), countOccurrences(fixture, "\"validation_mode\": \"route_contract_only\""));
    try expectOrdered(fixture, "\"archive_target_scope\"", "\"cross_targets\"");
    try expectOrdered(fixture, "\"target\": \"x86_64-linux\"", "\"target\": \"aarch64-linux\"");
}

test "phase2 cross README packet and fixture share the same public route" {
    const readme = try readRepoFile(testing.allocator, tests_readme_path);
    defer testing.allocator.free(readme);
    const fixture = try readRepoFile(testing.allocator, cross_fixture_path);
    defer testing.allocator.free(fixture);

    const route = "make -C zigux phase2-cross";
    try expectContains(readme, route);
    try expectContains(fixture, route);
    try expectContains(readme, "scripts/zigux/check-phase2-cross-selftest-alignment.py");
    try expectContains(readme, "python3 scripts/zigux/check-phase2-cross.py --self-test");
    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
}
