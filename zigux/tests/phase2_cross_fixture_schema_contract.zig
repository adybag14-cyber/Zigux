const std = @import("std");

const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";
const local_fixture_path = "fixtures/phase2_cross_targets.json";
const route = "make -C zigux phase2-cross";

const CrossTarget = struct {
    target: []const u8,
    review_status: []const u8,
    validation_mode: []const u8,
    route: []const u8,
};

const CrossFixture = struct {
    phase: []const u8,
    status: []const u8,
    route: []const u8,
    archive_target_scope: []const []const u8,
    cross_targets: []const CrossTarget,
};

fn readFixture(allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        fixture_path,
        allocator,
        .limited(16 * 1024),
    ) catch |err| switch (err) {
        error.FileNotFound => std.Io.Dir.cwd().readFileAlloc(
            io_instance.io(),
            local_fixture_path,
            allocator,
            .limited(16 * 1024),
        ),
        else => err,
    };
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |index| {
        count += 1;
        offset += index + needle.len;
    }
    return count;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    try std.testing.expectEqual(expected, countOccurrences(haystack, needle));
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.FirstMarkerMissing;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.SecondMarkerMissing;
    try std.testing.expect(first_index < second_index);
}

fn expectTarget(
    entry: CrossTarget,
    target: []const u8,
    review_status: []const u8,
    validation_mode: []const u8,
) !void {
    try std.testing.expectEqualStrings(target, entry.target);
    try std.testing.expectEqualStrings(review_status, entry.review_status);
    try std.testing.expectEqualStrings(validation_mode, entry.validation_mode);
    try std.testing.expectEqualStrings(route, entry.route);
}

test "phase2 cross fixture keeps the review schema vocabulary explicit" {
    const fixture_json = try readFixture(std.testing.allocator);
    defer std.testing.allocator.free(fixture_json);

    try expectCount(fixture_json, "\"phase\":", 1);
    try expectCount(fixture_json, "\"status\":", 1);
    try expectCount(fixture_json, "\"route\":", 3);
    try expectCount(fixture_json, "\"archive_target_scope\":", 1);
    try expectCount(fixture_json, "\"cross_targets\":", 1);
    try expectCount(fixture_json, "\"target\":", 2);
    try expectCount(fixture_json, "\"review_status\":", 2);
    try expectCount(fixture_json, "\"validation_mode\":", 2);

    try expectOrdered(fixture_json, "\"phase\":", "\"status\":");
    try expectOrdered(fixture_json, "\"status\":", "\"route\":");
    try expectOrdered(fixture_json, "\"route\":", "\"archive_target_scope\":");
    try expectOrdered(fixture_json, "\"archive_target_scope\":", "\"cross_targets\":");
}

test "phase2 cross fixture keeps the live two-target matrix shape" {
    const fixture_json = try readFixture(std.testing.allocator);
    defer std.testing.allocator.free(fixture_json);

    const parsed = try std.json.parseFromSlice(CrossFixture, std.testing.allocator, fixture_json, .{});
    defer parsed.deinit();

    const fixture = parsed.value;
    try std.testing.expectEqualStrings("Phase 2", fixture.phase);
    try std.testing.expectEqualStrings("active", fixture.status);
    try std.testing.expectEqualStrings(route, fixture.route);
    try std.testing.expectEqual(@as(usize, 1), fixture.archive_target_scope.len);
    try std.testing.expectEqualStrings("x86_64-linux", fixture.archive_target_scope[0]);
    try std.testing.expectEqual(@as(usize, 2), fixture.cross_targets.len);

    try expectTarget(
        fixture.cross_targets[0],
        "x86_64-linux",
        "pinned bootstrap archive",
        "archive_required",
    );
    try expectTarget(
        fixture.cross_targets[1],
        "aarch64-linux",
        "route contract only",
        "route_contract_only",
    );
}

test "phase2 cross fixture keeps archive scope tied to archive-required rows" {
    const fixture_json = try readFixture(std.testing.allocator);
    defer std.testing.allocator.free(fixture_json);

    const parsed = try std.json.parseFromSlice(CrossFixture, std.testing.allocator, fixture_json, .{});
    defer parsed.deinit();

    const fixture = parsed.value;
    var archive_required_count: usize = 0;
    for (fixture.cross_targets) |entry| {
        try std.testing.expectEqualStrings(route, entry.route);
        if (std.mem.eql(u8, entry.validation_mode, "archive_required")) {
            archive_required_count += 1;
            try std.testing.expectEqualStrings(fixture.archive_target_scope[0], entry.target);
        } else {
            try std.testing.expectEqualStrings("route_contract_only", entry.validation_mode);
        }
    }
    try std.testing.expectEqual(fixture.archive_target_scope.len, archive_required_count);

    try expectContains(fixture_json, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture_json, "\"target\": \"aarch64-linux\"");
    try std.testing.expect(std.mem.indexOf(u8, fixture_json, "\"target\": \"riscv64-linux\"") == null);
}
