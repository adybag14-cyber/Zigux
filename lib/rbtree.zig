// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");

pub const Color = enum {
    red,
    black,
};

pub const Node = struct {
    parent: ?*Node = null,
    left: ?*Node = null,
    right: ?*Node = null,
    color: Color = .red,

    pub fn init() Node {
        return .{};
    }
};

pub const Root = struct {
    node: ?*Node = null,

    pub fn init() Root {
        return .{};
    }
};

pub const RootCached = struct {
    root: Root = Root.init(),
    leftmost: ?*Node = null,

    pub fn init() RootCached {
        return .{};
    }
};

pub const NodeLinked = struct {
    node: Node = Node.init(),
    prev: ?*NodeLinked = null,
    next: ?*NodeLinked = null,

    pub fn init() NodeLinked {
        return .{};
    }
};

pub const RootLinked = struct {
    root: Root = Root.init(),
    leftmost: ?*NodeLinked = null,

    pub fn init() RootLinked {
        return .{};
    }
};

pub const LessFn = *const fn (*const Node, *const Node) bool;

fn orderToInt(order: std.math.Order) i32 {
    return switch (order) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

pub fn emptyRoot(root: *const Root) bool {
    return root.node == null;
}

pub fn emptyNode(node: *const Node) bool {
    return node.parent == node;
}

pub fn clearNode(node: *Node) void {
    node.parent = node;
    node.left = null;
    node.right = null;
    node.color = .red;
}

pub fn clearLinkedNode(node: *NodeLinked) void {
    clearNode(&node.node);
    node.prev = null;
    node.next = null;
}

pub fn linkNode(node: *Node, parent: ?*Node, link: *?*Node) void {
    node.parent = parent;
    node.left = null;
    node.right = null;
    node.color = .red;
    link.* = node;
}

fn colorOf(node: ?*Node) Color {
    return if (node) |n| n.color else .black;
}

fn leftOf(node: ?*Node) ?*Node {
    return if (node) |n| n.left else null;
}

fn rightOf(node: ?*Node) ?*Node {
    return if (node) |n| n.right else null;
}

fn minimum(node: *Node) *Node {
    var current = node;
    while (current.left) |left| {
        current = left;
    }
    return current;
}

fn maximum(node: *Node) *Node {
    var current = node;
    while (current.right) |right| {
        current = right;
    }
    return current;
}

fn leftRotate(root: *Root, node: *Node) void {
    var pivot = node.right orelse unreachable;

    node.right = pivot.left;
    if (pivot.left) |child| {
        child.parent = node;
    }

    pivot.parent = node.parent;
    if (node.parent == null) {
        root.node = pivot;
    } else if (node.parent.?.left == node) {
        node.parent.?.left = pivot;
    } else {
        node.parent.?.right = pivot;
    }

    pivot.left = node;
    node.parent = pivot;
}

fn rightRotate(root: *Root, node: *Node) void {
    var pivot = node.left orelse unreachable;

    node.left = pivot.right;
    if (pivot.right) |child| {
        child.parent = node;
    }

    pivot.parent = node.parent;
    if (node.parent == null) {
        root.node = pivot;
    } else if (node.parent.?.right == node) {
        node.parent.?.right = pivot;
    } else {
        node.parent.?.left = pivot;
    }

    pivot.right = node;
    node.parent = pivot;
}

pub fn insertColor(node: *Node, root: *Root) void {
    var current = node;

    while (colorOf(current.parent) == .red) {
        var parent = current.parent.?;
        var grandparent = parent.parent.?;

        if (grandparent.left == parent) {
            const uncle = grandparent.right;
            if (colorOf(uncle) == .red) {
                parent.color = .black;
                uncle.?.color = .black;
                grandparent.color = .red;
                current = grandparent;
                continue;
            }

            if (parent.right == current) {
                current = parent;
                leftRotate(root, current);
                parent = current.parent.?;
                grandparent = parent.parent.?;
            }

            parent.color = .black;
            grandparent.color = .red;
            rightRotate(root, grandparent);
        } else {
            const uncle = grandparent.left;
            if (colorOf(uncle) == .red) {
                parent.color = .black;
                uncle.?.color = .black;
                grandparent.color = .red;
                current = grandparent;
                continue;
            }

            if (parent.left == current) {
                current = parent;
                rightRotate(root, current);
                parent = current.parent.?;
                grandparent = parent.parent.?;
            }

            parent.color = .black;
            grandparent.color = .red;
            leftRotate(root, grandparent);
        }
    }

    if (root.node) |root_node| {
        root_node.color = .black;
    }
}

pub fn insertColorCached(node: *Node, root: *RootCached, leftmost: bool) void {
    if (leftmost) {
        root.leftmost = node;
    }
    insertColor(node, &root.root);
}

pub fn add(node: *Node, root: *Root, less: LessFn) void {
    var link = &root.node;
    var parent: ?*Node = null;

    while (link.*) |current| {
        parent = current;
        if (less(node, current)) {
            link = &current.left;
        } else {
            link = &current.right;
        }
    }

    linkNode(node, parent, link);
    insertColor(node, root);
}

pub fn addCached(node: *Node, root: *RootCached, less: LessFn) ?*Node {
    var link = &root.root.node;
    var parent: ?*Node = null;
    var leftmost = true;

    while (link.*) |current| {
        parent = current;
        if (less(node, current)) {
            link = &current.left;
        } else {
            link = &current.right;
            leftmost = false;
        }
    }

    linkNode(node, parent, link);
    insertColorCached(node, root, leftmost);
    return if (leftmost) node else null;
}

fn linkLinkedNode(node: *NodeLinked, parent: ?*Node, link: *?*Node) void {
    node.prev = null;
    node.next = null;

    const parent_node = parent orelse return;
    const parent_linked: *NodeLinked = @fieldParentPtr("node", parent_node);

    if (link == &parent_node.left) {
        node.prev = parent_linked.prev;
        node.next = parent_linked;
        parent_linked.prev = node;
        if (node.prev) |prev_link| {
            prev_link.next = node;
        }
    } else {
        node.next = parent_linked.next;
        node.prev = parent_linked;
        parent_linked.next = node;
        if (node.next) |next_link| {
            next_link.prev = node;
        }
    }
}

pub fn addLinked(node: *NodeLinked, root: *RootLinked, less: LessFn) bool {
    var link = &root.root.node;
    var parent: ?*Node = null;

    while (link.*) |current| {
        parent = current;
        if (less(&node.node, current)) {
            link = &current.left;
        } else {
            link = &current.right;
        }
    }

    linkLinkedNode(node, parent, link);
    linkNode(&node.node, parent, link);
    insertColor(&node.node, &root.root);
    if (node.prev == null) {
        root.leftmost = node;
    }
    return node.prev == null;
}

pub fn find(key: anytype, root: *const Root, cmp: *const fn (@TypeOf(key), *const Node) i32) ?*Node {
    var node = root.node;

    while (node) |current| {
        const order = cmp(key, current);
        if (order < 0) {
            node = current.left;
        } else if (order > 0) {
            node = current.right;
        } else {
            return current;
        }
    }

    return null;
}

pub fn findFirst(key: anytype, root: *const Root, cmp: *const fn (@TypeOf(key), *const Node) i32) ?*Node {
    var node = root.node;
    var match: ?*Node = null;

    while (node) |current| {
        const order = cmp(key, current);
        if (order <= 0) {
            if (order == 0) {
                match = current;
            }
            node = current.left;
        } else {
            node = current.right;
        }
    }

    return match;
}

pub fn nextMatch(key: anytype, node: *const Node, cmp: *const fn (@TypeOf(key), *const Node) i32) ?*Node {
    const candidate = next(node) orelse return null;
    if (cmp(key, candidate) != 0) {
        return null;
    }
    return candidate;
}

fn transplant(root: *Root, victim: *Node, replacement: ?*Node) void {
    if (victim.parent == null) {
        root.node = replacement;
    } else if (victim.parent.?.left == victim) {
        victim.parent.?.left = replacement;
    } else {
        victim.parent.?.right = replacement;
    }

    if (replacement) |node| {
        node.parent = victim.parent;
    }
}

fn deleteFixup(root: *Root, initial_node: ?*Node, initial_parent: ?*Node) void {
    var node = initial_node;
    var parent = initial_parent;

    while (node != root.node and colorOf(node) == .black) {
        const current_parent = parent orelse break;

        if (current_parent.left == node) {
            var sibling = current_parent.right;

            if (colorOf(sibling) == .red) {
                sibling.?.color = .black;
                current_parent.color = .red;
                leftRotate(root, current_parent);
                sibling = current_parent.right;
            }

            if (colorOf(leftOf(sibling)) == .black and colorOf(rightOf(sibling)) == .black) {
                if (sibling) |s| {
                    s.color = .red;
                }
                node = current_parent;
                parent = current_parent.parent;
            } else {
                if (colorOf(rightOf(sibling)) == .black) {
                    if (leftOf(sibling)) |left| {
                        left.color = .black;
                    }
                    if (sibling) |s| {
                        s.color = .red;
                        rightRotate(root, s);
                    }
                    sibling = current_parent.right;
                }

                if (sibling) |s| {
                    s.color = current_parent.color;
                }
                current_parent.color = .black;
                if (rightOf(sibling)) |right| {
                    right.color = .black;
                }
                leftRotate(root, current_parent);
                node = root.node;
                parent = null;
            }
        } else {
            var sibling = current_parent.left;

            if (colorOf(sibling) == .red) {
                sibling.?.color = .black;
                current_parent.color = .red;
                rightRotate(root, current_parent);
                sibling = current_parent.left;
            }

            if (colorOf(leftOf(sibling)) == .black and colorOf(rightOf(sibling)) == .black) {
                if (sibling) |s| {
                    s.color = .red;
                }
                node = current_parent;
                parent = current_parent.parent;
            } else {
                if (colorOf(leftOf(sibling)) == .black) {
                    if (rightOf(sibling)) |right| {
                        right.color = .black;
                    }
                    if (sibling) |s| {
                        s.color = .red;
                        leftRotate(root, s);
                    }
                    sibling = current_parent.left;
                }

                if (sibling) |s| {
                    s.color = current_parent.color;
                }
                current_parent.color = .black;
                if (leftOf(sibling)) |left| {
                    left.color = .black;
                }
                rightRotate(root, current_parent);
                node = root.node;
                parent = null;
            }
        }
    }

    if (node) |n| {
        n.color = .black;
    }
}

pub fn erase(node: *Node, root: *Root) void {
    var replacement = node;
    var replacement_color = replacement.color;
    var child: ?*Node = null;
    var parent: ?*Node = null;

    if (node.left == null) {
        child = node.right;
        parent = node.parent;
        transplant(root, node, node.right);
    } else if (node.right == null) {
        child = node.left;
        parent = node.parent;
        transplant(root, node, node.left);
    } else {
        replacement = minimum(node.right.?);
        replacement_color = replacement.color;
        child = replacement.right;

        if (replacement.parent == node) {
            parent = replacement;
        } else {
            parent = replacement.parent;
            transplant(root, replacement, replacement.right);
            replacement.right = node.right;
            replacement.right.?.parent = replacement;
        }

        transplant(root, node, replacement);
        replacement.left = node.left;
        replacement.left.?.parent = replacement;
        replacement.color = node.color;
    }

    if (replacement_color == .black) {
        deleteFixup(root, child, parent);
    }
}

pub fn eraseCached(node: *Node, root: *RootCached) ?*Node {
    var leftmost: ?*Node = null;
    if (root.leftmost == node) {
        leftmost = next(node);
        root.leftmost = leftmost;
    }
    erase(node, &root.root);
    return leftmost;
}

pub fn eraseLinked(node: *NodeLinked, root: *RootLinked) bool {
    if (node.prev) |prev_link| {
        prev_link.next = node.next;
    } else {
        root.leftmost = node.next;
    }

    if (node.next) |next_link| {
        next_link.prev = node.prev;
    }

    erase(&node.node, &root.root);
    clearLinkedNode(node);

    return root.leftmost != null;
}

pub fn eraseInit(node: *Node, root: *Root) void {
    erase(node, root);
    clearNode(node);
}

pub fn eraseInitCached(node: *Node, root: *RootCached) void {
    _ = eraseCached(node, root);
    clearNode(node);
}

pub fn firstCached(root: *const RootCached) ?*Node {
    return root.leftmost;
}

pub fn first(root: *const Root) ?*Node {
    const node = root.node orelse return null;
    return minimum(node);
}

pub fn last(root: *const Root) ?*Node {
    const node = root.node orelse return null;
    return maximum(node);
}

pub fn next(node: *const Node) ?*Node {
    if (emptyNode(node)) {
        return null;
    }

    if (node.right) |right| {
        return minimum(right);
    }

    var current: *const Node = node;
    var parent = current.parent;
    while (parent != null and parent.?.right == current) {
        current = parent.?;
        parent = current.parent;
    }

    return parent;
}

pub fn prev(node: *const Node) ?*Node {
    if (emptyNode(node)) {
        return null;
    }

    if (node.left) |left| {
        return maximum(left);
    }

    var current: *const Node = node;
    var parent = current.parent;
    while (parent != null and parent.?.left == current) {
        current = parent.?;
        parent = current.parent;
    }

    return parent;
}

pub fn replaceNode(victim: *Node, new: *Node, root: *Root) void {
    const parent = victim.parent;

    // Match the C helper by copying the full node shape before reconnecting
    // neighboring links, so stale detached-node state cannot leak into the tree.
    new.* = victim.*;

    if (victim.left) |left| {
        left.parent = new;
    }
    if (victim.right) |right| {
        right.parent = new;
    }

    if (parent == null) {
        root.node = new;
    } else if (parent.?.left == victim) {
        parent.?.left = new;
    } else {
        parent.?.right = new;
    }
}

pub fn replaceNodeCached(victim: *Node, new: *Node, root: *RootCached) void {
    if (root.leftmost == victim) {
        root.leftmost = new;
    }
    replaceNode(victim, new, &root.root);
}

fn leftDeepestNode(node: *const Node) *Node {
    var current: *const Node = node;
    while (true) {
        if (current.left) |left| {
            current = left;
        } else if (current.right) |right| {
            current = right;
        } else {
            return @constCast(current);
        }
    }
}

pub fn firstPostorder(root: *const Root) ?*Node {
    const node = root.node orelse return null;
    return leftDeepestNode(node);
}

pub fn nextPostorder(node: ?*const Node) ?*Node {
    const current = node orelse return null;
    if (emptyNode(current)) {
        return null;
    }

    const parent = current.parent;
    if (parent != null and parent.?.left == current and parent.?.right != null) {
        return leftDeepestNode(parent.?.right.?);
    }
    return parent;
}

test "rbtree inserts and traverses in sorted order" {
    const Entry = struct {
        key: i32,
        node: Node = Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const Node, rhs: *const Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 20 },
        .{ .key = 5 },
        .{ .key = 15 },
        .{ .key = 25 },
    };
    var root = Root.init();

    for (&entries) |*entry| {
        add(&entry.node, &root, less);
    }

    var order: [5]i32 = undefined;
    var count: usize = 0;
    var current = first(&root);
    while (current) |node| : (current = next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 5), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 10, 15, 20, 25 }, order[0..count]);
}

