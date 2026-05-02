const std = @import("std");
const bsearch = @import("bsearch");

const Symbol = struct {
    name: []const u8,
    address: usize,
};

fn compareU32(key: *const u32, item: *const u32) callconv(.c) i32 {
    return switch (std.math.order(key.*, item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareDescendingU32(key: *const u32, item: *const u32) callconv(.c) i32 {
    return compareU32(item, key);
}

fn compareOpaqueU32(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return compareU32(typed_key, typed_item);
}

fn compareOpaqueDescendingU32(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return compareDescendingU32(typed_key, typed_item);
}

fn compareSymbolName(key: *const []const u8, item: *const Symbol) callconv(.c) i32 {
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
    try writeIndexCase(writer, "raw-hit", 34, bsearch.bsearchIndex(&@as(u32, 34), @ptrCast(values[0..].ptr), values.len, @sizeOf(u32), compareOpaqueU32));
    try writeIndexCase(writer, "raw-miss", 20, bsearch.bsearchIndex(&@as(u32, 20), @ptrCast(values[0..].ptr), values.len, @sizeOf(u32), compareOpaqueU32));
    try writeIndexCase(writer, "raw-descending-hit", 34, bsearch.bsearchIndex(&@as(u32, 34), @ptrCast(descending_values[0..].ptr), descending_values.len, @sizeOf(u32), compareOpaqueDescendingU32));
    try writeRuntimeTypedCases(writer, values[0..], descending_values[0..]);
    try writeRuntimeRawCases(writer, values[0..], descending_values[0..]);

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

    try writeRuntimeTypedMutableCase(writer, "mutable-hit", 34, compareDescendingU32, descending_values[0..]);
    try writeRuntimeRawMutableCase(writer, "raw-mutable-hit", 34, compareOpaqueDescendingU32, descending_values[0..]);

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

fn writeRuntimeTypedCases(
    writer: *std.Io.Writer,
    ascending_values: []const u32,
    descending_values: []const u32,
) !void {
    const cases = [_]struct {
        label: []const u8,
        key: u32,
        values: []const u32,
        compare: bsearch.CComparator(u32, u32),
    }{
        .{ .label = "runtime-typed-hit", .key = 55, .values = ascending_values, .compare = compareU32 },
        .{ .label = "runtime-typed-hit", .key = 34, .values = descending_values, .compare = compareDescendingU32 },
        .{ .label = "runtime-typed-miss-ascending", .key = 20, .values = ascending_values, .compare = compareU32 },
        .{ .label = "runtime-typed-miss-descending", .key = 20, .values = descending_values, .compare = compareDescendingU32 },
    };

    for (cases) |case| {
        try writeIndexCase(writer, case.label, case.key, bsearch.searchIndex(u32, u32, &case.key, case.values, case.compare));
    }
}

fn writeRuntimeRawCases(
    writer: *std.Io.Writer,
    ascending_values: []const u32,
    descending_values: []const u32,
) !void {
    const cases = [_]struct {
        label: []const u8,
        key: u32,
        values: []const u32,
        compare: bsearch.CRawComparator,
    }{
        .{ .label = "runtime-raw-hit", .key = 55, .values = ascending_values, .compare = compareOpaqueU32 },
        .{ .label = "runtime-raw-hit", .key = 34, .values = descending_values, .compare = compareOpaqueDescendingU32 },
        .{ .label = "runtime-raw-miss-ascending", .key = 20, .values = ascending_values, .compare = compareOpaqueU32 },
        .{ .label = "runtime-raw-miss-descending", .key = 20, .values = descending_values, .compare = compareOpaqueDescendingU32 },
    };

    for (cases) |case| {
        try writeIndexCase(
            writer,
            case.label,
            case.key,
            bsearch.bsearchIndex(&case.key, @ptrCast(case.values.ptr), case.values.len, @sizeOf(u32), case.compare),
        );
    }
}

fn writeRuntimeTypedMutableCase(
    writer: *std.Io.Writer,
    label: []const u8,
    key: u32,
    compare: bsearch.CComparator(u32, u32),
    source_values: []const u32,
) !void {
    var mutable_values: [7]u32 = undefined;
    @memcpy(mutable_values[0..], source_values);
    const found_mutable = bsearch.searchMutable(u32, u32, &key, mutable_values[0..], compare);
    if (found_mutable) |item| {
        item.* += 1;
        try writer.print("{s}\t{}\t{}\n", .{ label, key, item.* });
    } else {
        try writer.print("{s}\t{}\tnull\n", .{ label, key });
    }
}

fn writeRuntimeRawMutableCase(
    writer: *std.Io.Writer,
    label: []const u8,
    key: u32,
    compare: bsearch.CRawComparator,
    source_values: []const u32,
) !void {
    var mutable_values: [7]u32 = undefined;
    @memcpy(mutable_values[0..], source_values);
    const found_mutable = bsearch.bsearchMutable(&key, @ptrCast(mutable_values[0..].ptr), mutable_values.len, @sizeOf(u32), compare);
    if (found_mutable) |item| {
        const typed_item: *u32 = @ptrCast(@alignCast(item));
        typed_item.* += 1;
        try writer.print("{s}\t{}\t{}\n", .{ label, key, typed_item.* });
    } else {
        try writer.print("{s}\t{}\tnull\n", .{ label, key });
    }
}
