const std = @import("std");
const abi = @import("abi_bindings");
const chrdev_xfer_plan = @import("chrdev_xfer_plan");

fn mapXferFlags(xfer_flags: u32) u32 {
    var flags: u32 = 0;
    if ((xfer_flags & abi.CHRDEV_XFER_FLAG_TRUNCATED) != 0) flags |= abi.CHRDEV_RESUME_FLAG_TRUNCATED;
    if ((xfer_flags & abi.CHRDEV_XFER_FLAG_FOUND) != 0) flags |= abi.CHRDEV_RESUME_FLAG_FOUND;
    if ((xfer_flags & abi.CHRDEV_XFER_FLAG_EXHAUSTED) != 0) flags |= abi.CHRDEV_RESUME_FLAG_EXHAUSTED;
    if ((xfer_flags & abi.CHRDEV_XFER_FLAG_HIT) != 0) flags |= abi.CHRDEV_RESUME_FLAG_HIT;
    if ((xfer_flags & abi.CHRDEV_XFER_FLAG_PERMITTED) != 0) flags |= abi.CHRDEV_RESUME_FLAG_PERMITTED;
    if ((xfer_flags & abi.CHRDEV_XFER_FLAG_DENIED) != 0) flags |= abi.CHRDEV_RESUME_FLAG_DENIED;
    if ((xfer_flags & abi.CHRDEV_XFER_FLAG_ROUTABLE) != 0) flags |= abi.CHRDEV_RESUME_FLAG_ROUTABLE;
    if ((xfer_flags & abi.CHRDEV_XFER_FLAG_BLOCKED) != 0) flags |= abi.CHRDEV_RESUME_FLAG_BLOCKED;
    if ((xfer_flags & abi.CHRDEV_XFER_FLAG_DISPATCHABLE) != 0) flags |= abi.CHRDEV_RESUME_FLAG_DISPATCHABLE;
    if ((xfer_flags & abi.CHRDEV_XFER_FLAG_RESUMED) != 0) flags |= abi.CHRDEV_RESUME_FLAG_RESUMED;
    if ((xfer_flags & abi.CHRDEV_XFER_FLAG_CONTINUABLE) != 0) flags |= abi.CHRDEV_RESUME_FLAG_CONTINUABLE;
    if ((xfer_flags & abi.CHRDEV_XFER_FLAG_COMPLETES) != 0) flags |= abi.CHRDEV_RESUME_FLAG_COMPLETES;
    return flags;
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
    resume_passes: u32,
) abi.ChrdevResumeView {
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
        .resume_passes = resume_passes,
        .reserved = 0,
    };
}

pub fn asChrdevXferView(view: abi.ChrdevResumeView) abi.ChrdevXferView {
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
            .file_offset = 0,
            .bytes_completed = 0,
            .max_segments = 0,
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
        .file_offset = view.file_offset,
        .bytes_completed = view.bytes_completed,
        .max_segments = view.max_segments,
        .reserved = 0,
    };
}

pub fn isValid(view: abi.ChrdevResumeView) bool {
    if (view.reserved != 0) return false;
    if (view.resume_passes == 0) return false;
    return chrdev_xfer_plan.isValid(asChrdevXferView(view));
}

pub fn summarize(view: abi.ChrdevResumeView) abi.ChrdevResumeSummary {
    if (!isValid(view)) {
        return .{
            .major = 0,
            .target_minor = 0,
            .selected_count = 0,
            .resolved_index = abi.CHRDEV_RESUME_INDEX_NONE,
            .resolved_dev = 0,
            .granted_mode = 0,
            .io_op = 0,
            .requested_bytes = 0,
            .start_offset = 0,
            .next_offset = 0,
            .initial_bytes_completed = 0,
            .final_bytes_completed = 0,
            .pass_count = 0,
            .issued_bytes = 0,
            .remaining_bytes = 0,
            .entry_ops = 0,
            .data_ops = 0,
            .exit_ops = 0,
            .blocked_ops = 0,
            .flags = 0,
        };
    }

    const start_offset = view.file_offset + view.bytes_completed;
    var current_completed = view.bytes_completed;
    var issued_total: u32 = 0;
    var pass_count: u32 = 0;
    var next_offset = start_offset;
    var flags: u32 = 0;
    var selected_count: u32 = 0;
    var resolved_index = abi.CHRDEV_RESUME_INDEX_NONE;
    var resolved_dev: u32 = 0;
    var granted_mode: u32 = 0;
    var entry_ops: u32 = 0;
    var data_ops: u32 = 0;
    var exit_ops: u32 = 0;
    var blocked_ops: u32 = 0;

    var pass_index: u32 = 0;
    while (pass_index < view.resume_passes) : (pass_index += 1) {
        var pass_view = asChrdevXferView(view);
        pass_view.bytes_completed = current_completed;
        const pass_summary = chrdev_xfer_plan.summarize(pass_view);

        selected_count = pass_summary.selected_count;
        resolved_index = pass_summary.resolved_index;
        resolved_dev = pass_summary.resolved_dev;
        granted_mode = pass_summary.granted_mode;
        entry_ops = pass_summary.entry_ops;
        data_ops = pass_summary.data_ops;
        exit_ops = pass_summary.exit_ops;
        blocked_ops = pass_summary.blocked_ops;
        flags |= mapXferFlags(pass_summary.flags);

        if (pass_summary.issued_bytes == 0) {
            if (pass_summary.requested_remaining != 0) flags |= abi.CHRDEV_RESUME_FLAG_STALLED;
            break;
        }

        pass_count += 1;
        issued_total += pass_summary.issued_bytes;
        current_completed += pass_summary.issued_bytes;
        next_offset = pass_summary.next_offset;

        if (pass_summary.remaining_bytes == 0) {
            flags |= abi.CHRDEV_RESUME_FLAG_COMPLETE_OK;
            break;
        }
    }

    if (issued_total != 0) flags |= abi.CHRDEV_RESUME_FLAG_PROGRESSED;

    return .{
        .major = view.major,
        .target_minor = view.target_minor,
        .selected_count = selected_count,
        .resolved_index = if (resolved_index == abi.CHRDEV_XFER_INDEX_NONE) abi.CHRDEV_RESUME_INDEX_NONE else resolved_index,
        .resolved_dev = resolved_dev,
        .granted_mode = granted_mode,
        .io_op = view.io_op,
        .requested_bytes = view.requested_bytes,
        .start_offset = start_offset,
        .next_offset = next_offset,
        .initial_bytes_completed = view.bytes_completed,
        .final_bytes_completed = current_completed,
        .pass_count = pass_count,
        .issued_bytes = issued_total,
        .remaining_bytes = view.requested_bytes - current_completed,
        .entry_ops = entry_ops,
        .data_ops = data_ops,
        .exit_ops = exit_ops,
        .blocked_ops = blocked_ops,
        .flags = flags,
    };
}

