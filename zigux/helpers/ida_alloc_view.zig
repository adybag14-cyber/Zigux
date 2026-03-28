const std = @import("std");
const abi = @import("abi_bindings");
const bitmap_view = @import("bitmap_view");
const narrow = @import("narrow_unsafe");

pub fn viewFromBits(bits: []const usize, base_id: u32, nbits: u32, max_scan: u32, request_count: u32) abi.IdaAllocView {
    return .{
        .bits_addr = if (bits.len == 0) 0 else narrow.addressOf(&bits[0]),
        .base_id = base_id,
        .nbits = nbits,
        .max_scan = max_scan,
        .request_count = request_count,
        .reserved = 0,
    };
}

pub fn isValid(view: abi.IdaAllocView) bool {
    if (view.reserved != 0) return false;
    if (view.request_count == 0) return false;
    if (view.nbits == 0) return true;
    return view.bits_addr != 0 and view.max_scan != 0;
}

fn asBitmap(view: abi.IdaAllocView) abi.BitmapView {
    if (!isValid(view)) return .{ .words_addr = 0, .nbits = 0, .word_count = 0 };
    return .{
        .words_addr = view.bits_addr,
        .nbits = view.nbits,
        .word_count = bitmap_view.wordCount(view.nbits),
    };
}

pub fn summarize(view: abi.IdaAllocView) abi.IdaAllocSummary {
    if (!isValid(view)) {
        return .{ .scanned_count = 0, .request_count = 0, .first_fit_id = 0, .longest_free_run = 0, .flags = 0, .reserved = 0 };
    }

    const scanned: u32 = @min(view.nbits, view.max_scan);
    const bitmap = asBitmap(view);
    var summary = abi.IdaAllocSummary{
        .scanned_count = scanned,
        .request_count = view.request_count,
        .first_fit_id = view.base_id + scanned,
        .longest_free_run = 0,
        .flags = if (scanned < view.nbits) abi.IDA_ALLOC_FLAG_TRUNCATED else 0,
        .reserved = 0,
    };
    var current_run: u32 = 0;
    var current_start: u32 = 0;
    var index: u32 = 0;
    while (index < scanned) : (index += 1) {
        if (bitmap_view.testBit(bitmap, index)) {
            current_run = 0;
            continue;
        }

        if (current_run == 0) current_start = index;
        current_run += 1;
        if (current_run > summary.longest_free_run) summary.longest_free_run = current_run;
        if ((summary.flags & abi.IDA_ALLOC_FLAG_FOUND) == 0 and current_run >= view.request_count) {
            summary.first_fit_id = view.base_id + current_start;
            summary.flags |= abi.IDA_ALLOC_FLAG_FOUND;
        }
    }

    if ((summary.flags & abi.IDA_ALLOC_FLAG_FOUND) == 0) summary.flags |= abi.IDA_ALLOC_FLAG_EXHAUSTED;
    return summary;
}

test "phase3 ida alloc helpers stay bounded and predictable" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const view = viewFromBits(words[0..], 100, 8, 6, 2);
    const summary = summarize(view);
    try std.testing.expect(isValid(view));
    try std.testing.expectEqual(@as(u32, 6), summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 2), summary.request_count);
    try std.testing.expectEqual(@as(u32, 101), summary.first_fit_id);
    try std.testing.expectEqual(@as(u32, 2), summary.longest_free_run);
    try std.testing.expectEqual(@as(u32, abi.IDA_ALLOC_FLAG_TRUNCATED | abi.IDA_ALLOC_FLAG_FOUND), summary.flags);
}

test "phase3 ida alloc exhaustion stays explicit" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};
    const view = viewFromBits(words[0..], 40, 5, 5, 2);
    const summary = summarize(view);
    try std.testing.expect(isValid(view));
    try std.testing.expectEqual(@as(u32, 45), summary.first_fit_id);
    try std.testing.expectEqual(@as(u32, 1), summary.longest_free_run);
    try std.testing.expectEqual(@as(u32, abi.IDA_ALLOC_FLAG_EXHAUSTED), summary.flags);
}
