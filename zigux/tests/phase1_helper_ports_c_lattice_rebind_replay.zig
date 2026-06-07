const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectFallback(errnum: i32, window: []const u8, rendered: []const u8) !void {
    var scratch: [64]u8 = undefined;
    const message = try std.fmt.bufPrint(
        &scratch,
        "INTERNAL ERROR: strerror_r({d}, [buf], {d})=22",
        .{ errnum, window.len },
    );
    const copied = @min(message.len, window.len - 1);
    try std.testing.expectEqualStrings(message[0..copied], rendered);
    try std.testing.expectEqual(@as(u8, 0), window[copied]);
}

test "lattice rebinds slab fallback windows into zalloc formatting storage" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var owner: ?[]u8 = slab.kmallocBytes(96, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(owner);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memset(owner.?, 0xcc);
    const fallback_window = owner.?[8..49];
    const fallback = str_error_r.strErrorR(8123, fallback_window);
    try expectFallback(8123, fallback_window, fallback);
    try std.testing.expectEqual(@as(usize, 40), fallback.len);
    try std.testing.expectEqual(@as(u8, 0xcc), owner.?[7]);
    try std.testing.expectEqual(@as(u8, 0xcc), owner.?[49]);

    var summary_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 64);
    defer zalloc.zfreeBytes(allocator, &summary_owner);
    for (summary_owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const summary_window = summary_owner.?[5..30];
    const summary_written = vsprintf.scnprintf(summary_window, "fb:{d}:{s}", .{ fallback.len, fallback[0..4] });
    try std.testing.expectEqual(@as(usize, 10), summary_written);
    try std.testing.expectEqualStrings("fb:40:INTE", summary_window[0..summary_written]);
    try std.testing.expectEqual(@as(u8, 0), summary_window[summary_written]);
    try std.testing.expectEqual(@as(u8, 0), summary_owner.?[4]);
    try std.testing.expectEqual(@as(u8, 0), summary_owner.?[30]);

    const known_window = owner.?[56..79];
    const known = str_error_r.strErrorR(12, known_window);
    try std.testing.expectEqualStrings("Cannot allocate memory", known);
    try std.testing.expectEqual(@as(u8, 0), known_window[known.len]);
    try std.testing.expectEqual(@as(u8, 0xcc), owner.?[55]);
    try std.testing.expectEqual(@as(u8, 0xcc), owner.?[79]);

    const padded_window = owner.?[80..94];
    const padded_written = vsprintf.scnprintfPad(padded_window, 12, "s:{d}", .{summary_written});
    try std.testing.expect(padded_written == 11 or padded_written == 12);
    try std.testing.expectEqualStrings("s:10        ", padded_window[0..12]);
    try std.testing.expectEqual(@as(u8, 0), padded_window[12]);
    try std.testing.expectEqual(@as(u8, 0xcc), owner.?[94]);

    zalloc.zfreeBytes(allocator, &summary_owner);
    try std.testing.expect(summary_owner == null);
    slab.kfree(owner);
    owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "failed slab rebind attempts preserve live owners and zalloc value state" {
    const allocator = std.testing.allocator;
    const Record = struct {
        lengths: [3]usize,
        active: bool,
    };

    slab.kmalloc_nr_allocated = 0;
    var primary: ?[]u8 = slab.kmallocArray(4, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    var secondary: ?[]u8 = slab.kmallocBytes(24, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(primary);
    defer slab.kfree(secondary);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    @memset(primary.?, 0x51);
    @memset(secondary.?, 0x62);

    try std.testing.expect(slab.kmallocBytes(16, slab.__GFP_ZERO) == null);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(u8, 0x51), primary.?[0]);
    try std.testing.expectEqual(@as(u8, 0x51), primary.?[31]);
    try std.testing.expectEqual(@as(u8, 0x62), secondary.?[0]);
    try std.testing.expectEqual(@as(u8, 0x62), secondary.?[23]);

    var record: ?*Record = try zalloc.zallocValue(allocator, Record);
    defer zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expectEqual(@as(usize, 0), record.?.lengths[0]);
    try std.testing.expectEqual(false, record.?.active);

    const known_window = secondary.?[3..20];
    const known = str_error_r.strErrorR(22, known_window);
    try std.testing.expectEqualStrings("Invalid argument", known);
    try std.testing.expectEqual(@as(u8, 0x62), secondary.?[2]);
    try std.testing.expectEqual(@as(u8, 0), secondary.?[19]);
    try std.testing.expectEqual(@as(u8, 0x62), secondary.?[20]);

    const formatted_window = primary.?[4..17];
    const formatted = vsprintf.vscnprintf(formatted_window, "ok:{d}:{d}", .{ known.len, slab.kmalloc_nr_allocated });
    try std.testing.expectEqual(@as(usize, 7), formatted);
    try std.testing.expectEqualStrings("ok:16:2", formatted_window[0..formatted]);
    try std.testing.expectEqual(@as(u8, 0), formatted_window[formatted]);
    try std.testing.expectEqual(@as(u8, 0x51), primary.?[3]);
    try std.testing.expectEqual(@as(u8, 0x51), primary.?[17]);

    record.?.lengths = .{ known.len, formatted, @intCast(slab.kmalloc_nr_allocated) };
    record.?.active = true;

    slab.kfree(primary);
    primary = null;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(true, record.?.active);
    try std.testing.expectEqual(@as(usize, 16), record.?.lengths[0]);
    try std.testing.expectEqual(@as(usize, 7), record.?.lengths[1]);
    try std.testing.expectEqual(@as(usize, 2), record.?.lengths[2]);
    try std.testing.expectEqual(@as(u8, 0x62), secondary.?[0]);

    primary = slab.kmallocBytes(32, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (primary.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expect(record == null);
    slab.kfree(primary);
    primary = null;
    slab.kfree(secondary);
    secondary = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
