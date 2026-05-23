const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps zero-sized tracked allocations balanced across failed requests" {
    slab.kmalloc_nr_allocated = 0;

    const zero_bytes = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    const zero_array = slab.kmallocArray(0, 9, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        slab.kfree(zero_bytes);
        return error.TestUnexpectedResult;
    };

    try std.testing.expectEqual(@as(usize, 0), zero_bytes.len);
    try std.testing.expectEqual(@as(usize, 0), zero_array.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocBytes(4, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(zero_array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(zero_bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR rewrites shorter known messages inside the same offset window" {
    var backing = [_]u8{'!'} ** 64;
    const window = backing[4..52];

    const generated = str_error_r.strErrorR(123, window);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(123, [buf], 48)=22", generated);
    try std.testing.expectEqual(@as(u8, 0), window[generated.len]);
    try std.testing.expectEqual(@as(u8, '!'), backing[3]);
    try std.testing.expectEqual(@as(u8, '!'), backing[52]);

    const known = str_error_r.strErrorR(0, window);
    try std.testing.expectEqualStrings("Success", known);
    try std.testing.expectEqual(@as(u8, 0), window[known.len]);
    try std.testing.expectEqual(@as(u8, '!'), backing[3]);
    try std.testing.expectEqual(@as(u8, '!'), backing[52]);
}

test "vsprintf reuses offset windows across padded and unpadded rewrites" {
    var backing = [_]u8{'#'} ** 12;
    const window = backing[3..10];

    const padded = vsprintf.scnprintfPad(window, 5, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 4), padded);
    try std.testing.expectEqualStrings("xy   ", window[0..5]);
    try std.testing.expectEqual(@as(u8, 0), window[5]);

    const rewritten = vsprintf.scnprintf(window, "{s}", .{"q"});
    try std.testing.expectEqual(@as(usize, 1), rewritten);
    try std.testing.expectEqual(@as(u8, 'q'), window[0]);
    try std.testing.expectEqual(@as(u8, 0), window[1]);
    try std.testing.expectEqual(@as(u8, '#'), backing[2]);
    try std.testing.expectEqual(@as(u8, '#'), backing[10]);
}

test "zalloc keeps holder sentinels while re-zeroing nested extern storage" {
    const allocator = std.testing.allocator;

    const Cell = extern union {
        word: u32,
        flag: u8,
    };
    const Value = extern struct {
        header: u16,
        cells: [2]Cell,
        tail: u8,
    };
    const Holder = struct {
        keep: u8,
        bytes: ?[]u8,
        value: ?*Value,
        tail: u8,
    };

    var holder = Holder{
        .keep = 0x11,
        .bytes = try zalloc.zallocBytes(allocator, 0),
        .value = try zalloc.zallocValue(allocator, Value),
        .tail = 0x22,
    };
    defer zalloc.zfreeBytes(allocator, &holder.bytes);
    defer zalloc.zfreeValue(allocator, Value, &holder.value);

    try std.testing.expectEqual(@as(usize, 0), holder.bytes.?.len);
    try std.testing.expectEqual(@as(u16, 0), holder.value.?.header);
    try std.testing.expectEqual(@as(u32, 0), holder.value.?.cells[0].word);
    try std.testing.expectEqual(@as(u32, 0), holder.value.?.cells[1].word);
    try std.testing.expectEqual(@as(u8, 0), holder.value.?.tail);

    zalloc.zfreeBytes(allocator, &holder.bytes);
    try std.testing.expect(holder.bytes == null);
    try std.testing.expectEqual(@as(u8, 0x11), holder.keep);
    try std.testing.expectEqual(@as(u8, 0x22), holder.tail);

    holder.value.?.header = 9;
    holder.value.?.cells[0].word = 17;
    holder.value.?.cells[1].word = 23;
    holder.value.?.tail = 5;
    zalloc.zfreeValue(allocator, Value, &holder.value);
    try std.testing.expect(holder.value == null);
    try std.testing.expectEqual(@as(u8, 0x11), holder.keep);
    try std.testing.expectEqual(@as(u8, 0x22), holder.tail);

    holder.value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expectEqual(@as(u16, 0), holder.value.?.header);
    try std.testing.expectEqual(@as(u32, 0), holder.value.?.cells[0].word);
    try std.testing.expectEqual(@as(u32, 0), holder.value.?.cells[1].word);
    try std.testing.expectEqual(@as(u8, 0), holder.value.?.tail);
}