test "phase3 chrdev resume complete and continuable plans stay bounded" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};

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
        1,
        3,
    );
    const complete_summary = summarize(complete_view);
    try std.testing.expect(isValid(complete_view));
    try std.testing.expectEqual(@as(u32, 2), complete_summary.pass_count);
    try std.testing.expectEqual(@as(u32, 16), complete_summary.issued_bytes);
    try std.testing.expectEqual(@as(u32, 20), complete_summary.final_bytes_completed);
    try std.testing.expectEqual(@as(u32, 0), complete_summary.remaining_bytes);
    try std.testing.expectEqual(@as(u64, 1028), complete_summary.start_offset);
    try std.testing.expectEqual(@as(u64, 1044), complete_summary.next_offset);
    try std.testing.expect((complete_summary.flags & abi.CHRDEV_RESUME_FLAG_PROGRESSED) != 0);
    try std.testing.expect((complete_summary.flags & abi.CHRDEV_RESUME_FLAG_COMPLETE_OK) != 0);
    try std.testing.expect((complete_summary.flags & abi.CHRDEV_RESUME_FLAG_COMPLETES) != 0);

    const continuable_view = viewFromBits(
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
        1,
        1,
    );
    const continuable_summary = summarize(continuable_view);
    try std.testing.expectEqual(@as(u32, 1), continuable_summary.pass_count);
    try std.testing.expectEqual(@as(u32, 8), continuable_summary.issued_bytes);
    try std.testing.expectEqual(@as(u32, 12), continuable_summary.final_bytes_completed);
    try std.testing.expectEqual(@as(u32, 8), continuable_summary.remaining_bytes);
    try std.testing.expectEqual(@as(u64, 1028), continuable_summary.start_offset);
    try std.testing.expectEqual(@as(u64, 1036), continuable_summary.next_offset);
    try std.testing.expect((continuable_summary.flags & abi.CHRDEV_RESUME_FLAG_PROGRESSED) != 0);
    try std.testing.expect((continuable_summary.flags & abi.CHRDEV_RESUME_FLAG_CONTINUABLE) != 0);
    try std.testing.expect((continuable_summary.flags & abi.CHRDEV_RESUME_FLAG_COMPLETE_OK) == 0);
}

test "phase3 chrdev resume blocked and exhausted plans stay explicit" {
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
        3,
    );
    const blocked_summary = summarize(blocked_view);
    try std.testing.expectEqual(@as(u32, 0), blocked_summary.pass_count);
    try std.testing.expectEqual(@as(u32, 0), blocked_summary.issued_bytes);
    try std.testing.expectEqual(@as(u32, 8), blocked_summary.remaining_bytes);
    try std.testing.expectEqual(@as(u64, 2052), blocked_summary.start_offset);
    try std.testing.expectEqual(@as(u64, 2052), blocked_summary.next_offset);
    try std.testing.expect((blocked_summary.flags & abi.CHRDEV_RESUME_FLAG_BLOCKED) != 0);
    try std.testing.expect((blocked_summary.flags & abi.CHRDEV_RESUME_FLAG_RESUMED) != 0);
    try std.testing.expect((blocked_summary.flags & abi.CHRDEV_RESUME_FLAG_STALLED) != 0);
    try std.testing.expect((blocked_summary.flags & abi.CHRDEV_RESUME_FLAG_PROGRESSED) == 0);

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
        2,
    );
    const exhausted_summary = summarize(exhausted_view);
    try std.testing.expectEqual(@as(u32, 0), exhausted_summary.pass_count);
    try std.testing.expectEqual(@as(u32, 0), exhausted_summary.issued_bytes);
    try std.testing.expectEqual(@as(u32, 12), exhausted_summary.remaining_bytes);
    try std.testing.expect((exhausted_summary.flags & abi.CHRDEV_RESUME_FLAG_EXHAUSTED) != 0);
    try std.testing.expect((exhausted_summary.flags & abi.CHRDEV_RESUME_FLAG_STALLED) != 0);
}
