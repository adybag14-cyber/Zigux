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

pub const MatchIterator = struct {
    key: *const anyopaque,
    cmp: CmpKeyFn,
    current: ?*Node,

    pub fn next(self: *MatchIterator) ?*Node {
        const node = self.current orelse return null;
        self.current = nextMatch(self.key, node, self.cmp);
        return node;
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

pub fn rb_insert_color_cached(node: *Node, root: *RootCached, leftmost: bool) void {
    insertColorCached(node, root, leftmost);
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

pub fn rb_add_cached(node: *Node, root: *RootCached, less: LessFn) ?*Node {
    return addCached(node, root, less);
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

pub fn findAddCached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {
    var link = &root.root.node;
    var parent: ?*Node = null;
    var leftmost = true;

    while (link.*) |current| {
        parent = current;
        const order = cmp(node, current);
        if (order < 0) {
            link = &current.left;
        } else if (order > 0) {
            link = &current.right;
            leftmost = false;
        } else {
            return current;
        }
    }

    linkNode(node, parent, link);
    insertColorCached(node, root, leftmost);
    return null;
}

pub fn rb_find_add_cached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {
    return findAddCached(node, root, cmp);
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

pub fn matchIterator(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) MatchIterator {
    return .{
        .key = key,
        .cmp = cmp,
        .current = findFirst(key, root, cmp),
    };
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
    if (root.leftmost == node) {
        const leftmost = next(node);
        root.leftmost = leftmost;
        erase(node, &root.root);
        return leftmost;
    }

    erase(node, &root.root);
    return null;
}

pub fn rb_erase_cached(node: *Node, root: *RootCached) ?*Node {
    return eraseCached(node, root);
}

pub fn eraseInit(node: *Node, root: *Root) void {
    erase(node, root);
    clearNode(node);
}

pub fn eraseInitCached(node: *Node, root: *RootCached) void {
    _ = eraseCached(node, root);
    clearNode(node);
}

pub fn rb_erase_init_cached(node: *Node, root: *RootCached) void {
    eraseInitCached(node, root);
}

pub fn first(root: *const Root) ?*Node {
    const node = root.node orelse return null;
    return minimum(node);
}

pub fn rb_first(root: *const Root) ?*Node {
    return first(root);
}

pub fn firstCached(root: *const RootCached) ?*Node {
    return root.leftmost;
}

pub fn rb_first_cached(root: *const RootCached) ?*Node {
    return firstCached(root);
}

pub fn last(root: *const Root) ?*Node {
    const node = root.node orelse return null;
    return maximum(node);
}

pub fn rb_last(root: *const Root) ?*Node {
    return last(root);
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

pub fn rb_next(node: *const Node) ?*Node {
    return next(node);
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

pub fn rb_prev(node: *const Node) ?*Node {
    return prev(node);
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

pub fn rb_replace_node(victim: *Node, new: *Node, root: *Root) void {
    replaceNode(victim, new, root);
}

pub fn replaceNodeCached(victim: *Node, new: *Node, root: *RootCached) void {
    if (root.leftmost == victim) {
        root.leftmost = new;
    }
    replaceNode(victim, new, &root.root);
}

pub fn rb_replace_node_cached(victim: *Node, new: *Node, root: *RootCached) void {
    replaceNodeCached(victim, new, root);
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

pub fn rb_first_postorder(root: *const Root) ?*Node {
    return firstPostorder(root);
}

pub fn nextPostorder(node: ?*const Node) ?*Node {
    const current = node orelse return null;
    const parent = current.parent;
    if (parent != null and parent.?.left == current and parent.?.right != null) {
        return leftDeepestNode(parent.?.right.?);
    }
    return parent;
}

pub fn rb_next_postorder(node: ?*const Node) ?*Node {
    return nextPostorder(node);
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

test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers" {
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

    var primary_entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 20 },
        .{ .key = 5 },
        .{ .key = 15 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 20 },
        .{ .key = 5 },
        .{ .key = 15 },
    };
    var primary_replacement = Entry{ .key = 10 };
    var alias_replacement = Entry{ .key = 10 };
    var primary_root = Root.init();
    var alias_root = Root.init();
    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        add(&primary_entry.node, &primary_root, less);
        add(&alias_entry.node, &alias_root, less);
    }

    var primary_forward: [4]i32 = undefined;
    var alias_forward: [4]i32 = undefined;
    var count: usize = 0;
    var current = first(&primary_root);
    while (current) |node| : (current = next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        primary_forward[count] = entry.key;
        count += 1;
    }

    var alias_count: usize = 0;
    current = rb_first(&alias_root);
    while (current) |node| : (current = rb_next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        alias_forward[alias_count] = entry.key;
        alias_count += 1;
    }

    try std.testing.expectEqual(count, alias_count);
    try std.testing.expectEqualSlices(i32, primary_forward[0..count], alias_forward[0..alias_count]);

    var primary_reverse: [4]i32 = undefined;
    var alias_reverse: [4]i32 = undefined;
    count = 0;
    current = last(&primary_root);
    while (current) |node| : (current = prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        primary_reverse[count] = entry.key;
        count += 1;
    }

    alias_count = 0;
    current = rb_last(&alias_root);
    while (current) |node| : (current = rb_prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        alias_reverse[alias_count] = entry.key;
        alias_count += 1;
    }

    try std.testing.expectEqual(count, alias_count);
    try std.testing.expectEqualSlices(i32, primary_reverse[0..count], alias_reverse[0..alias_count]);

    replaceNode(&primary_entries[0].node, &primary_replacement.node, &primary_root);
    rb_replace_node(&alias_entries[0].node, &alias_replacement.node, &alias_root);

    count = 0;
    current = first(&primary_root);
    while (current) |node| : (current = next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        primary_forward[count] = entry.key;
        count += 1;
    }

    alias_count = 0;
    current = rb_first(&alias_root);
    while (current) |node| : (current = rb_next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        alias_forward[alias_count] = entry.key;
        alias_count += 1;
    }

    try std.testing.expectEqual(count, alias_count);
    try std.testing.expectEqualSlices(i32, primary_forward[0..count], alias_forward[0..alias_count]);
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
        .{ .key = 15 },
        .{ .key = 25 },
    };
    var root = Root.init();
    for (&entries) |*entry| {
        add(&entry.node, &root, less);
    }

    eraseInit(&entries[1].node, &root);

    try std.testing.expect(emptyNode(&entries[1].node));

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

test "rbtree postorder and empty node helpers behave" {
    const Entry = struct {
        key: i32,
        node: Node = Node.init(),
    };

    var detached = Node.init();
    clearNode(&detached);
    try std.testing.expect(emptyNode(&detached));
    try std.testing.expect(nextPostorder(&detached) == null);
    try std.testing.expect(rb_next_postorder(&detached) == null);

    var entries = [_]Entry{
        .{ .key = 8 },
        .{ .key = 4 },
        .{ .key = 12 },
        .{ .key = 2 },
        .{ .key = 6 },
    };
    var root = Root.init();

    root.node = &entries[0].node;
    entries[0].node.parent = null;
    entries[0].node.left = &entries[1].node;
    entries[0].node.right = &entries[2].node;

    entries[1].node.parent = &entries[0].node;
    entries[1].node.left = &entries[3].node;
    entries[1].node.right = &entries[4].node;

    entries[2].node.parent = &entries[0].node;
    entries[2].node.left = null;
    entries[2].node.right = null;

    entries[3].node.parent = &entries[1].node;
    entries[3].node.left = null;
    entries[3].node.right = null;

    entries[4].node.parent = &entries[1].node;
    entries[4].node.left = null;
    entries[4].node.right = null;

    const first_postorder = firstPostorder(&root) orelse return error.TestUnexpectedResult;
    const first_entry: *const Entry = @fieldParentPtr("node", first_postorder);
    try std.testing.expectEqual(@as(i32, 2), first_entry.key);

    const second = nextPostorder(first_postorder) orelse return error.TestUnexpectedResult;
    const second_entry: *const Entry = @fieldParentPtr("node", second);
    try std.testing.expectEqual(@as(i32, 6), second_entry.key);

    const third = nextPostorder(second) orelse return error.TestUnexpectedResult;
    const third_entry: *const Entry = @fieldParentPtr("node", third);
    try std.testing.expectEqual(@as(i32, 4), third_entry.key);

    const fourth = nextPostorder(third) orelse return error.TestUnexpectedResult;
    const fourth_entry: *const Entry = @fieldParentPtr("node", fourth);
    try std.testing.expectEqual(@as(i32, 12), fourth_entry.key);

    const fifth = nextPostorder(fourth) orelse return error.TestUnexpectedResult;
    const fifth_entry: *const Entry = @fieldParentPtr("node", fifth);
    try std.testing.expectEqual(@as(i32, 8), fifth_entry.key);

    try std.testing.expect(nextPostorder(fifth) == null);
    try std.testing.expectEqual(@as(?*Node, first_postorder), rb_first_postorder(&root));
    try std.testing.expectEqual(@as(?*Node, second), rb_next_postorder(first_postorder));
    try std.testing.expectEqual(@as(?*Node, third), rb_next_postorder(second));
    try std.testing.expectEqual(@as(?*Node, fourth), rb_next_postorder(third));
    try std.testing.expectEqual(@as(?*Node, fifth), rb_next_postorder(fourth));
    try std.testing.expect(rb_next_postorder(fifth) == null);
    try std.testing.expect(emptyNode(&detached));
}

test "rbtree postorder unwinds parents when no right sibling subtree exists" {
    const Entry = struct {
        key: i32,
        node: Node = Node.init(),
    };

    var primary_entries = [_]Entry{
        .{ .key = 8 },
        .{ .key = 4 },
        .{ .key = 6 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 8 },
        .{ .key = 4 },
        .{ .key = 6 },
    };
    var primary_root = Root.init();
    var alias_root = Root.init();

    const wireShape = struct {
        fn apply(root: *Root, entries: []Entry) void {
            root.node = &entries[0].node;
            entries[0].node.parent = null;
            entries[0].node.left = &entries[1].node;
            entries[0].node.right = null;

            entries[1].node.parent = &entries[0].node;
            entries[1].node.left = null;
            entries[1].node.right = &entries[2].node;

            entries[2].node.parent = &entries[1].node;
            entries[2].node.left = null;
            entries[2].node.right = null;
        }
    }.apply;

    wireShape(&primary_root, &primary_entries);
    wireShape(&alias_root, &alias_entries);

    var primary_order: [3]i32 = undefined;
    var alias_order: [3]i32 = undefined;

    var primary_count: usize = 0;
    var current = firstPostorder(&primary_root);
    while (current) |node| : (current = nextPostorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        primary_order[primary_count] = entry.key;
        primary_count += 1;
    }

    var alias_count: usize = 0;
    current = rb_first_postorder(&alias_root);
    while (current) |node| : (current = rb_next_postorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        alias_order[alias_count] = entry.key;
        alias_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), primary_count);
    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 6, 4, 8 }, primary_order[0..primary_count]);
    try std.testing.expectEqualSlices(i32, primary_order[0..primary_count], alias_order[0..alias_count]);
}

test "rbtree postorder walks left-deep and right-sibling branches in order" {
    const Entry = struct {
        key: i32,
        node: Node = Node.init(),
    };

    var primary_entries = [_]Entry{
        .{ .key = 8 },
        .{ .key = 4 },
        .{ .key = 2 },
        .{ .key = 6 },
        .{ .key = 12 },
        .{ .key = 10 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 8 },
        .{ .key = 4 },
        .{ .key = 2 },
        .{ .key = 6 },
        .{ .key = 12 },
        .{ .key = 10 },
    };
    var primary_root = Root.init();
    var alias_root = Root.init();

    const wireShape = struct {
        fn apply(root: *Root, entries: []Entry) void {
            root.node = &entries[0].node;
            entries[0].node.parent = null;
            entries[0].node.left = &entries[1].node;
            entries[0].node.right = &entries[4].node;

            entries[1].node.parent = &entries[0].node;
            entries[1].node.left = &entries[2].node;
            entries[1].node.right = &entries[3].node;

            entries[2].node.parent = &entries[1].node;
            entries[2].node.left = null;
            entries[2].node.right = null;

            entries[3].node.parent = &entries[1].node;
            entries[3].node.left = null;
            entries[3].node.right = null;

            entries[4].node.parent = &entries[0].node;
            entries[4].node.left = &entries[5].node;
            entries[4].node.right = null;

            entries[5].node.parent = &entries[4].node;
            entries[5].node.left = null;
            entries[5].node.right = null;
        }
    }.apply;

    wireShape(&primary_root, &primary_entries);
    wireShape(&alias_root, &alias_entries);

    var primary_order: [6]i32 = undefined;
    var alias_order: [6]i32 = undefined;

    var primary_count: usize = 0;
    var current = firstPostorder(&primary_root);
    while (current) |node| : (current = nextPostorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        primary_order[primary_count] = entry.key;
        primary_count += 1;
    }

    var alias_count: usize = 0;
    current = rb_first_postorder(&alias_root);
    while (current) |node| : (current = rb_next_postorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        alias_order[alias_count] = entry.key;
        alias_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 6), primary_count);
    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 2, 6, 4, 10, 12, 8 }, primary_order[0..primary_count]);
    try std.testing.expectEqualSlices(i32, primary_order[0..primary_count], alias_order[0..alias_count]);
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

test "rbtree matchIterator walks the duplicate range in order" {
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

    const duplicate = @as(i32, 10);
    var iter = matchIterator(&duplicate, &root, cmp);
    var serials: [3]usize = undefined;
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, serials[0..count]);

    const missing = @as(i32, 17);
    var missing_iter = matchIterator(&missing, &root, cmp);
    try std.testing.expect(missing_iter.next() == null);
}

