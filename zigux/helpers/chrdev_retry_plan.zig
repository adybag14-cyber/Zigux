const std = @import("std");
const abi = @import("abi_bindings");
const chrdev_resume_plan = @import("chrdev_resume_plan");

fn mapResumeFlags(resume_flags: u32) u32 {
    var flags: u32 = 0;
    if ((resume_flags & abi.CHRDEV_RESUME_FLAG_TRUNCATED) != 0) flags |= abi.CHRDEV_RETRY_FLAG_TRUNCATED;
    if ((resume_flags & abi.CHRDEV_RESUME_FLAG_FOUND) != 0) flags |= abi.CHRDEV_RETRY_FLAG_FOUND;
    if ((resume_flags & abi.CHRDEV_RESUME_FLAG_EXHAUSTED) != 0) flags |= abi.CHRDEV_RETRY_FLAG_EXHAUSTED;
    if ((resume_flags & abi.CHRDEV_RESUME_FLAG_HIT) != 0) flags |= abi.CHRDEV_RETRY_FLAG_HIT;
    if ((resume_flags & abi.CHRDEV_RESUME_FLAG_PERMITTED) != 0) flags |= abi.CHRDEV_RETRY_FLAG_PERMITTED;
    if ((resume_flags & abi.CHRDEV_RESUME_FLAG_DENIED) != 0) flags |= abi.CHRDEV_RETRY_FLAG_DENIED;
    if ((resume_flags & abi.CHRDEV_RESUME_FLAG_ROUTABLE) != 0) flags |= abi.CHRDEV_RETRY_FLAG_ROUTABLE;
    if ((resume_flags & abi.CHRDEV_RESUME_FLAG_BLOCKED) != 0) flags |= abi.CHRDEV_RETRY_FLAG_BLOCKED;
    if ((resume_flags & abi.CHRDEV_RESUME_FLAG_DISPATCHABLE) != 0) flags |= abi.CHRDEV_RETRY_FLAG_DISPATCHABLE;
    if ((resume_flags & abi.CHRDEV_RESUME_FLAG_RESUMED) != 0) flags |= abi.CHRDEV_RETRY_FLAG_RESUMED;
    if ((resume_flags & abi.CHRDEV_RESUME_FLAG_CONTINUABLE) != 0) flags |= abi.CHRDEV_RETRY_FLAG_CONTINUABLE;
    if ((resume_flags & abi.CHRDEV_RESUME_FLAG_COMPLETES) != 0) flags |= abi.CHRDEV_RETRY_FLAG_COMPLETES;
    if ((resume_flags & abi.CHRDEV_RESUME_FLAG_PROGRESSED) != 0) flags |= abi.CHRDEV_RETRY_FLAG_PROGRESSED;
    if ((resume_flags & abi.CHRDEV_RESUME_FLAG_STALLED) != 0) flags |= abi.CHRDEV_RETRY_FLAG_STALLED;
    if ((resume_flags & abi.CHRDEV_RESUME_FLAG_COMPLETE_OK) != 0) flags |= abi.CHRDEV_RETRY_FLAG_COMPLETE_OK;
    return flags;
}

fn ceilDiv(value: u32, step: u32) u32 {
    if (value == 0) return 0;
    return 1 + ((value - 1) / step);
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
    retry_budget: u32,
    stall_budget: u32,
    backoff_quanta: u32,
) abi.ChrdevRetryView {
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
        .retry_budget = retry_budget,
        .stall_budget = stall_budget,
        .backoff_quanta = backoff_quanta,
        .reserved = 0,
    };
}

pub fn asChrdevResumeView(view: abi.ChrdevRetryView) abi.ChrdevResumeView {
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
            .resume_passes = 0,
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
        .resume_passes = view.resume_passes,
        .reserved = 0,
    };
}

pub fn isValid(view: abi.ChrdevRetryView) bool {
    if (view.reserved != 0) return false;
    return chrdev_resume_plan.isValid(asChrdevResumeView(view));
}

