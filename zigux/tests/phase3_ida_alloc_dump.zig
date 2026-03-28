const std = @import("std");
const Io = std.Io;
const abi = @import("abi_bindings");
const ida_alloc_view = @import("ida_alloc_view");

fn writeSummary(writer: anytype, summary: abi.IdaAllocSummary) !void {
    try writer.writeAll("{\"scanned_count\":");
    try writer.print("{d}", .{summary.scanned_count});
    try writer.writeAll(",\"request_count\":");
    try writer.print("{d}", .{summary.request_count});
    try writer.writeAll(",\"first_fit_id\":");
    try writer.print("{d}", .{summary.first_fit_id});
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
    const truncated_view = ida_alloc_view.viewFromBits(words[0..], 100, 8, 6, 2);
    const full_view = ida_alloc_view.viewFromBits(words[0..], 100, 8, 8, 2);
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};
    const exhausted_view = ida_alloc_view.viewFromBits(exhausted_words[0..], 40, 5, 5, 2);
    const empty_view = abi.IdaAllocView{ .bits_addr = 0, .base_id = 32, .nbits = 0, .max_scan = 0, .request_count = 1, .reserved = 0 };

    try writer.writeAll("{\"constants\":{\"ida_alloc_flag_truncated\":");
    try writer.print("{d}", .{abi.IDA_ALLOC_FLAG_TRUNCATED});
    try writer.writeAll(",\"ida_alloc_flag_found\":");
    try writer.print("{d}", .{abi.IDA_ALLOC_FLAG_FOUND});
    try writer.writeAll(",\"ida_alloc_flag_exhausted\":");
    try writer.print("{d}", .{abi.IDA_ALLOC_FLAG_EXHAUSTED});
    try writer.writeAll("},\"truncated\":{\"summary\":");
    try writeSummary(writer, ida_alloc_view.summarize(truncated_view));
    try writer.writeAll("},\"full\":{\"summary\":");
    try writeSummary(writer, ida_alloc_view.summarize(full_view));
    try writer.writeAll("},\"exhausted\":{\"summary\":");
    try writeSummary(writer, ida_alloc_view.summarize(exhausted_view));
    try writer.writeAll("},\"empty\":{\"is_valid\":");
    try writer.writeAll(if (ida_alloc_view.isValid(empty_view)) "true" else "false");
    try writer.writeAll(",\"summary\":");
    try writeSummary(writer, ida_alloc_view.summarize(empty_view));
    try writer.writeAll("}}\n");

    try stdout_writer.interface.flush();
}