test "rbtree addCached returns the inserted node only when it becomes leftmost" {
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

    var first_entry = Entry{ .key = 10, .serial = 0 };
    var larger_entry = Entry{ .key = 12, .serial = 1 };
    var smaller_entry = Entry{ .key = 5, .serial = 2 };
    var duplicate_entry = Entry{ .key = 5, .serial = 3 };
    var root = RootCached.init();

    try std.testing.expectEqual(@as(?*Node, &first_entry.node), addCached(&first_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*Node, &first_entry.node), firstCached(&root));

    try std.testing.expectEqual(@as(?*Node, null), addCached(&larger_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*Node, &first_entry.node), firstCached(&root));

    try std.testing.expectEqual(@as(?*Node, &smaller_entry.node), addCached(&smaller_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*Node, &smaller_entry.node), firstCached(&root));

    try std.testing.expectEqual(@as(?*Node, null), addCached(&duplicate_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*Node, &smaller_entry.node), firstCached(&root));
    try std.testing.expectEqual(first(&root.root), firstCached(&root));
}

test "rbtree findAddCached keeps cached leftmost stable while inserting misses" {
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

    var leftmost = Entry{ .key = 5, .serial = 0 };
    var root_entry = Entry{ .key = 10, .serial = 1 };
    var larger_entry = Entry{ .key = 15, .serial = 2 };
    var duplicate_entries = [_]Entry{.{ .key = 10, .serial = 3 }};
    var root = RootCached.init();

    try std.testing.expectEqual(@as(?*Node, null), findAddCached(&root_entry.node, &root, cmp));
    try std.testing.expectEqual(@as(?*Node, &root_entry.node), firstCached(&root));

    try std.testing.expectEqual(@as(?*Node, null), findAddCached(&leftmost.node, &root, cmp));
    try std.testing.expectEqual(@as(?*Node, &leftmost.node), firstCached(&root));

    try std.testing.expectEqual(@as(?*Node, null), findAddCached(&larger_entry.node, &root, cmp));
    try std.testing.expectEqual(@as(?*Node, &leftmost.node), firstCached(&root));

    const duplicate = findAddCached(&duplicate_entries[0].node, &root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*Node, &root_entry.node), duplicate);
    try std.testing.expectEqual(@as(?*Node, &leftmost.node), firstCached(&root));
    try std.testing.expectEqual(first(&root.root), firstCached(&root));
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
        _ = addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(first(&root.root), firstCached(&root));
    const initial_leftmost = firstCached(&root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*Node, &entries[1].node), initial_leftmost);

    try std.testing.expect(eraseCached(&entries[2].node, &root) == null);
    try std.testing.expectEqual(@as(*Node, &entries[1].node), firstCached(&root).?);

    const promoted_leftmost = eraseCached(&entries[1].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*Node, &entries[0].node), promoted_leftmost);
    try std.testing.expectEqual(@as(*Node, &entries[0].node), firstCached(&root).?);
    try std.testing.expectEqual(first(&root.root), firstCached(&root));

    replaceNodeCached(&entries[0].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(*Node, &replacement.node), firstCached(&root).?);
    try std.testing.expectEqual(first(&root.root), firstCached(&root));

    _ = addCached(&new_leftmost.node, &root, less);
    try std.testing.expectEqual(@as(*Node, &new_leftmost.node), firstCached(&root).?);
    try std.testing.expectEqual(first(&root.root), firstCached(&root));
}