test "rbtree erase and replace keep traversal consistent" {
    const Entry = struct {
        key: i32,
        node: Node = Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const Node, rhs: *const Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 20 },
        .{ .key = 5 },
        .{ .key = 15 },
        .{ .key = 25 },
    };
    var replacement = Entry{ .key = 10 };
    var root = Root.init();

    for (&entries) |*entry| {
        add(&entry.node, &root, less);
    }

    erase(&entries[1].node, &root);
    replaceNode(&entries[0].node, &replacement.node, &root);

    var order: [4]i32 = undefined;
    var count: usize = 0;
    var current = first(&root);
    while (current) |node| : (current = next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 10, 15, 25 }, order[0..count]);
}

test "rbtree cached helpers keep the leftmost pointer aligned" {
    const Entry = struct {
        key: i32,
        node: Node = Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const Node, rhs: *const Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 20 },
        .{ .key = 15 },
    };
    var replacement = Entry{ .key = 5 };
    var root = RootCached.init();

    try std.testing.expectEqual(@as(?*Node, &entries[0].node), addCached(&entries[0].node, &root, less));
    try std.testing.expectEqual(@as(?*Node, &entries[1].node), addCached(&entries[1].node, &root, less));
    try std.testing.expectEqual(@as(?*Node, null), addCached(&entries[2].node, &root, less));
    try std.testing.expectEqual(@as(?*Node, null), addCached(&entries[3].node, &root, less));
    try std.testing.expectEqual(@as(?*Node, &entries[1].node), firstCached(&root));

    replaceNodeCached(&entries[1].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*Node, &replacement.node), firstCached(&root));
    try std.testing.expectEqual(@as(?*Node, &replacement.node), first(&root.root));

    try std.testing.expectEqual(@as(?*Node, &entries[0].node), eraseCached(&replacement.node, &root));
    try std.testing.expectEqual(@as(?*Node, &entries[0].node), firstCached(&root));
    try std.testing.expectEqual(@as(?*Node, &entries[0].node), first(&root.root));

    try std.testing.expectEqual(@as(?*Node, null), eraseCached(&entries[3].node, &root));
    try std.testing.expectEqual(@as(?*Node, &entries[0].node), firstCached(&root));
    try std.testing.expectEqual(@as(?*Node, &entries[0].node), first(&root.root));
}

