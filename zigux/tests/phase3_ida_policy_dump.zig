const std = @import("std");
const Io = std.Io;
const abi = @import("abi_bindings");
const ida_policy_view = @import("ida_policy_view");

fn writeSummary(writer: anytype, summary: abi.IdaPolicySummary) !void {
    try writer.writeAll("{\"scanned_count\":");
    try writer.print("{d}", .{summary.scanned_count});
    try writer.writeAll(",\"request_count\":");
    try writer.print("{d}", .{summary.request_count});
    try writer.writeAll(",\"selected_fit_id\":");
    try writer.print("{d}", .{summary.selected_fit_id});
    try writer.writeAll(",\"alternate_fit_id\":");
    try writer.print("{d}", .{summary.alternate_fit_id});
    try writer.writeAll(",\"longest_free_run\":");
    try writer.print("{d}", .{summary.longest_free_run});
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
    const first_fit_view = ida_policy_view.viewFromBits(words[0..], 100, 8, 6, 2, abi.IDA_POLICY_FIRST_FIT);
    const last_fit_view = ida_policy_view.viewFromBits(words[0..], 100, 8, 8, 2, abi.IDA_POLICY_LAST_FIT);
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};
    const exhausted_view = ida_policy_view.viewFromBits(exhausted_words[0..], 40, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT);
    const empty_view = abi.IdaPolicyView{ .bits_addr = 0, .base_id = 32, .nbits = 0, .max_scan = 0, .request_count = 1, .policy = abi.IDA_POLICY_FIRST_FIT, .reserved = 0 };

    try writer.writeAll("{\"constants\":{\"ida_policy_first_fit\":");
    try writer.print("{d}", .{abi.IDA_POLICY_FIRST_FIT});
    try writer.writeAll(",\"ida_policy_last_fit\":");
    try writer.print("{d}", .{abi.IDA_POLICY_LAST_FIT});
    try writer.writeAll(",\"ida_policy_flag_truncated\":");
    try writer.print("{d}", .{abi.IDA_POLICY_FLAG_TRUNCATED});
    try writer.writeAll(",\"ida_policy_flag_found\":");
    try writer.print("{d}", .{abi.IDA_POLICY_FLAG_FOUND});
    try writer.writeAll(",\"ida_policy_flag_exhausted\":");
    try writer.print("{d}", .{abi.IDA_POLICY_FLAG_EXHAUSTED});
    try writer.writeAll("},\"first_fit\":{\"summary\":");
    try writeSummary(writer, ida_policy_view.summarize(first_fit_view));
    try writer.writeAll("},\"last_fit\":{\"summary\":");
    try writeSummary(writer, ida_policy_view.summarize(last_fit_view));
    try writer.writeAll("},\"exhausted\":{\"summary\":");
    try writeSummary(writer, ida_policy_view.summarize(exhausted_view));
    try writer.writeAll("},\"empty\":{\"is_valid\":");
    try writer.writeAll(if (ida_policy_view.isValid(empty_view)) "true" else "false");
    try writer.writeAll(",\"summary\":");
    try writeSummary(writer, ida_policy_view.summarize(empty_view));
    try writer.writeAll("}}\n");

    try stdout_writer.interface.flush();
}
