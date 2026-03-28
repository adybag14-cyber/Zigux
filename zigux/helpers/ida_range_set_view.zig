const std = @import("std");
const abi = @import("abi_bindings");
const bitmap_view = @import("bitmap_view");
const narrow = @import("narrow_unsafe");

pub fn viewFromBits(bits: []const usize, base_id: u32, nbits: u32, max_scan: u32, request_count: u32, max_ranges: u32, max_selected: u32) abi.IdaRangeSetView {
    return .{
        .bits_addr = if (bits.len == 0) 0 else narrow.addressOf(&bits[0]),
        .base_id = base_id,
        .nbits = nbits,
        .max_scan = max_scan,
        .request_count = request_count,
        .max_ranges = max_ranges,
        .max_selected = max_selected,
        .reserved = 0,
    };
}

pub fn isValid(view: abi.IdaRangeSetView) bool {
    if (view.reserved != 0) return false;
    if (view.request_count == 0 or view.max_ranges == 0 or view.max_selected == 0) return false;
    if (view.nbits == 0) return true;
    return view.bits_addr != 0 and view.max_scan != 0;
}

fn asBitmap(view: abi.IdaRangeSetView) abi.BitmapView {
    if (!isValid(view)) return .{ .words_addr = 0, .nbits = 0, .word_count = 0 };
    return .{
        .words_addr = view.bits_addr,
        .nbits = view.nbits,
        .word_count = bitmap_view.wordCount(view.nbits),
    };
}

pub fn summarize(view: abi.IdaRangeSetView) abi.IdaRangeSetSummary {
    if (!isValid(view)) {
        return .{
            .scanned_count = 0,
            .request_count = 0,
            .candidate_range_count = 0,
            .selected_range_count = 0,
            .first_selected_id = 0,
            .last_selected_id = 0,
            .flags = 0,
            .reserved = 0,
        };
    }

    const scanned: u32 = @min(view.nbits, view.max_scan);
    const bitmap = asBitmap(view);
    var summary = abi.IdaRangeSetSummary{
        .scanned_count = scanned,
        .request_count = view.request_count,
        .candidate_range_count = 0,
        .selected_range_count = 0,
        .first_selected_id = view.base_id + scanned,
        .last_selected_id = view.base_id + scanned,
        .flags = if (scanned < view.nbits) abi.IDA_RANGE_SET_FLAG_TRUNCATED else 0,
        .reserved = 0,
    };
    var next_allowed_start: u32 = 0;

    if (scanned < view.request_count) {
        summary.flags |= abi.IDA_RANGE_SET_FLAG_EXHAUSTED;
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

        summary.flags |= abi.IDA_RANGE_SET_FLAG_FOUND;
        if (summary.candidate_range_count < view.max_ranges) {
            summary.candidate_range_count += 1;
        } else {
            summary.flags |= abi.IDA_RANGE_SET_FLAG_TRUNCATED;
            continue;
        }

        if (start < next_allowed_start) continue;
        if (summary.selected_range_count < view.max_selected) {
            if ((summary.flags & abi.IDA_RANGE_SET_FLAG_SELECTED) == 0) {
                summary.first_selected_id = view.base_id + start;
            }
            summary.flags |= abi.IDA_RANGE_SET_FLAG_SELECTED;
            summary.last_selected_id = view.base_id + start;
            summary.selected_range_count += 1;
            next_allowed_start = start + view.request_count;
        } else {
            summary.flags |= abi.IDA_RANGE_SET_FLAG_TRUNCATED;
        }
    }

    if ((summary.flags & abi.IDA_RANGE_SET_FLAG_FOUND) == 0) {
        summary.flags |= abi.IDA_RANGE_SET_FLAG_EXHAUSTED;
    }
    return summary;
}

test "phase3 ida range-set helpers stay bounded and predictable" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const view = viewFromBits(words[0..], 100, 8, 6, 2, 4, 2);
    const summary = summarize(view);
    try std.testing.expect(isValid(view));
    try std.testing.expectEqual(@as(u32, 6), summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 2), summary.request_count);
    try std.testing.expectEqual(@as(u32, 2), summary.candidate_range_count);
    try std.testing.expectEqual(@as(u32, 2), summary.selected_range_count);
    try std.testing.expectEqual(@as(u32, 101), summary.first_selected_id);
    try std.testing.expectEqual(@as(u32, 104), summary.last_selected_id);
    try std.testing.expectEqual(@as(u32, abi.IDA_RANGE_SET_FLAG_TRUNCATED | abi.IDA_RANGE_SET_FLAG_FOUND | abi.IDA_RANGE_SET_FLAG_SELECTED), summary.flags);
}

test "phase3 ida range-set caps and exhaustion stay explicit" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const capped = viewFromBits(words[0..], 100, 8, 8, 2, 4, 1);
    const capped_summary = summarize(capped);
    try std.testing.expect(isValid(capped));
    try std.testing.expectEqual(@as(u32, 3), capped_summary.candidate_range_count);
    try std.testing.expectEqual(@as(u32, 1), capped_summary.selected_range_count);
    try std.testing.expectEqual(@as(u32, 101), capped_summary.first_selected_id);
    try std.testing.expectEqual(@as(u32, 101), capped_summary.last_selected_id);
    try std.testing.expectEqual(@as(u32, abi.IDA_RANGE_SET_FLAG_TRUNCATED | abi.IDA_RANGE_SET_FLAG_FOUND | abi.IDA_RANGE_SET_FLAG_SELECTED), capped_summary.flags);

    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};
    const exhausted = viewFromBits(exhausted_words[0..], 40, 5, 5, 2, 4, 2);
    const exhausted_summary = summarize(exhausted);
    try std.testing.expectEqual(@as(u32, 0), exhausted_summary.candidate_range_count);
    try std.testing.expectEqual(@as(u32, 0), exhausted_summary.selected_range_count);
    try std.testing.expectEqual(@as(u32, 45), exhausted_summary.first_selected_id);
    try std.testing.expectEqual(@as(u32, 45), exhausted_summary.last_selected_id);
    try std.testing.expectEqual(@as(u32, abi.IDA_RANGE_SET_FLAG_EXHAUSTED), exhausted_summary.flags);
}