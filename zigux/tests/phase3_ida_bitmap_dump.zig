const std = @import("std");
const Io = std.Io;
const abi = @import("abi_bindings");
const ida_bitmap_view = @import("ida_bitmap_view");

fn writeSummary(writer: anytype, summary: abi.IdaBitmapSummary) !void {
    try writer.writeAll("{\"scanned_count\":");
    try writer.print("{d}", .{summary.scanned_count});
    try writer.writeAll(",\"allocated_count\":");
    try writer.print("{d}", .{summary.allocated_count});
    try writer.writeAll(",\"first_allocated_id\":");
    try writer.print("{d}", .{summary.first_allocated_id});
    try writer.writeAll(",\"first_free_id\":");
    try writer.print("{d}", .{summary.first_free_id});
    try writer.writeAll(",\"flags\":");
    try writer.print("{d}", .{summary.flags});
    try writer.writeAll("}");
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout_writer.interface;

    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 3) | (@as(usize, 1) << 5)};
    const truncated_view = ida_bitmap_view.viewFromBits(words[0..], 100, 7, 6);
    const full_view = ida_bitmap_view.viewFromBits(words[0..], 100, 6, 6);
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 1) | (@as(usize, 1) << 2)};
    const exhausted_view = ida_bitmap_view.viewFromBits(exhausted_words[0..], 40, 3, 3);
    const empty_view = abi.IdaBitmapView{ .bits_addr = 0, .base_id = 32, .nbits = 0, .max_scan = 0, .reserved = 0 };

    try writer.writeAll("{\"constants\":{\"ida_bitmap_flag_truncated\":");
    try writer.print("{d}", .{abi.IDA_BITMAP_FLAG_TRUNCATED});
    try writer.writeAll(",\"ida_bitmap_flag_exhausted\":");
    try writer.print("{d}", .{abi.IDA_BITMAP_FLAG_EXHAUSTED});
    try writer.writeAll("},\"truncated\":{\"summary\":");
    try writeSummary(writer, ida_bitmap_view.summarize(truncated_view));
    try writer.writeAll("},\"full\":{\"summary\":");
    try writeSummary(writer, ida_bitmap_view.summarize(full_view));
    try writer.writeAll("},\"exhausted\":{\"summary\":");
    try writeSummary(writer, ida_bitmap_view.summarize(exhausted_view));
    try writer.writeAll("},\"empty\":{\"is_valid\":");
    try writer.writeAll(if (ida_bitmap_view.isValid(empty_view)) "true" else "false");
    try writer.writeAll(",\"summary\":");
    try writeSummary(writer, ida_bitmap_view.summarize(empty_view));
    try writer.writeAll("}}\n");

    try stdout_writer.interface.flush();
}
