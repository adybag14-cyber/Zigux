const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "checkpoint chain moves rendered state between slab and zalloc owners" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;
    var slab_owner: ?[]u8 = slab.kmallocArray(5, 16, slab.GFP_KERNEL | slab.__GFP_ZERO);
    defer slab.kfree(slab_owner);
    const arena = slab_owner orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const fallback_window = arena[6..38];
    const fallback = str_error_r.strErrorR(8080, fallback_window);
    try std.testing.expectEqual(fallback_window.len - 1, fallback.len);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(8080", fallback);
    try std.testing.expectEqual(@as(u8, 0), fallback_window[fallback.len]);
    try std.testing.expectEqual(@as(u8, 0), arena[5]);
    try std.testing.expectEqual(@as(u8, 0), arena[38]);

    var zbytes: ?[]u8 = try zalloc.zallocBytes(allocator, 48);
    defer zalloc.zfreeBytes(allocator, &zbytes);
    const scratch = zbytes.?;
    for (scratch) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const padded_written = vsprintf.scnprintfPad(
        scratch[4..28],
        18,
        "ck:{d}:{s}",
        .{ fallback.len, fallback[0..4] },
    );
    try std.testing.expect(padded_written == 18 or padded_written == 17);
    try std.testing.expectEqualStrings("ck:31:INTE        ", scratch[4..22]);
    try std.testing.expectEqual(@as(u8, 0), scratch[22]);
    try std.testing.expectEqual(@as(u8, 0), scratch[3]);
    try std.testing.expectEqual(@as(u8, 0), scratch[23]);

    const record_written = vsprintf.scnprintf(
        arena[42..66],
        "sum={s}|{d}",
        .{ scratch[4..14], padded_written },
    );
    try std.testing.expect(record_written == 17 or record_written == 16);
    try std.testing.expect(std.mem.startsWith(u8, arena[42 .. 42 + record_written], "sum=ck:31:INTE|1"));
    try std.testing.expectEqual(@as(u8, 0), arena[42 + record_written]);
    try std.testing.expectEqual(@as(u8, 0), arena[41]);
    try std.testing.expectEqual(@as(u8, 0), arena[66]);

    const known = str_error_r.strErrorR(0, scratch[1..10]);
    try std.testing.expectEqualStrings("Success", known);
    try std.testing.expectEqual(@as(u8, 0), scratch[0]);
    try std.testing.expectEqual(@as(u8, 0), scratch[1 + known.len]);
    try std.testing.expectEqual(@as(u8, ':'), scratch[9]);

    const State = struct {
        fallback_len: usize,
        record_len: usize,
        checkpoint: [5]u8,
    };
    var state: ?*State = try zalloc.zallocValue(allocator, State);
    defer zalloc.zfreeValue(allocator, State, &state);
    try std.testing.expectEqual(@as(usize, 0), state.?.fallback_len);
    try std.testing.expectEqual(@as(usize, 0), state.?.record_len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 0 }, &state.?.checkpoint);

    state.?.fallback_len = fallback.len;
    state.?.record_len = record_written;
    @memcpy(&state.?.checkpoint, arena[42..47]);
    try std.testing.expectEqualSlices(u8, "sum=c", &state.?.checkpoint);

    zalloc.zfreeBytes(allocator, &zbytes);
    try std.testing.expect(zbytes == null);
    zbytes = try zalloc.zallocBytes(allocator, 12);
    for (zbytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    zalloc.zfreeValue(allocator, State, &state);
    try std.testing.expect(state == null);

    slab.kfree(slab_owner);
    slab_owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "checkpoint chain preserves live buffers across slab failures" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;
    var slab_owner: ?[]u8 = slab.kmallocBytes(56, slab.GFP_KERNEL | slab.__GFP_ZERO);
    defer slab.kfree(slab_owner);
    const arena = slab_owner orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const first_written = vsprintf.scnprintf(arena[4..20], "slot={d}", .{11});
    try std.testing.expectEqual(@as(usize, 7), first_written);
    try std.testing.expectEqualStrings("slot=11", arena[4 .. 4 + first_written]);
    try std.testing.expectEqual(@as(u8, 0), arena[4 + first_written]);

    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualStrings("slot=11", arena[4 .. 4 + first_written]);

    var zbytes: ?[]u8 = try zalloc.zallocBytes(allocator, 32);
    defer zalloc.zfreeBytes(allocator, &zbytes);
    const errbuf = zbytes.?;
    const denied = str_error_r.strErrorR(13, errbuf[2..13]);
    try std.testing.expectEqualStrings("Permission", denied);
    try std.testing.expectEqual(@as(u8, 0), errbuf[2 + denied.len]);
    try std.testing.expectEqual(@as(u8, 0), errbuf[0]);
    try std.testing.expectEqual(@as(u8, 0), errbuf[1]);

    const err_written = vsprintf.scnprintfPad(arena[24..42], 12, "err={s}", .{denied[0..4]});
    try std.testing.expect(err_written == 12 or err_written == 11);
    try std.testing.expectEqualStrings("err=Perm    ", arena[24..36]);
    try std.testing.expectEqual(@as(u8, 0), arena[36]);
    try std.testing.expectEqual(@as(u8, 0), arena[23]);
    try std.testing.expectEqual(@as(u8, 0), arena[42]);

    zalloc.zfreeBytes(allocator, &zbytes);
    try std.testing.expect(zbytes == null);
    zbytes = try zalloc.zallocBytes(allocator, 32);
    for (zbytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(slab_owner);
    slab_owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
