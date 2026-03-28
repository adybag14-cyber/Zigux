const std = @import("std");
const abi = @import("abi_bindings");
const chrdev_route_plan = @import("chrdev_route_plan");

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
    io_op: u32,
    requested_bytes: u32,
    max_chunk_bytes: u32,
) abi.ChrdevIoView {
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
        .io_op = io_op,
        .requested_bytes = requested_bytes,
        .max_chunk_bytes = max_chunk_bytes,
        .reserved = 0,
    };
}

pub fn isValid(view: abi.ChrdevIoView) bool {
    if (view.reserved != 0) return false;
    if (view.io_op != abi.CHRDEV_IO_OP_READ and view.io_op != abi.CHRDEV_IO_OP_WRITE) return false;
    if (view.requested_bytes == 0 or view.max_chunk_bytes == 0) return false;
    return chrdev_route_plan.isValid(asChrdevRouteView(view));
}

pub fn asChrdevRouteView(view: abi.ChrdevIoView) abi.ChrdevRouteView {
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
            .available_ops = 0,
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
        .available_ops = view.available_ops,
        .reserved = 0,
    };
}

pub fn summarize(view: abi.ChrdevIoView) abi.ChrdevIoSummary {
    if (!isValid(view)) {
        return .{
            .major = 0,
            .target_minor = 0,
            .selected_count = 0,
            .resolved_index = abi.CHRDEV_IO_INDEX_NONE,
            .resolved_dev = 0,
            .granted_mode = 0,
            .io_op = 0,
            .requested_bytes = 0,
            .chunk_bytes = 0,
            .entry_ops = 0,
            .data_ops = 0,
            .exit_ops = 0,
            .blocked_ops = 0,
            .flags = 0,
        };
    }

    const route_summary = chrdev_route_plan.summarize(asChrdevRouteView(view));
    const requested_data_op: u32 = switch (view.io_op) {
        abi.CHRDEV_IO_OP_READ => abi.CHRDEV_FOP_READ,
        abi.CHRDEV_IO_OP_WRITE => abi.CHRDEV_FOP_WRITE,
        else => 0,
    };

    var flags: u32 = 0;
    if ((route_summary.flags & abi.CHRDEV_ROUTE_FLAG_TRUNCATED) != 0) flags |= abi.CHRDEV_IO_FLAG_TRUNCATED;
    if ((route_summary.flags & abi.CHRDEV_ROUTE_FLAG_FOUND) != 0) flags |= abi.CHRDEV_IO_FLAG_FOUND;
    if ((route_summary.flags & abi.CHRDEV_ROUTE_FLAG_EXHAUSTED) != 0) flags |= abi.CHRDEV_IO_FLAG_EXHAUSTED;
    if ((route_summary.flags & abi.CHRDEV_ROUTE_FLAG_HIT) != 0) flags |= abi.CHRDEV_IO_FLAG_HIT;
    if ((route_summary.flags & abi.CHRDEV_ROUTE_FLAG_PERMITTED) != 0) flags |= abi.CHRDEV_IO_FLAG_PERMITTED;
    if ((route_summary.flags & abi.CHRDEV_ROUTE_FLAG_DENIED) != 0) flags |= abi.CHRDEV_IO_FLAG_DENIED;

    var blocked_ops = route_summary.blocked_ops;
    var chunk_bytes: u32 = 0;
    var entry_ops: u32 = 0;
    var data_ops: u32 = 0;
    var exit_ops: u32 = 0;

    if ((flags & abi.CHRDEV_IO_FLAG_PERMITTED) != 0 and (flags & abi.CHRDEV_IO_FLAG_HIT) != 0) {
        const has_data_op = (route_summary.data_ops & requested_data_op) != 0;
        const op_blocked = (route_summary.blocked_ops & requested_data_op) != 0;
        if (has_data_op and !op_blocked and route_summary.entry_ops != 0 and route_summary.exit_ops != 0) {
            entry_ops = route_summary.entry_ops;
            data_ops = requested_data_op;
            exit_ops = route_summary.exit_ops;
            chunk_bytes = @min(view.requested_bytes, view.max_chunk_bytes);
            flags |= abi.CHRDEV_IO_FLAG_ROUTABLE | abi.CHRDEV_IO_FLAG_DISPATCHABLE;
        } else {
            blocked_ops |= requested_data_op;
            flags |= abi.CHRDEV_IO_FLAG_BLOCKED;
        }
    }

    return .{
        .major = route_summary.major,
        .target_minor = route_summary.target_minor,
        .selected_count = route_summary.selected_count,
        .resolved_index = if (route_summary.resolved_index == abi.CHRDEV_ROUTE_INDEX_NONE) abi.CHRDEV_IO_INDEX_NONE else route_summary.resolved_index,
        .resolved_dev = route_summary.resolved_dev,
        .granted_mode = route_summary.granted_mode,
        .io_op = view.io_op,
        .requested_bytes = view.requested_bytes,
        .chunk_bytes = chunk_bytes,
        .entry_ops = entry_ops,
        .data_ops = data_ops,
        .exit_ops = exit_ops,
        .blocked_ops = blocked_ops,
        .flags = flags,
    };
}

