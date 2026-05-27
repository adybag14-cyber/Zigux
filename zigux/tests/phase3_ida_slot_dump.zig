const std = @import("std");
const Io = std.Io;
const ida_slot_view = @import("ida_slot_view");

fn kindName(kind: ida_slot_view.SlotKind) []const u8 {
    return switch (kind) {
        .empty => "empty",
        .inline_bits => "inline_bits",
        .bitmap_pointer => "bitmap_pointer",
        .unexpected_err => "unexpected_err",
    };
}

fn writeOptionalSigned(writer: anytype, value: ?isize) !void {
    if (value) |signed| {
        try writer.print("{}", .{signed});
        return;
    }
    try writer.writeAll("null");
}

fn writeOptionalUnsigned(writer: anytype, value: ?usize) !void {
    if (value) |unsigned| {
        try writer.print("{}", .{unsigned});
        return;
    }
    try writer.writeAll("null");
}

fn writeCase(writer: anytype, name: []const u8, raw: usize, trailing_comma: bool) !void {
    const slot = ida_slot_view.fromRaw(raw);

    var hex_buffer: [2 + (@sizeOf(usize) * 2) + 1]u8 = undefined;
    const raw_hex = try std.fmt.bufPrint(&hex_buffer, "0x{x}", .{raw});

    try writer.print(
        "    {{\n" ++
            "      \"name\": \"{s}\",\n" ++
            "      \"kind\": \"{s}\",\n" ++
            "      \"raw_hex\": \"{s}\",\n" ++
            "      \"inline_mask\": ",
        .{
            name,
            kindName(slot.kind()),
            raw_hex,
        },
    );
    try writeOptionalUnsigned(writer, slot.inlineMask());
    try writer.writeAll(",\n      \"inline_bit_count\": ");
    try writeOptionalUnsigned(writer, slot.inlineBitCount());
    try writer.writeAll(",\n      \"first_inline_bit\": ");
    try writeOptionalUnsigned(writer, slot.firstInlineBit());
    try writer.writeAll(",\n      \"bitmap_pointer\": ");
    try writeOptionalUnsigned(writer, slot.bitmapPointer());
    try writer.writeAll(",\n      \"unexpected_error\": ");
    try writeOptionalSigned(writer, slot.unexpectedErrorCode());
    try writer.writeAll("\n    }");
    if (trailing_comma) {
        try writer.writeAll(",");
    }
    try writer.writeAll("\n");
}

fn bitMask(bit_index: usize) usize {
    return @as(usize, 1) << @intCast(bit_index);
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout_writer.interface;

    const inline_sparse = try ida_slot_view.fromInlineMask(bitMask(1) | bitMask(4) | bitMask(9));
    const inline_top = try ida_slot_view.fromInlineMask(bitMask(ida_slot_view.inline_bit_capacity - 1));

    try writer.print(
        "{{\n" ++
            "  \"word_bits\": {},\n" ++
            "  \"inline_bit_capacity\": {},\n" ++
            "  \"cases\": [\n",
        .{
            @bitSizeOf(usize),
            ida_slot_view.inline_bit_capacity,
        },
    );

    try writeCase(writer, "empty", 0, true);
    try writeCase(writer, "inline_one", (try ida_slot_view.fromInlineMask(bitMask(0))).rawValue(), true);
    try writeCase(writer, "inline_sparse", inline_sparse.rawValue(), true);
    try writeCase(writer, "inline_top", inline_top.rawValue(), true);
    try writeCase(writer, "bitmap_pointer", ida_slot_view.fromBitmapPointer(0x4000).rawValue(), true);
    try writeCase(writer, "unexpected_err", ida_slot_view.fromUnexpectedError(-22).rawValue(), false);

    try writer.writeAll("  ]\n}\n");
    try stdout_writer.interface.flush();
}
