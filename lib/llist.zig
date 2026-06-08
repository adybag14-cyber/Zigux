// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");

pub const LlistNode = struct {
    next: ?*LlistNode = null,
};

pub const LlistHead = struct {
    first: ?*LlistNode = null,

    pub fn init() LlistHead {
        return .{};
    }
};

pub fn init_llist_head(head: *LlistHead) void {
    head.first = null;
}

pub fn init_llist_node(node: *LlistNode) void {
    node.next = node;
}

pub fn llist_on_list(node: *const LlistNode) bool {
    return node.next != node;
}

pub fn llist_empty(head: *const LlistHead) bool {
    return head.first == null;
}

pub fn llist_next(node: *const LlistNode) ?*LlistNode {
    return node.next;
}

pub fn llist_add_batch(new_first: *LlistNode, new_last: *LlistNode, head: *LlistHead) bool {
    const old_first = head.first;
    new_last.next = old_first;
    head.first = new_first;
    return old_first == null;
}

pub fn __llist_add_batch(new_first: *LlistNode, new_last: *LlistNode, head: *LlistHead) bool {
    new_last.next = head.first;
    head.first = new_first;
    return new_last.next == null;
}

pub fn llist_add(new_node: *LlistNode, head: *LlistHead) bool {
    return llist_add_batch(new_node, new_node, head);
}

pub fn __llist_add(new_node: *LlistNode, head: *LlistHead) bool {
    return __llist_add_batch(new_node, new_node, head);
}

pub fn llist_del_all(head: *LlistHead) ?*LlistNode {
    const first = head.first;
    head.first = null;
    return first;
}

pub fn __llist_del_all(head: *LlistHead) ?*LlistNode {
    return llist_del_all(head);
}

pub fn llist_del_first(head: *LlistHead) ?*LlistNode {
    const entry = head.first orelse return null;
    head.first = entry.next;
    return entry;
}

pub fn llist_del_first_init(head: *LlistHead) ?*LlistNode {
    const node = llist_del_first(head) orelse return null;
    init_llist_node(node);
    return node;
}

pub fn llist_del_first_this(head: *LlistHead, this: *LlistNode) bool {
    const entry = head.first orelse return false;
    if (entry != this) return false;
    head.first = entry.next;
    return true;
}

pub fn llist_reverse_order(first: ?*LlistNode) ?*LlistNode {
    var head = first;
    var new_head: ?*LlistNode = null;

    while (head) |node| {
        const next = node.next;
        node.next = new_head;
        new_head = node;
        head = next;
    }

    return new_head;
}

fn expectChain(first: ?*LlistNode, expected: []const *LlistNode) !void {
    var cur = first;
    var index: usize = 0;
    while (cur) |node| : (index += 1) {
        try std.testing.expect(index < expected.len);
        try std.testing.expect(node == expected[index]);
        cur = node.next;
    }
    try std.testing.expectEqual(expected.len, index);
}

test "llist init helpers mark empty head and off-list node" {
    var head = LlistHead.init();
    var node: LlistNode = .{};

    init_llist_node(&node);
    try std.testing.expect(llist_empty(&head));
    try std.testing.expect(!llist_on_list(&node));

    try std.testing.expect(llist_add(&node, &head));
    try std.testing.expect(llist_on_list(&node));
    try std.testing.expect(head.first == &node);
}

test "llist add and del all preserve newest-to-oldest order" {
    var head = LlistHead.init();
    var a: LlistNode = .{};
    var b: LlistNode = .{};
    var c: LlistNode = .{};

    try std.testing.expect(llist_add(&a, &head));
    try std.testing.expect(!llist_add(&b, &head));
    try std.testing.expect(!llist_add(&c, &head));

    const chain = llist_del_all(&head);
    try std.testing.expect(llist_empty(&head));
    try expectChain(chain, &[_]*LlistNode{ &c, &b, &a });
}

test "llist add batch prepends linked entries" {
    var head = LlistHead.init();
    var a: LlistNode = .{};
    var b: LlistNode = .{};
    var c: LlistNode = .{};
    var d: LlistNode = .{};
    var e: LlistNode = .{};

    a.next = &b;
    b.next = &c;
    c.next = null;
    try std.testing.expect(llist_add_batch(&a, &c, &head));
    try expectChain(head.first, &[_]*LlistNode{ &a, &b, &c });

    d.next = &e;
    e.next = null;
    try std.testing.expect(!llist_add_batch(&d, &e, &head));
    try expectChain(head.first, &[_]*LlistNode{ &d, &e, &a, &b, &c });
}

test "llist del first and del first this remove only the current head" {
    var head = LlistHead.init();
    var a: LlistNode = .{};
    var b: LlistNode = .{};
    var c: LlistNode = .{};

    _ = llist_add(&a, &head);
    _ = llist_add(&b, &head);
    _ = llist_add(&c, &head);

    try std.testing.expect(!llist_del_first_this(&head, &a));
    try std.testing.expect(llist_del_first_this(&head, &c));
    try std.testing.expect(llist_del_first(&head).? == &b);
    try std.testing.expect(llist_del_first_init(&head).? == &a);
    try std.testing.expect(!llist_on_list(&a));
    try std.testing.expect(llist_del_first(&head) == null);
}

test "llist reverse order flips a deleted chain" {
    var head = LlistHead.init();
    var a: LlistNode = .{};
    var b: LlistNode = .{};
    var c: LlistNode = .{};

    _ = llist_add(&a, &head);
    _ = llist_add(&b, &head);
    _ = llist_add(&c, &head);

    const newest_first = llist_del_all(&head);
    try expectChain(newest_first, &[_]*LlistNode{ &c, &b, &a });

    const oldest_first = llist_reverse_order(newest_first);
    try expectChain(oldest_first, &[_]*LlistNode{ &a, &b, &c });
}
