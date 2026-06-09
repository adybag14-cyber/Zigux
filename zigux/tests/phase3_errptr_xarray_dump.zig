const std = @import("std");
const Io = std.Io;
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");

fn kindFor(raw: usize) []const u8 {
    if (raw == 0) {
        return "null";
    }
    if (xa_value.isValue(raw)) {
        return "xa_value";
    }
    if (err_ptr.isErrValue(raw)) {
        return "err_ptr";
    }
    return "pointer_like";
}

test "dump kind classification keeps err_ptr precedence for rejected inline raws" {
    const inline_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const first_rejected_inline = xa_value.safe_inline_limit + 1;
    const overlapping_raw = (first_rejected_inline << 1) | xa_value.value_tag_mask;

    try std.testing.expectEqual(err_ptr.err_floor - 2, inline_limit_raw);
    try std.testing.expectEqual(err_ptr.err_floor - 1, inline_limit_raw + 1);
    try std.testing.expectEqual(err_ptr.err_floor, overlapping_raw);

    try std.testing.expectEqualStrings("xa_value", kindFor(inline_limit_raw));
    try std.testing.expectEqualStrings("pointer_like", kindFor(inline_limit_raw + 1));
    try std.testing.expectEqualStrings("err_ptr", kindFor(overlapping_raw));
    try std.testing.expectEqualStrings("err_ptr", kindFor(err_ptr.fromErrorCode(-1)));
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
    var hex_buffer: [2 + (@sizeOf(usize) * 2) + 1]u8 = undefined;
    const raw_hex = try std.fmt.bufPrint(&hex_buffer, "0x{x}", .{raw});

    var decimal_buffer: [std.fmt.count("{}", .{std.math.maxInt(usize)})]u8 = undefined;
    const raw_decimal = try std.fmt.bufPrint(&decimal_buffer, "{}", .{raw});

    const is_err = err_ptr.isErrValue(raw);
    const is_value = xa_value.isValue(raw);
    const decoded_error: ?isize = if (is_err) err_ptr.toErrorCode(raw) else null;
    const decoded_value: ?usize = if (is_value) xa_value.toValue(raw) else null;

    try writer.print(
        "    {{\n" ++
            "      \"name\": \"{s}\",\n" ++
            "      \"kind\": \"{s}\",\n" ++
            "      \"raw_hex\": \"{s}\",\n" ++
            "      \"raw_decimal\": \"{s}\",\n" ++
            "      \"is_err\": {s},\n" ++
            "      \"is_value\": {s},\n" ++
            "      \"decoded_error\": ",
        .{
            name,
            kindFor(raw),
            raw_hex,
            raw_decimal,
            if (is_err) "true" else "false",
            if (is_value) "true" else "false",
        },
    );
    try writeOptionalSigned(writer, decoded_error);
    try writer.writeAll(",\n      \"decoded_value\": ");
    try writeOptionalUnsigned(writer, decoded_value);
    try writer.writeAll("\n    }");
    if (trailing_comma) {
        try writer.writeAll(",");
    }
    try writer.writeAll("\n");
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout_writer.interface;

    const inline_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);

    try writer.print(
        "{{\n" ++
            "  \"word_bits\": {},\n" ++
            "  \"safe_inline_limit\": {},\n" ++
            "  \"safe_inline_limit_raw_hex\": \"0x{x}\",\n" ++
            "  \"cases\": [\n",
        .{
            @bitSizeOf(usize),
            xa_value.safe_inline_limit,
            inline_limit_raw,
        },
    );

    try writeCase(writer, "null", 0, true);
    try writeCase(writer, "pointer_like", 64, true);
    try writeCase(writer, "inline_small", try xa_value.makeValue(29), true);
    try writeCase(writer, "inline_limit", inline_limit_raw, true);
    try writeCase(writer, "gap_before_err_floor", err_ptr.err_floor - 1, true);
    try writeCase(writer, "err_enomem", err_ptr.fromErrorCode(-12), true);
    try writeCase(writer, "err_max", err_ptr.fromErrorCode(-4095), false);

    try writer.writeAll("  ]\n}\n");
    try stdout_writer.interface.flush();
}
