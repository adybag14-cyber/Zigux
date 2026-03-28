const std = @import("std");
const abi = @import("abi_bindings");
const chrdev_open_plan = @import("chrdev_open_plan");

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
    available_ops: u32,
) abi.ChrdevFopsView {
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
        .available_ops = available_ops,
        .reserved = 0,
    };
}

pub fn isValid(view: abi.ChrdevFopsView) bool {
    if (view.reserved != 0) return false;
    if ((view.available_ops & ~(abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE)) != 0) return false;
    const open_view = asChrdevOpenView(view);
    return chrdev_open_plan.isValid(open_view);
}

pub fn asChrdevOpenView(view: abi.ChrdevFopsView) abi.ChrdevOpenView {
    if (view.reserved != 0) {
        return .{
            .bits_addr = 0,
            .major = 0,
            .first_minor = 0,
            .minor_count = 0,
            .max_scan = 0,
            .request_count = 0,
            .policy = 0,
            .target_minor = 0,
            .requested_mode = 0,
            .supported_mode = 0,
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
        .requested_mode = view.requested_mode,
        .supported_mode = view.supported_mode,
        .reserved = 0,
    };
}

pub fn summarize(view: abi.ChrdevFopsView) abi.ChrdevFopsSummary {
    if (!isValid(view)) {
        return .{
            .major = 0,
            .target_minor = 0,
            .selected_count = 0,
            .resolved_index = abi.CHRDEV_FOPS_INDEX_NONE,
            .resolved_dev = 0,
            .granted_mode = 0,
            .available_ops = 0,
            .required_ops = 0,
            .missing_ops = 0,
            .flags = 0,
        };
    }

    const open_summary = chrdev_open_plan.summarize(asChrdevOpenView(view));
    var flags: u32 = 0;
    if ((open_summary.flags & abi.CHRDEV_OPEN_FLAG_TRUNCATED) != 0) flags |= abi.CHRDEV_FOPS_FLAG_TRUNCATED;
    if ((open_summary.flags & abi.CHRDEV_OPEN_FLAG_FOUND) != 0) flags |= abi.CHRDEV_FOPS_FLAG_FOUND;
    if ((open_summary.flags & abi.CHRDEV_OPEN_FLAG_EXHAUSTED) != 0) flags |= abi.CHRDEV_FOPS_FLAG_EXHAUSTED;
    if ((open_summary.flags & abi.CHRDEV_OPEN_FLAG_HIT) != 0) flags |= abi.CHRDEV_FOPS_FLAG_HIT;
    if ((open_summary.flags & abi.CHRDEV_OPEN_FLAG_PERMITTED) != 0) flags |= abi.CHRDEV_FOPS_FLAG_PERMITTED;
    if ((open_summary.flags & abi.CHRDEV_OPEN_FLAG_DENIED) != 0) flags |= abi.CHRDEV_FOPS_FLAG_DENIED;

    var required_ops: u32 = 0;
    var missing_ops: u32 = 0;
    if ((flags & abi.CHRDEV_FOPS_FLAG_PERMITTED) != 0 and (flags & abi.CHRDEV_FOPS_FLAG_HIT) != 0) {
        required_ops |= abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE;
        if ((open_summary.granted_mode & abi.CHRDEV_MODE_READ) != 0) required_ops |= abi.CHRDEV_FOP_READ;
        if ((open_summary.granted_mode & abi.CHRDEV_MODE_WRITE) != 0) required_ops |= abi.CHRDEV_FOP_WRITE;
        missing_ops = required_ops & ~view.available_ops;
        if (missing_ops == 0 and required_ops != 0) {
            flags |= abi.CHRDEV_FOPS_FLAG_ROUTABLE;
        } else if (missing_ops != 0) {
            flags |= abi.CHRDEV_FOPS_FLAG_MISSING_OPS;
        }
    }

    return .{
        .major = open_summary.major,
        .target_minor = open_summary.target_minor,
        .selected_count = open_summary.selected_count,
        .resolved_index = if (open_summary.resolved_index == abi.CHRDEV_OPEN_INDEX_NONE) abi.CHRDEV_FOPS_INDEX_NONE else open_summary.resolved_index,
        .resolved_dev = open_summary.resolved_dev,
        .granted_mode = open_summary.granted_mode,
        .available_ops = view.available_ops,
        .required_ops = required_ops,
        .missing_ops = missing_ops,
        .flags = flags,
    };
}

test "phase3 chrdev fops routable path stays bounded and explicit" {
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
        abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE,
    );
    const summary = summarize(view);
    try std.testing.expect(isValid(view));
    try std.testing.expectEqual(@as(u32, 240), summary.major);
    try std.testing.expectEqual(@as(u32, 34), summary.target_minor);
    try std.testing.expectEqual(@as(u32, 2), summary.selected_count);
    try std.testing.expectEqual(@as(u32, 1), summary.resolved_index);
    try std.testing.expectEqual(@as(u32, 251658274), summary.resolved_dev);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE), summary.granted_mode);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE), summary.available_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE), summary.required_ops);
    try std.testing.expectEqual(@as(u32, 0), summary.missing_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOPS_FLAG_TRUNCATED | abi.CHRDEV_FOPS_FLAG_FOUND | abi.CHRDEV_FOPS_FLAG_HIT | abi.CHRDEV_FOPS_FLAG_PERMITTED | abi.CHRDEV_FOPS_FLAG_ROUTABLE), summary.flags);
}

test "phase3 chrdev fops missing ops, denied, miss, and exhaustion stay explicit" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const missing_view = viewFromBits(
        words[0..],
        240,
        32,
        8,
        8,
        2,
        abi.IDA_POLICY_LAST_FIT,
        37,
        abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE,
        abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE,
        abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE,
    );
    const missing_summary = summarize(missing_view);
    try std.testing.expectEqual(@as(u32, 2), missing_summary.selected_count);
    try std.testing.expectEqual(@as(u32, 1), missing_summary.resolved_index);
    try std.testing.expectEqual(@as(u32, 251658277), missing_summary.resolved_dev);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE), missing_summary.required_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_READ), missing_summary.missing_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOPS_FLAG_FOUND | abi.CHRDEV_FOPS_FLAG_HIT | abi.CHRDEV_FOPS_FLAG_PERMITTED | abi.CHRDEV_FOPS_FLAG_MISSING_OPS), missing_summary.flags);

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
        abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE,
    );
    const denied_summary = summarize(denied_view);
    try std.testing.expectEqual(@as(u32, 0), denied_summary.required_ops);
    try std.testing.expectEqual(@as(u32, 0), denied_summary.missing_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOPS_FLAG_FOUND | abi.CHRDEV_FOPS_FLAG_HIT | abi.CHRDEV_FOPS_FLAG_DENIED), denied_summary.flags);

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
        abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ,
    );
    const miss_summary = summarize(miss_view);
    try std.testing.expectEqual(@as(u32, 2), miss_summary.selected_count);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOPS_INDEX_NONE), miss_summary.resolved_index);
    try std.testing.expectEqual(@as(u32, 0), miss_summary.required_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOPS_FLAG_FOUND), miss_summary.flags);

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
        abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ,
    );
    const exhausted_summary = summarize(exhausted_view);
    try std.testing.expectEqual(@as(u32, 0), exhausted_summary.selected_count);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOPS_INDEX_NONE), exhausted_summary.resolved_index);
    try std.testing.expectEqual(@as(u32, 0), exhausted_summary.required_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOPS_FLAG_EXHAUSTED), exhausted_summary.flags);
}