pub fn summarize(view: abi.ChrdevRetryView) abi.ChrdevRetrySummary {
    if (!isValid(view)) {
        return .{
            .major = 0,
            .target_minor = 0,
            .selected_count = 0,
            .resolved_index = abi.CHRDEV_RETRY_INDEX_NONE,
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
            .retry_count = 0,
            .stall_count = 0,
            .remaining_retry_budget = 0,
            .backoff_ticks = 0,
            .flags = 0,
        };
    }

    const resume_summary = chrdev_resume_plan.summarize(asChrdevResumeView(view));
    var flags = mapResumeFlags(resume_summary.flags);
    const stall_count: u32 = if ((flags & abi.CHRDEV_RETRY_FLAG_STALLED) != 0) 1 else 0;
    const remaining = resume_summary.remaining_bytes;
    const progress_quantum: u32 = if (resume_summary.pass_count != 0 and resume_summary.issued_bytes != 0)
        ceilDiv(resume_summary.issued_bytes, resume_summary.pass_count)
    else
        0;

    var retry_count: u32 = 0;
    var remaining_retry_budget = view.retry_budget;
    var backoff_ticks: u32 = 0;
    var needed_retries: u32 = 0;
    var retryable = false;

    if (remaining != 0 and (flags & abi.CHRDEV_RETRY_FLAG_PERMITTED) != 0 and (flags & abi.CHRDEV_RETRY_FLAG_DENIED) == 0 and (flags & abi.CHRDEV_RETRY_FLAG_EXHAUSTED) == 0) {
        if ((flags & abi.CHRDEV_RETRY_FLAG_CONTINUABLE) != 0 and progress_quantum != 0) {
            retryable = true;
            needed_retries = ceilDiv(remaining, progress_quantum);
        } else if ((flags & abi.CHRDEV_RETRY_FLAG_STALLED) != 0) {
            retryable = true;
            needed_retries = 1;
        }
    }

    if (retryable) {
        flags |= abi.CHRDEV_RETRY_FLAG_RETRYABLE;
        if (view.retry_budget == 0 or stall_count > view.stall_budget) {
            flags |= abi.CHRDEV_RETRY_FLAG_RETRY_EXHAUSTED | abi.CHRDEV_RETRY_FLAG_FAILS;
            remaining_retry_budget = 0;
        } else {
            retry_count = @min(needed_retries, view.retry_budget);
            if (retry_count != 0) {
                flags |= abi.CHRDEV_RETRY_FLAG_RETRY_PLANNED;
                remaining_retry_budget = view.retry_budget - retry_count;
                if (stall_count != 0 and view.backoff_quanta != 0) {
                    flags |= abi.CHRDEV_RETRY_FLAG_BACKOFF_APPLIED;
                    backoff_ticks = retry_count * view.backoff_quanta;
                }
            }
            if (needed_retries > view.retry_budget) {
                flags |= abi.CHRDEV_RETRY_FLAG_RETRY_EXHAUSTED;
            }
        }
    } else if (remaining != 0 and ((flags & abi.CHRDEV_RETRY_FLAG_DENIED) != 0 or (flags & abi.CHRDEV_RETRY_FLAG_EXHAUSTED) != 0 or (flags & abi.CHRDEV_RETRY_FLAG_BLOCKED) != 0 or (flags & abi.CHRDEV_RETRY_FLAG_STALLED) != 0)) {
        flags |= abi.CHRDEV_RETRY_FLAG_FAILS;
        if ((flags & abi.CHRDEV_RETRY_FLAG_EXHAUSTED) != 0) {
            flags |= abi.CHRDEV_RETRY_FLAG_RETRY_EXHAUSTED;
            remaining_retry_budget = 0;
        }
    }

    return .{
        .major = resume_summary.major,
        .target_minor = resume_summary.target_minor,
        .selected_count = resume_summary.selected_count,
        .resolved_index = if (resume_summary.resolved_index == abi.CHRDEV_RESUME_INDEX_NONE) abi.CHRDEV_RETRY_INDEX_NONE else resume_summary.resolved_index,
        .resolved_dev = resume_summary.resolved_dev,
        .granted_mode = resume_summary.granted_mode,
        .io_op = resume_summary.io_op,
        .requested_bytes = resume_summary.requested_bytes,
        .start_offset = resume_summary.start_offset,
        .next_offset = resume_summary.next_offset,
        .initial_bytes_completed = resume_summary.initial_bytes_completed,
        .final_bytes_completed = resume_summary.final_bytes_completed,
        .pass_count = resume_summary.pass_count,
        .issued_bytes = resume_summary.issued_bytes,
        .remaining_bytes = resume_summary.remaining_bytes,
        .entry_ops = resume_summary.entry_ops,
        .data_ops = resume_summary.data_ops,
        .exit_ops = resume_summary.exit_ops,
        .blocked_ops = resume_summary.blocked_ops,
        .retry_count = retry_count,
        .stall_count = stall_count,
        .remaining_retry_budget = remaining_retry_budget,
        .backoff_ticks = backoff_ticks,
        .flags = flags,
    };
}

