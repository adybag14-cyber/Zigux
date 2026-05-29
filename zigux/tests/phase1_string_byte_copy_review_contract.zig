const std = @import("std");
const string = @import("string");

const ReviewAnchorKind = enum {
    bounded_copy,
    fixed_memory_copy,
    fixed_memory_pad,
    fixed_memory_to_string,
};

const ReviewAnchor = struct {
    symbol: []const u8,
    kind: ReviewAnchorKind,
    helper_local: bool,
};

const string_byte_copy_anchors = [_]ReviewAnchor{
    .{ .symbol = "memcpyAndPad", .kind = .bounded_copy, .helper_local = true },
    .{ .symbol = "memcpy_and_pad", .kind = .bounded_copy, .helper_local = true },
    .{ .symbol = "strtomem", .kind = .fixed_memory_copy, .helper_local = true },
    .{ .symbol = "strtomem_pad", .kind = .fixed_memory_pad, .helper_local = true },
    .{ .symbol = "memtostr", .kind = .fixed_memory_to_string, .helper_local = true },
    .{ .symbol = "memtostrPad", .kind = .fixed_memory_to_string, .helper_local = true },
    .{ .symbol = "memtostr_pad", .kind = .fixed_memory_to_string, .helper_local = true },
};

const closure_string_review_marker =
    "PHASE1_STRING_REVIEW_GUARD=python3 scripts/zigux/check-phase1-string-review-packet.py";

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn countKind(kind: ReviewAnchorKind) usize {
    var count: usize = 0;
    for (string_byte_copy_anchors) |anchor| {
        if (anchor.kind == kind) count += 1;
    }
    return count;
}

test "phase1 string byte-copy review roster stays helper-local" {
    try std.testing.expectEqual(@as(usize, 7), string_byte_copy_anchors.len);
    try std.testing.expect(contains(closure_string_review_marker, "check-phase1-string-review-packet.py"));

    for (string_byte_copy_anchors) |anchor| {
        try std.testing.expect(anchor.helper_local);
        try std.testing.expect(!contains(anchor.symbol, "validate-phase1-closure"));
        try std.testing.expect(!contains(anchor.symbol, "shared-fixture"));
    }
}

test "phase1 string byte-copy review roster keeps copy and pad families distinct" {
    try std.testing.expectEqual(@as(usize, 2), countKind(.bounded_copy));
    try std.testing.expectEqual(@as(usize, 1), countKind(.fixed_memory_copy));
    try std.testing.expectEqual(@as(usize, 1), countKind(.fixed_memory_pad));
    try std.testing.expectEqual(@as(usize, 3), countKind(.fixed_memory_to_string));
}

test "memcpyAndPad and Linux-style alias copy bounded source then pad remainder" {
    var direct = [_]u8{0} ** 8;
    var alias = [_]u8{0} ** 8;

    string.memcpyAndPad(&direct, "abc", 5, 'x');
    string.memcpy_and_pad(&alias, "abc", 5, 'x');

    try std.testing.expectEqualSlices(u8, "abcxxxxx", &direct);
    try std.testing.expectEqualSlices(u8, &direct, &alias);
}

test "strtomem copies fixed memory while strtomem_pad owns trailing pad bytes" {
    var fixed = [_]u8{ '?', '?', '?', '?', '?' };
    var padded = [_]u8{ '?', '?', '?', '?', '?' };

    string.strtomem(&fixed, "ab\x00cd");
    string.strtomem_pad(&padded, "ab\x00cd", '.');

    try std.testing.expectEqualSlices(u8, "ab???", &fixed);
    try std.testing.expectEqualSlices(u8, "ab...", &padded);
}

test "memtostr family keeps nul termination and pad semantics review-visible" {
    var unpadded = [_]u8{ '?', '?', '?', '?', '?' };
    var padded_direct = [_]u8{ '?', '?', '?', '?', '?' };
    var padded_alias = [_]u8{ '?', '?', '?', '?', '?' };

    string.memtostr(&unpadded, "ab\x00cd");
    string.memtostrPad(&padded_direct, "ab\x00cd");
    string.memtostr_pad(&padded_alias, "ab\x00cd");

    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 0, '?', '?' }, &unpadded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 0, 0, 0 }, &padded_direct);
    try std.testing.expectEqualSlices(u8, &padded_direct, &padded_alias);
}