test "rbtree replaceNode copies victim links over dirty replacement nodes" {
    const Entry = struct {
        key: i32,
        node: Node = Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const Node, rhs: *const Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var root_entry = Entry{ .key = 10 };
    var left_entry = Entry{ .key = 5 };
    var right_entry = Entry{ .key = 15 };
    var replacement = Entry{ .key = 5 };
    var stale_parent = Node.init();
    var stale_left = Node.init();
    var stale_right = Node.init();
    var root = Root.init();

    add(&root_entry.node, &root, less);
    add(&left_entry.node, &root, less);
    add(&right_entry.node, &root, less);

    replacement.node.parent = &stale_parent;
    replacement.node.left = &stale_left;
    replacement.node.right = &stale_right;
    replacement.node.color = .red;

    replaceNode(&left_entry.node, &replacement.node, &root);

    try std.testing.expectEqual(@as(?*Node, &replacement.node), root_entry.node.left);
    try std.testing.expectEqual(@as(?*Node, &root_entry.node), replacement.node.parent);
    try std.testing.expectEqual(@as(?*Node, null), replacement.node.left);
    try std.testing.expectEqual(@as(?*Node, null), replacement.node.right);
    try std.testing.expectEqual(left_entry.node.color, replacement.node.color);
    try std.testing.expectEqual(@as(?*Node, &replacement.node), prev(&root_entry.node));
    try std.testing.expectEqual(@as(?*Node, &root_entry.node), next(&replacement.node));
}

test "rbtree linked helpers track leftmost and neighbour links" {
    const Entry = struct {
        key: i32,
        linked: NodeLinked = NodeLinked.init(),
    };

    const helpers = struct {
        fn entryFromNode(node: *const Node) *const Entry {
            const linked: *const NodeLinked = @fieldParentPtr("node", node);
            return @fieldParentPtr("linked", linked);
        }

        fn compare(lhs: *const Node, rhs: *const Node) bool {
            return entryFromNode(lhs).key < entryFromNode(rhs).key;
        }
    };

    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 15 },
        .{ .key = 5 },
        .{ .key = 12 },
    };
    var root = RootLinked.init();

    try std.testing.expect(addLinked(&entries[0].linked, &root, helpers.compare));
    try std.testing.expect(!addLinked(&entries[1].linked, &root, helpers.compare));
    try std.testing.expect(addLinked(&entries[2].linked, &root, helpers.compare));
    try std.testing.expect(!addLinked(&entries[3].linked, &root, helpers.compare));

    try std.testing.expectEqual(@as(?*NodeLinked, &entries[2].linked), root.leftmost);
    try std.testing.expectEqual(@as(?*NodeLinked, null), entries[2].linked.prev);
    try std.testing.expectEqual(@as(?*NodeLinked, &entries[0].linked), entries[2].linked.next);
    try std.testing.expectEqual(@as(?*NodeLinked, &entries[2].linked), entries[0].linked.prev);
    try std.testing.expectEqual(@as(?*NodeLinked, &entries[3].linked), entries[0].linked.next);
    try std.testing.expectEqual(@as(?*NodeLinked, &entries[0].linked), entries[3].linked.prev);
    try std.testing.expectEqual(@as(?*NodeLinked, &entries[1].linked), entries[3].linked.next);
    try std.testing.expectEqual(@as(?*NodeLinked, &entries[3].linked), entries[1].linked.prev);
    try std.testing.expectEqual(@as(?*NodeLinked, null), entries[1].linked.next);
    try std.testing.expectEqual(@as(?*Node, &entries[0].linked.node), next(&entries[2].linked.node));
    try std.testing.expectEqual(@as(?*Node, &entries[3].linked.node), next(&entries[0].linked.node));

    try std.testing.expect(eraseLinked(&entries[3].linked, &root));
    try std.testing.expect(emptyNode(&entries[3].linked.node));
    try std.testing.expectEqual(@as(?*NodeLinked, null), entries[3].linked.prev);
    try std.testing.expectEqual(@as(?*NodeLinked, null), entries[3].linked.next);
    try std.testing.expectEqual(@as(?*NodeLinked, &entries[0].linked), entries[2].linked.next);
    try std.testing.expectEqual(@as(?*NodeLinked, &entries[2].linked), entries[0].linked.prev);
    try std.testing.expectEqual(@as(?*NodeLinked, &entries[1].linked), entries[0].linked.next);
    try std.testing.expectEqual(@as(?*NodeLinked, &entries[0].linked), entries[1].linked.prev);

    try std.testing.expect(eraseLinked(&entries[2].linked, &root));
    try std.testing.expectEqual(@as(?*NodeLinked, &entries[0].linked), root.leftmost);
    try std.testing.expect(eraseLinked(&entries[0].linked, &root));
    try std.testing.expectEqual(@as(?*NodeLinked, &entries[1].linked), root.leftmost);
    try std.testing.expect(!eraseLinked(&entries[1].linked, &root));
    try std.testing.expectEqual(@as(?*NodeLinked, null), root.leftmost);
    try std.testing.expect(emptyRoot(&root.root));
}

