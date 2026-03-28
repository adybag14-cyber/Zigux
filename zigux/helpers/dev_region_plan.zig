const std = @import("std");
const abi = @import("abi_bindings");
const minor_alloc_plan = @import("minor_alloc_plan");

pub fn mkdev(major: u32, minor: u32) u32 {
    return (major << abi.DEV_MINOR_BITS) | (minor & abi.DEV_MINOR_MASK);
}

pub fn viewFromBits(bits: []const usize, major: u32, first_minor: u32, minor_count: u32, max_scan: u32, request_count: u32, policy: u32) abi.DevRegionView {
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

pub fn isValid(view: abi.DevRegionView) bool {
    if (view.reserved != 0) return false;
    if (view.request_count == 0) return false;
    if (view.policy != abi.IDA_POLICY_FIRST_FIT and view.policy != abi.IDA_POLICY_LAST_FIT) return false;
    if (view.minor_count == 0) return true;
    return view.bits_addr != 0 and view.max_scan != 0;
}

pub fn asMinorAllocView(view: abi.DevRegionView) abi.MinorAllocView {
    if (!isValid(view)) return .{ .bits_addr = 0, .major = 0, .first_minor = 0, .minor_count = 0, .max_scan = 0, .request_count = 0, .policy = 0, .reserved = 0 };
    return .{
        .bits_addr = view.bits_addr,
        .major = view.major,
        .first_minor = view.first_minor,
        .minor_count = view.minor_count,
        .max_scan = view.max_scan,
        .request_count = view.request_count,
        .policy = view.policy,
        .reserved = 0,
    };
}

pub fn summarize(view: abi.DevRegionView) abi.DevRegionSummary {
    if (!isValid(view)) {
        return .{
            .major = 0,
            .scanned_count = 0,
            .request_count = 0,
            .selected_minor_start = 0,
            .selected_minor_end = 0,
            .first_dev = 0,
            .last_dev = 0,
            .flags = 0,
        };
    }

    const minor_summary = minor_alloc_plan.summarize(asMinorAllocView(view));
    var flags: u32 = 0;
    if ((minor_summary.flags & abi.MINOR_ALLOC_FLAG_TRUNCATED) != 0) flags |= abi.DEV_REGION_FLAG_TRUNCATED;
    if ((minor_summary.flags & abi.MINOR_ALLOC_FLAG_FOUND) != 0) flags |= abi.DEV_REGION_FLAG_FOUND;
    if ((minor_summary.flags & abi.MINOR_ALLOC_FLAG_EXHAUSTED) != 0) flags |= abi.DEV_REGION_FLAG_EXHAUSTED;

    return .{
        .major = minor_summary.major,
        .scanned_count = minor_summary.scanned_count,
        .request_count = minor_summary.request_count,
        .selected_minor_start = minor_summary.selected_minor_start,
        .selected_minor_end = minor_summary.selected_minor_end,
        .first_dev = mkdev(minor_summary.major, minor_summary.selected_minor_start),
        .last_dev = mkdev(minor_summary.major, minor_summary.selected_minor_end),
        .flags = flags,
    };
}

test "phase3 dev region first-fit stays bounded and encodes dev numbers" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const view = viewFromBits(words[0..], 240, 32, 8, 6, 2, abi.IDA_POLICY_FIRST_FIT);
    const summary = summarize(view);
    try std.testing.expect(isValid(view));
    try std.testing.expectEqual(@as(u32, 240), summary.major);
    try std.testing.expectEqual(@as(u32, 6), summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 2), summary.request_count);
    try std.testing.expectEqual(@as(u32, 33), summary.selected_minor_start);
    try std.testing.expectEqual(@as(u32, 34), summary.selected_minor_end);
    try std.testing.expectEqual(mkdev(240, 33), summary.first_dev);
    try std.testing.expectEqual(mkdev(240, 34), summary.last_dev);
    try std.testing.expectEqual(@as(u32, abi.DEV_REGION_FLAG_TRUNCATED | abi.DEV_REGION_FLAG_FOUND), summary.flags);
}

test "phase3 dev region last-fit and exhaustion stay explicit" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const last_fit_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT);
    const last_fit_summary = summarize(last_fit_view);
    try std.testing.expectEqual(@as(u32, 36), last_fit_summary.selected_minor_start);
    try std.testing.expectEqual(@as(u32, 37), last_fit_summary.selected_minor_end);
    try std.testing.expectEqual(mkdev(240, 36), last_fit_summary.first_dev);
    try std.testing.expectEqual(mkdev(240, 37), last_fit_summary.last_dev);
    try std.testing.expectEqual(@as(u32, abi.DEV_REGION_FLAG_FOUND), last_fit_summary.flags);

    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};
    const exhausted_view = viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT);
    const exhausted_summary = summarize(exhausted_view);
    try std.testing.expectEqual(@as(u32, 21), exhausted_summary.selected_minor_start);
    try std.testing.expectEqual(@as(u32, 21), exhausted_summary.selected_minor_end);
    try std.testing.expectEqual(mkdev(240, 21), exhausted_summary.first_dev);
    try std.testing.expectEqual(mkdev(240, 21), exhausted_summary.last_dev);
    try std.testing.expectEqual(@as(u32, abi.DEV_REGION_FLAG_EXHAUSTED), exhausted_summary.flags);
}
