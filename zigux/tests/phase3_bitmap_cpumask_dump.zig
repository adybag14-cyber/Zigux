const std = @import("std");
const Io = std.Io;
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout_writer.interface;

    var bitmap_words = [_]usize{
        (@as(usize, 1) << 1) | (@as(usize, 1) << 5) | (@as(usize, 1) << 63),
        (@as(usize, 1) << 4) | (@as(usize, 1) << 9),
    };
    const bitmap = bitmap_view.viewFromWords(bitmap_words[0..], bitmap_view.bits_per_long + 10);
    const bitmap_summary = bitmap_view.summarize(bitmap);
    const empty_bitmap = bitmap_view.viewFromWords(&.{}, 0);
    const empty_bitmap_summary = bitmap_view.summarize(empty_bitmap);

    var cpumask_bits = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 6) | (@as(usize, 1) << 9)};
    const cpumask = cpumask_view.viewFromBits(cpumask_bits[0..], 12);
    const cpumask_summary = cpumask_view.summarize(cpumask);
    const empty_cpumask = cpumask_view.viewFromBits(&.{}, 0);
    const empty_cpumask_summary = cpumask_view.summarize(empty_cpumask);

    try writer.writeAll("{\"constants\":{\"bits_per_long\":");
    try writer.print("{d}", .{bitmap_view.bits_per_long});
    try writer.writeAll("},\"bitmap\":{");
    try writer.writeAll("\"word_count\":");
    try writer.print("{d}", .{bitmap.word_count});
    try writer.writeAll(",\"valid\":");
    try writer.writeAll(if (bitmap_view.isValid(bitmap)) "true" else "false");
    try writer.writeAll(",\"first_set\":");
    try writer.print("{d}", .{bitmap_view.firstSet(bitmap)});
    try writer.writeAll(",\"first_zero\":");
    try writer.print("{d}", .{bitmap_view.firstZero(bitmap)});
    try writer.writeAll(",\"weight\":");
    try writer.print("{d}", .{bitmap_view.weight(bitmap)});
    try writer.writeAll(",\"test_bit_4\":");
    try writer.writeAll(if (bitmap_view.testBit(bitmap, 4)) "true" else "false");
    try writer.writeAll(",\"test_bit_63\":");
    try writer.writeAll(if (bitmap_view.testBit(bitmap, 63)) "true" else "false");
    try writer.writeAll(",\"summary\":{\"first_set\":");
    try writer.print("{d}", .{bitmap_summary.first_set});
    try writer.writeAll(",\"first_zero\":");
    try writer.print("{d}", .{bitmap_summary.first_zero});
    try writer.writeAll(",\"weight\":");
    try writer.print("{d}", .{bitmap_summary.weight});
    try writer.writeAll("}},\"empty_bitmap\":{");
    try writer.writeAll("\"first_set\":");
    try writer.print("{d}", .{bitmap_view.firstSet(empty_bitmap)});
    try writer.writeAll(",\"first_zero\":");
    try writer.print("{d}", .{bitmap_view.firstZero(empty_bitmap)});
    try writer.writeAll(",\"weight\":");
    try writer.print("{d}", .{empty_bitmap_summary.weight});
    try writer.writeAll("},\"cpumask\":{");
    try writer.writeAll("\"word_count\":");
    try writer.print("{d}", .{bitmap_view.wordCount(cpumask.nr_cpu_ids)});
    try writer.writeAll(",\"valid\":");
    try writer.writeAll(if (cpumask_view.isValid(cpumask)) "true" else "false");
    try writer.writeAll(",\"first_cpu\":");
    try writer.print("{d}", .{cpumask_view.firstCpu(cpumask)});
    try writer.writeAll(",\"next_cpu_after_first\":");
    try writer.print("{d}", .{cpumask_view.nextCpu(cpumask, cpumask_view.firstCpu(cpumask))});
    try writer.writeAll(",\"weight\":");
    try writer.print("{d}", .{cpumask_view.weight(cpumask)});
    try writer.writeAll(",\"test_cpu_3\":");
    try writer.writeAll(if (cpumask_view.testCpu(cpumask, 3)) "true" else "false");
    try writer.writeAll(",\"test_cpu_9\":");
    try writer.writeAll(if (cpumask_view.testCpu(cpumask, 9)) "true" else "false");
    try writer.writeAll(",\"summary\":{\"first_cpu\":");
    try writer.print("{d}", .{cpumask_summary.first_cpu});
    try writer.writeAll(",\"next_cpu\":");
    try writer.print("{d}", .{cpumask_summary.next_cpu});
    try writer.writeAll(",\"weight\":");
    try writer.print("{d}", .{cpumask_summary.weight});
    try writer.writeAll("}},\"empty_cpumask\":{");
    try writer.writeAll("\"first_cpu\":");
    try writer.print("{d}", .{cpumask_view.firstCpu(empty_cpumask)});
    try writer.writeAll(",\"next_cpu\":");
    try writer.print("{d}", .{cpumask_view.nextCpu(empty_cpumask, 0)});
    try writer.writeAll(",\"weight\":");
    try writer.print("{d}", .{empty_cpumask_summary.weight});
    try writer.writeAll("}}\n");

    try stdout_writer.interface.flush();
}
