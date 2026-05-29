const std = @import("std");

const fixture = @embedFile("fixtures/phase2_cross_targets.json");

const route = "make -C zigux phase2-cross";
const archive_target = "x86_64-linux";
const route_contract_target = "aarch64-linux";

fn countNeedle(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

fn requireNeedle(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, fixture, needle) != null);
}

test "phase2 cross target fixture keeps one archive-backed target" {
    try requireNeedle("\"phase\": \"Phase 2\"");
    try requireNeedle("\"status\": \"active\"");
    try requireNeedle("\"archive_target_scope\"");
    try requireNeedle("\"validation_mode\": \"archive_required\"");
    try requireNeedle("\"review_status\": \"pinned bootstrap archive\"");

    try std.testing.expectEqual(@as(usize, 2), countNeedle(fixture, archive_target));
    try std.testing.expectEqual(@as(usize, 1), countNeedle(fixture, "\"validation_mode\": \"archive_required\""));
}

test "phase2 cross target fixture keeps route-contract target explicit" {
    try requireNeedle("\"validation_mode\": \"route_contract_only\"");
    try requireNeedle("\"review_status\": \"route contract only\"");

    try std.testing.expectEqual(@as(usize, 1), countNeedle(fixture, route_contract_target));
    try std.testing.expectEqual(@as(usize, 1), countNeedle(fixture, "\"validation_mode\": \"route_contract_only\""));
}

test "phase2 cross target fixture keeps the shared route on every entry" {
    try std.testing.expectEqual(@as(usize, 3), countNeedle(fixture, route));
    try requireNeedle("\"route\": \"make -C zigux phase2-cross\"");
    try requireNeedle("\"cross_targets\"");
}
