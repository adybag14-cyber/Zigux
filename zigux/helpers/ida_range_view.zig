const std = @import("std");
const ida_bitmap_view = @import("ida_bitmap_view");
const ida_alloc_view = @import("ida_alloc_view");

pub const AllocationRange = ida_alloc_view.AllocationRange;
pub const Selection = ida_alloc_view.Selection;

pub const ClampedWindow = struct {
    first_id: u32,
    last_id: u32,
    first_relative_bit: u32,
    last_relative_bit: u32,

    pub fn spanLen(self: ClampedWindow) u32 {
        return self.last_id - self.first_id + 1;
    }
};

pub const RangeSummary = struct {
    window: ClampedWindow,
    allocated_bits: u32,
    first_allocated: ?Selection,
    first_free: ?Selection,

    pub fn isFullyAllocated(self: RangeSummary) bool {
        return self.allocated_bits == self.window.spanLen();
    }

    pub fn isFullyFree(self: RangeSummary) bool {
        return self.allocated_bits == 0;
    }
};

pub const RangeView = struct {
    alloc: ida_alloc_view.AllocationView,

    pub fn clampWindow(self: RangeView, alloc_range: AllocationRange) ?ClampedWindow {
        const first = self.alloc.firstCandidateInRange(alloc_range) orelse return null;
        const last = self.alloc.lastCandidateInRange(alloc_range) orelse return null;
        return .{
            .first_id = first.id,
            .last_id = last.id,
            .first_relative_bit = first.relative_bit,
            .last_relative_bit = last.relative_bit,
        };
    }

    pub fn firstAllocatedInRange(self: RangeView, alloc_range: AllocationRange) ?Selection {
        const window = self.clampWindow(alloc_range) orelse return null;
        var id = window.first_id;
        while (true) : (id += 1) {
            if (self.alloc.isAllocated(id)) {
                return .{
                    .id = id,
                    .relative_bit = id - self.alloc.chunk_base,
                };
            }
            if (id == window.last_id) break;
        }
        return null;
    }

    pub fn allocatedCount(self: RangeView, alloc_range: AllocationRange) ?u32 {
        const window = self.clampWindow(alloc_range) orelse return null;
        var total: u32 = 0;
        var id = window.first_id;
        while (true) : (id += 1) {
            if (self.alloc.isAllocated(id)) total += 1;
            if (id == window.last_id) break;
        }
        return total;
    }

    pub fn summarize(self: RangeView, alloc_range: AllocationRange) ?RangeSummary {
        const window = self.clampWindow(alloc_range) orelse return null;
        return .{
            .window = window,
            .allocated_bits = self.allocatedCount(alloc_range) orelse return null,
            .first_allocated = self.firstAllocatedInRange(alloc_range),
            .first_free = self.alloc.firstFreeInRange(alloc_range),
        };
    }
};

pub fn range(min_id: u32, max_id: u32) AllocationRange {
    return ida_alloc_view.range(min_id, max_id);
}

pub fn fromWords(words: *const ida_bitmap_view.BitmapWords, chunk_base: u32) RangeView {
    return .{
        .alloc = ida_alloc_view.fromWords(words, chunk_base),
    };
}

test "ida range view keeps clamped window geometry explicit" {
    const words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    const view = fromWords(&words, 1024);

    const window = view.clampWindow(range(1000, 1027)) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(u32, 1024), window.first_id);
    try std.testing.expectEqual(@as(u32, 1027), window.last_id);
    try std.testing.expectEqual(@as(u32, 0), window.first_relative_bit);
    try std.testing.expectEqual(@as(u32, 3), window.last_relative_bit);
    try std.testing.expectEqual(@as(u32, 4), window.spanLen());
}

test "ida range view counts partial allocation windows" {
    var words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    words[0] |= (@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 3);
    const view = fromWords(&words, 1024);
    const summary = view.summarize(range(1000, 1027)) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(u32, 3), summary.allocated_bits);
    try std.testing.expect(!summary.isFullyAllocated());
    try std.testing.expect(!summary.isFullyFree());

    const first_allocated = summary.first_allocated orelse return error.TestUnexpectedResult;
    const first_free = summary.first_free orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(u32, 1024), first_allocated.id);
    try std.testing.expectEqual(@as(u32, 1025), first_free.id);
}

test "ida range view reports fully allocated windows at the chunk ceiling" {
    var words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    const high_a: u32 = ida_alloc_view.chunk_id_span - 2;
    const high_b: u32 = ida_alloc_view.chunk_id_span - 1;
    words[high_a / ida_bitmap_view.word_bits] |= @as(usize, 1) << @intCast(high_a % ida_bitmap_view.word_bits);
    words[high_b / ida_bitmap_view.word_bits] |= @as(usize, 1) << @intCast(high_b % ida_bitmap_view.word_bits);

    const view = fromWords(&words, 2048);
    const summary = view.summarize(range(3070, 4096)) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(u32, 2), summary.window.spanLen());
    try std.testing.expectEqual(@as(u32, 2), summary.allocated_bits);
    try std.testing.expect(summary.isFullyAllocated());
    try std.testing.expect(!summary.isFullyFree());
    try std.testing.expectEqual(@as(?Selection, null), summary.first_free);
}

test "ida range view reports fully free middle windows" {
    const words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    const view = fromWords(&words, 0);
    const summary = view.summarize(range(8, 11)) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(u32, 0), summary.allocated_bits);
    try std.testing.expect(!summary.isFullyAllocated());
    try std.testing.expect(summary.isFullyFree());
    try std.testing.expectEqual(@as(?Selection, null), summary.first_allocated);

    const first_free = summary.first_free orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(u32, 8), first_free.id);
}

test "ida range view keeps disjoint and unordered windows closed" {
    const words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    const view = fromWords(&words, 4096);

    try std.testing.expectEqual(@as(?ClampedWindow, null), view.clampWindow(range(0, 100)));
    try std.testing.expectEqual(@as(?RangeSummary, null), view.summarize(range(0, 100)));
    try std.testing.expectEqual(@as(?Selection, null), view.firstAllocatedInRange(range(17, 12)));
    try std.testing.expectEqual(@as(?u32, null), view.allocatedCount(range(17, 12)));
}
