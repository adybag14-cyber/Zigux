const std = @import("std");
const testing = std.testing;

const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";
const route = "make -C zigux phase2-cross";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectMissing(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn count(haystack: []const u8, needle: []const u8) usize {
    var total: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        total += 1;
        rest = rest[index + needle.len ..];
    }
    return total;
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try testing.expect(earlier_index < later_index);
}

test "phase2 cross fixture exposes the current top level shape" {
    const fixture = try readRepoFile(testing.allocator, fixture_path);
    defer testing.allocator.free(fixture);

    try expectContains(fixture, "\"phase\": \"Phase 2\"");
    try expectContains(fixture, "\"status\": \"active\"");
    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(fixture, "\"archive_target_scope\"");
    try expectContains(fixture, "\"cross_targets\"");
    try expectMissing(fixture, "\"targets\"");
    try expectMissing(fixture, "\"target_count\"");
    try expectMissing(fixture, "\"zig_test_files\"");

    try testing.expectEqual(@as(usize, 1), count(fixture, "\"phase\":"));
    try testing.expectEqual(@as(usize, 1), count(fixture, "\"status\":"));
    try testing.expectEqual(@as(usize, 1), count(fixture, "\"archive_target_scope\""));
    try testing.expectEqual(@as(usize, 1), count(fixture, "\"cross_targets\""));
    try testing.expectEqual(@as(usize, 3), count(fixture, route));

    try expectBefore(fixture, "\"phase\"", "\"status\"");
    try expectBefore(fixture, "\"status\"", "\"route\"");
    try expectBefore(fixture, "\"route\"", "\"archive_target_scope\"");
    try expectBefore(fixture, "\"archive_target_scope\"", "\"cross_targets\"");
}

test "phase2 cross fixture entries keep the required field vocabulary" {
    const fixture = try readRepoFile(testing.allocator, fixture_path);
    defer testing.allocator.free(fixture);

    try testing.expectEqual(@as(usize, 2), count(fixture, "\"target\":"));
    try testing.expectEqual(@as(usize, 2), count(fixture, "\"review_status\":"));
    try testing.expectEqual(@as(usize, 2), count(fixture, "\"validation_mode\":"));
    try testing.expectEqual(@as(usize, 3), count(fixture, "\"route\": \"make -C zigux phase2-cross\""));

    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"review_status\": \"pinned bootstrap archive\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"review_status\": \"route contract only\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
}

test "phase2 cross fixture keeps archive scope aligned with the archive-required entry" {
    const fixture = try readRepoFile(testing.allocator, fixture_path);
    defer testing.allocator.free(fixture);

    try testing.expectEqual(@as(usize, 2), count(fixture, "\"x86_64-linux\""));
    try testing.expectEqual(@as(usize, 1), count(fixture, "\"aarch64-linux\""));
    try testing.expectEqual(@as(usize, 1), count(fixture, "\"validation_mode\": \"archive_required\""));
    try testing.expectEqual(@as(usize, 1), count(fixture, "\"validation_mode\": \"route_contract_only\""));
    try expectMissing(fixture, "\"target\": \"riscv64-linux\"");
    try expectMissing(fixture, "\"validation_mode\": \"archive_optional\"");

    try expectBefore(fixture, "\"archive_target_scope\"", "\"target\": \"x86_64-linux\"");
    try expectBefore(fixture, "\"target\": \"x86_64-linux\"", "\"target\": \"aarch64-linux\"");
}
