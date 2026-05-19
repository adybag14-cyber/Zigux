const std = @import("std");
const binding = @import("binding_list_hlist");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

fn asListViewHead(head: *const binding.ListHead) *const list_view.ListHead {
    return @ptrCast(head);
}

fn asHListViewHead(head: *const binding.HListHead) *const hlist_view.HListHead {
    return @ptrCast(head);
}

test "starter packet keeps an empty sentinel list explicit across binding and helper views" {
    var head = binding.emptyListHead();
    head = binding.initEmptyListHead(@intFromPtr(&head));

    try std.testing.expect(binding.isEmptyListHead(head, @intFromPtr(&head)));

    const view = list_view.ListView.init(asListViewHead(&head));
    try std.testing.expect(view.isEmpty());
    try std.testing.expectEqual(@as(usize, 0), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
}

test "starter packet keeps a malformed sentinel list visible as non-empty and broken" {
    var head = binding.emptyListHead();
    const self_addr = @intFromPtr(&head);
    head = binding.initListHead(self_addr, 0);

    try std.testing.expect(!binding.isEmptyListHead(head, self_addr));

    const view = list_view.ListView.init(asListViewHead(&head));
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 0), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), view.last());
    try std.testing.expect(!view.hasConsistentBacklinks());

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(self_addr, breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, 0), breakage.actual_prev);
}

test "starter packet walks a binding-backed list through list_view" {
    var head = binding.emptyListHead();
    var first = binding.emptyListHead();
    var second = binding.emptyListHead();

    head = binding.initListHead(@intFromPtr(&first), @intFromPtr(&second));
    first = binding.initListHead(@intFromPtr(&second), @intFromPtr(&head));
    second = binding.initListHead(@intFromPtr(&head), @intFromPtr(&first));

    const view = list_view.ListView.init(asListViewHead(&head));
    try std.testing.expect(!binding.isEmptyListHead(head, @intFromPtr(&head)));
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), @intFromPtr(view.first().?));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&second)), @intFromPtr(view.last().?));
    try std.testing.expect(view.hasConsistentBacklinks());

    var it = view.iterator();
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), @intFromPtr(it.next().?));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&second)), @intFromPtr(it.next().?));
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), it.next());
}

test "starter packet reports a binding-backed broken list backlink" {
    var head = binding.emptyListHead();
    var first = binding.emptyListHead();
    var second = binding.emptyListHead();

    head = binding.initListHead(@intFromPtr(&first), @intFromPtr(&second));
    first = binding.initListHead(@intFromPtr(&second), @intFromPtr(&head));
    second = binding.initListHead(@intFromPtr(&head), @intFromPtr(&head));

    const view = list_view.ListView.init(asListViewHead(&head));
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expect(!view.hasConsistentBacklinks());

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);
}

test "starter packet keeps an empty detached hlist explicit across binding and helper views" {
    const head = binding.emptyHListHead();
    const node = binding.emptyHListNode();

    try std.testing.expect(binding.isEmptyHListHead(head));
    try std.testing.expect(binding.isDetachedHListNode(node));

    const view = hlist_view.HListView.init(asHListViewHead(&head));
    try std.testing.expect(view.isEmpty());
    try std.testing.expectEqual(@as(usize, 0), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "starter packet keeps a malformed single-node hlist visible as non-empty and broken" {
    var head = binding.emptyHListHead();
    var first = binding.emptyHListNode();

    head = binding.initHListHead(@intFromPtr(&first));
    first = binding.initHListNode(0, 0);

    try std.testing.expect(!binding.isEmptyHListHead(head));
    try std.testing.expect(binding.isDetachedHListNode(first));

    const view = hlist_view.HListView.init(asHListViewHead(&head));
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 1), view.len());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), @intFromPtr(view.first().?));
    try std.testing.expect(!view.firstPprevMatchesHead());
    try std.testing.expect(!view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, 0), breakage.actual_pprev);
}

test "starter packet walks a binding-backed hlist through hlist_view" {
    var head = binding.emptyHListHead();
    var first = binding.emptyHListNode();
    var second = binding.emptyHListNode();

    head = binding.initHListHead(@intFromPtr(&first));
    first = binding.initHListNode(@intFromPtr(&second), @intFromPtr(&head.first));
    second = binding.initHListNode(0, @intFromPtr(&first.next));

    const view = hlist_view.HListView.init(asHListViewHead(&head));
    try std.testing.expect(!binding.isEmptyHListHead(head));
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), @intFromPtr(view.first().?));
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());

    var it = view.iterator();
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), @intFromPtr(it.next().?));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&second)), @intFromPtr(it.next().?));
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), it.next());
}

test "starter packet reports a binding-backed broken hlist prev-link" {
    var head = binding.emptyHListHead();
    var first = binding.emptyHListNode();
    var second = binding.emptyHListNode();

    head = binding.initHListHead(@intFromPtr(&first));
    first = binding.initHListNode(@intFromPtr(&second), @intFromPtr(&head.first));
    second = binding.initHListNode(0, @intFromPtr(&head.first));

    const view = hlist_view.HListView.init(asHListViewHead(&head));
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(!view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);
}
