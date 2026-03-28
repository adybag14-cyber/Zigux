const std = @import("std");
const abi = @import("abi_bindings");
const cdev_lookup_plan = @import("cdev_lookup_plan");

pub fn viewFromBits(
    bits: []const usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    target_minor: u32,
    requested_mode: u32,
    supported_mode: u32,
) abi.ChrdevOpenView {
    return .{
        .bits_addr = if (bits.len == 0) 0 else @intFromPtr(&bits[0]),
        .major = major,
        .first_minor = first_minor,
        .minor_count = minor_count,
        .max_scan = max_scan,
        .request_count = request_count,
        .policy = policy,
        .target_minor = target_minor,
        .requested_mode = requested_mode,
        .supported_mode = supported_mode,
        .reserved = 0,
    };
}

pub fn isValid(view: abi.ChrdevOpenView) bool {
    if (view.reserved != 0) return false;
    if (view.request_count == 0) return false;
    if (view.policy != abi.IDA_POLICY_FIRST_FIT and view.policy != abi.IDA_POLICY_LAST_FIT) return false;
    if (view.requested_mode == 0) return false;
    if ((view.requested_mode & ~(abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE)) != 0) return false;
    if ((view.supported_mode & ~(abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE)) != 0) return false;
    if (view.minor_count == 0) return true;
    return view.bits_addr != 0 and view.max_scan != 0;
}

pub fn asCdevLookupView(view: abi.ChrdevOpenView) abi.CdevLookupView {
    if (!isValid(view)) {
        return .{
            .bits_addr = 0,
            .major = 0,
            .first_minor = 0,
            .minor_count = 0,
            .max_scan = 0,
            .request_count = 0,
            .policy = 0,
            .target_minor = 0,
            .reserved = 0,
        };
    }

    return .{
        .bits_addr = view.bits_addr,
        .major = view.major,
        .first_minor = view.first_minor,
        .minor_count = view.minor_count,
        .max_scan = view.max_scan,
        .request_count = view.request_count,
        .policy = view.policy,
        .target_minor = view.target_minor,
        .reserved = 0,
    };
}

pub fn summarize(view: abi.ChrdevOpenView) abi.ChrdevOpenSummary {
    if (!isValid(view)) {
        return .{
            .major = 0,
            .target_minor = 0,
            .selected_count = 0,
            .resolved_index = abi.CHRDEV_OPEN_INDEX_NONE,
            .resolved_dev = 0,
            .requested_mode = 0,
            .supported_mode = 0,
            .granted_mode = 0,
            .denied_mode = 0,
            .flags = 0,
        };
    }

    const lookup_summary = cdev_lookup_plan.summarize(asCdevLookupView(view));
    var flags: u32 = 0;
    if ((lookup_summary.flags & abi.CDEV_LOOKUP_FLAG_TRUNCATED) != 0) flags |= abi.CHRDEV_OPEN_FLAG_TRUNCATED;
    if ((lookup_summary.flags & abi.CDEV_LOOKUP_FLAG_FOUND) != 0) flags |= abi.CHRDEV_OPEN_FLAG_FOUND;
    if ((lookup_summary.flags & abi.CDEV_LOOKUP_FLAG_EXHAUSTED) != 0) flags |= abi.CHRDEV_OPEN_FLAG_EXHAUSTED;

    var granted_mode: u32 = 0;
    var denied_mode: u32 = 0;
    if ((lookup_summary.flags & abi.CDEV_LOOKUP_FLAG_HIT) != 0) {
        flags |= abi.CHRDEV_OPEN_FLAG_HIT;
        denied_mode = view.requested_mode & ~view.supported_mode;
        if (denied_mode == 0) {
            flags |= abi.CHRDEV_OPEN_FLAG_PERMITTED;
            granted_mode = view.requested_mode;
        } else {
            flags |= abi.CHRDEV_OPEN_FLAG_DENIED;
        }
    }

    return .{
        .major = lookup_summary.major,
        .target_minor = lookup_summary.target_minor,
        .selected_count = lookup_summary.selected_count,
        .resolved_index = lookup_summary.resolved_index,
        .resolved_dev = lookup_summary.resolved_dev,
        .requested_mode = view.requested_mode,
        .supported_mode = view.supported_mode,
        .granted_mode = granted_mode,
        .denied_mode = denied_mode,
        .flags = flags,
    };
}

