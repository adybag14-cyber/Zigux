const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "mailbox bridge moves slab error windows into zalloc summaries" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;

    var mailbox_owner: ?[]u8 = slab.kmallocArray(4, 24, slab.GFP_KERNEL | slab.__GFP_ZERO);
    const mailbox = mailbox_owner orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 96), mailbox.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (mailbox) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memset(mailbox, 0x5a);

    const known_window = mailbox[3..20];
    const known = str_error_r.strErrorR(22, known_window);
    try std.testing.expectEqualStrings("Invalid argument", known);
    try std.testing.expectEqual(@as(u8, 0x5a), mailbox[2]);
    try std.testing.expectEqual(@as(u8, 0), mailbox[19]);
    try std.testing.expectEqual(@as(u8, 0x5a), mailbox[20]);

    const fallback_window = mailbox[24..72];
    const fallback = str_error_r.strErrorR(4242, fallback_window);
    try std.testing.expectEqualStrings(
        "INTERNAL ERROR: strerror_r(4242, [buf], 48)=22",
        fallback,
    );
    try std.testing.expectEqual(@as(u8, 0x5a), mailbox[23]);
    try std.testing.expectEqual(@as(u8, 0), mailbox[70]);
    try std.testing.expectEqual(@as(u8, 0x5a), mailbox[71]);
    try std.testing.expectEqual(@as(u8, 0x5a), mailbox[72]);

    var summary_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 80);
    defer zalloc.zfreeBytes(allocator, &summary_owner);
    const summary = summary_owner.?;
    for (summary) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const summary_written = vsprintf.scnprintf(
        summary,
        "mail:{s}|{s}|cnt={d}",
        .{ known, fallback[0..8], slab.kmalloc_nr_allocated },
    );
    try std.testing.expectEqualStrings("mail:Invalid argument|INTERNAL|cnt=1", summary[0..summary_written]);
    try std.testing.expectEqual(@as(u8, 0), summary[summary_written]);

    const padded_window = mailbox[80..90];
    @memset(padded_window, 0x33);
    const padded_written = vsprintf.scnprintfPad(padded_window, 7, "b{d}", .{9});
    try std.testing.expect(padded_written == 7 or padded_written == 6);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'b', '9', ' ', ' ', ' ', ' ', ' ', 0 }, padded_window[0..8]);
    try std.testing.expectEqual(@as(u8, 0x33), padded_window[8]);
    try std.testing.expectEqual(@as(u8, 0x33), padded_window[9]);

    const MailboxState = struct {
        written: usize,
        active: bool,
        first: u8,
    };

    var state_owner: ?*MailboxState = try zalloc.zallocValue(allocator, MailboxState);
    defer zalloc.zfreeValue(allocator, MailboxState, &state_owner);
    try std.testing.expectEqual(@as(usize, 0), state_owner.?.written);
    try std.testing.expectEqual(false, state_owner.?.active);
    try std.testing.expectEqual(@as(u8, 0), state_owner.?.first);

    state_owner.?.* = .{
        .written = summary_written,
        .active = true,
        .first = summary[0],
    };

    try std.testing.expect(slab.kmallocBytes(32, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    zalloc.zfreeValue(allocator, MailboxState, &state_owner);
    try std.testing.expect(state_owner == null);

    slab.kfree(mailbox_owner);
    mailbox_owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "mailbox bridge keeps zero-sized owners and empty views balanced" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;

    var empty_slab_owner: ?[]u8 = slab.kmallocBytes(0, slab.GFP_KERNEL);
    const empty_slab = empty_slab_owner orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty_slab.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const empty_written = vsprintf.scnprintf(empty_slab, "unused-{d}", .{17});
    try std.testing.expectEqual(@as(usize, 0), empty_written);

    var empty_error_buffer = [_]u8{};
    try std.testing.expectEqual(@as(usize, 0), str_error_r.strErrorR(0, empty_error_buffer[0..]).len);
    try std.testing.expectEqual(@as(usize, 0), str_error_r.strErrorR(9001, empty_error_buffer[0..]).len);

    var empty_zalloc_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(empty_zalloc_owner != null);
    try std.testing.expectEqual(@as(usize, 0), empty_zalloc_owner.?.len);
    zalloc.zfreeBytes(allocator, &empty_zalloc_owner);
    try std.testing.expect(empty_zalloc_owner == null);
    zalloc.zfreeBytes(allocator, &empty_zalloc_owner);
    try std.testing.expect(empty_zalloc_owner == null);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(empty_slab_owner);
    empty_slab_owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