test "rbtree find helpers return duplicate-key ranges" {
    const Entry = struct {
        key: i32,
        serial: i32,
        node: Node = Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const Node, rhs: *const Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) {
                return lhs_entry.key < rhs_entry.key;
            }
            return lhs_entry.serial < rhs_entry.serial;
        }
    }.compare;

    const cmp = struct {
        fn compare(key: i32, node: *const Node) i32 {
            const entry: *const Entry = @fieldParentPtr("node", node);
            return orderToInt(std.math.order(key, entry.key));
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 0 },
        .{ .key = 10, .serial = 1 },
        .{ .key = 5, .serial = 0 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 15, .serial = 0 },
    };
    var root = Root.init();

    for (&entries) |*entry| {
        add(&entry.node, &root, less);
    }

    const found = find(@as(i32, 10), &root, cmp) orelse return error.TestUnexpectedResult;
    const found_entry: *const Entry = @fieldParentPtr("node", found);
    try std.testing.expectEqual(@as(i32, 10), found_entry.key);

    const first_match = findFirst(@as(i32, 10), &root, cmp) orelse return error.TestUnexpectedResult;
    const first_entry: *const Entry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(i32, 10), first_entry.key);
    try std.testing.expectEqual(@as(i32, 0), first_entry.serial);

    const second_match = nextMatch(@as(i32, 10), first_match, cmp) orelse return error.TestUnexpectedResult;
    const second_entry: *const Entry = @fieldParentPtr("node", second_match);
    try std.testing.expectEqual(@as(i32, 10), second_entry.key);
    try std.testing.expectEqual(@as(i32, 1), second_entry.serial);

    const third_match = nextMatch(@as(i32, 10), second_match, cmp) orelse return error.TestUnexpectedResult;
    const third_entry: *const Entry = @fieldParentPtr("node", third_match);
    try std.testing.expectEqual(@as(i32, 10), third_entry.key);
    try std.testing.expectEqual(@as(i32, 2), third_entry.serial);

    try std.testing.expectEqual(@as(?*Node, null), nextMatch(@as(i32, 10), third_match, cmp));
    try std.testing.expectEqual(@as(?*Node, null), find(@as(i32, 99), &root, cmp));
    try std.testing.expectEqual(@as(?*Node, null), findFirst(@as(i32, 99), &root, cmp));
}

