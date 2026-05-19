const std = @import("std");
const Io = std.Io;
const binding = @import("bitmap_cpumask_binding");
const bitmap_view = @import("bitmap_view_helper");
const cpumask_view = @import("cpumask_view_helper");

fn writeNullableU32(writer: anytype, value: ?u32) !void {
    if (value) |v| {
        try writer.print("{}", .{v});
        return;
    }
    try writer.writeAll("null");
}

fn writeCase(
    writer: anytype,
    name: []const u8,
    kind: []const u8,
    nbits: u32,
    nr_cpu_ids: ?u32,
    word_count: u32,
    first_set: u32,
    first_zero: u32,
    weight: u32,
    probe_present_index: u32,
    probe_present: bool,
    probe_absent_index: u32,
    probe_absent: bool,
    trailing_comma: bool,
) !void {
    try writer.print(
        "    {\n" ++
            "      \"name\": \"{s}\",\n" ++
            "      \"kind\": \"{s}\",\n" ++
            "      \"nbits\": {},\n" ++
            "      \"nr_cpu_ids\": ",
        .{ name, kind, nbits },
    );
    try writeNullableU32(writer, nr_cpu_ids);
    try writer.print(
        ",\n" ++
            "      \"word_count\": {},\n" ++
            "      \"first_set\": {},\n" ++
            "      \"first_zero\": {},\n" ++
            "      \"weight\": {},\n" ++
            "      \"probe_present_index\": {},\n" ++
            "      \"probe_present\": {s},\n" ++
            "      \"probe_absent_index\": {},\n" ++
            "      \"probe_absent\": {s}\n" ++
            "    }}{s}\n",
        .{
            word_count,
            first_set,
            first_zero,
            weight,
            probe_present_index,
            if (probe_present) "true" else "false",
            probe_absent_index,
            if (probe_absent) "true" else "false",
            if (trailing_comma) "," else "",
        },
    );
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout_writer.interface;

    var bitmap_words = [_]usize{
        (@as(usize, 1) << 1) | (@as(usize, 1) << 3) | (@as(usize, 1) << 5),
        (@as(usize, 1) << 1) | (@as(usize, 1) << 5) | (@as(usize, 1) << 10),
    };
    const bitmap = bitmap_view.viewFromWords(bitmap_words[0..], bitmap_view.bits_per_word + 6);
    const bitmap_summary = bitmap_view.summarize(bitmap);

    var cpumask_words = [_]usize{
        (@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 7),
    };
    const cpumask = cpumask_view.viewFromWords(cpumask_words[0..], 16);
    const cpumask_summary = cpumask_view.summarize(cpumask);

    var cpumask_clear_words = [_]usize{0};
    const cpumask_clear = cpumask_view.viewFromWords(cpumask_clear_words[0..], 16);
    const cpumask_clear_summary = cpumask_view.summarize(cpumask_clear);
    const cpumask_clear_projected = binding.asBitmap(cpumask_clear);
    const cpumask_clear_projected_summary = bitmap_view.summarize(cpumask_clear_projected);

    var cpumask_cross_words = [_]usize{
        (@as(usize, 1) << 5) | (@as(usize, 1) << (bitmap_view.bits_per_word - 1)),
        (@as(usize, 1) << 1) | (@as(usize, 1) << 6) | (@as(usize, 1) << 10),
    };
    const cpumask_cross = cpumask_view.viewFromWords(cpumask_cross_words[0..], bitmap_view.bits_per_word + 11);
    const cpumask_cross_summary = cpumask_view.summarize(cpumask_cross);

    var cpumask_full_words = [_]usize{
        ~@as(usize, 0),
        bitmap_view.lastWordMask(bitmap_view.bits_per_word + 11),
    };
    const cpumask_full = cpumask_view.viewFromWords(cpumask_full_words[0..], bitmap_view.bits_per_word + 11);
    const cpumask_full_summary = cpumask_view.summarize(cpumask_full);

    try writer.print(
        "{\n" ++
            "  \"word_bits\": {},\n" ++
            "  \"bitmap_view_abi_version\": {},\n" ++
            "  \"cpumask_view_abi_version\": {},\n" ++
            "  \"cases\": [\n",
        .{
            @bitSizeOf(usize),
            binding.bitmap_view_abi_version,
            binding.cpumask_view_abi_version,
        },
    );

    try writeCase(
        writer,
        "bitmap_tail_masked",
        "bitmap",
        bitmap.nbits,
        null,
        bitmap.word_count,
        bitmap_summary.first_set,
        bitmap_summary.first_zero,
        bitmap_summary.weight,
        69,
        bitmap_view.testBit(bitmap, 69),
        66,
        bitmap_view.testBit(bitmap, 66),
        true,
    );
    try writeCase(
        writer,
        "cpumask_window",
        "cpumask",
        cpumask.nbits,
        cpumask.nr_cpu_ids,
        cpumask.word_count,
        cpumask_summary.first_set,
        cpumask_summary.first_zero,
        cpumask_summary.weight,
        7,
        cpumask_view.cpuIsSet(cpumask, 7),
        1,
        cpumask_view.cpuIsSet(cpumask, 1),
        true,
    );
    try writeCase(
        writer,
        "cpumask_all_clear_window",
        "cpumask",
        cpumask_clear.nbits,
        cpumask_clear.nr_cpu_ids,
        cpumask_clear.word_count,
        cpumask_clear_summary.first_set,
        cpumask_clear_summary.first_zero,
        cpumask_clear_summary.weight,
        0,
        cpumask_view.cpuIsSet(cpumask_clear, 0),
        15,
        cpumask_view.cpuIsSet(cpumask_clear, 15),
        true,
    );
    try writeCase(
        writer,
        "cpumask_all_clear_projected_bitmap",
        "bitmap",
        cpumask_clear_projected.nbits,
        null,
        cpumask_clear_projected.word_count,
        cpumask_clear_projected_summary.first_set,
        cpumask_clear_projected_summary.first_zero,
        cpumask_clear_projected_summary.weight,
        0,
        bitmap_view.testBit(cpumask_clear_projected, 0),
        15,
        bitmap_view.testBit(cpumask_clear_projected, 15),
        true,
    );
    try writeCase(
        writer,
        "cpumask_cross_word_window",
        "cpumask",
        cpumask_cross.nbits,
        cpumask_cross.nr_cpu_ids,
        cpumask_cross.word_count,
        cpumask_cross_summary.first_set,
        cpumask_cross_summary.first_zero,
        cpumask_cross_summary.weight,
        bitmap_view.bits_per_word + 10,
        cpumask_view.cpuIsSet(cpumask_cross, bitmap_view.bits_per_word + 10),
        bitmap_view.bits_per_word + 11,
        cpumask_view.cpuIsSet(cpumask_cross, bitmap_view.bits_per_word + 11),
        true,
    );
    try writeCase(
        writer,
        "cpumask_full_tail_masked",
        "cpumask",
        cpumask_full.nbits,
        cpumask_full.nr_cpu_ids,
        cpumask_full.word_count,
        cpumask_full_summary.first_set,
        cpumask_full_summary.first_zero,
        cpumask_full_summary.weight,
        bitmap_view.bits_per_word + 10,
        cpumask_view.cpuIsSet(cpumask_full, bitmap_view.bits_per_word + 10),
        bitmap_view.bits_per_word + 11,
        cpumask_view.cpuIsSet(cpumask_full, bitmap_view.bits_per_word + 11),
        false,
    );

    try writer.writeAll("  ]\n}\n");
    try stdout_writer.interface.flush();
}
