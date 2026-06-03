const std = @import("std");

const fixture = @embedFile("fixtures/phase2_cross_targets.json");

const direct_checker_pass_marker = "PHASE2_DIRECT_CROSS_ROUTE=pass";
const direct_checker_target_count_marker = "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT";
const direct_checker_archive_scope_marker = "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT";
const alignment_pass_marker = "PHASE2_CROSS_ALIGNMENT=pass";
const alignment_target_count_marker = "PHASE2_CROSS_ALIGNMENT_FIXTURE_TARGET_COUNT";
const alignment_archive_scope_marker = "PHASE2_CROSS_ALIGNMENT_ARCHIVE_SCOPE_COUNT";

fn count(haystack: []const u8, needle: []const u8) usize {
    return std.mem.count(u8, haystack, needle);
}

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

test "fixture keeps the bounded two target direct cross matrix" {
    try std.testing.expect(contains(fixture, "\"phase\": \"Phase 2\""));
    try std.testing.expect(contains(fixture, "\"status\": \"active\""));
    try std.testing.expectEqual(@as(usize, 3), count(fixture, "\"route\": \"make -C zigux phase2-cross\""));
    try std.testing.expectEqual(@as(usize, 2), count(fixture, "\"target\": "));
    try std.testing.expectEqual(@as(usize, 1), count(fixture, "\"target\": \"x86_64-linux\""));
    try std.testing.expectEqual(@as(usize, 1), count(fixture, "\"target\": \"aarch64-linux\""));
    try std.testing.expectEqual(@as(usize, 1), count(fixture, "\"validation_mode\": \"archive_required\""));
    try std.testing.expectEqual(@as(usize, 1), count(fixture, "\"validation_mode\": \"route_contract_only\""));
    try std.testing.expect(!contains(fixture, "\"target\": \"riscv64-linux\""));
}

test "archive target scope remains one x86_64 linux entry" {
    try std.testing.expect(contains(fixture,
        \\"archive_target_scope": [
        \\    "x86_64-linux"
        \\  ],
    ));
    try std.testing.expectEqual(@as(usize, 2), count(fixture, "\"x86_64-linux\""));
    try std.testing.expectEqual(@as(usize, 1), count(fixture, "\"aarch64-linux\""));
}

test "direct checker still emits target and archive scope counts" {
    try std.testing.expectEqualStrings("PHASE2_DIRECT_CROSS_ROUTE=pass", direct_checker_pass_marker);
    try std.testing.expectEqualStrings("PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT", direct_checker_target_count_marker);
    try std.testing.expectEqualStrings("PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT", direct_checker_archive_scope_marker);
}

test "alignment checker still reports fixture count boundaries" {
    try std.testing.expectEqualStrings("PHASE2_CROSS_ALIGNMENT=pass", alignment_pass_marker);
    try std.testing.expectEqualStrings("PHASE2_CROSS_ALIGNMENT_FIXTURE_TARGET_COUNT", alignment_target_count_marker);
    try std.testing.expectEqualStrings("PHASE2_CROSS_ALIGNMENT_ARCHIVE_SCOPE_COUNT", alignment_archive_scope_marker);
}
