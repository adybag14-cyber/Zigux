const std = @import("std");
const abi = @import("abi_bindings");
const chrdev_io_plan = @import("chrdev_io_plan");

fn ceilDivU32(value: u32, step: u32) u32 {
    return if (value == 0) 0 else 1 + ((value - 1) / step);
}

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
    file_offset: u64,
    bytes_completed: u32,
    max_segments: u32,
) abi.ChrdevXferView {
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
        .file_offset = file_offset,
        .bytes_completed = bytes_completed,
        .max_segments = max_segments,
        .reserved = 0,
    };
}

pub fn isValid(view: abi.ChrdevXferView) bool {
    if (view.reserved != 0) return false;
    if (view.max_segments == 0) return false;
    if (view.bytes_completed > view.requested_bytes) return false;
    _ = std.math.add(u64, view.file_offset, view.bytes_completed) catch return false;
    return chrdev_io_plan.isValid(asChrdevIoView(view));
}

pub fn asChrdevIoView(view: abi.ChrdevXferView) abi.ChrdevIoView {
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
            .io_op = 0,
            .requested_bytes = 0,
            .max_chunk_bytes = 0,
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
        .io_op = view.io_op,
        .requested_bytes = view.requested_bytes,
        .max_chunk_bytes = view.max_chunk_bytes,
        .reserved = 0,
    };
}

pub fn summarize(view: abi.ChrdevXferView) abi.ChrdevXferSummary {
    if (!isValid(view)) {
        return .{
            .major = 0,
            .target_minor = 0,
            .selected_count = 0,
            .resolved_index = abi.CHRDEV_XFER_INDEX_NONE,
            .resolved_dev = 0,
            .granted_mode = 0,
            .io_op = 0,
            .requested_bytes = 0,
            .start_offset = 0,
            .next_offset = 0,
            .bytes_completed = 0,
            .requested_remaining = 0,
            .segment_count = 0,
            .first_chunk_bytes = 0,
            .final_chunk_bytes = 0,
            .issued_bytes = 0,
            .remaining_bytes = 0,
            .entry_ops = 0,
            .data_ops = 0,
            .exit_ops = 0,
            .blocked_ops = 0,
            .flags = 0,
        };
    }

    const io_summary = chrdev_io_plan.summarize(asChrdevIoView(view));
    const requested_remaining = view.requested_bytes - view.bytes_completed;
    const start_offset = view.file_offset + view.bytes_completed;

    var flags: u32 = 0;
    if ((io_summary.flags & abi.CHRDEV_IO_FLAG_TRUNCATED) != 0) flags |= abi.CHRDEV_XFER_FLAG_TRUNCATED;
    if ((io_summary.flags & abi.CHRDEV_IO_FLAG_FOUND) != 0) flags |= abi.CHRDEV_XFER_FLAG_FOUND;
    if ((io_summary.flags & abi.CHRDEV_IO_FLAG_EXHAUSTED) != 0) flags |= abi.CHRDEV_XFER_FLAG_EXHAUSTED;
    if ((io_summary.flags & abi.CHRDEV_IO_FLAG_HIT) != 0) flags |= abi.CHRDEV_XFER_FLAG_HIT;
    if ((io_summary.flags & abi.CHRDEV_IO_FLAG_PERMITTED) != 0) flags |= abi.CHRDEV_XFER_FLAG_PERMITTED;
    if ((io_summary.flags & abi.CHRDEV_IO_FLAG_DENIED) != 0) flags |= abi.CHRDEV_XFER_FLAG_DENIED;
    if ((io_summary.flags & abi.CHRDEV_IO_FLAG_ROUTABLE) != 0) flags |= abi.CHRDEV_XFER_FLAG_ROUTABLE;
    if ((io_summary.flags & abi.CHRDEV_IO_FLAG_BLOCKED) != 0) flags |= abi.CHRDEV_XFER_FLAG_BLOCKED;
    if ((io_summary.flags & abi.CHRDEV_IO_FLAG_DISPATCHABLE) != 0) flags |= abi.CHRDEV_XFER_FLAG_DISPATCHABLE;
    if (view.bytes_completed != 0) flags |= abi.CHRDEV_XFER_FLAG_RESUMED;

    var segment_count: u32 = 0;
    var first_chunk_bytes: u32 = 0;
    var final_chunk_bytes: u32 = 0;
    var issued_bytes: u32 = 0;
    var remaining_bytes = requested_remaining;
    var next_offset = start_offset;

    if ((flags & abi.CHRDEV_XFER_FLAG_DISPATCHABLE) != 0 and requested_remaining != 0) {
        const needed_segments = ceilDivU32(requested_remaining, view.max_chunk_bytes);
        segment_count = @min(view.max_segments, needed_segments);
        first_chunk_bytes = @min(requested_remaining, view.max_chunk_bytes);
        const issued_u64 = @min(
            @as(u64, requested_remaining),
            @as(u64, segment_count) * @as(u64, view.max_chunk_bytes),
        );
        issued_bytes = @intCast(issued_u64);
        remaining_bytes = requested_remaining - issued_bytes;
        final_chunk_bytes = if (segment_count == 0)
            0
        else if (segment_count == 1)
            issued_bytes
        else
            issued_bytes - (view.max_chunk_bytes * (segment_count - 1));
        next_offset = start_offset + issued_bytes;
        if (remaining_bytes == 0)
            flags |= abi.CHRDEV_XFER_FLAG_COMPLETES
        else
            flags |= abi.CHRDEV_XFER_FLAG_CONTINUABLE;
    } else if ((flags & abi.CHRDEV_XFER_FLAG_DISPATCHABLE) != 0 and requested_remaining == 0) {
        flags |= abi.CHRDEV_XFER_FLAG_COMPLETES;
    }

    return .{
        .major = io_summary.major,
        .target_minor = io_summary.target_minor,
        .selected_count = io_summary.selected_count,
        .resolved_index = if (io_summary.resolved_index == abi.CHRDEV_IO_INDEX_NONE) abi.CHRDEV_XFER_INDEX_NONE else io_summary.resolved_index,
        .resolved_dev = io_summary.resolved_dev,
        .granted_mode = io_summary.granted_mode,
        .io_op = io_summary.io_op,
        .requested_bytes = io_summary.requested_bytes,
        .start_offset = start_offset,
        .next_offset = next_offset,
        .bytes_completed = view.bytes_completed,
        .requested_remaining = requested_remaining,
        .segment_count = segment_count,
        .first_chunk_bytes = first_chunk_bytes,
        .final_chunk_bytes = final_chunk_bytes,
        .issued_bytes = issued_bytes,
        .remaining_bytes = remaining_bytes,
        .entry_ops = io_summary.entry_ops,
        .data_ops = io_summary.data_ops,
        .exit_ops = io_summary.exit_ops,
        .blocked_ops = io_summary.blocked_ops,
        .flags = flags,
    };
}