test "phase3 chrdev retry complete and continuable plans stay bounded" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};

    const complete_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5);
    const complete_summary = summarize(complete_view);
    try std.testing.expect(isValid(complete_view));
    try std.testing.expectEqual(@as(u32, 0), complete_summary.retry_count);
    try std.testing.expectEqual(@as(u32, 0), complete_summary.stall_count);
    try std.testing.expectEqual(@as(u32, 2), complete_summary.remaining_retry_budget);
    try std.testing.expectEqual(@as(u32, 0), complete_summary.backoff_ticks);
    try std.testing.expect((complete_summary.flags & abi.CHRDEV_RETRY_FLAG_COMPLETE_OK) != 0);
    try std.testing.expect((complete_summary.flags & abi.CHRDEV_RETRY_FLAG_RETRY_PLANNED) == 0);

    const continuable_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 1, 2, 1, 0);
    const continuable_summary = summarize(continuable_view);
    try std.testing.expectEqual(@as(u32, 1), continuable_summary.retry_count);
    try std.testing.expectEqual(@as(u32, 1), continuable_summary.remaining_retry_budget);
    try std.testing.expect((continuable_summary.flags & abi.CHRDEV_RETRY_FLAG_RETRYABLE) != 0);
    try std.testing.expect((continuable_summary.flags & abi.CHRDEV_RETRY_FLAG_RETRY_PLANNED) != 0);
    try std.testing.expect((continuable_summary.flags & abi.CHRDEV_RETRY_FLAG_RETRY_EXHAUSTED) == 0);
}

test "phase3 chrdev retry stalled and budget-limited plans stay explicit" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};

    const stalled_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_READ, 12, 32, 2048, 4, 2, 3, 2, 1, 5);
    const stalled_summary = summarize(stalled_view);
    try std.testing.expectEqual(@as(u32, 1), stalled_summary.retry_count);
    try std.testing.expectEqual(@as(u32, 1), stalled_summary.stall_count);
    try std.testing.expectEqual(@as(u32, 1), stalled_summary.remaining_retry_budget);
    try std.testing.expectEqual(@as(u32, 5), stalled_summary.backoff_ticks);
    try std.testing.expect((stalled_summary.flags & abi.CHRDEV_RETRY_FLAG_RETRYABLE) != 0);
    try std.testing.expect((stalled_summary.flags & abi.CHRDEV_RETRY_FLAG_RETRY_PLANNED) != 0);
    try std.testing.expect((stalled_summary.flags & abi.CHRDEV_RETRY_FLAG_BACKOFF_APPLIED) != 0);
    try std.testing.expect((stalled_summary.flags & abi.CHRDEV_RETRY_FLAG_FAILS) == 0);

    const budget_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 36, 8, 1024, 4, 1, 1, 2, 1, 0);
    const budget_summary = summarize(budget_view);
    try std.testing.expectEqual(@as(u32, 2), budget_summary.retry_count);
    try std.testing.expectEqual(@as(u32, 0), budget_summary.remaining_retry_budget);
    try std.testing.expect((budget_summary.flags & abi.CHRDEV_RETRY_FLAG_RETRYABLE) != 0);
    try std.testing.expect((budget_summary.flags & abi.CHRDEV_RETRY_FLAG_RETRY_PLANNED) != 0);
    try std.testing.expect((budget_summary.flags & abi.CHRDEV_RETRY_FLAG_RETRY_EXHAUSTED) != 0);
}

test "phase3 chrdev retry denied and exhausted plans stay explicit" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};

    const denied_view = viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 12, 8, 512, 0, 2, 2, 2, 1, 5);
    const denied_summary = summarize(denied_view);
    try std.testing.expectEqual(@as(u32, 0), denied_summary.retry_count);
    try std.testing.expectEqual(@as(u32, 1), denied_summary.stall_count);
    try std.testing.expectEqual(@as(u32, 2), denied_summary.remaining_retry_budget);
    try std.testing.expect((denied_summary.flags & abi.CHRDEV_RETRY_FLAG_DENIED) != 0);
    try std.testing.expect((denied_summary.flags & abi.CHRDEV_RETRY_FLAG_FAILS) != 0);
    try std.testing.expect((denied_summary.flags & abi.CHRDEV_RETRY_FLAG_RETRYABLE) == 0);

    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};
    const exhausted_view = viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5);
    const exhausted_summary = summarize(exhausted_view);
    try std.testing.expectEqual(@as(u32, 0), exhausted_summary.retry_count);
    try std.testing.expectEqual(@as(u32, 1), exhausted_summary.stall_count);
    try std.testing.expectEqual(@as(u32, 0), exhausted_summary.remaining_retry_budget);
    try std.testing.expect((exhausted_summary.flags & abi.CHRDEV_RETRY_FLAG_EXHAUSTED) != 0);
    try std.testing.expect((exhausted_summary.flags & abi.CHRDEV_RETRY_FLAG_RETRY_EXHAUSTED) != 0);
    try std.testing.expect((exhausted_summary.flags & abi.CHRDEV_RETRY_FLAG_FAILS) != 0);
}
