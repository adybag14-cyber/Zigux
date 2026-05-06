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
    root: Root = .{},
    leftmost: ?*Node = null,

    pub fn init() RootCached {
        return .{};
    }
};

pub const LessFn = *const fn (*const Node, *const Node) bool;
pub const CmpNodeFn = *const fn (*const Node, *const Node) i32;
pub const CmpKeyFn = *const fn (*const anyopaque, *const Node) i32;

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

pub fn addCached(node: *Node, root: *RootCached, less: LessFn) void {
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
}

pub fn findAdd(node: *Node, root: *Root, cmp: CmpNodeFn) ?*Node {
    var link = &root.node;
    var parent: ?*Node = null;

    while (link.*) |current| {
        parent = current;
        const order = cmp(node, current);
        if (order < 0) {
            link = &current.left;
        } else if (order > 0) {
            link = &current.right;
        } else {
            return current;
        }
    }

    linkNode(node, parent, link);
    insertColor(node, root);
    return null;
}

pub fn find(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) ?*Node {
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

pub fn findFirst(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) ?*Node {
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

pub fn nextMatch(key: *const anyopaque, node: *const Node, cmp: CmpKeyFn) ?*Node {
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

pub fn eraseCached(node: *Node, root: *RootCached) void {
    if (root.leftmost == node) {
        root.leftmost = next(node);
    }
    erase(node, &root.root);
}

pub fn eraseInit(node: *Node, root: *Root) void {
    erase(node, root);
    clearNode(node);
}

pub fn first(root: *const Root) ?*Node {
    const node = root.node orelse return null;
    return minimum(node);
}

pub fn firstCached(root: *const RootCached) ?*Node {
    return root.leftmost;
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

    try std.testing.expect(emptyRoot(&root));

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

    var reverse_order: [5]i32 = undefined;
    var reverse_count: usize = 0;
    current = last(&root);
    while (current) |node| : (current = prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        reverse_order[reverse_count] = entry.key;
        reverse_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 5), reverse_count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 25, 20, 15, 10, 5 }, reverse_order[0..reverse_count]);
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

test "rbtree eraseInit detaches erased node" {
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
    };
    var root = Root.init();

    for (&entries) |*entry| {
        add(&entry.node, &root, less);
    }

    eraseInit(&entries[0].node, &root);

    try std.testing.expect(emptyNode(&entries[0].node));

    var order: [2]i32 = undefined;
    var count: usize = 0;
    var current = first(&root);
    while (current) |node| : (current = next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 2), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 20 }, order[0..count]);
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
    try std.testing.expect(nextPostorder(null) == null);

    var detached = Node.init();
    clearNode(&detached);
    try std.testing.expect(emptyNode(&detached));
}

test "rbtree findAdd keeps the first duplicate and inserts new keys" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: Node = Node.init(),
    };

    const cmp = struct {
        fn compare(lhs: *const Node, rhs: *const Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 5, .serial = 2 },
        .{ .key = 10, .serial = 3 },
        .{ .key = 15, .serial = 4 },
    };
    var root = Root.init();

    try std.testing.expectEqual(@as(?*Node, null), findAdd(&entries[0].node, &root, cmp));
    try std.testing.expectEqual(@as(?*Node, null), findAdd(&entries[1].node, &root, cmp));
    try std.testing.expectEqual(@as(?*Node, null), findAdd(&entries[2].node, &root, cmp));

    const existing = findAdd(&entries[3].node, &root, cmp) orelse return error.TestUnexpectedResult;
    const existing_entry: *const Entry = @fieldParentPtr("node", existing);
    try std.testing.expectEqual(@as(i32, 10), existing_entry.key);
    try std.testing.expectEqual(@as(usize, 0), existing_entry.serial);

    try std.testing.expectEqual(@as(?*Node, null), findAdd(&entries[4].node, &root, cmp));

    var order: [4]i32 = undefined;
    var count: usize = 0;
    var current = first(&root);
    while (current) |node| : (current = next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 4), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 10, 15, 20 }, order[0..count]);
}

test "rbtree nextMatch walks the duplicate range in order" {
    const Entry = struct {
        key: i32,
        serial: usize,
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
        fn compare(key: *const anyopaque, node: *const Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    var root = Root.init();

    for (&entries) |*entry| {
        add(&entry.node, &root, less);
    }

    const wanted = @as(i32, 15);
    const found = find(&wanted, &root, cmp) orelse return error.TestUnexpectedResult;
    const found_entry: *const Entry = @fieldParentPtr("node", found);
    try std.testing.expectEqual(@as(i32, 15), found_entry.key);

    const missing = @as(i32, 17);
    try std.testing.expect(find(&missing, &root, cmp) == null);

    const duplicate = @as(i32, 10);
    const first_match = findFirst(&duplicate, &root, cmp) orelse return error.TestUnexpectedResult;
    const first_match_entry: *const Entry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(usize, 0), first_match_entry.serial);

    var serials: [3]usize = undefined;
    var count: usize = 0;
    var cursor = first_match;
    while (true) {
        const entry: *const Entry = @fieldParentPtr("node", cursor);
        serials[count] = entry.serial;
        count += 1;
        cursor = nextMatch(&duplicate, cursor, cmp) orelse break;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, serials[0..count]);
    try std.testing.expect(nextMatch(&duplicate, cursor, cmp) == null);
}

test "rbtree cached root keeps the leftmost pointer in sync" {
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
    var replacement = Entry{ .key = 10 };
    var new_leftmost = Entry{ .key = 3 };
    var root = RootCached.init();

    try std.testing.expect(firstCached(&root) == null);

    for (&entries) |*entry| {
        addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(first(&root.root), firstCached(&root));
    const initial_leftmost = firstCached(&root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*Node, &entries[1].node), initial_leftmost);

    eraseCached(&entries[2].node, &root);
    try std.testing.expectEqual(@as(*Node, &entries[1].node), firstCached(&root).?);

    eraseCached(&entries[1].node, &root);
    try std.testing.expectEqual(@as(*Node, &entries[0].node), firstCached(&root).?);
    try std.testing.expectEqual(first(&root.root), firstCached(&root));

    replaceNodeCached(&entries[0].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(*Node, &replacement.node), firstCached(&root).?);
    try std.testing.expectEqual(first(&root.root), firstCached(&root));

    addCached(&new_leftmost.node, &root, less);
    try std.testing.expectEqual(@as(*Node, &new_leftmost.node), firstCached(&root).?);
    try std.testing.expectEqual(first(&root.root), firstCached(&root));
}
