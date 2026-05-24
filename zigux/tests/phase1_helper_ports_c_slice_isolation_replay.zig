const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab split allocations keep counts isolated across null frees and failures" {
    slab.kmalloc_nr_allocated = 0;

    const empty = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    const live = slab.kmallocArray(3, 1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (live) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocArray(3, 1, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocBytes(std.math.maxInt(usize), slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(live);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR offset slices leave neighboring caller bytes untouched" {
    var known_backing = [_]u8{0xaa} ** 7;
    const known = str_error_r.strErrorR(0, known_backing[1..5]);
    try std.testing.expectEqualStrings("Suc", known);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 'S', 'u', 'c', 0, 0xaa, 0xaa }, &known_backing);

    var generated_backing = [_]u8{0xbb} ** 9;
    const generated = str_error_r.strErrorR(4096, generated_backing[2..8]);
    try std.testing.expectEqualStrings("INTER", generated);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 0xbb, 0xbb, 'I', 'N', 'T', 'E', 'R', 0, 0xbb },
        &generated_backing,
    );
}

test "vsprintf offset slices keep outer storage stable" {
    var direct_backing = [_]u8{0xcc} ** 7;
    const direct_written = vsprintf.scnprintf(direct_backing[1..6], "{s}:{d}", .{ "z", 7 });
    try std.testing.expectEqual(@as(usize, 3), direct_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 'z', ':', '7', 0, 0xcc, 0xcc }, &direct_backing);

    var alias_backing = [_]u8{0xdd} ** 7;
    const alias_written = vsprintf.vscnprintf(alias_backing[1..6], "{s}:{d}", .{ "z", 7 });
    try std.testing.expectEqual(direct_written, alias_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xdd, 'z', ':', '7', 0, 0xdd, 0xdd }, &alias_backing);

    var padded_backing = [_]u8{0xee} ** 8;
    const padded_written = vsprintf.scnprintfPad(padded_backing[2..6], 2, "{s}", .{"ok"});
    try std.testing.expectEqual(@as(usize, 2), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xee, 0xee, 'o', 'k', 0, 0xee, 0xee, 0xee }, &padded_backing);
}

test "zalloc re-zeroes nested extern aggregates after a dirty free" {
    const allocator = std.testing.allocator;

    const Word = extern union {
        word: u16,
        bytes: extern struct {
            lo: u8,
            hi: u8,
        },
    };

    const Cell = extern struct {
        state: Word,
        marker: u8,
    };

    const Box = extern struct {
        prefix: u8,
        cells: [2]Cell,
        suffix: u8,
    };

    var box: ?*Box = try zalloc.zallocValue(allocator, Box);
    try std.testing.expect(box != null);
    try std.testing.expectEqual(@as(u8, 0), box.?.prefix);
    try std.testing.expectEqual(@as(u16, 0), box.?.cells[0].state.word);
    try std.testing.expectEqual(@as(u8, 0), box.?.cells[0].marker);
    try std.testing.expectEqual(@as(u16, 0), box.?.cells[1].state.word);
    try std.testing.expectEqual(@as(u8, 0), box.?.cells[1].marker);
    try std.testing.expectEqual(@as(u8, 0), box.?.suffix);

    box.?.prefix = 0x31;
    box.?.cells[0].state.word = 0xaaaa;
    box.?.cells[0].marker = 0x42;
    box.?.cells[1].state.bytes.lo = 0x77;
    box.?.cells[1].state.bytes.hi = 0x88;
    box.?.cells[1].marker = 0x24;
    box.?.suffix = 0x13;
    zalloc.zfreeValue(allocator, Box, &box);
    try std.testing.expect(box == null);

    var rebound: ?*Box = try zalloc.zallocValue(allocator, Box);
    defer zalloc.zfreeValue(allocator, Box, &rebound);
    try std.testing.expect(rebound != null);
    try std.testing.expectEqual(@as(u8, 0), rebound.?.prefix);
    try std.testing.expectEqual(@as(u16, 0), rebound.?.cells[0].state.word);
    try std.testing.expectEqual(@as(u8, 0), rebound.?.cells[0].marker);
    try std.testing.expectEqual(@as(u16, 0), rebound.?.cells[1].state.word);
    try std.testing.expectEqual(@as(u8, 0), rebound.?.cells[1].marker);
    try std.testing.expectEqual(@as(u8, 0), rebound.?.suffix);
}
