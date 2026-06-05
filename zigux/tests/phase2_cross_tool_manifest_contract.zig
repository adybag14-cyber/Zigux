const std = @import("std");

const manifest = @embedFile("fixtures/phase2_tool_manifest.json");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.FirstMarkerMissing;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.SecondMarkerMissing;
    try std.testing.expect(first_index < second_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, haystack[cursor..], needle)) |relative_index| {
        count += 1;
        cursor += relative_index + needle.len;
    }
    return count;
}

test "tool manifest keeps cross route support roster direct and narrow" {
    try requireContains(manifest, "\"cross_route_support\": [");
    try requireContains(manifest, "\"scripts/zigux/check-phase2-cross.py\"");
    try requireContains(manifest, "\"zigux/tests/fixtures/phase2_cross_targets.json\"");
    try requireOrdered(
        manifest,
        "\"scripts/zigux/check-phase2-cross.py\"",
        "\"zigux/tests/fixtures/phase2_cross_targets.json\"",
    );
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(manifest, "\"cross_route_support\": ["));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(manifest, "\"zigux/tests/fixtures/phase2_cross_targets.json\""));
}

test "tool manifest keeps cross checker visible in the shared checker packet" {
    try requireContains(manifest, "\"checkers\": [");
    try requireContains(manifest, "\"scripts/zigux/check-phase2-cross.py\"");
    try requireContains(manifest, "\"scripts/zigux/check-phase2-cross-selftest-alignment.py\"");
    try requireOrdered(
        manifest,
        "\"scripts/zigux/check-phase2-tests-readme-alignment.py\"",
        "\"scripts/zigux/check-phase2-cross.py\"",
    );
    try requireOrdered(
        manifest,
        "\"scripts/zigux/check-phase2-cross.py\"",
        "\"scripts/zigux/check-phase2-cross-selftest-alignment.py\"",
    );
}

test "tool manifest records cross matrix as present evidence, not a repo gap" {
    try requireContains(manifest, "\"repo_reality_gaps\": []");
    try requireContains(manifest, "direct cross-route checker");
    try requireContains(manifest, "phase2_cross_targets fixture");
    try requireContains(manifest, "returned `phase2_cross_targets.json` packet");
    try requireNotContains(manifest, "\"scripts/zigux/check-phase2-cross.py\", \"repo_reality_gaps\"");
    try requireNotContains(manifest, "\"zigux/tests/fixtures/phase2_cross_targets.json\", \"repo_reality_gaps\"");
}
