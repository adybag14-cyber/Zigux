const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 current replay imports helper ports cleanly" {
    _ = slab;
    _ = str_error_r;
    _ = vsprintf;
    _ = zalloc;
}

test "lane10 current replay keeps exact-fit and live-failure contracts" {
    slab.kmalloc_nr_allocated = 0;

    const live = slab.kmallocBytes(4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (live) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    try std.testing.expect(slab.kmallocBytes(4, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(live);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var success_buffer: [8]u8 = undefined;
    const success = str_error_r.strErrorR(0, &success_buffer);
    try std.testing.expectEqualStrings("Success", success);
    try std.testing.expectEqual(@as(u8, 0), success_buffer[success.len]);
    try std.testing.expectEqual(@intFromPtr(&success_buffer[0]), @intFromPtr(success.ptr));

    var generated_buffer: [48]u8 = undefined;
    const generated = str_error_r.strErrorR(4096, &generated_buffer);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(4096, [buf], 48)=22", generated);
    try std.testing.expectEqual(@as(u8, 0), generated_buffer[generated.len]);
    try std.testing.expectEqual(@intFromPtr(&generated_buffer[0]), @intFromPtr(generated.ptr));
}

test "lane10 current replay keeps render parity and re-zero contracts" {
    var scnprintf_buffer: [7]u8 = undefined;
    var vscnprintf_buffer: [7]u8 = undefined;
    const scnprintf_written = vsprintf.scnprintf(&scnprintf_buffer, "{s}:{d}", .{ "zigux", 7 });
    const vscnprintf_written = vsprintf.vscnprintf(&vscnprintf_buffer, "{s}:{d}", .{ "zigux", 7 });
    try std.testing.expectEqual(scnprintf_written, vscnprintf_written);
    try std.testing.expectEqualStrings(scnprintf_buffer[0..scnprintf_written], vscnprintf_buffer[0..vscnprintf_written]);

    var exact_pad_buffer: [8]u8 = undefined;
    const exact_pad_written = vsprintf.scnprintfPad(&exact_pad_buffer, 4, "id={d}", .{7});
    try std.testing.expectEqual(@as(usize, 4), exact_pad_written);
    try std.testing.expectEqualStrings("id=7", exact_pad_buffer[0..exact_pad_written]);
    try std.testing.expectEqual(@as(u8, 0), exact_pad_buffer[exact_pad_written]);

    const allocator = std.testing.allocator;
    const ReplayValue = struct {
        active: bool,
        maybe_ptr: ?*const u8,
        maybe_text: ?[]const u8,
        nested: struct {
            maybe_count: ?usize,
        },
    };

    var sentinel: u8 = 0xaa;
    var value = try zalloc.zallocValue(allocator, ReplayValue);
    value.active = true;
    value.maybe_ptr = &sentinel;
    value.maybe_text = "zigux";
    value.nested.maybe_count = 9;
    allocator.destroy(value);

    value = try zalloc.zallocValue(allocator, ReplayValue);
    defer allocator.destroy(value);
    try std.testing.expect(!value.active);
    try std.testing.expect(value.maybe_ptr == null);
    try std.testing.expect(value.maybe_text == null);
    try std.testing.expect(value.nested.maybe_count == null);
}
