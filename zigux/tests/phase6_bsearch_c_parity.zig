const std = @import("std");
const bsearch = @import("bsearch");

const Symbol = struct {
    name: []const u8,
    address: usize,
};

fn compareU32(key: *const u32, item: *const u32) callconv(.c) c_int {
    return switch (std.math.order(key.*, item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareDescendingU32(key: *const u32, item: *const u32) callconv(.c) c_int {
    return compareU32(item, key);
}

fn compareSymbolName(key: *const []const u8, item: *const Symbol) callconv(.c) c_int {
    return switch (std.mem.order(u8, key.*, item.name)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [2048]u8 = undefined;
    var stdout = std.Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout.interface;

    const values = [_]u32{ 3, 8, 13, 21, 34, 55, 89 };
    const duplicate_at_beginning = [_]u32{ 7, 7, 7, 12, 18, 24 };
    const duplicate_in_middle = [_]u32{ 2, 7, 7, 7, 12, 18 };
    const duplicate_at_end = [_]u32{ 2, 7, 12, 18, 18, 18 };
    const singleton = [_]u32{21};
    const empty = [_]u32{};
    const descending_values = [_]u32{ 89, 55, 34, 21, 13, 8, 3 };
    const symbols = [_]Symbol{
        .{ .name = "do_exit", .address = 0x1000 },
        .{ .name = "kfree", .address = 0x1200 },
        .{ .name = "kmalloc", .address = 0x1400 },
        .{ .name = "schedule", .address = 0x1800 },
    };

    try writeIndexCase(writer, "u32-hit", 3, bsearch.searchIndex(u32, u32, &@as(u32, 3), values[0..], compareU32));
    try writeIndexCase(writer, "u32-hit", 21, bsearch.searchIndex(u32, u32, &@as(u32, 21), values[0..], compareU32));
    try writeIndexCase(writer, "u32-hit", 89, bsearch.searchIndex(u32, u32, &@as(u32, 89), values[0..], compareU32));
    try writeIndexCase(writer, "u32-miss", 0, bsearch.searchIndex(u32, u32, &@as(u32, 0), values[0..], compareU32));
    try writeIndexCase(writer, "u32-miss", 15, bsearch.searchIndex(u32, u32, &@as(u32, 15), values[0..], compareU32));
    try writeIndexCase(writer, "u32-miss", 90, bsearch.searchIndex(u32, u32, &@as(u32, 90), values[0..], compareU32));
    try writeIndexCase(writer, "singleton-hit", 21, bsearch.searchIndex(u32, u32, &@as(u32, 21), singleton[0..], compareU32));
    try writeIndexCase(writer, "singleton-miss", 20, bsearch.searchIndex(u32, u32, &@as(u32, 20), singleton[0..], compareU32));
    try writeIndexCase(writer, "empty-miss", 21, bsearch.searchIndex(u32, u32, &@as(u32, 21), empty[0..], compareU32));
    try writeIndexCase(writer, "descending-hit", 34, bsearch.searchIndex(u32, u32, &@as(u32, 34), descending_values[0..], compareDescendingU32));
    try writeIndexCase(writer, "descending-miss", 20, bsearch.searchIndex(u32, u32, &@as(u32, 20), descending_values[0..], compareDescendingU32));
    try writeDuplicateCase(writer, "duplicate-hit-begin", 7, bsearch.searchIndex(u32, u32, &@as(u32, 7), duplicate_at_beginning[0..], compareU32));
    try writeDuplicateCase(writer, "duplicate-hit-middle", 7, bsearch.searchIndex(u32, u32, &@as(u32, 7), duplicate_in_middle[0..], compareU32));
    try writeDuplicateCase(writer, "duplicate-hit-end", 18, bsearch.searchIndex(u32, u32, &@as(u32, 18), duplicate_at_end[0..], compareU32));

    const kmalloc = bsearch.search([]const u8, Symbol, &@as([]const u8, "kmalloc"), symbols[0..], compareSymbolName);
    if (kmalloc) |item| {
        try writer.print("sym-hit\tkmalloc\t0x{x}\n", .{item.address});
    } else {
        try writer.writeAll("sym-hit\tkmalloc\tnull\n");
    }

    const vfree = bsearch.search([]const u8, Symbol, &@as([]const u8, "vfree"), symbols[0..], compareSymbolName);
    if (vfree) |item| {
        try writer.print("sym-miss\tvfree\t0x{x}\n", .{item.address});
    } else {
        try writer.writeAll("sym-miss\tvfree\tnull\n");
    }

    var mutable_values = [_]u32{ 3, 8, 13, 21, 34, 55, 89 };
    const found_mutable = bsearch.searchMutable(u32, u32, &@as(u32, 21), mutable_values[0..], compareU32);
    if (found_mutable) |item| {
        item.* = 22;
        try writer.print("mutable-hit\t21\t{}\n", .{mutable_values[3]});
    } else {
        try writer.writeAll("mutable-hit\t21\tnull\n");
    }

    try stdout.flush();
}

fn writeIndexCase(writer: *std.Io.Writer, label: []const u8, key: u32, index: ?usize) !void {
    if (index) |found| {
        try writer.print("{s}\t{}\t{}\n", .{ label, key, found });
    } else {
        try writer.print("{s}\t{}\tnull\n", .{ label, key });
    }
}

fn writeDuplicateCase(writer: *std.Io.Writer, label: []const u8, key: u32, index: ?usize) !void {
    if (index != null) {
        try writer.print("{s}\t{}\tfound\n", .{ label, key });
    } else {
        try writer.print("{s}\t{}\tnull\n", .{ label, key });
    }
}