test "phase3 chrdev open permitted path stays bounded and explicit" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const view = viewFromBits(
        words[0..],
        240,
        32,
        8,
        6,
        2,
        abi.IDA_POLICY_FIRST_FIT,
        34,
        abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE,
        abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE,
    );
    const summary = summarize(view);
    try std.testing.expect(isValid(view));
    try std.testing.expectEqual(@as(u32, 240), summary.major);
    try std.testing.expectEqual(@as(u32, 34), summary.target_minor);
    try std.testing.expectEqual(@as(u32, 2), summary.selected_count);
    try std.testing.expectEqual(@as(u32, 1), summary.resolved_index);
    try std.testing.expectEqual(@as(u32, 251658274), summary.resolved_dev);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE), summary.granted_mode);
    try std.testing.expectEqual(@as(u32, 0), summary.denied_mode);
    try std.testing.expectEqual(
        @as(u32, abi.CHRDEV_OPEN_FLAG_TRUNCATED | abi.CHRDEV_OPEN_FLAG_FOUND | abi.CHRDEV_OPEN_FLAG_HIT | abi.CHRDEV_OPEN_FLAG_PERMITTED),
        summary.flags,
    );
}

test "phase3 chrdev open denied, miss, and exhaustion stay explicit" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const denied_view = viewFromBits(
        words[0..],
        240,
        32,
        8,
        8,
        2,
        abi.IDA_POLICY_LAST_FIT,
        37,
        abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE,
        abi.CHRDEV_MODE_READ,
    );
    const denied_summary = summarize(denied_view);
    try std.testing.expectEqual(@as(u32, 2), denied_summary.selected_count);
    try std.testing.expectEqual(@as(u32, 1), denied_summary.resolved_index);
    try std.testing.expectEqual(@as(u32, 251658277), denied_summary.resolved_dev);
    try std.testing.expectEqual(@as(u32, 0), denied_summary.granted_mode);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_MODE_WRITE), denied_summary.denied_mode);
    try std.testing.expectEqual(
        @as(u32, abi.CHRDEV_OPEN_FLAG_FOUND | abi.CHRDEV_OPEN_FLAG_HIT | abi.CHRDEV_OPEN_FLAG_DENIED),
        denied_summary.flags,
    );

    const miss_view = viewFromBits(
        words[0..],
        240,
        32,
        8,
        8,
        2,
        abi.IDA_POLICY_LAST_FIT,
        35,
        abi.CHRDEV_MODE_READ,
        abi.CHRDEV_MODE_READ,
    );
    const miss_summary = summarize(miss_view);
    try std.testing.expectEqual(@as(u32, 2), miss_summary.selected_count);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_OPEN_INDEX_NONE), miss_summary.resolved_index);
    try std.testing.expectEqual(@as(u32, 0), miss_summary.resolved_dev);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_OPEN_FLAG_FOUND), miss_summary.flags);

    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};
    const exhausted_view = viewFromBits(
        exhausted_words[0..],
        240,
        16,
        5,
        5,
        2,
        abi.IDA_POLICY_FIRST_FIT,
        20,
        abi.CHRDEV_MODE_READ,
        abi.CHRDEV_MODE_READ,
    );
    const exhausted_summary = summarize(exhausted_view);
    try std.testing.expectEqual(@as(u32, 0), exhausted_summary.selected_count);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_OPEN_INDEX_NONE), exhausted_summary.resolved_index);
    try std.testing.expectEqual(@as(u32, 0), exhausted_summary.resolved_dev);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_OPEN_FLAG_EXHAUSTED), exhausted_summary.flags);
}
