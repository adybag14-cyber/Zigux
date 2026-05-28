const std = @import("std");
const Io = std.Io;
const ida_alloc_view = @import("ida_alloc_view");
const ida_bitmap_view = @import("ida_bitmap_view");

fn writeSelection(writer: anytype, value: ?ida_alloc_view.Selection) !void {
    if (value) |selection| {
        try writer.print(
            "{{\"id\":{},\"relative_bit\":{}}}",
            .{ selection.id, selection.relative_bit },
        );
        return;
    }
    try writer.writeAll("null");
}

fn writeCase(
    writer: anytype,
    name: []const u8,
    view: ida_alloc_view.AllocationView,
    request: ida_alloc_view.AllocationRange,
    trailing_comma: bool,
) !void {
    try writer.print(
        "    {{\n" ++
            "      \"name\": \"{s}\",\n" ++
            "      \"ordered\": {s},\n" ++
            "      \"first_candidate\": ",
        .{
            name,
            if (request.isOrdered()) "true" else "false",
        },
    );
    try writeSelection(writer, view.firstCandidateInRange(request));
    try writer.writeAll(",\n      \"last_candidate\": ");
    try writeSelection(writer, view.lastCandidateInRange(request));
    try writer.writeAll(",\n      \"first_free\": ");
    try writeSelection(writer, view.firstFreeInRange(request));
    try writer.writeAll("\n    }");
    if (trailing_comma) try writer.writeAll(",");
    try writer.writeAll("\n");
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout_writer.interface;

    const empty_words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    const empty_view = ida_alloc_view.fromWords(&empty_words, 0);

    var sparse_words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    sparse_words[0] |= (@as(usize, 1) << 0) | (@as(usize, 1) << 1) | (@as(usize, 1) << 3);
    const sparse_view = ida_alloc_view.fromWords(&sparse_words, 0);

    var floor_words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    floor_words[0] |= @as(usize, 1);
    const floor_view = ida_alloc_view.fromWords(&floor_words, 1024);

    var ceiling_words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    const last_used_bit: u32 = ida_alloc_view.chunk_id_span - 2;
    ceiling_words[last_used_bit / ida_bitmap_view.word_bits] |=
        @as(usize, 1) << @intCast(last_used_bit % ida_bitmap_view.word_bits);
    const ceiling_view = ida_alloc_view.fromWords(&ceiling_words, 2048);

    var full_window_words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    full_window_words[0] = 0xff;
    const full_window_view = ida_alloc_view.fromWords(&full_window_words, 0);

    try writer.print(
        "{\n  \"bitmap_bits\": {},\n  \"cases\": [\n",
        .{ida_alloc_view.chunk_id_span},
    );
    try writeCase(writer, "empty_window", empty_view, ida_alloc_view.range(0, 7), true);
    try writeCase(writer, "sparse_window", sparse_view, ida_alloc_view.range(0, 7), true);
    try writeCase(
        writer,
        "clamped_floor_window",
        floor_view,
        ida_alloc_view.range(1000, 1027),
        true,
    );
    try writeCase(
        writer,
        "clamped_ceiling_window",
        ceiling_view,
        ida_alloc_view.range(3070, 4096),
        true,
    );
    try writeCase(
        writer,
        "disjoint_window",
        ida_alloc_view.fromWords(&empty_words, 4096),
        ida_alloc_view.range(0, 100),
        true,
    );
    try writeCase(
        writer,
        "unordered_window",
        empty_view,
        ida_alloc_view.range(9, 3),
        true,
    );
    try writeCase(
        writer,
        "full_window",
        full_window_view,
        ida_alloc_view.range(0, 7),
        false,
    );
    try writer.writeAll("  ]\n}\n");
    try stdout_writer.interface.flush();
}
