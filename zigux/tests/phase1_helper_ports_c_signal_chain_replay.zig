const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectZeroed(bytes: []const u8) !void {
    for (bytes) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
}

fn expectPaddedReturn(written: usize, expected_current: usize) !void {
    try std.testing.expect(written == expected_current or written == expected_current -| 1);
}

test "signal-chain reuses slab error windows through zalloc formatting owners" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var slab_owner: ?[]u8 = slab.kmallocBytes(72, slab.GFP_KERNEL | slab.__GFP_ZERO);
    if (slab_owner == null) {
        return error.TestUnexpectedResult;
    }
    errdefer slab.kfree(slab_owner);

    const slab_window = slab_owner.?;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectZeroed(slab_window);

    @memset(slab_window, 0x7a);
    const fallback_window = slab_window[4..60];
    const fallback = str_error_r.strErrorR(3210, fallback_window);
    try std.testing.expectEqualStrings(
        "INTERNAL ERROR: strerror_r(3210, [buf], 56)=22",
        fallback,
    );
    try std.testing.expectEqual(@as(u8, 0x7a), slab_window[3]);
    try std.testing.expectEqual(@as(u8, 0), fallback_window[fallback.len]);
    try std.testing.expectEqual(@as(u8, 0x7a), slab_window[60]);

    var summary_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 32);
    defer zalloc.zfreeBytes(allocator, &summary_owner);
    try expectZeroed(summary_owner.?);

    const summary_written = vsprintf.scnprintf(
        summary_owner.?,
        "sig:{s}:{d}",
        .{ fallback[0..8], slab.kmalloc_nr_allocated },
    );
    try std.testing.expectEqual(@as(usize, 14), summary_written);
    try std.testing.expectEqualStrings("sig:INTERNAL:1", summary_owner.?[0..summary_written]);
    try std.testing.expectEqual(@as(u8, 0), summary_owner.?[summary_written]);

    const known = str_error_r.strErrorR(0, slab_window[8..16]);
    try std.testing.expectEqualStrings("Success", known);
    try std.testing.expectEqual(@as(u8, 0), slab_window[15]);

    const padded_written = vsprintf.scnprintfPad(
        slab_window[20..34],
        10,
        "{s}",
        .{known},
    );
    try expectPaddedReturn(padded_written, 10);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 'S', 'u', 'c', 'c', 'e', 's', 's', ' ', ' ', ' ', 0 },
        slab_window[20..31],
    );

    try std.testing.expect(slab.kmallocBytes(8, slab.__GFP_ZERO) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    zalloc.zfreeBytes(allocator, &summary_owner);
    try std.testing.expect(summary_owner == null);

    slab.kfree(slab_owner);
    slab_owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "signal-chain value owner survives failed slab array requests" {
    const allocator = std.testing.allocator;
    const Signal = struct {
        code: i32,
        armed: bool,
        label: [12]u8,
    };

    slab.kmalloc_nr_allocated = 0;

    var state_owner: ?*Signal = try zalloc.zallocValue(allocator, Signal);
    defer zalloc.zfreeValue(allocator, Signal, &state_owner);
    try std.testing.expectEqual(@as(i32, 0), state_owner.?.code);
    try std.testing.expectEqual(false, state_owner.?.armed);
    try expectZeroed(&state_owner.?.label);

    state_owner.?.code = 22;
    state_owner.?.armed = true;
    const label_written = vsprintf.vscnprintf(
        state_owner.?.label[0..],
        "err:{d}",
        .{state_owner.?.code},
    );
    try std.testing.expectEqual(@as(usize, 6), label_written);
    try std.testing.expectEqualStrings("err:22", state_owner.?.label[0..label_written]);
    try std.testing.expectEqual(@as(u8, 0), state_owner.?.label[label_written]);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var error_window = [_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };
    const known = str_error_r.strErrorR(state_owner.?.code, error_window[1..5]);
    try std.testing.expectEqualStrings("Inv", known);
    try std.testing.expectEqual(@as(u8, 0xaa), error_window[0]);
    try std.testing.expectEqual(@as(u8, 0), error_window[4]);
    try std.testing.expectEqual(@as(u8, 0xff), error_window[5]);

    zalloc.zfreeValue(allocator, Signal, &state_owner);
    try std.testing.expect(state_owner == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
