const std = @import("std");
const Io = std.Io;
const abi = @import("abi_bindings");
const cdev_lookup_plan = @import("cdev_lookup_plan");

fn writeSummary(writer: anytype, summary: abi.CdevLookupSummary) !void {
    try writer.writeAll("{\"major\":");
    try writer.print("{d}", .{summary.major});
    try writer.writeAll(",\"scanned_count\":");
    try writer.print("{d}", .{summary.scanned_count});
    try writer.writeAll(",\"request_count\":");
    try writer.print("{d}", .{summary.request_count});
    try writer.writeAll(",\"selected_count\":");
    try writer.print("{d}", .{summary.selected_count});
    try writer.writeAll(",\"first_minor\":");
    try writer.print("{d}", .{summary.first_minor});
    try writer.writeAll(",\"target_minor\":");
    try writer.print("{d}", .{summary.target_minor});
    try writer.writeAll(",\"resolved_index\":");
    try writer.print("{d}", .{summary.resolved_index});
    try writer.writeAll(",\"resolved_dev\":");
    try writer.print("{d}", .{summary.resolved_dev});
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
    const hit_view = cdev_lookup_plan.viewFromBits(words[0..], 240, 32, 8, 6, 2, abi.IDA_POLICY_FIRST_FIT, 34);
    const miss_view = cdev_lookup_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 35);
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};
    const exhausted_view = cdev_lookup_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20);
    const empty_view = abi.CdevLookupView{ .bits_addr = 0, .major = 240, .first_minor = 0, .minor_count = 0, .max_scan = 0, .request_count = 1, .policy = abi.IDA_POLICY_FIRST_FIT, .target_minor = 0, .reserved = 0 };

    try writer.writeAll("{\"constants\":{\"cdev_lookup_flag_truncated\":");
    try writer.print("{d}", .{abi.CDEV_LOOKUP_FLAG_TRUNCATED});
    try writer.writeAll(",\"cdev_lookup_flag_found\":");
    try writer.print("{d}", .{abi.CDEV_LOOKUP_FLAG_FOUND});
    try writer.writeAll(",\"cdev_lookup_flag_exhausted\":");
    try writer.print("{d}", .{abi.CDEV_LOOKUP_FLAG_EXHAUSTED});
    try writer.writeAll(",\"cdev_lookup_flag_hit\":");
    try writer.print("{d}", .{abi.CDEV_LOOKUP_FLAG_HIT});
    try writer.writeAll(",\"cdev_lookup_index_none\":");
    try writer.print("{d}", .{abi.CDEV_LOOKUP_INDEX_NONE});
    try writer.writeAll("},\"hit\":{\"summary\":");
    try writeSummary(writer, cdev_lookup_plan.summarize(hit_view));
    try writer.writeAll("},\"miss\":{\"summary\":");
    try writeSummary(writer, cdev_lookup_plan.summarize(miss_view));
    try writer.writeAll("},\"exhausted\":{\"summary\":");
    try writeSummary(writer, cdev_lookup_plan.summarize(exhausted_view));
    try writer.writeAll("},\"empty\":{\"is_valid\":");
    try writer.writeAll(if (cdev_lookup_plan.isValid(empty_view)) "true" else "false");
    try writer.writeAll(",\"summary\":");
    try writeSummary(writer, cdev_lookup_plan.summarize(empty_view));
    try writer.writeAll("}}\n");

    try stdout_writer.interface.flush();
}
