const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "phase1 alloc-format counter replay keeps reclaim and free accounting aligned" {
    slab.kmalloc_nr_allocated = 0;

    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const zeroed = slab.kmallocBytes(8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (zeroed) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const plain = slab.kmallocArray(2, 3, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    @memset(plain, 0xa5);
    slab.kfree(plain);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.slabIsAvailable());
}

test "phase1 alloc-format counter replay keeps truncation and terminator windows aligned" {
    var single_known = [_]u8{0xaa};
    const rendered_known = str_error_r.strErrorR(13, &single_known);
    try std.testing.expectEqual(@as(usize, 0), rendered_known.len);
    try std.testing.expectEqual(@as(u8, 0), single_known[0]);

    var single_unknown = [_]u8{0xbb};
    const rendered_unknown = str_error_r.strErrorR(-5, &single_unknown);
    try std.testing.expectEqual(@as(usize, 0), rendered_unknown.len);
    try std.testing.expectEqual(@as(u8, 0), single_unknown[0]);

    var detailed_unknown: [64]u8 = undefined;
    try std.testing.expectEqualStrings(
        "INTERNAL ERROR: strerror_r(-5, [buf], 64)=22",
        str_error_r.strErrorR(-5, &detailed_unknown),
    );

    var tiny_unknown: [8]u8 = undefined;
    try std.testing.expectEqualStrings("INTERNA", str_error_r.strErrorR(-5, &tiny_unknown));
    try std.testing.expectEqual(@as(u8, 0), tiny_unknown[7]);

    var one_byte = [_]u8{0xcc};
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintf(&one_byte, "{s}", .{"zigux"}));
    try std.testing.expectEqual(@as(u8, 0), one_byte[0]);

    var one_logical = [_]u8{ 0xdd, 0xdd, 0xdd };
    try std.testing.expectEqual(@as(usize, 1), vsprintf.scnprintfPad(&one_logical, 1, "{s}", .{"id"}));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 0, 0xdd }, &one_logical);

    var direct = [_]u8{ 0xee, 0xee, 0xee, 0xee, 0xee };
    var alias = [_]u8{ 0xff, 0xff, 0xff, 0xff, 0xff };
    const direct_written = vsprintf.scnprintf(&direct, "{s}", .{"host-tools"});
    const alias_written = vsprintf.vscnprintf(&alias, "{s}", .{"host-tools"});
    try std.testing.expectEqual(direct_written, alias_written);
    try std.testing.expectEqualStrings(direct[0..direct_written], alias[0..alias_written]);
    try std.testing.expectEqual(@as(u8, 0), direct[direct_written]);
    try std.testing.expectEqual(@as(u8, 0), alias[alias_written]);
}

test "phase1 alloc-format counter replay keeps zeroed optional allocations aligned" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);

    const Value = struct {
        count: u32,
        enabled: bool,
        nested: struct {
            marker: u8,
        },
    };

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as(u32, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.enabled);
    try std.testing.expectEqual(@as(u8, 0), value.?.nested.marker);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}
