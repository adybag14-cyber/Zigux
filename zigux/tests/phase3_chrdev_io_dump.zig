const std = @import("std");
const Io = std.Io;
const abi = @import("abi_bindings");
const chrdev_io_plan = @import("chrdev_io_plan");

fn writeSummary(writer: anytype, summary: abi.ChrdevIoSummary) !void {
    try writer.writeAll("{\"major\":");
    try writer.print("{d}", .{summary.major});
    try writer.writeAll(",\"target_minor\":");
    try writer.print("{d}", .{summary.target_minor});
    try writer.writeAll(",\"selected_count\":");
    try writer.print("{d}", .{summary.selected_count});
    try writer.writeAll(",\"resolved_index\":");
    try writer.print("{d}", .{summary.resolved_index});
    try writer.writeAll(",\"resolved_dev\":");
    try writer.print("{d}", .{summary.resolved_dev});
    try writer.writeAll(",\"granted_mode\":");
    try writer.print("{d}", .{summary.granted_mode});
    try writer.writeAll(",\"io_op\":");
    try writer.print("{d}", .{summary.io_op});
    try writer.writeAll(",\"requested_bytes\":");
    try writer.print("{d}", .{summary.requested_bytes});
    try writer.writeAll(",\"chunk_bytes\":");
    try writer.print("{d}", .{summary.chunk_bytes});
    try writer.writeAll(",\"entry_ops\":");
    try writer.print("{d}", .{summary.entry_ops});
    try writer.writeAll(",\"data_ops\":");
    try writer.print("{d}", .{summary.data_ops});
    try writer.writeAll(",\"exit_ops\":");
    try writer.print("{d}", .{summary.exit_ops});
    try writer.writeAll(",\"blocked_ops\":");
    try writer.print("{d}", .{summary.blocked_ops});
    try writer.writeAll(",\"flags\":");
    try writer.print("{d}", .{summary.flags});
    try writer.writeAll("}");
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout_writer.interface;

    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const read_view = chrdev_io_plan.viewFromBits(words[0..], 240, 32, 8, 6, 2, abi.IDA_POLICY_FIRST_FIT, 34, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_READ, 16, 8);
    const partial_write_view = chrdev_io_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 12, 32);
    const blocked_read_view = chrdev_io_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_READ, 12, 32);
    const denied_view = chrdev_io_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 12, 32);
    const miss_view = chrdev_io_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 35, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32);
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};
    const exhausted_view = chrdev_io_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32);
    const empty_view = abi.ChrdevIoView{ .bits_addr = 0, .major = 240, .first_minor = 0, .minor_count = 0, .max_scan = 0, .request_count = 2, .policy = abi.IDA_POLICY_FIRST_FIT, .target_minor = 0, .requested_mode = abi.CHRDEV_MODE_READ, .supported_mode = abi.CHRDEV_MODE_READ, .available_ops = abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, .io_op = abi.CHRDEV_IO_OP_READ, .requested_bytes = 8, .max_chunk_bytes = 8, .reserved = 0 };

    try writer.writeAll("{\"constants\":{\"chrdev_io_op_read\":");
    try writer.print("{d}", .{abi.CHRDEV_IO_OP_READ});
    try writer.writeAll(",\"chrdev_io_op_write\":");
    try writer.print("{d}", .{abi.CHRDEV_IO_OP_WRITE});
    try writer.writeAll(",\"chrdev_io_flag_truncated\":");
    try writer.print("{d}", .{abi.CHRDEV_IO_FLAG_TRUNCATED});
    try writer.writeAll(",\"chrdev_io_flag_found\":");
    try writer.print("{d}", .{abi.CHRDEV_IO_FLAG_FOUND});
    try writer.writeAll(",\"chrdev_io_flag_exhausted\":");
    try writer.print("{d}", .{abi.CHRDEV_IO_FLAG_EXHAUSTED});
    try writer.writeAll(",\"chrdev_io_flag_hit\":");
    try writer.print("{d}", .{abi.CHRDEV_IO_FLAG_HIT});
    try writer.writeAll(",\"chrdev_io_flag_permitted\":");
    try writer.print("{d}", .{abi.CHRDEV_IO_FLAG_PERMITTED});
    try writer.writeAll(",\"chrdev_io_flag_denied\":");
    try writer.print("{d}", .{abi.CHRDEV_IO_FLAG_DENIED});
    try writer.writeAll(",\"chrdev_io_flag_routable\":");
    try writer.print("{d}", .{abi.CHRDEV_IO_FLAG_ROUTABLE});
    try writer.writeAll(",\"chrdev_io_flag_blocked\":");
    try writer.print("{d}", .{abi.CHRDEV_IO_FLAG_BLOCKED});
    try writer.writeAll(",\"chrdev_io_flag_dispatchable\":");
    try writer.print("{d}", .{abi.CHRDEV_IO_FLAG_DISPATCHABLE});
    try writer.writeAll(",\"chrdev_io_index_none\":");
    try writer.print("{d}", .{abi.CHRDEV_IO_INDEX_NONE});
    try writer.writeAll("},\"read_dispatch\":{\"summary\":");
    try writeSummary(writer, chrdev_io_plan.summarize(read_view));
    try writer.writeAll("},\"write_partial\":{\"summary\":");
    try writeSummary(writer, chrdev_io_plan.summarize(partial_write_view));
    try writer.writeAll("},\"blocked_read\":{\"summary\":");
    try writeSummary(writer, chrdev_io_plan.summarize(blocked_read_view));
    try writer.writeAll("},\"denied\":{\"summary\":");
    try writeSummary(writer, chrdev_io_plan.summarize(denied_view));
    try writer.writeAll("},\"miss\":{\"summary\":");
    try writeSummary(writer, chrdev_io_plan.summarize(miss_view));
    try writer.writeAll("},\"exhausted\":{\"summary\":");
    try writeSummary(writer, chrdev_io_plan.summarize(exhausted_view));
    try writer.writeAll("},\"empty\":{\"is_valid\":");
    try writer.writeAll(if (chrdev_io_plan.isValid(empty_view)) "true" else "false");
    try writer.writeAll(",\"summary\":");
    try writeSummary(writer, chrdev_io_plan.summarize(empty_view));
    try writer.writeAll("}}\n");

    try stdout_writer.interface.flush();
}
