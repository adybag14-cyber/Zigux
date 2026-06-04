const std = @import("std");
const notifier_abi = @import("notifier_abi");

pub const HListHead = notifier_abi.HListHead;
pub const HListNode = notifier_abi.HListNode;

pub fn tailNextIsNull(head: ?*const HListHead) bool {
    return notifier_abi.hlistTailNextIsNull(head);
}

test "hlist tail abi accepts empty heads and null-terminated chains" {
    const empty = HListHead{ .first = 0 };
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var second = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&first.next);

    try std.testing.expect(tailNextIsNull(&empty));
    try std.testing.expect(tailNextIsNull(&head));
    try std.testing.expectEqual(notifier_abi.hlistTailNextIsNull(&head), tailNextIsNull(&head));
}

test "hlist tail abi keeps absent head semantics aligned" {
    try std.testing.expect(!tailNextIsNull(null));
    try std.testing.expectEqual(notifier_abi.hlistTailNextIsNull(null), tailNextIsNull(null));
}