test "rbtree eraseInit clears detached nodes after erase" {
    const Entry = struct {
        key: i32,
        node: Node = Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const Node, rhs: *const Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 20 },
        .{ .key = 5 },
        .{ .key = 15 },
    };
    var root = Root.init();

    for (&entries) |*entry| {
        add(&entry.node, &root, less);
    }

    eraseInit(&entries[0].node, &root);

    try std.testing.expect(emptyNode(&entries[0].node));
    try std.testing.expectEqual(@as(?*Node, null), next(&entries[0].node));
    try std.testing.expectEqual(@as(?*Node, null), prev(&entries[0].node));

    var order: [3]i32 = undefined;
    var count: usize = 0;
    var current = first(&root);
    while (current) |node| : (current = next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 15, 20 }, order[0..count]);
}

test "rbtree eraseInitCached detaches cached nodes and keeps cached roots reusable" {
    const Entry = struct {
        key: i32,
        node: Node = Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const Node, rhs: *const Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 15 },
    };
    var reseed = Entry{ .key = 6 };
    var root = RootCached.init();

    for (&entries) |*entry| {
        _ = addCached(&entry.node, &root, less);
    }

    eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*Node, &entries[0].node), firstCached(&root));
    try std.testing.expectEqual(first(&root.root), firstCached(&root));

    eraseInitCached(&entries[0].node, &root);
    try std.testing.expect(emptyNode(&entries[0].node));
    try std.testing.expectEqual(@as(?*Node, &entries[2].node), firstCached(&root));
    try std.testing.expectEqual(first(&root.root), firstCached(&root));

    eraseInitCached(&entries[2].node, &root);
    try std.testing.expect(emptyNode(&entries[2].node));
    try std.testing.expectEqual(@as(?*Node, null), firstCached(&root));
    try std.testing.expectEqual(@as(?*Node, null), root.root.node);

    try std.testing.expectEqual(@as(?*Node, &reseed.node), addCached(&reseed.node, &root, less));
    try std.testing.expectEqual(@as(?*Node, &reseed.node), firstCached(&root));
    try std.testing.expectEqual(first(&root.root), firstCached(&root));
}