test "rbtree cached-root Linux-style aliases mirror the primary helpers" {
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
        fn compare(lhs: *const Node, rhs: *const Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    const firstKey = struct {
        fn read(root: *const RootCached) ?i32 {
            const node = firstCached(root) orelse return null;
            const entry: *const Entry = @fieldParentPtr("node", node);
            return entry.key;
        }
    }.read;

    const returnedIdentity = struct {
        fn read(node: ?*Node) ?struct { i32, usize } {
            const current = node orelse return null;
            const entry: *const Entry = @fieldParentPtr("node", current);
            return .{ entry.key, entry.serial };
        }
    }.read;

    var primary_first = Entry{ .key = 10, .serial = 0 };
    var alias_first = Entry{ .key = 10, .serial = 0 };
    var primary_second = Entry{ .key = 5, .serial = 1 };
    var alias_second = Entry{ .key = 5, .serial = 1 };
    var primary_third = Entry{ .key = 15, .serial = 2 };
    var alias_third = Entry{ .key = 15, .serial = 2 };
    var primary_duplicate = Entry{ .key = 10, .serial = 3 };
    var alias_duplicate = Entry{ .key = 10, .serial = 3 };
    var primary_replacement = Entry{ .key = 10, .serial = 4 };
    var alias_replacement = Entry{ .key = 10, .serial = 4 };

    var primary_root = RootCached.init();
    var alias_root = RootCached.init();

    try std.testing.expectEqual(@as(?*Node, &primary_first.node), addCached(&primary_first.node, &primary_root, less));
    try std.testing.expectEqual(@as(?*Node, &alias_first.node), rb_add_cached(&alias_first.node, &alias_root, less));
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));

    try std.testing.expectEqual(@as(?*Node, null), findAddCached(&primary_second.node, &primary_root, cmp));
    try std.testing.expectEqual(@as(?*Node, null), rb_find_add_cached(&alias_second.node, &alias_root, cmp));
    try std.testing.expectEqual(@as(?*Node, null), findAddCached(&primary_third.node, &primary_root, cmp));
    try std.testing.expectEqual(@as(?*Node, null), rb_find_add_cached(&alias_third.node, &alias_root, cmp));
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));

    const primary_existing = findAddCached(&primary_duplicate.node, &primary_root, cmp) orelse return error.TestUnexpectedResult;
    const alias_existing = rb_find_add_cached(&alias_duplicate.node, &alias_root, cmp) orelse return error.TestUnexpectedResult;
    const primary_existing_entry: *const Entry = @fieldParentPtr("node", primary_existing);
    const alias_existing_entry: *const Entry = @fieldParentPtr("node", alias_existing);
    try std.testing.expectEqual(primary_existing_entry.key, alias_existing_entry.key);
    try std.testing.expectEqual(primary_existing_entry.serial, alias_existing_entry.serial);

    try std.testing.expectEqual(
        returnedIdentity(eraseCached(&primary_second.node, &primary_root)),
        returnedIdentity(rb_erase_cached(&alias_second.node, &alias_root)),
    );
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));

    replaceNodeCached(&primary_first.node, &primary_replacement.node, &primary_root);
    rb_replace_node_cached(&alias_first.node, &alias_replacement.node, &alias_root);
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));

    try std.testing.expectEqual(@as(?struct { i32, usize }, null), returnedIdentity(eraseCached(&primary_third.node, &primary_root)));
    try std.testing.expectEqual(@as(?struct { i32, usize }, null), returnedIdentity(rb_erase_cached(&alias_third.node, &alias_root)));
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));

    eraseInitCached(&primary_replacement.node, &primary_root);
    rb_erase_init_cached(&alias_replacement.node, &alias_root);
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));

    var manual_root = RootCached.init();
    var manual_entry = Entry{ .key = 1, .serial = 0 };
    linkNode(&manual_entry.node, null, &manual_root.root.node);
    insertColorCached(&manual_entry.node, &manual_root, true);

    var manual_alias_root = RootCached.init();
    var manual_alias_entry = Entry{ .key = 1, .serial = 0 };
    linkNode(&manual_alias_entry.node, null, &manual_alias_root.root.node);
    rb_insert_color_cached(&manual_alias_entry.node, &manual_alias_root, true);

    try std.testing.expectEqual(firstKey(&manual_root), firstKey(&manual_alias_root));
}

