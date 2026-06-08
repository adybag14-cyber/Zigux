const std = @import("std");

const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";
const checker_path = "scripts/zigux/check-phase2-cross.py";
const route = "make -C zigux phase2-cross";

const ExpectedTarget = struct {
    target: []const u8,
    validation_mode: []const u8,
    review_status: []const u8,
};

const expected_targets = [_]ExpectedTarget{
    .{
        .target = "x86_64-linux",
        .validation_mode = "archive_required",
        .review_status = "pinned bootstrap archive",
    },
    .{
        .target = "aarch64-linux",
        .validation_mode = "route_contract_only",
        .review_status = "route contract only",
    },
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(128 * 1024),
    );
}

fn assertContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn assertNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |index| {
        count += 1;
        offset = index + needle.len;
    }
    return count;
}

fn assertTargetPacket(fixture: []const u8, expected: ExpectedTarget) !void {
    const target_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "\"target\": \"{s}\"",
        .{expected.target},
    );
    defer std.testing.allocator.free(target_marker);

    const review_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "\"review_status\": \"{s}\"",
        .{expected.review_status},
    );
    defer std.testing.allocator.free(review_marker);

    const mode_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "\"validation_mode\": \"{s}\"",
        .{expected.validation_mode},
    );
    defer std.testing.allocator.free(mode_marker);

    try assertContains(fixture, target_marker);
    try assertContains(fixture, review_marker);
    try assertContains(fixture, mode_marker);
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(fixture, target_marker));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(fixture, review_marker));
}

test "phase2 cross review statuses stay tied to validation modes" {
    const fixture = try readRepoFile(std.testing.allocator, fixture_path);
    defer std.testing.allocator.free(fixture);

    try assertContains(fixture, "\"phase\": \"Phase 2\"");
    try assertContains(fixture, "\"status\": \"active\"");
    try assertContains(fixture, "\"route\": \"" ++ route ++ "\"");
    try assertContains(fixture, "\"archive_target_scope\"");
    try assertContains(fixture, "\"x86_64-linux\"");
    try assertContains(fixture, "\"cross_targets\"");
    try std.testing.expectEqual(@as(usize, expected_targets.len), countOccurrences(fixture, "\"review_status\": "));

    for (expected_targets) |expected| {
        try assertTargetPacket(fixture, expected);
    }

    try assertNotContains(fixture, "\"review_status\": \"\"");
    try assertNotContains(fixture, "\"review_status\": \"archive required\"");
    try assertNotContains(fixture, "\"review_status\": \"route_contract_only\"");
    try assertNotContains(fixture, "\"target\": \"riscv64-linux\"");
}

test "direct checker still treats review status as required fixture data" {
    const checker = try readRepoFile(std.testing.allocator, checker_path);
    defer std.testing.allocator.free(checker);

    try assertContains(checker, "review_status = entry.get(\"review_status\")");
    try assertContains(checker, "not isinstance(review_status, str) or not review_status.strip()");
    try assertContains(checker, "INVALID_CROSS_TARGET_ENTRY");
    try assertContains(checker, "{target}:review_status");
}

test "review status vocabulary remains separate from validation mode vocabulary" {
    const fixture = try readRepoFile(std.testing.allocator, fixture_path);
    defer std.testing.allocator.free(fixture);

    const archive_mode_index = std.mem.indexOf(u8, fixture, "\"validation_mode\": \"archive_required\"").?;
    const archive_status_index = std.mem.indexOf(u8, fixture, "\"review_status\": \"pinned bootstrap archive\"").?;
    const route_mode_index = std.mem.indexOf(u8, fixture, "\"validation_mode\": \"route_contract_only\"").?;
    const route_status_index = std.mem.indexOf(u8, fixture, "\"review_status\": \"route contract only\"").?;

    try std.testing.expect(archive_status_index < archive_mode_index);
    try std.testing.expect(route_status_index < route_mode_index);
    try std.testing.expect(!std.mem.eql(u8, "archive_required", "pinned bootstrap archive"));
    try std.testing.expect(!std.mem.eql(u8, "route_contract_only", "route contract only"));
}
