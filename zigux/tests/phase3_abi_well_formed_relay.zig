const std = @import("std");

const abi = @import("abi_bindings");

test "phase3 abi keeps well-formed notifier list relays visible through the shared ABI surface" {
    const notifier_third = abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 3,
    };
    const notifier_second = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&notifier_third),
        .priority = 5,
    };
    const notifier_first = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&notifier_second),
        .priority = 5,
    };

    try std.testing.expect(abi.chainHasNonincreasingPriority(&notifier_first));
    try std.testing.expect(abi.firstChainPriorityIncrease(&notifier_first) == null);

    var list_head = abi.ListHead{ .next = 0, .prev = 0 };
    var list_first = abi.ListHead{ .next = 0, .prev = 0 };
    var list_second = abi.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_second);
    list_first.next = @intFromPtr(&list_second);
    list_first.prev = @intFromPtr(&list_head);
    list_second.next = @intFromPtr(&list_head);
    list_second.prev = @intFromPtr(&list_first);

    try std.testing.expect(abi.firstBrokenBacklink(&list_head) == null);
    try std.testing.expect(abi.listHasConsistentBacklinks(&list_head));

    var hlist_head = abi.HListHead{ .first = 0 };
    var hlist_first = abi.HListNode{ .next = 0, .pprev = 0 };
    var hlist_second = abi.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_second);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_second.next = 0;
    hlist_second.pprev = @intFromPtr(&hlist_first.next);

    try std.testing.expect(abi.firstBrokenPrevLink(&hlist_head) == null);
    try std.testing.expect(abi.hlistHasConsistentPrevLinks(&hlist_head));
}
