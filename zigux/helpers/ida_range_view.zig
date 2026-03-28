const std = @import("std");
const abi = @import("abi_bindings");
const bitmap_view = @import("bitmap_view");
const narrow = @import("narrow_unsafe");

pub fn viewFromBits(bits: []const usize, base_id: u32, nbits: u32, max_scan: u32, request_count: u32, max_ranges: u32) abi.IdaRangeView {
    return .{
        .bits_addr = if (bits.len == 0) 0 else narrow.addressOf(&bits[0]),
        .base_id = base_id,
        .nbits = nbits,
        .max_scan = max_scan,
        .request_count = request_count,
        .max_ranges = max_ranges,
        .reserved = 0,
    };
}

pub fn isValid(view: abi.IdaRangeView) bool {
    if (view.reserved != 0) return false;
    if (view.request_count == 0 or view.max_ranges == 0) return false;
    if (view.nbits == 0) return true;
    return view.bits_addr != 0 and view.max_scan != 0;
}

fn asBitmap(view: abi.IdaRangeView) abi.BitmapView {
    if (!isValid(view)) return .{ .words_addr = 0, .nbits = 0, .word_count = 0 };
    return .{
        .words_addr = view.bits_addr,
        .nbits = view.nbits,
        .word_count = bitmap_view.wordCount(view.nbits),
    };
}

pub fn summarize(view: abi.IdaRangeView) abi.IdaRangeSummary {
    if (!isValid(view)) {
        return .{ .scanned_count = 0, .request_count = 0, .candidate_range_count = 0, .first_range_id = 0, .last_range_id = 0, .flags = 0 };
    }

    const scanned: u32 = @min(view.nbits, view.max_scan);
    const bitmap = asBitmap(view);
    var summary = abi.IdaRangeSummary{
        .scanned_count = scanned,
        .request_count = view.request_count,
        .candidate_range_count = 0,
        .first_range_id = view.base_id + scanned,
        .last_range_id = view.base_id + scanned,
        .flags = if (scanned < view.nbits) abi.IDA_RANGE_FLAG_TRUNCATED else 0,
    };

    if (scanned < view.request_count) {
        summary.flags |= abi.IDA_RANGE_FLAG_EXHAUSTED;
        return summary;
    }

    var start: u32 = 0;
    while (start + view.request_count <= scanned) : (start += 1) {
        var fits = true;
        var bit: u32 = 0;
        while (bit < view.request_count) : (bit += 1) {
            if (bitmap_view.testBit(bitmap, start + bit)) {
                fits = false;
                break;
            }
        }
        if (!fits) continue;

        if ((summary.flags & abi.IDA_RANGE_FLAG_FOUND) == 0) summary.first_range_id = view.base_id + start;
        summary.flags |= abi.IDA_RANGE_FLAG_FOUND;
        if (summary.candidate_range_count < view.max_ranges) {
            summary.last_range_id = view.base_id + start;
            summary.candidate_range_count += 1;
        } else {
            summary.flags |= abi.IDA_RANGE_FLAG_TRUNCATED;
        }
    }

    if ((summary.flags & abi.IDA_RANGE_FLAG_FOUND) == 0) summary.flags |= abi.IDA_RANGE_FLAG_EXHAUSTED;
    return summary;
}

test "phase3 ida range helpers stay bounded and predictable" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const view = viewFromBits(words[0..], 100, 8, 6, 2, 4);
    const summary = summarize(view);
    try std.testing.expect(isValid(view));
    try std.testing.expectEqual(@as(u32, 6), summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 2), summary.request_count);
    try std.testing.expectEqual(@as(u32, 2), summary.candidate_range_count);
    try std.testing.expectEqual(@as(u32, 101), summary.first_range_id);
    try std.testing.expectEqual(@as(u32, 104), summary.last_range_id);
    try std.testing.expectEqual(@as(u32, abi.IDA_RANGE_FLAG_TRUNCATED | abi.IDA_RANGE_FLAG_FOUND), summary.flags);
}

test "phase3 ida range cap and exhaustion stay explicit" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const capped = viewFromBits(words[0..], 100, 8, 8, 2, 2);
    const capped_summary = summarize(capped);
    try std.testing.expect(isValid(capped));
    try std.testing.expectEqual(@as(u32, 2), capped_summary.candidate_range_count);
    try std.testing.expectEqual(@as(u32, 101), capped_summary.first_range_id);
    try std.testing.expectEqual(@as(u32, 104), capped_summary.last_range_id);
    try std.testing.expectEqual(@as(u32, abi.IDA_RANGE_FLAG_TRUNCATED | abi.IDA_RANGE_FLAG_FOUND), capped_summary.flags);

    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};
    const exhausted = viewFromBits(exhausted_words[0..], 40, 5, 5, 2, 4);
    const exhausted_summary = summarize(exhausted);
    try std.testing.expectEqual(@as(u32, 0), exhausted_summary.candidate_range_count);
    try std.testing.expectEqual(@as(u32, 45), exhausted_summary.first_range_id);
    try std.testing.expectEqual(@as(u32, 45), exhausted_summary.last_range_id);
    try std.testing.expectEqual(@as(u32, abi.IDA_RANGE_FLAG_EXHAUSTED), exhausted_summary.flags);
}
