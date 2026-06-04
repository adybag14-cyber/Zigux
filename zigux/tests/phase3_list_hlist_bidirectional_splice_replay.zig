const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

fn expectListSequence(view: list_view.ListView, expected: []const *const list_view.ListHead) !void {
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(expected.len, view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, expected[0]), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, expected[expected.len - 1]), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const list_view.ListHead, node), it.next());
    }
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), it.next());
}

fn expectHListSequence(view: hlist_view.HListView, expected: []const *const hlist_view.HListNode) !void {
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(expected.len, view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, expected[0]), view.first());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, expected[expected.len - 1]), view.last());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const hlist_view.HListNode, node), it.next());
    }
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), it.next());
}

test "list front splice and hlist head rebase keep independent link invariants" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_alpha = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_beta = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_gamma = list_view.ListHead{ .next = 0, .prev = 0 };
    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_alpha = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_beta = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_gamma = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    list_head.next = @intFromPtr(&list_alpha);
    list_head.prev = @intFromPtr(&list_beta);
    list_alpha.next = @intFromPtr(&list_beta);
    list_alpha.prev = @intFromPtr(&list_head);
    list_beta.next = @intFromPtr(&list_head);
    list_beta.prev = @intFromPtr(&list_alpha);
    try expectListSequence(list_view.ListView.init(&list_head), &.{ &list_alpha, &list_beta });

    hlist_head.first = @intFromPtr(&hlist_alpha);
    hlist_alpha.next = @intFromPtr(&hlist_beta);
    hlist_alpha.pprev = @intFromPtr(&hlist_head.first);
    hlist_beta.next = 0;
    hlist_beta.pprev = @intFromPtr(&hlist_alpha.next);
    try expectHListSequence(hlist_view.HListView.init(&hlist_head), &.{ &hlist_alpha, &hlist_beta });

    list_head.next = @intFromPtr(&list_gamma);
    list_gamma.prev = @intFromPtr(&list_head);
    list_gamma.next = @intFromPtr(&list_alpha);
    list_alpha.prev = @intFromPtr(&list_gamma);
    try expectListSequence(list_view.ListView.init(&list_head), &.{ &list_gamma, &list_alpha, &list_beta });

    hlist_head.first = @intFromPtr(&hlist_beta);
    hlist_beta.pprev = @intFromPtr(&hlist_head.first);
    hlist_beta.next = @intFromPtr(&hlist_gamma);
    hlist_gamma.pprev = @intFromPtr(&hlist_beta.next);
    hlist_gamma.next = 0;
    hlist_alpha.next = 0;
    hlist_alpha.pprev = 0;
    try expectHListSequence(hlist_view.HListView.init(&hlist_head), &.{ &hlist_beta, &hlist_gamma });
}

test "list tail rotation mirrors hlist prev-link repair after middle detach" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_alpha = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_beta = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_gamma = list_view.ListHead{ .next = 0, .prev = 0 };
    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_alpha = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_beta = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_gamma = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    list_head.next = @intFromPtr(&list_alpha);
    list_head.prev = @intFromPtr(&list_gamma);
    list_alpha.next = @intFromPtr(&list_beta);
    list_alpha.prev = @intFromPtr(&list_head);
    list_beta.next = @intFromPtr(&list_gamma);
    list_beta.prev = @intFromPtr(&list_alpha);
    list_gamma.next = @intFromPtr(&list_head);
    list_gamma.prev = @intFromPtr(&list_beta);

    hlist_head.first = @intFromPtr(&hlist_alpha);
    hlist_alpha.next = @intFromPtr(&hlist_beta);
    hlist_alpha.pprev = @intFromPtr(&hlist_head.first);
    hlist_beta.next = @intFromPtr(&hlist_gamma);
    hlist_beta.pprev = @intFromPtr(&hlist_alpha.next);
    hlist_gamma.next = 0;
    hlist_gamma.pprev = @intFromPtr(&hlist_beta.next);

    list_alpha.next = @intFromPtr(&list_gamma);
    list_gamma.prev = @intFromPtr(&list_alpha);
    list_gamma.next = @intFromPtr(&list_beta);
    list_beta.prev = @intFromPtr(&list_gamma);
    list_beta.next = @intFromPtr(&list_head);
    list_head.prev = @intFromPtr(&list_beta);
    try expectListSequence(list_view.ListView.init(&list_head), &.{ &list_alpha, &list_gamma, &list_beta });

    hlist_alpha.next = @intFromPtr(&hlist_gamma);
    hlist_gamma.pprev = @intFromPtr(&hlist_alpha.next);
    hlist_gamma.next = @intFromPtr(&hlist_beta);
    hlist_beta.pprev = @intFromPtr(&hlist_gamma.next);
    hlist_beta.next = 0;
    try expectHListSequence(hlist_view.HListView.init(&hlist_head), &.{ &hlist_alpha, &hlist_gamma, &hlist_beta });
}
