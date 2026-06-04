const std = @import("std");

const fixture_text =
    \\{
    \\  "phase": "Phase 2",
    \\  "status": "active",
    \\  "route": "make -C zigux phase2-cross",
    \\  "archive_target_scope": [
    \\    "x86_64-linux"
    \\  ],
    \\  "cross_targets": [
    \\    {
    \\      "target": "x86_64-linux",
    \\      "review_status": "pinned bootstrap archive",
    \\      "validation_mode": "archive_required",
    \\      "route": "make -C zigux phase2-cross"
    \\    },
    \\    {
    \\      "target": "aarch64-linux",
    \\      "review_status": "route contract only",
    \\      "validation_mode": "route_contract_only",
    \\      "route": "make -C zigux phase2-cross"
    \\    }
    \\  ]
    \\}
;

const expected_route = "make -C zigux phase2-cross";

fn countNeedle(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    return count;
}

fn mustContainOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countNeedle(haystack, needle));
}

test "phase2 cross matrix keeps exactly one archive-backed target" {
    try mustContainOnce(fixture_text, "\"archive_target_scope\"");
    try std.testing.expectEqual(@as(usize, 2), countNeedle(fixture_text, "\"x86_64-linux\""));
    try mustContainOnce(fixture_text, "\"validation_mode\": \"archive_required\"");
    try mustContainOnce(fixture_text, "\"review_status\": \"pinned bootstrap archive\"");

    try std.testing.expectEqual(@as(usize, 0), countNeedle(fixture_text, "\"riscv64-linux\""));
    try std.testing.expectEqual(@as(usize, 0), countNeedle(fixture_text, "\"validation_mode\": \"archive_optional\""));
}

test "phase2 cross matrix keeps aarch64 as route contract only" {
    try mustContainOnce(fixture_text, "\"aarch64-linux\"");
    try mustContainOnce(fixture_text, "\"validation_mode\": \"route_contract_only\"");
    try mustContainOnce(fixture_text, "\"review_status\": \"route contract only\"");

    const aarch64_index = std.mem.indexOf(u8, fixture_text, "\"aarch64-linux\"").?;
    const route_contract_index = std.mem.indexOf(u8, fixture_text, "\"route_contract_only\"").?;
    try std.testing.expect(route_contract_index > aarch64_index);
}

test "phase2 cross route is shared by fixture root and every target" {
    try std.testing.expectEqual(@as(usize, 3), countNeedle(fixture_text, expected_route));
    try mustContainOnce(fixture_text, "\"phase\": \"Phase 2\"");
    try mustContainOnce(fixture_text, "\"status\": \"active\"");
}

test "phase2 cross target ordering preserves bootstrap archive before contract-only target" {
    const x86_index = std.mem.indexOf(u8, fixture_text, "\"x86_64-linux\"").?;
    const aarch64_index = std.mem.indexOf(u8, fixture_text, "\"aarch64-linux\"").?;
    const archive_mode_index = std.mem.indexOf(u8, fixture_text, "\"archive_required\"").?;
    const contract_mode_index = std.mem.indexOf(u8, fixture_text, "\"route_contract_only\"").?;

    try std.testing.expect(x86_index < aarch64_index);
    try std.testing.expect(archive_mode_index < contract_mode_index);
}
