const std = @import("std");
const testing = std.testing;

const fixture = @embedFile("fixtures/phase1_helpers.json");

const HweightExpectation = struct {
    field: []const u8,
    value: u8,
    source_width_bits: u8,
};

const hweight_expectations = [_]HweightExpectation{
    .{ .field = "w8", .value = 4, .source_width_bits = 8 },
    .{ .field = "w16", .value = 8, .source_width_bits = 16 },
    .{ .field = "w32", .value = 16, .source_width_bits = 32 },
    .{ .field = "w64", .value = 32, .source_width_bits = 64 },
    .{ .field = "wlong", .value = 8, .source_width_bits = @bitSizeOf(usize) },
};

fn expectContains(needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, fixture, needle) != null);
}

fn expectContainsEither(pretty: []const u8, compact: []const u8) !void {
    try testing.expect(
        std.mem.indexOf(u8, fixture, pretty) != null or
            std.mem.indexOf(u8, fixture, compact) != null,
    );
}

test "phase1 helper fixture keeps hweight packet anchored" {
    try expectContainsEither("\"hweight\": {", "\"hweight\":{");

    inline for (hweight_expectations) |expectation| {
        var expected_pretty_field: [64]u8 = undefined;
        const pretty_field = try std.fmt.bufPrint(
            &expected_pretty_field,
            "\"{s}\": {d}",
            .{ expectation.field, expectation.value },
        );
        var expected_compact_field: [64]u8 = undefined;
        const compact_field = try std.fmt.bufPrint(
            &expected_compact_field,
            "\"{s}\":{d}",
            .{ expectation.field, expectation.value },
        );
        try expectContainsEither(pretty_field, compact_field);
    }
}

test "phase1 hweight values remain half-populated per source width" {
    inline for (hweight_expectations[0..4]) |expectation| {
        try testing.expectEqual(expectation.source_width_bits / 2, expectation.value);
    }
}

test "phase1 hweight long fixture stays intentionally narrower than machine word" {
    try testing.expectEqual(@as(u8, 8), hweight_expectations[4].value);
    try testing.expect(hweight_expectations[4].value < hweight_expectations[4].source_width_bits);
}
