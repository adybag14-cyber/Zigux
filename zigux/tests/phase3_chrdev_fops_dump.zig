const std = @import("std");
const Io = std.Io;
const abi = @import("abi_bindings");
const chrdev_fops_plan = @import("chrdev_fops_plan");

fn writeSummary(writer: anytype, summary: abi.ChrdevFopsSummary) !void {
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
    try writer.writeAll(",\"available_ops\":");
    try writer.print("{d}", .{summary.available_ops});
    try writer.writeAll(",\"required_ops\":");
    try writer.print("{d}", .{summary.required_ops});
    try writer.writeAll(",\"missing_ops\":");
    try writer.print("{d}", .{summary.missing_ops});
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
    const routable_view = chrdev_fops_plan.viewFromBits(
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
    const missing_ops_view = chrdev_fops_plan.viewFromBits(
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
    const denied_view = chrdev_fops_plan.viewFromBits(
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
    const miss_view = chrdev_fops_plan.viewFromBits(
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
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};
    const exhausted_view = chrdev_fops_plan.viewFromBits(
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
    const empty_view = abi.ChrdevFopsView{
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
        .available_ops = abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ,
        .reserved = 0,
    };

    try writer.writeAll("{\"constants\":{\"chrdev_fop_open\":");
    try writer.print("{d}", .{abi.CHRDEV_FOP_OPEN});
    try writer.writeAll(",\"chrdev_fop_release\":");
    try writer.print("{d}", .{abi.CHRDEV_FOP_RELEASE});
    try writer.writeAll(",\"chrdev_fop_read\":");
    try writer.print("{d}", .{abi.CHRDEV_FOP_READ});
    try writer.writeAll(",\"chrdev_fop_write\":");
    try writer.print("{d}", .{abi.CHRDEV_FOP_WRITE});
    try writer.writeAll(",\"chrdev_fops_flag_truncated\":");
    try writer.print("{d}", .{abi.CHRDEV_FOPS_FLAG_TRUNCATED});
    try writer.writeAll(",\"chrdev_fops_flag_found\":");
    try writer.print("{d}", .{abi.CHRDEV_FOPS_FLAG_FOUND});
    try writer.writeAll(",\"chrdev_fops_flag_exhausted\":");
    try writer.print("{d}", .{abi.CHRDEV_FOPS_FLAG_EXHAUSTED});
    try writer.writeAll(",\"chrdev_fops_flag_hit\":");
    try writer.print("{d}", .{abi.CHRDEV_FOPS_FLAG_HIT});
    try writer.writeAll(",\"chrdev_fops_flag_permitted\":");
    try writer.print("{d}", .{abi.CHRDEV_FOPS_FLAG_PERMITTED});
    try writer.writeAll(",\"chrdev_fops_flag_denied\":");
    try writer.print("{d}", .{abi.CHRDEV_FOPS_FLAG_DENIED});
    try writer.writeAll(",\"chrdev_fops_flag_routable\":");
    try writer.print("{d}", .{abi.CHRDEV_FOPS_FLAG_ROUTABLE});
    try writer.writeAll(",\"chrdev_fops_flag_missing_ops\":");
    try writer.print("{d}", .{abi.CHRDEV_FOPS_FLAG_MISSING_OPS});
    try writer.writeAll(",\"chrdev_fops_index_none\":");
    try writer.print("{d}", .{abi.CHRDEV_FOPS_INDEX_NONE});
    try writer.writeAll("},\"routable\":{\"summary\":");
    try writeSummary(writer, chrdev_fops_plan.summarize(routable_view));
    try writer.writeAll("},\"missing_ops\":{\"summary\":");
    try writeSummary(writer, chrdev_fops_plan.summarize(missing_ops_view));
    try writer.writeAll("},\"denied\":{\"summary\":");
    try writeSummary(writer, chrdev_fops_plan.summarize(denied_view));
    try writer.writeAll("},\"miss\":{\"summary\":");
    try writeSummary(writer, chrdev_fops_plan.summarize(miss_view));
    try writer.writeAll("},\"exhausted\":{\"summary\":");
    try writeSummary(writer, chrdev_fops_plan.summarize(exhausted_view));
    try writer.writeAll("},\"empty\":{\"is_valid\":");
    try writer.writeAll(if (chrdev_fops_plan.isValid(empty_view)) "true" else "false");
    try writer.writeAll(",\"summary\":");
    try writeSummary(writer, chrdev_fops_plan.summarize(empty_view));
    try writer.writeAll("}}\n");

    try stdout_writer.interface.flush();
}
