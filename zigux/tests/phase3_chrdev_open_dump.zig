const std = @import("std");
const Io = std.Io;
const abi = @import("abi_bindings");
const chrdev_open_plan = @import("chrdev_open_plan");

fn writeSummary(writer: anytype, summary: abi.ChrdevOpenSummary) !void {
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
    try writer.writeAll(",\"requested_mode\":");
    try writer.print("{d}", .{summary.requested_mode});
    try writer.writeAll(",\"supported_mode\":");
    try writer.print("{d}", .{summary.supported_mode});
    try writer.writeAll(",\"granted_mode\":");
    try writer.print("{d}", .{summary.granted_mode});
    try writer.writeAll(",\"denied_mode\":");
    try writer.print("{d}", .{summary.denied_mode});
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
    const permitted_view = chrdev_open_plan.viewFromBits(
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
    const denied_view = chrdev_open_plan.viewFromBits(
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
    const miss_view = chrdev_open_plan.viewFromBits(
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
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};
    const exhausted_view = chrdev_open_plan.viewFromBits(
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
    const empty_view = abi.ChrdevOpenView{
        .bits_addr = 0,
        .major = 240,
        .first_minor = 0,
        .minor_count = 0,
        .max_scan = 0,
        .request_count = 1,
        .policy = abi.IDA_POLICY_FIRST_FIT,
        .target_minor = 0,
        .requested_mode = abi.CHRDEV_MODE_READ,
        .supported_mode = abi.CHRDEV_MODE_READ,
        .reserved = 0,
    };

    try writer.writeAll("{\"constants\":{\"chrdev_mode_read\":");
    try writer.print("{d}", .{abi.CHRDEV_MODE_READ});
    try writer.writeAll(",\"chrdev_mode_write\":");
    try writer.print("{d}", .{abi.CHRDEV_MODE_WRITE});
    try writer.writeAll(",\"chrdev_open_flag_truncated\":");
    try writer.print("{d}", .{abi.CHRDEV_OPEN_FLAG_TRUNCATED});
    try writer.writeAll(",\"chrdev_open_flag_found\":");
    try writer.print("{d}", .{abi.CHRDEV_OPEN_FLAG_FOUND});
    try writer.writeAll(",\"chrdev_open_flag_exhausted\":");
    try writer.print("{d}", .{abi.CHRDEV_OPEN_FLAG_EXHAUSTED});
    try writer.writeAll(",\"chrdev_open_flag_hit\":");
    try writer.print("{d}", .{abi.CHRDEV_OPEN_FLAG_HIT});
    try writer.writeAll(",\"chrdev_open_flag_permitted\":");
    try writer.print("{d}", .{abi.CHRDEV_OPEN_FLAG_PERMITTED});
    try writer.writeAll(",\"chrdev_open_flag_denied\":");
    try writer.print("{d}", .{abi.CHRDEV_OPEN_FLAG_DENIED});
    try writer.writeAll(",\"chrdev_open_index_none\":");
    try writer.print("{d}", .{abi.CHRDEV_OPEN_INDEX_NONE});
    try writer.writeAll("},\"permitted\":{\"summary\":");
    try writeSummary(writer, chrdev_open_plan.summarize(permitted_view));
    try writer.writeAll("},\"denied\":{\"summary\":");
    try writeSummary(writer, chrdev_open_plan.summarize(denied_view));
    try writer.writeAll("},\"miss\":{\"summary\":");
    try writeSummary(writer, chrdev_open_plan.summarize(miss_view));
    try writer.writeAll("},\"exhausted\":{\"summary\":");
    try writeSummary(writer, chrdev_open_plan.summarize(exhausted_view));
    try writer.writeAll("},\"empty\":{\"is_valid\":");
    try writer.writeAll(if (chrdev_open_plan.isValid(empty_view)) "true" else "false");
    try writer.writeAll(",\"summary\":");
    try writeSummary(writer, chrdev_open_plan.summarize(empty_view));
    try writer.writeAll("}}\n");

    try stdout_writer.interface.flush();
}
