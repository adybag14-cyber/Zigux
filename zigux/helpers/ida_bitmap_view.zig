const std = @import("std");
const abi = @import("abi_bindings");
const bitmap_view = @import("bitmap_view");
const narrow = @import("narrow_unsafe");

pub fn viewFromBits(bits: []const usize, base_id: u32, nbits: u32, max_scan: u32) abi.IdaBitmapView {
    return .{
        .bits_addr = if (bits.len == 0) 0 else narrow.addressOf(&bits[0]),
        .base_id = base_id,
        .nbits = nbits,
        .max_scan = max_scan,
        .reserved = 0,
    };
}

pub fn isValid(view: abi.IdaBitmapView) bool {
    if (view.reserved != 0) return false;
    if (view.nbits == 0) return true;
    return view.bits_addr != 0 and view.max_scan != 0;
}

fn asBitmap(view: abi.IdaBitmapView) abi.BitmapView {
    if (!isValid(view)) return .{ .words_addr = 0, .nbits = 0, .word_count = 0 };
    return .{
        .words_addr = view.bits_addr,
        .nbits = view.nbits,
        .word_count = bitmap_view.wordCount(view.nbits),
    };
}

pub fn summarize(view: abi.IdaBitmapView) abi.IdaBitmapSummary {
    if (!isValid(view)) {
        return .{ .scanned_count = 0, .allocated_count = 0, .first_allocated_id = 0, .first_free_id = 0, .flags = 0, .reserved = 0 };
    }
    if (view.nbits == 0) {
        return .{ .scanned_count = 0, .allocated_count = 0, .first_allocated_id = view.base_id, .first_free_id = view.base_id, .flags = 0, .reserved = 0 };
    }

    const scanned: u32 = @min(view.nbits, view.max_scan);
    const bitmap = asBitmap(view);
    var summary = abi.IdaBitmapSummary{
        .scanned_count = scanned,
        .allocated_count = 0,
        .first_allocated_id = view.base_id + scanned,
        .first_free_id = view.base_id + scanned,
        .flags = if (scanned < view.nbits) abi.IDA_BITMAP_FLAG_TRUNCATED else 0,
        .reserved = 0,
    };
    var have_first_allocated = false;
    var have_first_free = false;

    var index: u32 = 0;
    while (index < scanned) : (index += 1) {
        const current_id = view.base_id + index;
        if (bitmap_view.testBit(bitmap, index)) {
            summary.allocated_count += 1;
            if (!have_first_allocated) {
                summary.first_allocated_id = current_id;
                have_first_allocated = true;
            }
        } else if (!have_first_free) {
            summary.first_free_id = current_id;
            have_first_free = true;
        }
    }

    if (!have_first_free) summary.flags |= abi.IDA_BITMAP_FLAG_EXHAUSTED;
    return summary;
}

test "phase3 ida bitmap helpers stay bounded and predictable" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 3) | (@as(usize, 1) << 5)};
    const view = viewFromBits(words[0..], 100, 7, 6);
    const summary = summarize(view);
    try std.testing.expect(isValid(view));
    try std.testing.expectEqual(@as(u32, 6), summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 4), summary.allocated_count);
    try std.testing.expectEqual(@as(u32, 100), summary.first_allocated_id);
    try std.testing.expectEqual(@as(u32, 101), summary.first_free_id);
    try std.testing.expectEqual(@as(u32, abi.IDA_BITMAP_FLAG_TRUNCATED), summary.flags);
}

test "phase3 ida bitmap exhaustion stays explicit" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 1) | (@as(usize, 1) << 2)};
    const view = viewFromBits(words[0..], 40, 3, 3);
    const summary = summarize(view);
    try std.testing.expect(isValid(view));
    try std.testing.expectEqual(@as(u32, 3), summary.allocated_count);
    try std.testing.expectEqual(@as(u32, 43), summary.first_free_id);
    try std.testing.expectEqual(@as(u32, abi.IDA_BITMAP_FLAG_EXHAUSTED), summary.flags);
}