test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged" {
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
    };
    var replacement = Entry{ .key = 20 };
    var root = RootCached.init();

    for (&entries) |*entry| {
        _ = addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*Node, &entries[1].node), firstCached(&root));

    replaceNodeCached(&entries[2].node, &replacement.node, &root);

    try std.testing.expectEqual(@as(?*Node, &entries[1].node), firstCached(&root));
    try std.testing.expectEqual(first(&root.root), firstCached(&root));
    try std.testing.expectEqual(@as(?*Node, &replacement.node), last(&root.root));
}

test "rbtree eraseCached returns null for a singleton cached tree" {
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

    var entry = Entry{ .key = 7 };
    var root = RootCached.init();

    _ = addCached(&entry.node, &root, less);

    try std.testing.expectEqual(@as(*Node, &entry.node), firstCached(&root).?);
    try std.testing.expect(eraseCached(&entry.node, &root) == null);
    try std.testing.expect(firstCached(&root) == null);
    try std.testing.expect(root.root.node == null);
}

test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned" {
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
}

test "rbtree eraseInitCached clears singleton cached roots before reseed" {
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

    var first_entry = Entry{ .key = 10 };
    var second_entry = Entry{ .key = 6 };
    var root = RootCached.init();

    _ = addCached(&first_entry.node, &root, less);
    try std.testing.expectEqual(@as(?*Node, &first_entry.node), firstCached(&root));

    eraseInitCached(&first_entry.node, &root);
    try std.testing.expect(emptyNode(&first_entry.node));
    try std.testing.expectEqual(@as(?*Node, null), root.root.node);
    try std.testing.expectEqual(@as(?*Node, null), firstCached(&root));

    _ = addCached(&second_entry.node, &root, less);
    try std.testing.expectEqual(@as(?*Node, &second_entry.node), firstCached(&root));
    try std.testing.expectEqual(first(&root.root), firstCached(&root));
}
