const std = @import("std");
const cpu_mask = @import("cpu_mask.zig");
const perf_buffer_poll = @import("perf_buffer_poll.zig");

pub const OnlineCpuCursor = struct {
    start_index: usize,
    next_scan_index: usize,
    cpu_index: ?usize,
    skipped_offline_count: usize,
};

pub const OnlineCpuRoutingDisposition = enum {
    complete,
    requested_subset,
    no_online_cpu,
    missing_buffer_slot,
    missing_buffer_fd,
};

pub const OnlineCpuRoutingSummary = struct {
    online_cpu_count: usize,
    requested_cpu_count: usize,
    selected_cpu_count: usize,
    buffer_slot_count: usize,
    routed_cpu_count: usize,
    first_routed_cpu_index: ?usize,
    next_online_cpu_index: ?usize,
    missing_buffer_index: ?usize,
    disposition: OnlineCpuRoutingDisposition,
};

pub fn advanceOnlineCpuCursor(
    online_cpu_mask: []const bool,
    start_index: usize,
) OnlineCpuCursor {
    if (start_index >= online_cpu_mask.len) {
        return .{
            .start_index = start_index,
            .next_scan_index = online_cpu_mask.len,
            .cpu_index = null,
            .skipped_offline_count = 0,
        };
    }

    var index = start_index;
    while (index < online_cpu_mask.len) : (index += 1) {
        if (online_cpu_mask[index]) {
            return .{
                .start_index = start_index,
                .next_scan_index = index + 1,
                .cpu_index = index,
                .skipped_offline_count = index - start_index,
            };
        }
    }

    return .{
        .start_index = start_index,
        .next_scan_index = online_cpu_mask.len,
        .cpu_index = null,
        .skipped_offline_count = online_cpu_mask.len - start_index,
    };
}

pub fn summarizeOnlineCpuRouting(
    online_cpu_mask: []const bool,
    requested_cpu_count: usize,
    buffer_fds: []const ?i32,
) OnlineCpuRoutingSummary {
    const online_cpu_count = cpu_mask.countPossibleCpus(online_cpu_mask);
    const selected_cpu_count = cpu_mask.derivePerfBufferAutoCpuCount(
        online_cpu_count,
        requested_cpu_count,
    );

    if (selected_cpu_count == 0) {
        return .{
            .online_cpu_count = online_cpu_count,
            .requested_cpu_count = requested_cpu_count,
            .selected_cpu_count = selected_cpu_count,
            .buffer_slot_count = buffer_fds.len,
            .routed_cpu_count = 0,
            .first_routed_cpu_index = null,
            .next_online_cpu_index = null,
            .missing_buffer_index = null,
            .disposition = .no_online_cpu,
        };
    }

    var cursor_index: usize = 0;
    var routed_cpu_count: usize = 0;
    var first_routed_cpu_index: ?usize = null;

    while (routed_cpu_count < selected_cpu_count) {
        const cursor = advanceOnlineCpuCursor(online_cpu_mask, cursor_index);
        const cpu_index = cursor.cpu_index orelse break;
        if (first_routed_cpu_index == null) first_routed_cpu_index = cpu_index;

        const lookup = perf_buffer_poll.summarizeBufferFdLookup(buffer_fds, routed_cpu_count);
        switch (lookup.disposition) {
            .found_fd => {
                routed_cpu_count += 1;
                cursor_index = cursor.next_scan_index;
            },
            .invalid_index => return .{
                .online_cpu_count = online_cpu_count,
                .requested_cpu_count = requested_cpu_count,
                .selected_cpu_count = selected_cpu_count,
                .buffer_slot_count = buffer_fds.len,
                .routed_cpu_count = routed_cpu_count,
                .first_routed_cpu_index = first_routed_cpu_index,
                .next_online_cpu_index = cpu_index,
                .missing_buffer_index = routed_cpu_count,
                .disposition = .missing_buffer_slot,
            },
            .missing_fd => return .{
                .online_cpu_count = online_cpu_count,
                .requested_cpu_count = requested_cpu_count,
                .selected_cpu_count = selected_cpu_count,
                .buffer_slot_count = buffer_fds.len,
                .routed_cpu_count = routed_cpu_count,
                .first_routed_cpu_index = first_routed_cpu_index,
                .next_online_cpu_index = cpu_index,
                .missing_buffer_index = routed_cpu_count,
                .disposition = .missing_buffer_fd,
            },
        }
    }

    const next_cursor = advanceOnlineCpuCursor(online_cpu_mask, cursor_index);
    return .{
        .online_cpu_count = online_cpu_count,
        .requested_cpu_count = requested_cpu_count,
        .selected_cpu_count = selected_cpu_count,
        .buffer_slot_count = buffer_fds.len,
        .routed_cpu_count = routed_cpu_count,
        .first_routed_cpu_index = first_routed_cpu_index,
        .next_online_cpu_index = if (selected_cpu_count < online_cpu_count)
            next_cursor.cpu_index
        else
            null,
        .missing_buffer_index = null,
        .disposition = if (requested_cpu_count != 0 and selected_cpu_count < online_cpu_count)
            .requested_subset
        else
            .complete,
    };
}

