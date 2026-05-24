const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "narrow helper windows keep one live byte and one terminator slot" {
    slab.kmalloc_nr_allocated = 0;

    const zero_bytes = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    const zero_array = slab.kmallocArray(0, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero_bytes.len);
    try std.testing.expectEqual(@as(usize, 0), zero_array.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    slab.kfree(zero_array);
    slab.kfree(zero_bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var known_buffer = [_]u8{ 0xaa, 0xaa };
    const known = str_error_r.strErrorR(13, &known_buffer);
    try std.testing.expectEqualStrings("P", known);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'P', 0 }, &known_buffer);

    var unknown_buffer = [_]u8{ 0xbb, 0xbb };
    const unknown = str_error_r.strErrorR(4096, &unknown_buffer);
    try std.testing.expectEqualStrings("I", unknown);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'I', 0 }, &unknown_buffer);
}

test "vsprintf narrow windows preserve outer bytes while keeping terminators" {
    var direct = [_]u8{ 0xcc, 0xcc };
    const direct_written = vsprintf.scnprintf(&direct, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 1), direct_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 0 }, &direct);

    var padded_parent = [_]u8{ 0xdd, 0xdd, 0xdd, 0xdd };
    const padded_written = vsprintf.scnprintfPad(padded_parent[1..3], 1, "{s}", .{"ok"});
    try std.testing.expectEqual(@as(usize, 1), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xdd, 'o', 0, 0xdd }, &padded_parent);

    var alias = [_]u8{ 0xee, 0xee };
    const alias_written = vsprintf.vscnprintf(&alias, "{s}", .{"zigux"});
    try std.testing.expectEqual(direct_written, alias_written);
    try std.testing.expectEqualSlices(u8, &direct, &alias);
}

test "zalloc value replay re-zeroes narrow extern storage after dirty frees" {
    const allocator = std.testing.allocator;
    const NarrowValue = extern struct {
        prefix: u8,
        state: extern union {
            word: u16,
            bytes: extern struct {
                lo: u8,
                hi: u8,
            },
        },
        suffix: u8,
    };

    var value: ?*NarrowValue = try zalloc.zallocValue(allocator, NarrowValue);
    try std.testing.expect(value != null);
    try std.testing.expectEqual(@as(u8, 0), value.?.prefix);
    try std.testing.expectEqual(@as(u16, 0), value.?.state.word);
    try std.testing.expectEqual(@as(u8, 0), value.?.suffix);

    value.?.prefix = 0x7a;
    value.?.state.word = 0xffff;
    value.?.suffix = 0x31;
    zalloc.zfreeValue(allocator, NarrowValue, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, NarrowValue, &value);
    try std.testing.expect(value == null);

    var rebound: ?*NarrowValue = try zalloc.zallocValue(allocator, NarrowValue);
    defer zalloc.zfreeValue(allocator, NarrowValue, &rebound);
    try std.testing.expect(rebound != null);
    try std.testing.expectEqual(@as(u8, 0), rebound.?.prefix);
    try std.testing.expectEqual(@as(u16, 0), rebound.?.state.word);
    try std.testing.expectEqual(@as(u8, 0), rebound.?.suffix);
}
