const std = @import("std");
const abi = @import("abi_bindings");
const ida_policy_view = @import("ida_policy_view");

pub fn viewFromBits(bits: []const usize, major: u32, first_minor: u32, minor_count: u32, max_scan: u32, request_count: u32, policy: u32) abi.MinorAllocView {
    return .{
        .bits_addr = if (bits.len == 0) 0 else @intFromPtr(&bits[0]),
        .major = major,
        .first_minor = first_minor,
        .minor_count = minor_count,
        .max_scan = max_scan,
        .request_count = request_count,
        .policy = policy,
        .reserved = 0,
    };
}

pub fn isValid(view: abi.MinorAllocView) bool {
    if (view.reserved != 0) return false;
    if (view.request_count == 0) return false;
    if (view.policy != abi.IDA_POLICY_FIRST_FIT and view.policy != abi.IDA_POLICY_LAST_FIT) return false;
    if (view.minor_count == 0) return true;
    return view.bits_addr != 0 and view.max_scan != 0;
}

pub fn asIdaPolicyView(view: abi.MinorAllocView) abi.IdaPolicyView {
    if (!isValid(view)) return .{ .bits_addr = 0, .base_id = 0, .nbits = 0, .max_scan = 0, .request_count = 0, .policy = 0, .reserved = 0 };
    return .{
        .bits_addr = view.bits_addr,
        .base_id = view.first_minor,
        .nbits = view.minor_count,
        .max_scan = view.max_scan,
        .request_count = view.request_count,
        .policy = view.policy,
        .reserved = 0,
    };
}

pub fn summarize(view: abi.MinorAllocView) abi.MinorAllocSummary {
    if (!isValid(view)) {
        return .{
            .major = 0,
            .scanned_count = 0,
            .request_count = 0,
            .selected_minor_start = 0,
            .selected_minor_end = 0,
            .alternate_minor_start = 0,
            .longest_free_run = 0,
            .flags = 0,
        };
    }

    const ida_summary = ida_policy_view.summarize(asIdaPolicyView(view));
    var flags: u32 = 0;
    if ((ida_summary.flags & abi.IDA_POLICY_FLAG_TRUNCATED) != 0) flags |= abi.MINOR_ALLOC_FLAG_TRUNCATED;
    if ((ida_summary.flags & abi.IDA_POLICY_FLAG_FOUND) != 0) flags |= abi.MINOR_ALLOC_FLAG_FOUND;
    if ((ida_summary.flags & abi.IDA_POLICY_FLAG_EXHAUSTED) != 0) flags |= abi.MINOR_ALLOC_FLAG_EXHAUSTED;

    return .{
        .major = view.major,
        .scanned_count = ida_summary.scanned_count,
        .request_count = ida_summary.request_count,
        .selected_minor_start = ida_summary.selected_fit_id,
        .selected_minor_end = if ((flags & abi.MINOR_ALLOC_FLAG_FOUND) != 0) ida_summary.selected_fit_id + view.request_count - 1 else ida_summary.selected_fit_id,
        .alternate_minor_start = ida_summary.alternate_fit_id,
        .longest_free_run = ida_summary.longest_free_run,
        .flags = flags,
    };
}

test "phase3 minor alloc first-fit stays bounded and explicit" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const view = viewFromBits(words[0..], 240, 32, 8, 6, 2, abi.IDA_POLICY_FIRST_FIT);
    const summary = summarize(view);
    try std.testing.expect(isValid(view));
    try std.testing.expectEqual(@as(u32, 240), summary.major);
    try std.testing.expectEqual(@as(u32, 6), summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 2), summary.request_count);
    try std.testing.expectEqual(@as(u32, 33), summary.selected_minor_start);
    try std.testing.expectEqual(@as(u32, 34), summary.selected_minor_end);
    try std.testing.expectEqual(@as(u32, 36), summary.alternate_minor_start);
    try std.testing.expectEqual(@as(u32, 2), summary.longest_free_run);
    try std.testing.expectEqual(@as(u32, abi.MINOR_ALLOC_FLAG_TRUNCATED | abi.MINOR_ALLOC_FLAG_FOUND), summary.flags);
}

test "phase3 minor alloc last-fit and exhaustion stay explicit" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const last_fit_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT);
    const last_fit_summary = summarize(last_fit_view);
    try std.testing.expectEqual(@as(u32, 36), last_fit_summary.selected_minor_start);
    try std.testing.expectEqual(@as(u32, 37), last_fit_summary.selected_minor_end);
    try std.testing.expectEqual(@as(u32, 33), last_fit_summary.alternate_minor_start);
    try std.testing.expectEqual(@as(u32, 3), last_fit_summary.longest_free_run);
    try std.testing.expectEqual(@as(u32, abi.MINOR_ALLOC_FLAG_FOUND), last_fit_summary.flags);

    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};
    const exhausted_view = viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT);
    const exhausted_summary = summarize(exhausted_view);
    try std.testing.expectEqual(@as(u32, 21), exhausted_summary.selected_minor_start);
    try std.testing.expectEqual(@as(u32, 21), exhausted_summary.selected_minor_end);
    try std.testing.expectEqual(@as(u32, 21), exhausted_summary.alternate_minor_start);
    try std.testing.expectEqual(@as(u32, 1), exhausted_summary.longest_free_run);
    try std.testing.expectEqual(@as(u32, abi.MINOR_ALLOC_FLAG_EXHAUSTED), exhausted_summary.flags);
}
