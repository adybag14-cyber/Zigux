const std = @import("std");
const Io = std.Io;
const abi = @import("abi_bindings");
const chrdev_notify_ack_window_policy_budget_plan = @import("chrdev_notify_ack_window_policy_budget_plan");

fn writeSummary(writer: anytype, summary: abi.ChrdevNotifyAckWindowPolicyBudgetSummary) !void {
    try writer.writeAll("{\"window_status\":");
    try writer.print("{d}", .{summary.window_status});
    try writer.writeAll(",\"window_policy_flags\":");
    try writer.print("{d}", .{summary.window_policy_flags});
    try writer.writeAll(",\"effective_window_policy_flags\":");
    try writer.print("{d}", .{summary.effective_window_policy_flags});
    try writer.writeAll(",\"effective_window_cookie\":");
    try writer.print("{d}", .{summary.effective_window_cookie});
    try writer.writeAll(",\"window_policy_status\":");
    try writer.print("{d}", .{summary.window_policy_status});
    try writer.writeAll(",\"window_policy_budget_flags\":");
    try writer.print("{d}", .{summary.window_policy_budget_flags});
    try writer.writeAll(",\"window_policy_budget_before\":");
    try writer.print("{d}", .{summary.window_policy_budget_before});
    try writer.writeAll(",\"window_policy_budget_after\":");
    try writer.print("{d}", .{summary.window_policy_budget_after});
    try writer.writeAll(",\"deferred_window_policy_budget_before\":");
    try writer.print("{d}", .{summary.deferred_window_policy_budget_before});
    try writer.writeAll(",\"deferred_window_policy_budget_after\":");
    try writer.print("{d}", .{summary.deferred_window_policy_budget_after});
    try writer.writeAll(",\"window_policy_budget_status\":");
    try writer.print("{d}", .{summary.window_policy_budget_status});
    try writer.writeAll(",\"budget_window_acked_count\":");
    try writer.print("{d}", .{summary.budget_window_acked_count});
    try writer.writeAll(",\"budget_window_deferred_count\":");
    try writer.print("{d}", .{summary.budget_window_deferred_count});
    try writer.writeAll(",\"budget_window_suppressed_count\":");
    try writer.print("{d}", .{summary.budget_window_suppressed_count});
    try writer.writeAll(",\"budget_window_coalesced_count\":");
    try writer.print("{d}", .{summary.budget_window_coalesced_count});
    try writer.writeAll(",\"budget_window_dropped_count\":");
    try writer.print("{d}", .{summary.budget_window_dropped_count});
    try writer.writeAll(",\"budget_window_skipped_count\":");
    try writer.print("{d}", .{summary.budget_window_skipped_count});
    try writer.writeAll("}");
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [32768]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout_writer.interface;

    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const acked_view = chrdev_notify_ack_window_policy_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0, 0, 1, 0);
    const fallback_deferred_view = chrdev_notify_ack_window_policy_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xBBBB, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xB2B2, 1, 0, 1, 0, 0, 0, 0, 1);
    const policy_deferred_view = chrdev_notify_ack_window_policy_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xCCCC, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xC3C3, 1, 0, 1, 0, 0, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_FORCE_DEFERRED, 1, 1);
    const coalesced_view = chrdev_notify_ack_window_policy_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0xE5E5, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xE5E5, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xE5E5, 1, 0, 1, 0, 0, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_COALESCE_COOKIE, 1, 0);
    const suppressed_view = chrdev_notify_ack_window_policy_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xE5E5, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 0, 0xE5E5, 1, 0, 1, 0, 0, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_SUPPRESS_DROPPED, 1, 1);
    const dropped_view = chrdev_notify_ack_window_policy_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xDDDD, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 0, 0xD4D4, 1, 0, 1, 0, 0, 0, 1, 1);
    const skipped_view = chrdev_notify_ack_window_policy_budget_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xF6F6, abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xF6F6, 0, 0, 1, 1, 0, 0, 1, 1);
    const empty_view = abi.ChrdevNotifyAckWindowPolicyBudgetView{
        .bits_addr = 0,
        .major = 240,
        .first_minor = 0,
        .minor_count = 0,
        .max_scan = 0,
        .request_count = 2,
        .policy = abi.IDA_POLICY_FIRST_FIT,
        .target_minor = 0,
        .requested_mode = abi.CHRDEV_MODE_READ,
        .supported_mode = abi.CHRDEV_MODE_READ,
        .available_ops = abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ,
        .io_op = abi.CHRDEV_IO_OP_READ,
        .requested_bytes = 8,
        .max_chunk_bytes = 8,
        .file_offset = 0,
        .bytes_completed = 0,
        .max_segments = 1,
        .resume_passes = 2,
        .retry_budget = 1,
        .stall_budget = 1,
        .backoff_quanta = 5,
        .queue_depth = 0,
        .queue_capacity = 2,
        .requeue_budget = 1,
        .completion_cookie = 0x9999,
        .completion_budget = 0,
        .notify_mask = abi.CHRDEV_NOTIFY_MASK_SUCCESS,
        .notify_cookie = 0xFFFF,
        .notify_budget = 0,
        .reserved = 0,
        .policy_flags = 0,
        .policy_reserved = 0,
        .delivery_budget = 0,
        .deferred_budget = 0,
        .ack_mask = abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED,
        .ack_window = 0,
        .ack_cookie = 0xABCD,
        .ack_observed = 0,
        .ack_reserved = 0,
        .ack_policy_flags = 0,
        .ack_policy_reserved = 0,
        .ack_budget = 0,
        .deferred_ack_budget = 0,
        .ack_budget_reserved = 0,
        .window_floor = 0,
        .window_reserved = 0,
        .window_policy_flags = 0,
        .window_policy_reserved = 0,
        .window_policy_budget = 0,
        .deferred_window_policy_budget = 0,
        .window_policy_budget_reserved = 0,
    };

    try writer.writeAll("{\"constants\":{\"chrdev_notify_ack_window_policy_force_deferred\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_FORCE_DEFERRED});
    try writer.writeAll(",\"chrdev_notify_ack_window_policy_suppress_dropped\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_SUPPRESS_DROPPED});
    try writer.writeAll(",\"chrdev_notify_ack_window_policy_coalesce_cookie\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_COALESCE_COOKIE});
    try writer.writeAll(",\"chrdev_notify_ack_window_policy_budget_flag_budget_applied\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_BUDGET_APPLIED});
    try writer.writeAll(",\"chrdev_notify_ack_window_policy_budget_flag_window_policy_budget_used\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_WINDOW_POLICY_BUDGET_USED});
    try writer.writeAll(",\"chrdev_notify_ack_window_policy_budget_flag_deferred_window_policy_budget_used\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_DEFERRED_WINDOW_POLICY_BUDGET_USED});
    try writer.writeAll(",\"chrdev_notify_ack_window_policy_budget_flag_window_policy_budget_exhausted\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_WINDOW_POLICY_BUDGET_EXHAUSTED});
    try writer.writeAll(",\"chrdev_notify_ack_window_policy_budget_flag_deferred_window_policy_budget_exhausted\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_DEFERRED_WINDOW_POLICY_BUDGET_EXHAUSTED});
    try writer.writeAll(",\"chrdev_notify_ack_window_policy_budget_status_none\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_NONE});
    try writer.writeAll(",\"chrdev_notify_ack_window_policy_budget_status_acked\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_ACKED});
    try writer.writeAll(",\"chrdev_notify_ack_window_policy_budget_status_deferred\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_DEFERRED});
    try writer.writeAll(",\"chrdev_notify_ack_window_policy_budget_status_suppressed\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_SUPPRESSED});
    try writer.writeAll(",\"chrdev_notify_ack_window_policy_budget_status_coalesced\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_COALESCED});
    try writer.writeAll(",\"chrdev_notify_ack_window_policy_budget_status_dropped\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_DROPPED});
    try writer.writeAll(",\"chrdev_notify_ack_window_policy_budget_status_skipped\":");
    try writer.print("{d}", .{abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_SKIPPED});
    try writer.writeAll("},\"acked\":{\"summary\":");
    try writeSummary(writer, chrdev_notify_ack_window_policy_budget_plan.summarize(acked_view));
    try writer.writeAll("},\"fallback_deferred\":{\"summary\":");
    try writeSummary(writer, chrdev_notify_ack_window_policy_budget_plan.summarize(fallback_deferred_view));
    try writer.writeAll("},\"policy_deferred\":{\"summary\":");
    try writeSummary(writer, chrdev_notify_ack_window_policy_budget_plan.summarize(policy_deferred_view));
    try writer.writeAll("},\"coalesced\":{\"summary\":");
    try writeSummary(writer, chrdev_notify_ack_window_policy_budget_plan.summarize(coalesced_view));
    try writer.writeAll("},\"suppressed\":{\"summary\":");
    try writeSummary(writer, chrdev_notify_ack_window_policy_budget_plan.summarize(suppressed_view));
    try writer.writeAll("},\"dropped\":{\"summary\":");
    try writeSummary(writer, chrdev_notify_ack_window_policy_budget_plan.summarize(dropped_view));
    try writer.writeAll("},\"skipped\":{\"summary\":");
    try writeSummary(writer, chrdev_notify_ack_window_policy_budget_plan.summarize(skipped_view));
    try writer.writeAll("},\"empty\":{\"is_valid\":");
    try writer.writeAll(if (chrdev_notify_ack_window_policy_budget_plan.isValid(empty_view)) "true" else "false");
    try writer.writeAll(",\"summary\":");
    try writeSummary(writer, chrdev_notify_ack_window_policy_budget_plan.summarize(empty_view));
    try writer.writeAll("}}\n");
    try stdout_writer.interface.flush();
}
