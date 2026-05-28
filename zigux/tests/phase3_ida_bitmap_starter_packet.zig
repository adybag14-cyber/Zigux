const std = @import("std");
const testing = std.testing;

const ida_bitmap_view = @import("ida_bitmap_view");

test "ida bitmap starter packet keeps the fixed chunk geometry explicit" {
    try testing.expectEqual(@as(usize, 128), ida_bitmap_view.chunk_size_bytes);
    try testing.expectEqual(
        ida_bitmap_view.chunk_size_bytes / @sizeOf(usize),
        ida_bitmap_view.bitmap_longs,
    );
    try testing.expectEqual(ida_bitmap_view.chunk_size_bytes * 8, ida_bitmap_view.bitmap_bits);
}

test "ida bitmap starter packet keeps an empty chunk reviewable" {
    const words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    const view = ida_bitmap_view.fromWords(&words);

    try testing.expect(view.isEmpty());
    try testing.expect(!view.isFull());
    try testing.expectEqual(@as(usize, 0), view.weight());
    try testing.expectEqual(@as(?usize, null), view.firstSet());
    try testing.expectEqual(@as(?usize, 0), view.firstZero());
}

test "ida bitmap starter packet keeps sparse words explicit across chunk boundaries" {
    var words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    words[0] |= @as(usize, 1) << 1;
    words[1] |= @as(usize, 1) << 5;
    words[ida_bitmap_view.bitmap_longs - 1] |=
        @as(usize, 1) << @as(std.math.Log2Int(usize), @intCast(ida_bitmap_view.word_bits - 1));
    const view = ida_bitmap_view.fromWords(&words);

    try testing.expect(!view.isEmpty());
    try testing.expect(!view.isFull());
    try testing.expect(view.isSet(1));
    try testing.expect(view.isSet(ida_bitmap_view.word_bits + 5));
    try testing.expect(view.isSet(ida_bitmap_view.bitmap_bits - 1));
    try testing.expectEqual(@as(usize, 3), view.weight());
    try testing.expectEqual(@as(?usize, 1), view.firstSet());
    try testing.expectEqual(@as(?usize, 0), view.firstZero());
}

test "ida bitmap starter packet keeps full chunks and first-zero exhaustion distinct" {
    const words = [_]usize{~@as(usize, 0)} ** ida_bitmap_view.bitmap_longs;
    const view = ida_bitmap_view.fromWords(&words);

    try testing.expect(!view.isEmpty());
    try testing.expect(view.isFull());
    try testing.expectEqual(ida_bitmap_view.bitmap_bits, view.weight());
    try testing.expectEqual(@as(?usize, 0), view.firstSet());
    try testing.expectEqual(@as(?usize, null), view.firstZero());
}

test "ida bitmap starter packet keeps the first clear position visible inside a partially used word" {
    var words = [_]usize{0} ** ida_bitmap_view.bitmap_longs;
    words[0] = (@as(usize, 1) << 0) | (@as(usize, 1) << 1) | (@as(usize, 1) << 3);
    words[1] = ~@as(usize, 0);
    const view = ida_bitmap_view.fromWords(&words);

    try testing.expectEqual(@as(?usize, 2), view.firstZero());
    try testing.expectEqual(@as(?usize, 0), view.firstSet());
    try testing.expectEqual(@as(usize, ida_bitmap_view.word_bits + 3), view.weight());
}
