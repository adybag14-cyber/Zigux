const std = @import("std");
const Io = std.Io;
const abi = @import("abi_bindings");

fn isIntegerConstant(comptime T: type) bool {
    return switch (@typeInfo(T)) {
        .int, .comptime_int => true,
        else => false,
    };
}

fn isExternStruct(comptime T: type) bool {
    return switch (@typeInfo(T)) {
        .@"struct" => |info| info.layout == .@"extern",
        else => false,
    };
}

fn writeQuoted(writer: anytype, text: []const u8) !void {
    try writer.writeByte('"');
    try writer.writeAll(text);
    try writer.writeByte('"');
}

fn writeStruct(writer: anytype, comptime name: []const u8, comptime T: type) !void {
    try writeQuoted(writer, name);
    try writer.writeAll(":{\"size\":");
    try writer.print("{d}", .{@sizeOf(T)});
    try writer.writeAll(",\"align\":");
    try writer.print("{d}", .{@alignOf(T)});
    try writer.writeAll(",\"offsets\":{");
    inline for (std.meta.fields(T), 0..) |field, index| {
        if (index != 0) try writer.writeByte(',');
        try writeQuoted(writer, field.name);
        try writer.writeByte(':');
        try writer.print("{d}", .{@offsetOf(T, field.name)});
    }
    try writer.writeAll("}}");
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    const abi_decls = comptime std.meta.declarations(abi);
    var stdout_buffer: [4096]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout_writer.interface;

    try writer.writeAll("{\"abi_version\":");
    if (@hasDecl(abi, "ABI_VERSION")) {
        try writer.print("{d}", .{@field(abi, "ABI_VERSION")});
    } else {
        try writer.writeByte('0');
    }

    try writer.writeAll(",\"constants\":{");
    var first_constant = true;
    inline for (abi_decls) |decl| {
        const value = @field(abi, decl.name);
        const T = @TypeOf(value);
        if (comptime isIntegerConstant(T) and !std.mem.eql(u8, decl.name, "ABI_VERSION")) {
            if (!first_constant) try writer.writeByte(',');
            first_constant = false;
            try writeQuoted(writer, decl.name);
            try writer.writeByte(':');
            try writer.print("{d}", .{value});
        }
    }

    try writer.writeAll("},\"structs\":{");
    var first_struct = true;
    inline for (abi_decls) |decl| {
        const value = @field(abi, decl.name);
        const T = @TypeOf(value);
        if (comptime T == type and isExternStruct(value)) {
            if (!first_struct) try writer.writeByte(',');
            first_struct = false;
            try writeStruct(writer, decl.name, value);
        }
    }

    try writer.writeAll("}}\n");
    try stdout_writer.interface.flush();
}