test "rbtree replaceNode keeps displaced nodes non-empty until cleared" {
    const Entry = struct {
        key: i32,
        node: Node = Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const Node, rhs: *const Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 20 },
        .{ .key = 5 },
        .{ .key = 15 },
    };
    var replacement = Entry{ .key = 10 };
    var root = Root.init();

    for (&entries) |*entry| {
        add(&entry.node, &root, less);
    }

    replaceNode(&entries[0].node, &replacement.node, &root);

    try std.testing.expect(!emptyNode(&entries[0].node));
    try std.testing.expectEqual(@as(?*Node, &entries[2].node), first(&root));
    try std.testing.expectEqual(@as(?*Node, &replacement.node), next(&entries[2].node));
    try std.testing.expectEqual(@as(?*Node, &entries[3].node), next(&entries[0].node));
    try std.testing.expectEqual(@as(?*Node, &entries[2].node), prev(&entries[0].node));

    clearNode(&entries[0].node);
    try std.testing.expect(emptyNode(&entries[0].node));
    try std.testing.expectEqual(@as(?*Node, null), next(&entries[0].node));
    try std.testing.expectEqual(@as(?*Node, null), prev(&entries[0].node));
}

test "rbtree postorder and empty node helpers behave" {
    const Entry = struct {
        key: i32,
        node: Node = Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const Node, rhs: *const Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 2 },
        .{ .key = 1 },
        .{ .key = 3 },
    };
    var root = Root.init();

    for (&entries) |*entry| {
        add(&entry.node, &root, less);
    }

    var count: usize = 0;
    var current = firstPostorder(&root);
    while (current) |node| : (current = nextPostorder(node)) {
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqual(@as(?*Node, null), nextPostorder(null));

    var detached = Node.init();
    clearNode(&detached);
    try std.testing.expect(emptyNode(&detached));
    try std.testing.expectEqual(@as(?*Node, null), nextPostorder(&detached));
}
