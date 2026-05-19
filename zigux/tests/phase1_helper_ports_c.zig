const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

const Fixture = struct {
    zalloc: struct {
        zeroed: bool,
        freed_is_null: bool,
        value_zeroed: bool,
        value_freed_is_null: bool,
    },
    str_error_r: struct {
        enoent: []const u8,
        unknown: []const u8,
    },
    slab: struct {
        null_without_reclaim: bool,
        alloc_count_after_kmalloc: isize,
        zero_after_kmalloc: bool,
        alloc_count_after_kmalloc_free: isize,
        array_zeroed: bool,
        alloc_count_after_kmalloc_array: isize,
        alloc_count_after_kmalloc_array_free: isize,
        slab_is_available: bool,
    },
    vsprintf: struct {
        scnprintf_text: []const u8,
        scnprintf_len: usize,
        pad_text: []const u8,
        pad_len: usize,
    },
};

fn loadFixture(allocator: std.mem.Allocator) !std.json.Parsed(Fixture) {
    return std.json.parseFromSlice(Fixture, allocator, @embedFile("fixtures/phase1_helpers.json"), .{
        .ignore_unknown_fields = true,
    });
}

test "lane10 helper ports import cleanly" {
    _ = slab;
    _ = str_error_r;
    _ = vsprintf;
    _ = zalloc;
}

