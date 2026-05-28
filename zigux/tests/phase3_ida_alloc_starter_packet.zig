const std = @import("std");
const testing = std.testing;

const ida_alloc_view = @import("ida_alloc_view");
const ida_bitmap_view = @import("ida_bitmap_view");

test "ida alloc starter packet keeps the chunk-span contract explicit" {
    try testing.expectEqual(
        @as(u32, @intCast(ida_bitmap_view.bitmap_bits)),
        ida_alloc_view.chunk_id_span,
    );
    try testing.expectEqual(@as(u32, std.math.maxInt(i32)), ida_alloc_view.kernel_id_limit);
}

test "ida alloc starter packet keeps sparse allocation search explicit" {
    var words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    words[0] |= (@as(usize, 1) << 0) | (@as(usize, 1) << 1) | (@as(usize, 1) << 3);
    const view = ida_alloc_view.fromWords(&words, 0);
    const request = ida_alloc_view.range(0, 7);

    const first = view.firstCandidateInRange(request) orelse return error.TestUnexpectedResult;
    const first_free = view.firstFreeInRange(request) orelse return error.TestUnexpectedResult;

    try testing.expectEqual(@as(u32, 0), first.id);
    try testing.expectEqual(@as(u32, 0), first.relative_bit);
    try testing.expectEqual(@as(u32, 2), first_free.id);
    try testing.expectEqual(@as(u32, 2), first_free.relative_bit);
}

test "ida alloc starter packet keeps chunk-floor clamping explicit" {
    var words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    words[0] |= @as(usize, 1);
    const view = ida_alloc_view.fromWords(&words, 1024);
    const request = ida_alloc_view.range(1000, 1027);

    const first_free = view.firstFreeInRange(request) orelse return error.TestUnexpectedResult;

    try testing.expectEqual(@as(u32, 1025), first_free.id);
    try testing.expectEqual(@as(u32, 1), first_free.relative_bit);
}

test "ida alloc starter packet keeps ceiling clamping and disjoint windows distinct" {
    var words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    const last_bit: u32 = ida_alloc_view.chunk_id_span - 2;
    words[last_bit / ida_bitmap_view.word_bits] |=
        @as(usize, 1) << @intCast(last_bit % ida_bitmap_view.word_bits);
    const clamped = ida_alloc_view.fromWords(&words, 2048);
    const disjoint = ida_alloc_view.fromWords(&words, 4096);

    const clamped_free = clamped.firstFreeInRange(ida_alloc_view.range(3070, 4096)) orelse
        return error.TestUnexpectedResult;

    try testing.expectEqual(@as(u32, 3071), clamped_free.id);
    try testing.expectEqual(@as(u32, 1023), clamped_free.relative_bit);
    try testing.expectEqual(
        @as(?ida_alloc_view.Selection, null),
        disjoint.firstFreeInRange(ida_alloc_view.range(0, 100)),
    );
}

test "ida alloc starter packet keeps ordered-range failure explicit" {
    const words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    const view = ida_alloc_view.fromWords(&words, 0);

    try testing.expectEqual(
        @as(?ida_alloc_view.Selection, null),
        view.firstCandidateInRange(ida_alloc_view.range(9, 3)),
    );
    try testing.expectEqual(
        @as(?ida_alloc_view.Selection, null),
        view.firstFreeInRange(ida_alloc_view.range(9, 3)),
    );
}
