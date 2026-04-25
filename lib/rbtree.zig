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

pub fn linkNode(node: *Node, parent: ?*Node, link: *?*Node) void {
    node.parent = parent;
    node.left = null;
    node.right = null;
    node.color = .red;
    link.* = node;
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
    new.parent = parent;
    new.left = victim.left;
    new.right = victim.right;
    new.color = victim.color;

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

pub fn firstPostorder(root: *const Root) ?*Node {
    const node = root.node orelse return null;
    return leftDeepestNode(node);
}

pub fn nextPostorder(node: *const Node) ?*Node {
    const parent = node.parent;
    if (parent != null and parent.?.left == node and parent.?.right != null) {
        return leftDeepestNode(parent.?.right.?);
    }
    return parent;
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

test "linkNode plus traversal helpers walk a manually linked tree in order" {
    const Entry = struct {
        key: i32,
        node: Node = Node.init(),
    };

    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 15 },
        .{ .key = 2 },
        .{ .key = 7 },
        .{ .key = 12 },
    };
    var root = Root.init();

    linkNode(&entries[0].node, null, &root.node);
    entries[0].node.color = .black;
    linkNode(&entries[1].node, &entries[0].node, &entries[0].node.left);
    linkNode(&entries[2].node, &entries[0].node, &entries[0].node.right);
    linkNode(&entries[3].node, &entries[1].node, &entries[1].node.left);
    linkNode(&entries[4].node, &entries[1].node, &entries[1].node.right);
    linkNode(&entries[5].node, &entries[2].node, &entries[2].node.left);

    var in_order: [6]i32 = undefined;
    var count: usize = 0;
    var current = first(&root);
    while (current) |node| : (current = next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        in_order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 6), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 2, 5, 7, 10, 12, 15 }, in_order[0..count]);
    try std.testing.expectEqual(@as(?*Node, &entries[5].node), prev(&entries[2].node));
    try std.testing.expectEqual(@as(?*Node, &entries[0].node), next(&entries[4].node));
    try std.testing.expectEqual(@as(?*Node, &entries[2].node), last(&root));
}

test "replaceNode and postorder helpers preserve the linked-tree structure" {
    const Entry = struct {
        key: i32,
        node: Node = Node.init(),
    };

    var root_entry = Entry{ .key = 10 };
    var left_entry = Entry{ .key = 5 };
    var right_entry = Entry{ .key = 15 };
    var left_left_entry = Entry{ .key = 2 };
    var replacement = Entry{ .key = 5 };
    var root = Root.init();

    linkNode(&root_entry.node, null, &root.node);
    root_entry.node.color = .black;
    linkNode(&left_entry.node, &root_entry.node, &root_entry.node.left);
    linkNode(&right_entry.node, &root_entry.node, &root_entry.node.right);
    linkNode(&left_left_entry.node, &left_entry.node, &left_entry.node.left);

    replaceNode(&left_entry.node, &replacement.node, &root);

    try std.testing.expectEqual(@as(?*Node, &replacement.node), root_entry.node.left);
    try std.testing.expectEqual(@as(?*Node, &replacement.node), left_left_entry.node.parent);
    try std.testing.expectEqual(@as(?*Node, &left_left_entry.node), first(&root));

    var postorder_count: usize = 0;
    var current = firstPostorder(&root);
    while (current) |node| : (current = nextPostorder(node)) {
        postorder_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 4), postorder_count);
}

test "clearNode marks a detached node as empty" {
    var node = Node.init();
    try std.testing.expect(!emptyNode(&node));

    clearNode(&node);

    try std.testing.expect(emptyNode(&node));
    try std.testing.expectEqual(@as(?*Node, null), next(&node));
    try std.testing.expectEqual(@as(?*Node, null), prev(&node));
}