test "phase3 chrdev xfer continuable and complete plans stay bounded" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};

    const continuable_view = viewFromBits(
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
        4096,
        0,
        1,
    );
    const continuable_summary = summarize(continuable_view);
    try std.testing.expect(isValid(continuable_view));
    try std.testing.expectEqual(@as(u32, 1), continuable_summary.segment_count);
    try std.testing.expectEqual(@as(u32, 8), continuable_summary.first_chunk_bytes);
    try std.testing.expectEqual(@as(u32, 8), continuable_summary.final_chunk_bytes);
    try std.testing.expectEqual(@as(u32, 8), continuable_summary.issued_bytes);
    try std.testing.expectEqual(@as(u32, 8), continuable_summary.remaining_bytes);
    try std.testing.expectEqual(@as(u64, 4096), continuable_summary.start_offset);
    try std.testing.expectEqual(@as(u64, 4104), continuable_summary.next_offset);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_XFER_FLAG_TRUNCATED | abi.CHRDEV_XFER_FLAG_FOUND | abi.CHRDEV_XFER_FLAG_HIT | abi.CHRDEV_XFER_FLAG_PERMITTED | abi.CHRDEV_XFER_FLAG_ROUTABLE | abi.CHRDEV_XFER_FLAG_DISPATCHABLE | abi.CHRDEV_XFER_FLAG_CONTINUABLE), continuable_summary.flags);

    const complete_view = viewFromBits(
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
        20,
        8,
        1024,
        4,
        3,
    );
    const complete_summary = summarize(complete_view);
    try std.testing.expectEqual(@as(u32, 2), complete_summary.segment_count);
    try std.testing.expectEqual(@as(u32, 8), complete_summary.first_chunk_bytes);
    try std.testing.expectEqual(@as(u32, 8), complete_summary.final_chunk_bytes);
    try std.testing.expectEqual(@as(u32, 16), complete_summary.issued_bytes);
    try std.testing.expectEqual(@as(u32, 0), complete_summary.remaining_bytes);
    try std.testing.expectEqual(@as(u64, 1028), complete_summary.start_offset);
    try std.testing.expectEqual(@as(u64, 1044), complete_summary.next_offset);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_READ), complete_summary.blocked_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_XFER_FLAG_FOUND | abi.CHRDEV_XFER_FLAG_HIT | abi.CHRDEV_XFER_FLAG_PERMITTED | abi.CHRDEV_XFER_FLAG_ROUTABLE | abi.CHRDEV_XFER_FLAG_DISPATCHABLE | abi.CHRDEV_XFER_FLAG_RESUMED | abi.CHRDEV_XFER_FLAG_COMPLETES), complete_summary.flags);
}

test "phase3 chrdev xfer blocked and exhausted plans stay explicit" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};

    const blocked_view = viewFromBits(
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
        2048,
        4,
        2,
    );
    const blocked_summary = summarize(blocked_view);
    try std.testing.expectEqual(@as(u32, 0), blocked_summary.segment_count);
    try std.testing.expectEqual(@as(u32, 0), blocked_summary.issued_bytes);
    try std.testing.expectEqual(@as(u32, 8), blocked_summary.requested_remaining);
    try std.testing.expectEqual(@as(u32, 8), blocked_summary.remaining_bytes);
    try std.testing.expectEqual(@as(u64, 2052), blocked_summary.start_offset);
    try std.testing.expectEqual(@as(u64, 2052), blocked_summary.next_offset);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_READ), blocked_summary.blocked_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_XFER_FLAG_FOUND | abi.CHRDEV_XFER_FLAG_HIT | abi.CHRDEV_XFER_FLAG_PERMITTED | abi.CHRDEV_XFER_FLAG_BLOCKED | abi.CHRDEV_XFER_FLAG_RESUMED), blocked_summary.flags);

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
        0,
        0,
        2,
    );
    const exhausted_summary = summarize(exhausted_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_XFER_INDEX_NONE), exhausted_summary.resolved_index);
    try std.testing.expectEqual(@as(u32, 0), exhausted_summary.segment_count);
    try std.testing.expectEqual(@as(u32, 12), exhausted_summary.requested_remaining);
    try std.testing.expectEqual(@as(u32, 12), exhausted_summary.remaining_bytes);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_XFER_FLAG_EXHAUSTED), exhausted_summary.flags);
}
