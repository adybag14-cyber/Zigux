const std = @import("std");
const notifier_abi = @import("notifier_abi.zig");

pub const ListHead = notifier_abi.ListHead;
pub const ListBackLinkBreak = notifier_abi.ListBackLinkBreak;

pub const list_head_size = notifier_abi.list_head_size;
pub const list_head_align = notifier_abi.list_head_align;
pub const list_head_next_offset = notifier_abi.list_head_next_offset;
pub const list_head_prev_offset = notifier_abi.list_head_prev_offset;
pub const list_back_link_break_size = notifier_abi.list_back_link_break_size;
pub const list_back_link_break_align = notifier_abi.list_back_link_break_align;
pub const list_back_link_break_current_index_offset = notifier_abi.list_back_link_break_current_index_offset;
pub const list_back_link_break_expected_prev_offset = notifier_abi.list_back_link_break_expected_prev_offset;
pub const list_back_link_break_actual_prev_offset = notifier_abi.list_back_link_break_actual_prev_offset;

pub fn listIsEmpty(head: ?*const ListHead) bool {
    return notifier_abi.listIsEmpty(head);
}

pub fn listLength(head: ?*const ListHead) usize {
    return notifier_abi.listLength(head);
}

pub fn firstBrokenBacklink(head: ?*const ListHead) ?ListBackLinkBreak {
    return notifier_abi.firstBrokenBacklink(head);
}

pub fn listHasConsistentBacklinks(head: ?*const ListHead) bool {
    return notifier_abi.listHasConsistentBacklinks(head);
}

test "list binding exposes notifier ABI layout constants" {
    try std.testing.expectEqual(@sizeOf(ListHead), list_head_size);
    try std.testing.expectEqual(@alignOf(ListHead), list_head_align);
    try std.testing.expectEqual(@offsetOf(ListHead, "next"), list_head_next_offset);
    try std.testing.expectEqual(@offsetOf(ListHead, "prev"), list_head_prev_offset);
    try std.testing.expectEqual(@sizeOf(ListBackLinkBreak), list_back_link_break_size);
    try std.testing.expectEqual(@alignOf(ListBackLinkBreak), list_back_link_break_align);
    try std.testing.expectEqual(@offsetOf(ListBackLinkBreak, "current_index"), list_back_link_break_current_index_offset);
    try std.testing.expectEqual(@offsetOf(ListBackLinkBreak, "expected_prev"), list_back_link_break_expected_prev_offset);
    try std.testing.expectEqual(@offsetOf(ListBackLinkBreak, "actual_prev"), list_back_link_break_actual_prev_offset);
}

test "list binding relays sentinel-only emptiness through notifier ABI" {
    var head = ListHead{ .next = 0, .prev = 0 };
    head.next = @intFromPtr(&head);
    head.prev = @intFromPtr(&head);

    try std.testing.expect(listIsEmpty(&head));
    try std.testing.expectEqual(notifier_abi.listIsEmpty(&head), listIsEmpty(&head));
    try std.testing.expectEqual(@as(usize, 0), listLength(&head));
    try std.testing.expect(listHasConsistentBacklinks(&head));
    try std.testing.expectEqual(@as(?ListBackLinkBreak, null), firstBrokenBacklink(&head));
}

test "list binding rejects null, node-present, and broken-sentinel empty states" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };

    try std.testing.expect(!listIsEmpty(null));
    try std.testing.expectEqual(notifier_abi.listIsEmpty(null), listIsEmpty(null));

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&first);
    first.next = @intFromPtr(&head);
    first.prev = @intFromPtr(&head);
    try std.testing.expect(!listIsEmpty(&head));
    try std.testing.expectEqual(notifier_abi.listIsEmpty(&head), listIsEmpty(&head));
    try std.testing.expectEqual(@as(usize, 1), listLength(&head));
    try std.testing.expect(listHasConsistentBacklinks(&head));

    head.next = @intFromPtr(&head);
    head.prev = 0;
    try std.testing.expect(!listIsEmpty(&head));
    try std.testing.expectEqual(notifier_abi.listIsEmpty(&head), listIsEmpty(&head));
    try std.testing.expect(!listHasConsistentBacklinks(&head));
}
