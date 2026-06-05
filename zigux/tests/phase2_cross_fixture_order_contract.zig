const std = @import("std");
const testing = std.testing;

const fixture = @embedFile("fixtures/phase2_cross_targets.json");

const expected_header =
    \\{
    \\  "phase": "Phase 2",
    \\  "status": "active",
    \\  "route": "make -C zigux phase2-cross",
    \\  "archive_target_scope": [
    \\    "x86_64-linux"
    \\  ],
    \\  "cross_targets": [
;

const expected_archive_target =
    \\    {
    \\      "target": "x86_64-linux",
    \\      "review_status": "pinned bootstrap archive",
    \\      "validation_mode": "archive_required",
    \\      "route": "make -C zigux phase2-cross"
    \\    },
;

const expected_route_only_target =
    \\    {
    \\      "target": "aarch64-linux",
    \\      "review_status": "route contract only",
    \\      "validation_mode": "route_contract_only",
    \\      "route": "make -C zigux phase2-cross"
    \\    }
;

const expected_footer =
    \\  ]
    \\}
    \\
;

fn requireContains(text: []const u8, marker: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, text, marker) != null);
}

fn requireAbsent(text: []const u8, marker: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, text, marker) == null);
}

fn countNeedle(text: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var remaining = text;
    while (std.mem.indexOf(u8, remaining, needle)) |index| {
        count += 1;
        remaining = remaining[index + needle.len ..];
    }
    return count;
}

test "phase2 cross fixture keeps the direct matrix header order" {
    try requireContains(fixture, expected_header);
    try requireContains(fixture, expected_footer);
    try testing.expectEqual(@as(usize, 1), countNeedle(fixture, "\"phase\": \"Phase 2\""));
    try testing.expectEqual(@as(usize, 1), countNeedle(fixture, "\"status\": \"active\""));
    try testing.expectEqual(@as(usize, 3), countNeedle(fixture, "\"route\": \"make -C zigux phase2-cross\""));
    try testing.expectEqual(@as(usize, 1), countNeedle(fixture, "\"archive_target_scope\""));
    try testing.expectEqual(@as(usize, 1), countNeedle(fixture, "\"cross_targets\""));
}

test "phase2 cross fixture keeps archive-backed target before route-only target" {
    const archive_index = std.mem.indexOf(u8, fixture, expected_archive_target) orelse return error.MissingArchiveTarget;
    const route_only_index = std.mem.indexOf(u8, fixture, expected_route_only_target) orelse return error.MissingRouteOnlyTarget;

    try testing.expect(archive_index < route_only_index);
    try testing.expectEqual(@as(usize, 1), countNeedle(fixture, "\"target\": \"x86_64-linux\""));
    try testing.expectEqual(@as(usize, 1), countNeedle(fixture, "\"target\": \"aarch64-linux\""));
    try testing.expectEqual(@as(usize, 1), countNeedle(fixture, "\"validation_mode\": \"archive_required\""));
    try testing.expectEqual(@as(usize, 1), countNeedle(fixture, "\"validation_mode\": \"route_contract_only\""));
}

test "phase2 cross fixture stays in the current two-target review boundary" {
    try requireContains(fixture, "\"review_status\": \"pinned bootstrap archive\"");
    try requireContains(fixture, "\"review_status\": \"route contract only\"");
    try requireAbsent(fixture, "\"target\": \"riscv64-linux\"");
    try requireAbsent(fixture, "\"target_count\"");
    try requireAbsent(fixture, "\"targets\"");
    try requireAbsent(fixture, "\"zig_test_files\"");
    try requireAbsent(fixture, "-musl");
}