test "lane10 helper ports match committed parity fixture" {
    var parsed = try loadFixture(std.testing.allocator);
    defer parsed.deinit();
    const fixture = parsed.value;

    const allocator = std.testing.allocator;

    var zalloc_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 8);
    defer zalloc.zfreeBytes(allocator, &zalloc_bytes);
    var zalloc_zeroed = true;
    for (zalloc_bytes.?) |value| {
        if (value != 0) {
            zalloc_zeroed = false;
            break;
        }
    }
    try std.testing.expectEqual(fixture.zalloc.zeroed, zalloc_zeroed);
    zalloc.zfreeBytes(allocator, &zalloc_bytes);
    try std.testing.expectEqual(fixture.zalloc.freed_is_null, zalloc_bytes == null);

    const ZallocValue = struct {
        a: u32,
        b: bool,
    };
    var zalloc_value: ?*ZallocValue = try zalloc.zallocValue(allocator, ZallocValue);
    defer zalloc.zfreeValue(allocator, ZallocValue, &zalloc_value);
    try std.testing.expectEqual(fixture.zalloc.value_zeroed, zalloc_value.?.a == 0 and !zalloc_value.?.b);
    zalloc.zfreeValue(allocator, ZallocValue, &zalloc_value);
    try std.testing.expectEqual(fixture.zalloc.value_freed_is_null, zalloc_value == null);

    var strerror_buffer: [64]u8 = undefined;
    try std.testing.expectEqualStrings(fixture.str_error_r.enoent, str_error_r.strErrorR(2, &strerror_buffer));
    try std.testing.expectEqualStrings(fixture.str_error_r.unknown, str_error_r.strErrorR(4096, &strerror_buffer));

    slab.kmalloc_nr_allocated = 0;
    try std.testing.expectEqual(fixture.slab.null_without_reclaim, slab.kmallocBytes(8, 0) == null);

    const slab_plain = slab.kmallocBytes(8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(fixture.slab.alloc_count_after_kmalloc, slab.kmalloc_nr_allocated);
    var slab_plain_zeroed = true;
    for (slab_plain) |value| {
        if (value != 0) {
            slab_plain_zeroed = false;
            break;
        }
    }
    try std.testing.expectEqual(fixture.slab.zero_after_kmalloc, slab_plain_zeroed);
    for (slab_plain) |*value| {
        value.* = 0xaa;
    }
    slab.kfree(slab_plain);
    try std.testing.expectEqual(fixture.slab.alloc_count_after_kmalloc_free, slab.kmalloc_nr_allocated);

    var slab_array: ?[]u8 = slab.kmallocArray(4, 2, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_array);
    var slab_array_zeroed = true;
    for (slab_array.?) |value| {
        if (value != 0) {
            slab_array_zeroed = false;
            break;
        }
    }
    try std.testing.expectEqual(fixture.slab.array_zeroed, slab_array_zeroed);
    try std.testing.expectEqual(fixture.slab.alloc_count_after_kmalloc_array, slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(fixture.slab.slab_is_available, slab.slabIsAvailable());
    slab.kfree(slab_array);
    slab_array = null;
    try std.testing.expectEqual(fixture.slab.alloc_count_after_kmalloc_array_free, slab.kmalloc_nr_allocated);

    var vsprintf_buffer: [16]u8 = undefined;
    const scnprintf_len = vsprintf.scnprintf(&vsprintf_buffer, "{s}:{d}", .{ "zigux", 7 });
    try std.testing.expectEqual(fixture.vsprintf.scnprintf_len, scnprintf_len);
    try std.testing.expectEqualStrings(fixture.vsprintf.scnprintf_text, vsprintf_buffer[0..scnprintf_len]);

    var padded_buffer: [16]u8 = undefined;
    const padded_len = vsprintf.scnprintfPad(&padded_buffer, 8, "id={d}", .{7});
    try std.testing.expectEqual(fixture.vsprintf.pad_len, padded_len);
    try std.testing.expectEqualStrings(fixture.vsprintf.pad_text, padded_buffer[0..8]);
}

test "lane10 helper ports keep current edge contracts" {
    var parsed = try loadFixture(std.testing.allocator);
    defer parsed.deinit();
    const fixture = parsed.value;

    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var empty_error_buffer: [0]u8 = .{};
    try std.testing.expectEqual(@as(usize, 0), str_error_r.strErrorR(2, &empty_error_buffer).len);

    var single_error_buffer: [1]u8 = undefined;
    try std.testing.expectEqual(@as(usize, 0), str_error_r.strErrorR(2, &single_error_buffer).len);
    try std.testing.expectEqual(@as(u8, 0), single_error_buffer[0]);

    var truncated_error_buffer: [8]u8 = undefined;
    const truncated_error = str_error_r.strErrorR(4096, &truncated_error_buffer);
    try std.testing.expectEqualStrings(fixture.str_error_r.unknown[0..truncated_error.len], truncated_error);
    try std.testing.expectEqual(@as(u8, 0), truncated_error_buffer[truncated_error.len]);

    var empty_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    defer zalloc.zfreeBytes(allocator, &empty_bytes);
    try std.testing.expectEqual(@as(usize, 0), empty_bytes.?.len);
    zalloc.zfreeBytes(allocator, &empty_bytes);
    try std.testing.expect(empty_bytes == null);
    zalloc.zfreeBytes(allocator, &empty_bytes);
    try std.testing.expect(empty_bytes == null);

    const EmptyValue = struct {};
    var empty_value: ?*EmptyValue = null;
    zalloc.zfreeValue(allocator, EmptyValue, &empty_value);
    try std.testing.expect(empty_value == null);

    var single_vsnprintf_buffer: [1]u8 = undefined;
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintf(&single_vsnprintf_buffer, "{s}", .{"zigux"}));
    try std.testing.expectEqual(@as(u8, 0), single_vsnprintf_buffer[0]);

    var scnprintf_buffer: [7]u8 = undefined;
    var vscnprintf_buffer: [7]u8 = undefined;
    const scnprintf_written = vsprintf.scnprintf(&scnprintf_buffer, "{s}:{d}", .{ "zigux", 7 });
    const vscnprintf_written = vsprintf.vscnprintf(&vscnprintf_buffer, "{s}:{d}", .{ "zigux", 7 });
    try std.testing.expectEqual(scnprintf_written, vscnprintf_written);
    try std.testing.expectEqualStrings(scnprintf_buffer[0..scnprintf_written], vscnprintf_buffer[0..vscnprintf_written]);

    var zero_pad_buffer: [4]u8 = undefined;
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintfPad(&zero_pad_buffer, 0, "id={d}", .{7}));
    try std.testing.expectEqual(@as(u8, 0), zero_pad_buffer[0]);
}