test "phase3 chrdev io dispatchable paths stay bounded and explicit" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};

    const read_view = viewFromBits(
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
        abi.CHRDEV_IO_OP_READ,
        16,
        8,
    );
    const read_summary = summarize(read_view);
    try std.testing.expect(isValid(read_view));
    try std.testing.expectEqual(@as(u32, 8), read_summary.chunk_bytes);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_OPEN), read_summary.entry_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_READ), read_summary.data_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_RELEASE), read_summary.exit_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_IO_FLAG_TRUNCATED | abi.CHRDEV_IO_FLAG_FOUND | abi.CHRDEV_IO_FLAG_HIT | abi.CHRDEV_IO_FLAG_PERMITTED | abi.CHRDEV_IO_FLAG_ROUTABLE | abi.CHRDEV_IO_FLAG_DISPATCHABLE), read_summary.flags);

    const partial_write_view = viewFromBits(
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
        abi.CHRDEV_IO_OP_WRITE,
        12,
        32,
    );
    const partial_write_summary = summarize(partial_write_view);
    try std.testing.expectEqual(@as(u32, 12), partial_write_summary.chunk_bytes);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_WRITE), partial_write_summary.data_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_READ), partial_write_summary.blocked_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_IO_FLAG_FOUND | abi.CHRDEV_IO_FLAG_HIT | abi.CHRDEV_IO_FLAG_PERMITTED | abi.CHRDEV_IO_FLAG_ROUTABLE | abi.CHRDEV_IO_FLAG_DISPATCHABLE), partial_write_summary.flags);
}

test "phase3 chrdev io blocked, denied, miss, and exhaustion stay explicit" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};

    const blocked_read_view = viewFromBits(
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
        abi.CHRDEV_IO_OP_READ,
        12,
        32,
    );
    const blocked_read_summary = summarize(blocked_read_view);
    try std.testing.expectEqual(@as(u32, 0), blocked_read_summary.chunk_bytes);
    try std.testing.expectEqual(@as(u32, 0), blocked_read_summary.data_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_READ), blocked_read_summary.blocked_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_IO_FLAG_FOUND | abi.CHRDEV_IO_FLAG_HIT | abi.CHRDEV_IO_FLAG_PERMITTED | abi.CHRDEV_IO_FLAG_BLOCKED), blocked_read_summary.flags);

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
        abi.CHRDEV_IO_OP_WRITE,
        12,
        32,
    );
    const denied_summary = summarize(denied_view);
    try std.testing.expectEqual(@as(u32, 0), denied_summary.chunk_bytes);
    try std.testing.expectEqual(@as(u32, 0), denied_summary.blocked_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_IO_FLAG_FOUND | abi.CHRDEV_IO_FLAG_HIT | abi.CHRDEV_IO_FLAG_DENIED), denied_summary.flags);

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
        abi.CHRDEV_IO_OP_READ,
        12,
        32,
    );
    const miss_summary = summarize(miss_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_IO_INDEX_NONE), miss_summary.resolved_index);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_IO_FLAG_FOUND), miss_summary.flags);

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
        abi.CHRDEV_IO_OP_READ,
        12,
        32,
    );
    const exhausted_summary = summarize(exhausted_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_IO_INDEX_NONE), exhausted_summary.resolved_index);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_IO_FLAG_EXHAUSTED), exhausted_summary.flags);
}
