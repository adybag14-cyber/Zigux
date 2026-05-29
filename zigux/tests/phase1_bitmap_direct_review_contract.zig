const std = @import("std");
const bitmap = @import("bitmap");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

const ReviewMarkerKind = enum {
    closure_direct_review,
    multiword_tail_unit,
    empty_format_unit,
    final_partial_word,
    linux_alias,
};

const ReviewMarker = struct {
    status: []const u8,
    kind: ReviewMarkerKind,
    helper_local: bool,
};

const bitmap_direct_review_markers = [_]ReviewMarker{
    .{ .status = "PHASE1_BITMAP_DIRECT_REVIEW", .kind = .closure_direct_review, .helper_local = true },
    .{ .status = "PHASE1_BITMAP_UNIT_REVIEW", .kind = .multiword_tail_unit, .helper_local = true },
    .{ .status = "PHASE1_BITMAP_EMPTY_UNIT_REVIEW", .kind = .empty_format_unit, .helper_local = true },
    .{ .status = "PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW", .kind = .final_partial_word, .helper_local = true },
    .{ .status = "PHASE1_BITMAP_LINUX_ALIAS_REVIEW", .kind = .linux_alias, .helper_local = true },
};

const closure_bitmap_guard_marker =
    "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py";

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn countKind(kind: ReviewMarkerKind) usize {
    var count: usize = 0;
    for (bitmap_direct_review_markers) |marker| {
        if (marker.kind == kind) count += 1;
    }
    return count;
}

test "phase1 bitmap direct-review roster stays helper-local" {
    try std.testing.expectEqual(@as(usize, 5), bitmap_direct_review_markers.len);
    try std.testing.expect(contains(closure_bitmap_guard_marker, "check-phase1-direct-anchor-manifest-gate.py"));

    for (bitmap_direct_review_markers) |marker| {
        try std.testing.expect(marker.helper_local);
        try std.testing.expect(contains(marker.status, "PHASE1_BITMAP_"));
        try std.testing.expect(!contains(marker.status, "VALIDATE_PHASE1_CLOSURE"));
        try std.testing.expect(!contains(marker.status, "SHARED_FIXTURE"));
    }
}

test "phase1 bitmap direct-review roster keeps closure markers distinct" {
    try std.testing.expectEqual(@as(usize, 1), countKind(.closure_direct_review));
    try std.testing.expectEqual(@as(usize, 1), countKind(.multiword_tail_unit));
    try std.testing.expectEqual(@as(usize, 1), countKind(.empty_format_unit));
    try std.testing.expectEqual(@as(usize, 1), countKind(.final_partial_word));
    try std.testing.expectEqual(@as(usize, 1), countKind(.linux_alias));
}

test "bitmap direct review keeps copy extend and tail-masked predicates visible" {
    const count = bits_per_long + 5;
    const size = bits_per_long * 3;
    const src = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };
    var dst = [_]Word{ 0xaaaa, 0xbbbb, 0xcccc };

    bitmap.copyAndExtend(&dst, &src, count, size);

    try std.testing.expectEqual(~@as(Word, 0), dst[0]);
    try std.testing.expectEqual(bitmap.lastWordMask(count), dst[1]);
    try std.testing.expectEqual(@as(Word, 0), dst[2]);
    try std.testing.expect(bitmap.equal(dst[0..2], src[0..2], count));
    try std.testing.expect(bitmap.subset(dst[0..2], src[0..2], count));
    try std.testing.expectEqual(@as(usize, count), bitmap.weight(&dst, count));
}

test "bitmap unit review keeps multiword tail xor clamped by callers" {
    const nbits = bits_per_long + 7;
    const lhs = [_]Word{ 0b1010, (@as(Word, 1) << 2) | (@as(Word, 1) << 8) };
    const rhs = [_]Word{ 0b0011, (@as(Word, 1) << 5) | (@as(Word, 1) << 9) };
    var out = [_]Word{ 0, 0 };

    bitmap.xorBits(&out, &lhs, &rhs, nbits);

    const visible_tail = bitmap.lastWordMask(nbits);
    const clamped_tail = out[1] & visible_tail;
    try std.testing.expectEqual(lhs[0] ^ rhs[0], out[0]);
    try std.testing.expectEqual((lhs[1] ^ rhs[1]) & visible_tail, clamped_tail);
    try std.testing.expectEqual(@as(usize, 2), @popCount(clamped_tail));
}

test "bitmap empty unit review keeps caller buffer untouched" {
    const map = [_]Word{0};
    var buffer = [_]u8{ 0xaa, 0xbb, 0xcc, 0xdd };

    const written = bitmap.scnprintf(&map, bits_per_long, &buffer);

    try std.testing.expectEqual(@as(usize, 0), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd }, &buffer);
}

test "bitmap final partial-word review clamps range mutations" {
    const start = bits_per_long + 2;
    const len = 5;
    const end = start + len;
    var map = [_]Word{ 0, 0, ~@as(Word, 0) };

    bitmap.setRange(&map, start, len);
    try std.testing.expectEqual(@as(Word, 0), map[0]);
    try std.testing.expectEqual(bitmap.firstWordMask(start) & bitmap.lastWordMask(end), map[1]);
    try std.testing.expectEqual(~@as(Word, 0), map[2]);

    bitmap.clearRange(&map, start + 1, len - 2);
    const remaining = (@as(Word, 1) << (start % bits_per_long)) |
        (@as(Word, 1) << ((end - 1) % bits_per_long));
    try std.testing.expectEqual(remaining, map[1]);
}

test "bitmap Linux-style alias review mirrors primary helpers" {
    const nbits = bits_per_long + 6;
    const lhs = [_]Word{ 0b1110, (@as(Word, 1) << 1) | (@as(Word, 1) << 5) };
    const rhs = [_]Word{ 0b1011, (@as(Word, 1) << 5) | (@as(Word, 1) << 9) };
    var direct = [_]Word{ 0, 0 };
    var alias = [_]Word{ 0, 0 };

    bitmap.orBits(&direct, &lhs, &rhs, nbits);
    bitmap.bitmap_or(&alias, &lhs, &rhs, nbits);
    try std.testing.expectEqualSlices(Word, &direct, &alias);

    const primary_result = bitmap.andNotBits(&direct, &lhs, &rhs, nbits);
    const direct_result = bitmap.andNotBits(&alias, &lhs, &rhs, nbits);
    const alias_result = bitmap.bitmap_andnot(&direct, &lhs, &rhs, nbits);
    try std.testing.expectEqual(primary_result, direct_result);
    try std.testing.expectEqual(direct_result, alias_result);
    try std.testing.expectEqualSlices(Word, &alias, &direct);

    try std.testing.expectEqual(bitmap.equal(&lhs, &rhs, nbits), bitmap.bitmap_equal(&lhs, &rhs, nbits));
    try std.testing.expectEqual(bitmap.intersects(&lhs, &rhs, nbits), bitmap.bitmap_intersects(&lhs, &rhs, nbits));
    try std.testing.expectEqual(bitmap.subset(&lhs, &rhs, nbits), bitmap.bitmap_subset(&lhs, &rhs, nbits));
}
