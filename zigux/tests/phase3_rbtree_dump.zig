const std = @import("std");
const Io = std.Io;
const rbtree = @import("rbtree_bindings");

fn writeStructLayout(writer: anytype, comptime name: []const u8, comptime T: type) !void {
    try writer.writeAll("\"");
    try writer.writeAll(name);
    try writer.writeAll("\":{\"size\":");
    try writer.print("{d}", .{@sizeOf(T)});
    try writer.writeAll(",\"align\":");
    try writer.print("{d}", .{@alignOf(T)});
    try writer.writeAll(",\"offsets\":{");
    const fields = std.meta.fields(T);
    inline for (fields, 0..) |field, index| {
        try writer.writeAll("\"");
        try writer.writeAll(field.name);
        try writer.writeAll("\":");
        try writer.print("{d}", .{@offsetOf(T, field.name)});
        if (index + 1 < fields.len) try writer.writeAll(",");
    }
    try writer.writeAll("}}");
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [512]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout_writer.interface;

    try writer.writeAll("{\"constants\":{\"root_flag_empty\":");
    try writer.print("{d}", .{rbtree.ROOT_FLAG_EMPTY});
    try writer.writeAll(",\"root_flag_cached\":");
    try writer.print("{d}", .{rbtree.ROOT_FLAG_CACHED});
    try writer.writeAll(",\"root_flag_leftmost_valid\":");
    try writer.print("{d}", .{rbtree.ROOT_FLAG_LEFTMOST_VALID});
    try writer.writeAll("},\"structs\":{");
    try writeStructLayout(writer, "zigux_rbtree_root_view", rbtree.RootView);
    try writer.writeAll("}}\n");
    try writer.flush();
}
