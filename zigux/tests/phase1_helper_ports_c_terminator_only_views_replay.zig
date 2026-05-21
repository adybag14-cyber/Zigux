const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "phase1 helper ports C keeps slab null frees and one-byte allocations balanced" {
    slab.kmalloc_nr_allocated = 0;
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const single = slab.kmallocBytes(1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(single);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(usize, 1), single.len);
    try std.testing.expectEqual(@as(u8, 0), single[0]);

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "phase1 helper ports C keeps strErrorR terminator-only views inside caller bounds" {
    var known_backing = [_]u8{ '^', '^', '^' };
    const known = str_error_r.strErrorR(0, known_backing[1..2]);
    try std.testing.expectEqual(@as(usize, 0), known.len);
    try std.testing.expectEqual(@as(u8, '^'), known_backing[0]);
    try std.testing.expectEqual(@as(u8, 0), known_backing[1]);
    try std.testing.expectEqual(@as(u8, '^'), known_backing[2]);

    var generated_backing = [_]u8{ '&', '&', '&' };
    const generated = str_error_r.strErrorR(4096, generated_backing[1..2]);
    try std.testing.expectEqual(@as(usize, 0), generated.len);
    try std.testing.expectEqual(@as(u8, '&'), generated_backing[0]);
    try std.testing.expectEqual(@as(u8, 0), generated_backing[1]);
    try std.testing.expectEqual(@as(u8, '&'), generated_backing[2]);
}

test "phase1 helper ports C keeps vsprintf terminator-only and zero-logical views stable" {
    var single_backing = [_]u8{ '!', '!', '!' };
    const single_view = single_backing[1..2];
    const single_written = vsprintf.scnprintf(single_view, "{s}", .{"wide"});
    try std.testing.expectEqual(@as(usize, 0), single_written);
    try std.testing.expectEqual(@as(u8, '!'), single_backing[0]);
    try std.testing.expectEqual(@as(u8, 0), single_backing[1]);
    try std.testing.expectEqual(@as(u8, '!'), single_backing[2]);

    var padded_backing = [_]u8{ '?', '?', '?', '?' };
    const padded_view = padded_backing[1..3];
    const padded_written = vsprintf.scnprintfPad(padded_view, 0, "{s}", .{"zig"});
    try std.testing.expectEqual(@as(usize, 0), padded_written);
    try std.testing.expectEqual(@as(u8, '?'), padded_backing[0]);
    try std.testing.expectEqual(@as(u8, 0), padded_backing[1]);
    try std.testing.expectEqual(@as(u8, '?'), padded_backing[2]);
    try std.testing.expectEqual(@as(u8, '?'), padded_backing[3]);
}

test "phase1 helper ports C keeps zalloc null optionals and tiny allocations aligned" {
    const allocator = std.testing.allocator;
    const Value = struct {
        byte: u8,
    };

    var bytes: ?[]u8 = null;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 1);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 1), bytes.?.len);
    try std.testing.expectEqual(@as(u8, 0), bytes.?[0]);

    var value: ?*Value = null;
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as(u8, 0), value.?.byte);
}