test "advanceOnlineCpuCursor walks sparse online CPU masks in order" {
    const mask = [_]bool{ false, true, false, true, true };

    const first = advanceOnlineCpuCursor(&mask, 0);
    try std.testing.expectEqual(@as(usize, 0), first.start_index);
    try std.testing.expectEqual(@as(?usize, 1), first.cpu_index);
    try std.testing.expectEqual(@as(usize, 2), first.next_scan_index);
    try std.testing.expectEqual(@as(usize, 1), first.skipped_offline_count);

    const second = advanceOnlineCpuCursor(&mask, first.next_scan_index);
    try std.testing.expectEqual(@as(usize, 2), second.start_index);
    try std.testing.expectEqual(@as(?usize, 3), second.cpu_index);
    try std.testing.expectEqual(@as(usize, 4), second.next_scan_index);
    try std.testing.expectEqual(@as(usize, 1), second.skipped_offline_count);

    const third = advanceOnlineCpuCursor(&mask, second.next_scan_index);
    try std.testing.expectEqual(@as(?usize, 4), third.cpu_index);
    try std.testing.expectEqual(@as(usize, 5), third.next_scan_index);
    try std.testing.expectEqual(@as(usize, 0), third.skipped_offline_count);

    const exhausted = advanceOnlineCpuCursor(&mask, third.next_scan_index);
    try std.testing.expectEqual(@as(?usize, null), exhausted.cpu_index);
    try std.testing.expectEqual(@as(usize, 5), exhausted.next_scan_index);
    try std.testing.expectEqual(@as(usize, 0), exhausted.skipped_offline_count);
}

test "summarizeOnlineCpuRouting auto-selects all online CPUs when request count is zero" {
    const summary = summarizeOnlineCpuRouting(
        &.{ true, false, true, true },
        0,
        &.{ 11, 17, 21 },
    );

    try std.testing.expectEqual(@as(usize, 3), summary.online_cpu_count);
    try std.testing.expectEqual(@as(usize, 3), summary.selected_cpu_count);
    try std.testing.expectEqual(@as(usize, 3), summary.routed_cpu_count);
    try std.testing.expectEqual(@as(?usize, 0), summary.first_routed_cpu_index);
    try std.testing.expectEqual(@as(?usize, null), summary.next_online_cpu_index);
    try std.testing.expectEqual(@as(?usize, null), summary.missing_buffer_index);
    try std.testing.expectEqual(OnlineCpuRoutingDisposition.complete, summary.disposition);
}

test "summarizeOnlineCpuRouting keeps requested subsets explicit without inventing missing buffers" {
    const summary = summarizeOnlineCpuRouting(
        &.{ false, true, true, false, true },
        2,
        &.{ 11, 17, 21 },
    );

    try std.testing.expectEqual(@as(usize, 3), summary.online_cpu_count);
    try std.testing.expectEqual(@as(usize, 2), summary.selected_cpu_count);
    try std.testing.expectEqual(@as(usize, 2), summary.routed_cpu_count);
    try std.testing.expectEqual(@as(?usize, 1), summary.first_routed_cpu_index);
    try std.testing.expectEqual(@as(?usize, 4), summary.next_online_cpu_index);
    try std.testing.expectEqual(@as(?usize, null), summary.missing_buffer_index);
    try std.testing.expectEqual(
        OnlineCpuRoutingDisposition.requested_subset,
        summary.disposition,
    );
}

test "summarizeOnlineCpuRouting reports the first online CPU that outgrows the buffer table" {
    const summary = summarizeOnlineCpuRouting(
        &.{ true, false, true, true },
        0,
        &.{ 11, 17 },
    );

    try std.testing.expectEqual(@as(usize, 3), summary.online_cpu_count);
    try std.testing.expectEqual(@as(usize, 3), summary.selected_cpu_count);
    try std.testing.expectEqual(@as(usize, 2), summary.routed_cpu_count);
    try std.testing.expectEqual(@as(?usize, 0), summary.first_routed_cpu_index);
    try std.testing.expectEqual(@as(?usize, 3), summary.next_online_cpu_index);
    try std.testing.expectEqual(@as(?usize, 2), summary.missing_buffer_index);
    try std.testing.expectEqual(
        OnlineCpuRoutingDisposition.missing_buffer_slot,
        summary.disposition,
    );
}

test "summarizeOnlineCpuRouting reports the first routed online CPU whose fd slot is empty" {
    const summary = summarizeOnlineCpuRouting(
        &.{ false, true, false, true, true },
        0,
        &.{ 11, null, 29 },
    );

    try std.testing.expectEqual(@as(usize, 3), summary.online_cpu_count);
    try std.testing.expectEqual(@as(usize, 3), summary.selected_cpu_count);
    try std.testing.expectEqual(@as(usize, 1), summary.routed_cpu_count);
    try std.testing.expectEqual(@as(?usize, 1), summary.first_routed_cpu_index);
    try std.testing.expectEqual(@as(?usize, 3), summary.next_online_cpu_index);
    try std.testing.expectEqual(@as(?usize, 1), summary.missing_buffer_index);
    try std.testing.expectEqual(
        OnlineCpuRoutingDisposition.missing_buffer_fd,
        summary.disposition,
    );
}

test "summarizeOnlineCpuRouting keeps empty masks compact and non-claiming" {
    const summary = summarizeOnlineCpuRouting(&.{ false, false }, 3, &.{});

    try std.testing.expectEqual(@as(usize, 0), summary.online_cpu_count);
    try std.testing.expectEqual(@as(usize, 0), summary.selected_cpu_count);
    try std.testing.expectEqual(@as(usize, 0), summary.routed_cpu_count);
    try std.testing.expectEqual(@as(?usize, null), summary.first_routed_cpu_index);
    try std.testing.expectEqual(@as(?usize, null), summary.next_online_cpu_index);
    try std.testing.expectEqual(@as(?usize, null), summary.missing_buffer_index);
    try std.testing.expectEqual(
        OnlineCpuRoutingDisposition.no_online_cpu,
        summary.disposition,
    );
}