test "lane10 helper ports keep current helper-local safety contracts" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;
    try std.testing.expect(slab.kmallocArray(4, 2, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const zero_bytes = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero_bytes.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(zero_bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const zero_array = slab.kmallocArray(0, 8, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero_array.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(zero_array);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const zero_element_array = slab.kmallocArray(8, 0, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero_element_array.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(zero_element_array);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var known_message_buffer: [6]u8 = undefined;
    const known_message = str_error_r.strErrorR(0, &known_message_buffer);
    try std.testing.expectEqualStrings("Succe", known_message);
    try std.testing.expectEqual(@as(u8, 0), known_message_buffer[known_message_buffer.len - 1]);

    var truncated_pad_buffer: [8]u8 = undefined;
    const truncated_pad_len = vsprintf.scnprintfPad(&truncated_pad_buffer, 4, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 4), truncated_pad_len);
    try std.testing.expectEqualStrings("zigu", truncated_pad_buffer[0..truncated_pad_len]);
    try std.testing.expectEqual(@as(u8, 0), truncated_pad_buffer[truncated_pad_len]);

    const AggregateValue = struct {
        bytes: [4]u8,
        flags: [2]bool,
        maybe_count: ?usize,
    };

    var aggregate_value: ?*AggregateValue = try zalloc.zallocValue(allocator, AggregateValue);
    defer zalloc.zfreeValue(allocator, AggregateValue, &aggregate_value);
    try std.testing.expectEqualSlices(u8, &.{ 0, 0, 0, 0 }, &aggregate_value.?.bytes);
    try std.testing.expectEqualSlices(bool, &.{ false, false }, &aggregate_value.?.flags);
    try std.testing.expect(aggregate_value.?.maybe_count == null);

    zalloc.zfreeValue(allocator, AggregateValue, &aggregate_value);
    try std.testing.expect(aggregate_value == null);
    zalloc.zfreeValue(allocator, AggregateValue, &aggregate_value);
    try std.testing.expect(aggregate_value == null);

    var dirty_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    try std.testing.expect(dirty_bytes != null);
    @memset(dirty_bytes.?, 0xaa);
    zalloc.zfreeBytes(allocator, &dirty_bytes);
    try std.testing.expect(dirty_bytes == null);

    dirty_bytes = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &dirty_bytes);
    try std.testing.expectEqualSlices(u8, &.{ 0, 0, 0, 0 }, dirty_bytes.?);
}

test "lane10 helper ports keep exact-fit and fresh-rezero contracts" {
    const allocator = std.testing.allocator;

    var success_buffer: [8]u8 = undefined;
    const success_rendered = str_error_r.strErrorR(0, &success_buffer);
    try std.testing.expectEqualStrings("Success", success_rendered);
    try std.testing.expectEqual(@as(u8, 0), success_buffer[success_rendered.len]);
    try std.testing.expectEqual(@intFromPtr(&success_buffer[0]), @intFromPtr(success_rendered.ptr));

    var generated_exact: [48]u8 = undefined;
    const generated_rendered = str_error_r.strErrorR(4096, &generated_exact);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(4096, [buf], 48)=22", generated_rendered);
    try std.testing.expectEqual(@as(u8, 0), generated_exact[generated_rendered.len]);
    try std.testing.expectEqual(@intFromPtr(&generated_exact[0]), @intFromPtr(generated_rendered.ptr));

    slab.kmalloc_nr_allocated = 0;
    const first_array = slab.kmallocArray(4, 1, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    @memset(first_array, 0xaa);
    slab.kfree(first_array);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const second_array = slab.kmallocArray(4, 1, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &.{ 0, 0, 0, 0 }, second_array);

    slab.kfree(second_array);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const first_bytes = slab.kmallocBytes(4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    @memset(first_bytes, 0xaa);
    slab.kfree(first_bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const second_bytes = slab.kmallocBytes(4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(second_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &.{ 0, 0, 0, 0 }, second_bytes);

    const Payload = struct {
        active: bool,
        maybe_ptr: ?*const u8,
        nested: struct {
            maybe_count: ?usize,
        },
    };

    var sentinel: u8 = 0xaa;
    var payload: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    try std.testing.expect(payload != null);
    payload.?.active = true;
    payload.?.maybe_ptr = &sentinel;
    payload.?.nested.maybe_count = 9;
    zalloc.zfreeValue(allocator, Payload, &payload);
    try std.testing.expect(payload == null);

    payload = try zalloc.zallocValue(allocator, Payload);
    defer zalloc.zfreeValue(allocator, Payload, &payload);
    try std.testing.expect(payload != null);
    try std.testing.expect(!payload.?.active);
    try std.testing.expect(payload.?.maybe_ptr == null);
    try std.testing.expect(payload.?.nested.maybe_count == null);
}
