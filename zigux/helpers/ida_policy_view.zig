const std = @import("std");
const abi = @import("abi_bindings");
const bitmap_view = @import("bitmap_view");
const narrow = @import("narrow_unsafe");

pub fn viewFromBits(bits: []const usize, base_id: u32, nbits: u32, max_scan: u32, request_count: u32, policy: u32) abi.IdaPolicyView {
    return .{
        .bits_addr = if (bits.len == 0) 0 else narrow.addressOf(&bits[0]),
        .base_id = base_id,
        .nbits = nbits,
        .max_scan = max_scan,
        .request_count = request_count,
        .policy = policy,
        .reserved = 0,
    };
}

pub fn isValid(view: abi.IdaPolicyView) bool {
    if (view.reserved != 0) return false;
    if (view.request_count == 0) return false;
    if (view.policy != abi.IDA_POLICY_FIRST_FIT and view.policy != abi.IDA_POLICY_LAST_FIT) return false;
    if (view.nbits == 0) return true;
    return view.bits_addr != 0 and view.max_scan != 0;
}

fn asBitmap(view: abi.IdaPolicyView) abi.BitmapView {
    if (!isValid(view)) return .{ .words_addr = 0, .nbits = 0, .word_count = 0 };
    return .{
        .words_addr = view.bits_addr,
        .nbits = view.nbits,
        .word_count = bitmap_view.wordCount(view.nbits),
    };
}

pub fn summarize(view: abi.IdaPolicyView) abi.IdaPolicySummary {
    if (!isValid(view)) {
        return .{
            .scanned_count = 0,
            .request_count = 0,
            .selected_fit_id = 0,
            .alternate_fit_id = 0,
            .longest_free_run = 0,
            .flags = 0,
        };
    }

    const scanned: u32 = @min(view.nbits, view.max_scan);
    const bitmap = asBitmap(view);
    var summary = abi.IdaPolicySummary{
        .scanned_count = scanned,
        .request_count = view.request_count,
        .selected_fit_id = view.base_id + scanned,
        .alternate_fit_id = view.base_id + scanned,
        .longest_free_run = 0,
        .flags = if (scanned < view.nbits) abi.IDA_POLICY_FLAG_TRUNCATED else 0,
    };
    var current_run: u32 = 0;
    var current_start: u32 = 0;
    var first_candidate: u32 = 0;
    var last_candidate: u32 = 0;
    var have_candidate = false;
    var index: u32 = 0;
    while (index < scanned) : (index += 1) {
        if (bitmap_view.testBit(bitmap, index)) {
            current_run = 0;
            continue;
        }

        if (current_run == 0) current_start = index;
        current_run += 1;
        if (current_run > summary.longest_free_run) summary.longest_free_run = current_run;
        if (current_run < view.request_count) continue;

        if (!have_candidate) {
            first_candidate = view.base_id + current_start;
            have_candidate = true;
        }
        last_candidate = view.base_id + current_start;
    }

    if (!have_candidate) {
        summary.flags |= abi.IDA_POLICY_FLAG_EXHAUSTED;
        return summary;
    }

    summary.flags |= abi.IDA_POLICY_FLAG_FOUND;
    if (view.policy == abi.IDA_POLICY_LAST_FIT) {
        summary.selected_fit_id = last_candidate;
        summary.alternate_fit_id = first_candidate;
    } else {
        summary.selected_fit_id = first_candidate;
        summary.alternate_fit_id = last_candidate;
    }
    return summary;
}

test "phase3 ida policy first-fit stays bounded and predictable" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const view = viewFromBits(words[0..], 100, 8, 6, 2, abi.IDA_POLICY_FIRST_FIT);
    const summary = summarize(view);
    try std.testing.expect(isValid(view));
    try std.testing.expectEqual(@as(u32, 6), summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 2), summary.request_count);
    try std.testing.expectEqual(@as(u32, 101), summary.selected_fit_id);
    try std.testing.expectEqual(@as(u32, 104), summary.alternate_fit_id);
    try std.testing.expectEqual(@as(u32, 2), summary.longest_free_run);
    try std.testing.expectEqual(@as(u32, abi.IDA_POLICY_FLAG_TRUNCATED | abi.IDA_POLICY_FLAG_FOUND), summary.flags);
}

test "phase3 ida policy last-fit and exhaustion stay explicit" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const last_fit = viewFromBits(words[0..], 100, 8, 8, 2, abi.IDA_POLICY_LAST_FIT);
    const last_fit_summary = summarize(last_fit);
    try std.testing.expect(isValid(last_fit));
    try std.testing.expectEqual(@as(u32, 104), last_fit_summary.selected_fit_id);
    try std.testing.expectEqual(@as(u32, 101), last_fit_summary.alternate_fit_id);
    try std.testing.expectEqual(@as(u32, 3), last_fit_summary.longest_free_run);
    try std.testing.expectEqual(@as(u32, abi.IDA_POLICY_FLAG_FOUND), last_fit_summary.flags);

    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};
    const exhausted = viewFromBits(exhausted_words[0..], 40, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT);
    const exhausted_summary = summarize(exhausted);
    try std.testing.expectEqual(@as(u32, 45), exhausted_summary.selected_fit_id);
    try std.testing.expectEqual(@as(u32, 45), exhausted_summary.alternate_fit_id);
    try std.testing.expectEqual(@as(u32, 1), exhausted_summary.longest_free_run);
    try std.testing.expectEqual(@as(u32, abi.IDA_POLICY_FLAG_EXHAUSTED), exhausted_summary.flags);
}
