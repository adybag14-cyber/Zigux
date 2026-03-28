const std = @import("std");
const abi = @import("abi_bindings");
const cdev_add_plan = @import("cdev_add_plan");

pub fn viewFromBits(bits: []const usize, major: u32, first_minor: u32, minor_count: u32, max_scan: u32, request_count: u32, policy: u32, target_minor: u32) abi.CdevLookupView {
    return .{
        .bits_addr = if (bits.len == 0) 0 else @intFromPtr(&bits[0]),
        .major = major,
        .first_minor = first_minor,
        .minor_count = minor_count,
        .max_scan = max_scan,
        .request_count = request_count,
        .policy = policy,
        .target_minor = target_minor,
        .reserved = 0,
    };
}

pub fn isValid(view: abi.CdevLookupView) bool {
    if (view.reserved != 0) return false;
    if (view.request_count == 0) return false;
    if (view.policy != abi.IDA_POLICY_FIRST_FIT and view.policy != abi.IDA_POLICY_LAST_FIT) return false;
    if (view.minor_count == 0) return true;
    return view.bits_addr != 0 and view.max_scan != 0;
}

pub fn asCdevAddView(view: abi.CdevLookupView) abi.CdevAddView {
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

pub fn summarize(view: abi.CdevLookupView) abi.CdevLookupSummary {
    if (!isValid(view)) {
        return .{
            .major = 0,
            .scanned_count = 0,
            .request_count = 0,
            .selected_count = 0,
            .first_minor = 0,
            .target_minor = 0,
            .resolved_index = abi.CDEV_LOOKUP_INDEX_NONE,
            .resolved_dev = 0,
            .flags = 0,
        };
    }

    const add_summary = cdev_add_plan.summarize(asCdevAddView(view));
    var flags: u32 = 0;
    if ((add_summary.flags & abi.CDEV_ADD_FLAG_TRUNCATED) != 0) flags |= abi.CDEV_LOOKUP_FLAG_TRUNCATED;
    if ((add_summary.flags & abi.CDEV_ADD_FLAG_FOUND) != 0) flags |= abi.CDEV_LOOKUP_FLAG_FOUND;
    if ((add_summary.flags & abi.CDEV_ADD_FLAG_EXHAUSTED) != 0) flags |= abi.CDEV_LOOKUP_FLAG_EXHAUSTED;

    var resolved_index: u32 = abi.CDEV_LOOKUP_INDEX_NONE;
    var resolved_dev: u32 = 0;
    if ((flags & abi.CDEV_LOOKUP_FLAG_FOUND) != 0 and add_summary.selected_count != 0) {
        const last_minor = add_summary.first_minor + add_summary.selected_count - 1;
        if (view.target_minor >= add_summary.first_minor and view.target_minor <= last_minor) {
            flags |= abi.CDEV_LOOKUP_FLAG_HIT;
            resolved_index = view.target_minor - add_summary.first_minor;
            resolved_dev = add_summary.first_dev + resolved_index;
        }
    }

    return .{
        .major = add_summary.major,
        .scanned_count = add_summary.scanned_count,
        .request_count = add_summary.request_count,
        .selected_count = add_summary.selected_count,
        .first_minor = add_summary.first_minor,
        .target_minor = view.target_minor,
        .resolved_index = resolved_index,
        .resolved_dev = resolved_dev,
        .flags = flags,
    };
}

test "phase3 cdev lookup hit stays bounded and explicit" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const hit_view = viewFromBits(words[0..], 240, 32, 8, 6, 2, abi.IDA_POLICY_FIRST_FIT, 34);
    const hit_summary = summarize(hit_view);
    try std.testing.expect(isValid(hit_view));
    try std.testing.expectEqual(@as(u32, 240), hit_summary.major);
    try std.testing.expectEqual(@as(u32, 6), hit_summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 2), hit_summary.request_count);
    try std.testing.expectEqual(@as(u32, 2), hit_summary.selected_count);
    try std.testing.expectEqual(@as(u32, 33), hit_summary.first_minor);
    try std.testing.expectEqual(@as(u32, 34), hit_summary.target_minor);
    try std.testing.expectEqual(@as(u32, 1), hit_summary.resolved_index);
    try std.testing.expectEqual(@as(u32, 251658274), hit_summary.resolved_dev);
    try std.testing.expectEqual(@as(u32, abi.CDEV_LOOKUP_FLAG_TRUNCATED | abi.CDEV_LOOKUP_FLAG_FOUND | abi.CDEV_LOOKUP_FLAG_HIT), hit_summary.flags);
}

test "phase3 cdev lookup miss and exhaustion stay explicit" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const miss_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 35);
    const miss_summary = summarize(miss_view);
    try std.testing.expectEqual(@as(u32, 2), miss_summary.selected_count);
    try std.testing.expectEqual(@as(u32, 36), miss_summary.first_minor);
    try std.testing.expectEqual(@as(u32, 35), miss_summary.target_minor);
    try std.testing.expectEqual(@as(u32, abi.CDEV_LOOKUP_INDEX_NONE), miss_summary.resolved_index);
    try std.testing.expectEqual(@as(u32, 0), miss_summary.resolved_dev);
    try std.testing.expectEqual(@as(u32, abi.CDEV_LOOKUP_FLAG_FOUND), miss_summary.flags);

    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};
    const exhausted_view = viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20);
    const exhausted_summary = summarize(exhausted_view);
    try std.testing.expectEqual(@as(u32, 0), exhausted_summary.selected_count);
    try std.testing.expectEqual(@as(u32, 21), exhausted_summary.first_minor);
    try std.testing.expectEqual(@as(u32, 20), exhausted_summary.target_minor);
    try std.testing.expectEqual(@as(u32, abi.CDEV_LOOKUP_INDEX_NONE), exhausted_summary.resolved_index);
    try std.testing.expectEqual(@as(u32, 0), exhausted_summary.resolved_dev);
    try std.testing.expectEqual(@as(u32, abi.CDEV_LOOKUP_FLAG_EXHAUSTED), exhausted_summary.flags);
}
