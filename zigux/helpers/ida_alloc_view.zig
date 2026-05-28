const std = @import("std");
const ida_bitmap_view = @import("ida_bitmap_view");

pub const chunk_id_span: u32 = @intCast(ida_bitmap_view.bitmap_bits);
pub const kernel_id_limit: u32 = std.math.maxInt(i32);

pub const AllocationRange = struct {
    min_id: u32,
    max_id: u32,

    pub fn isOrdered(self: AllocationRange) bool {
        return self.min_id <= self.max_id;
    }
};

pub const Selection = struct {
    id: u32,
    relative_bit: u32,
};

pub const AllocationView = struct {
    bitmap: ida_bitmap_view.BitmapView,
    chunk_base: u32,

    pub fn chunkEnd(self: AllocationView) u32 {
        return self.chunk_base + chunk_id_span - 1;
    }

    pub fn containsId(self: AllocationView, id: u32) bool {
        return id >= self.chunk_base and id <= self.chunkEnd();
    }

    pub fn relativeBit(self: AllocationView, id: u32) ?u32 {
        if (!self.containsId(id)) return null;
        return id - self.chunk_base;
    }

    pub fn idAtRelativeBit(self: AllocationView, relative_bit: u32) u32 {
        std.debug.assert(relative_bit < chunk_id_span);
        return self.chunk_base + relative_bit;
    }

    pub fn intersectsRange(self: AllocationView, alloc_range: AllocationRange) bool {
        return alloc_range.isOrdered() and
            alloc_range.max_id >= self.chunk_base and
            alloc_range.min_id <= self.chunkEnd();
    }

    pub fn firstCandidateInRange(self: AllocationView, alloc_range: AllocationRange) ?Selection {
        if (!self.intersectsRange(alloc_range)) return null;
        const id = @max(alloc_range.min_id, self.chunk_base);
        return .{
            .id = id,
            .relative_bit = id - self.chunk_base,
        };
    }

    pub fn lastCandidateInRange(self: AllocationView, alloc_range: AllocationRange) ?Selection {
        if (!self.intersectsRange(alloc_range)) return null;
        const id = @min(alloc_range.max_id, self.chunkEnd());
        return .{
            .id = id,
            .relative_bit = id - self.chunk_base,
        };
    }

    pub fn isAllocated(self: AllocationView, id: u32) bool {
        const relative_bit = self.relativeBit(id) orelse return false;
        return self.bitmap.isSet(relative_bit);
    }

    pub fn firstFreeInRange(self: AllocationView, alloc_range: AllocationRange) ?Selection {
        const first = self.firstCandidateInRange(alloc_range) orelse return null;
        const last = self.lastCandidateInRange(alloc_range) orelse return null;

        var id = first.id;
        while (true) : (id += 1) {
            if (!self.isAllocated(id)) {
                return .{
                    .id = id,
                    .relative_bit = id - self.chunk_base,
                };
            }
            if (id == last.id) break;
        }
        return null;
    }
};

pub fn range(min_id: u32, max_id: u32) AllocationRange {
    return .{
        .min_id = min_id,
        .max_id = max_id,
    };
}

pub fn fromWords(words: *const ida_bitmap_view.BitmapWords, chunk_base: u32) AllocationView {
    std.debug.assert(chunk_base <= kernel_id_limit);
    std.debug.assert(chunk_base <= kernel_id_limit - (chunk_id_span - 1));
    return .{
        .bitmap = ida_bitmap_view.fromWords(words),
        .chunk_base = chunk_base,
    };
}

test "ida alloc view keeps chunk mapping explicit" {
    const words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    const view = fromWords(&words, 1024);

    try std.testing.expectEqual(@as(u32, 1024), view.chunk_base);
    try std.testing.expectEqual(@as(u32, 2047), view.chunkEnd());
    try std.testing.expect(view.containsId(1024));
    try std.testing.expect(view.containsId(2047));
    try std.testing.expect(!view.containsId(2048));
    try std.testing.expectEqual(@as(?u32, 0), view.relativeBit(1024));
    try std.testing.expectEqual(@as(?u32, 1023), view.relativeBit(2047));
    try std.testing.expectEqual(@as(?u32, null), view.relativeBit(2048));
}

test "ida alloc view clamps the first candidate to the chunk floor" {
    var words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    words[0] |= @as(usize, 1);
    const view = fromWords(&words, 1024);
    const request = range(1000, 1027);

    const first = view.firstCandidateInRange(request) orelse return error.TestUnexpectedResult;
    const first_free = view.firstFreeInRange(request) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(u32, 1024), first.id);
    try std.testing.expectEqual(@as(u32, 0), first.relative_bit);
    try std.testing.expectEqual(@as(u32, 1025), first_free.id);
    try std.testing.expectEqual(@as(u32, 1), first_free.relative_bit);
}

test "ida alloc view clamps the last candidate to the chunk ceiling" {
    var words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    const last_bit: u32 = chunk_id_span - 2;
    words[last_bit / ida_bitmap_view.word_bits] |=
        @as(usize, 1) << @intCast(last_bit % ida_bitmap_view.word_bits);
    const view = fromWords(&words, 2048);
    const request = range(3070, 4096);

    const last = view.lastCandidateInRange(request) orelse return error.TestUnexpectedResult;
    const first_free = view.firstFreeInRange(request) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(u32, 3071), last.id);
    try std.testing.expectEqual(@as(u32, 1023), last.relative_bit);
    try std.testing.expectEqual(@as(u32, 3071), first_free.id);
    try std.testing.expectEqual(@as(u32, 1023), first_free.relative_bit);
}

test "ida alloc view keeps disjoint and unordered ranges closed" {
    const words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    const view = fromWords(&words, 4096);

    try std.testing.expectEqual(@as(?Selection, null), view.firstCandidateInRange(range(0, 100)));
    try std.testing.expectEqual(@as(?Selection, null), view.lastCandidateInRange(range(0, 100)));
    try std.testing.expectEqual(@as(?Selection, null), view.firstFreeInRange(range(0, 100)));
    try std.testing.expectEqual(@as(?Selection, null), view.firstCandidateInRange(range(17, 12)));
    try std.testing.expectEqual(@as(?Selection, null), view.firstFreeInRange(range(17, 12)));
}

test "ida alloc view reports a full requested window as exhausted" {
    var words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    words[0] = 0xff;
    const view = fromWords(&words, 0);
    const request = range(0, 7);

    try std.testing.expectEqual(@as(?Selection, null), view.firstFreeInRange(request));
}
