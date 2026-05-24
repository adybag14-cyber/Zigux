const std = @import("std");
const vectors = @import("fixtures/phase6_base64_c_parity_vectors.zig");

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
    var stdout = std.Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout.interface;

    for (vectors.encode_cases) |case| {
        try writer.print("enc\t{s}\t{}\t", .{
            vectors.variantName(case.variant),
            @intFromBool(case.padding),
        });
        try writeHex(writer, case.input);
        try writer.writeAll("\n");
    }

    for (vectors.decode_cases) |case| {
        try writer.print("dec\t{s}\t{}\t", .{
            vectors.variantName(case.variant),
            @intFromBool(case.padding),
        });
        try writeHex(writer, case.input);
        try writer.writeAll("\n");
    }

    for (vectors.invalid_cases) |case| {
        try writer.print("inv\t{s}\t{}\t", .{
            vectors.variantName(case.variant),
            @intFromBool(case.padding),
        });
        try writeHex(writer, case.input);
        try writer.writeAll("\n");
    }

    try stdout.flush();
}

fn writeHex(writer: *std.Io.Writer, bytes: []const u8) !void {
    const hex = "0123456789abcdef";
    for (bytes) |byte| {
        const pair = [_]u8{
            hex[byte >> 4],
            hex[byte & 0x0f],
        };
        try writer.writeAll(&pair);
    }
}

test "casegen emits the expected corpus size" {
    try std.testing.expectEqual(@as(usize, 40), vectors.encode_cases.len + vectors.decode_cases.len + vectors.invalid_cases.len);
}
