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

pub fn rb_add(node: *Node, root: *Root, less: LessFn) void {
    add(node, root, less);
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

pub fn rb_find_add(node: *Node, root: *Root, cmp: CmpNodeFn) ?*Node {
    return findAdd(node, root, cmp);
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

pub fn rb_find(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) ?*Node {
    return find(key, root, cmp);
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

pub fn rb_find_first(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) ?*Node {
    return findFirst(key, root, cmp);
}

pub fn nextMatch(key: *const anyopaque, node: *const Node, cmp: CmpKeyFn) ?*Node {
    const candidate = next(node) orelse return null;
    if (cmp(key, candidate) != 0) {
        return null;
    }
    return candidate;
}

pub fn rb_next_match(key: *const anyopaque, node: *const Node, cmp: CmpKeyFn) ?*Node {
    return nextMatch(key, node, cmp);
}

pub fn matchIterator(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) MatchIterator {
    return .{
        .key = key,
        .cmp = cmp,
        .current = findFirst(key, root, cmp),
    };
}

pub fn rb_match_iterator(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) MatchIterator {
    return matchIterator(key, root, cmp);
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
    if (emptyNode(current)) {
        return null;
    }
    const parent = current.parent;
    if (parent != null and parent.?.left == current and parent.?.right != null) {
        return leftDeepestNode(parent.?.right.?);
    }
    return parent;
}

pub fn rb_next_postorder(node: ?*const Node) ?*Node {
    return nextPostorder(node);
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

test "rbtree replaceNode keeps root ownership and traversal stable when replacing the current root" {
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
    var right_entry = Entry{ .key = 20 };
    var replacement = Entry{ .key = 10 };
    var root = Root.init();

    add(&root_entry.node, &root, less);
    add(&left_entry.node, &root, less);
    add(&right_entry.node, &root, less);

    replaceNode(&root_entry.node, &replacement.node, &root);

    try std.testing.expectEqual(@as(?*Node, &replacement.node), root.node);
    try std.testing.expectEqual(@as(?*Node, null), replacement.node.parent);
    try std.testing.expectEqual(@as(?*Node, &left_entry.node), replacement.node.left);
    try std.testing.expectEqual(@as(?*Node, &right_entry.node), replacement.node.right);
    try std.testing.expectEqual(@as(?*Node, &replacement.node), left_entry.node.parent);
    try std.testing.expectEqual(@as(?*Node, &replacement.node), right_entry.node.parent);
    try std.testing.expectEqual(@as(?*Node, &left_entry.node), first(&root));
    try std.testing.expectEqual(@as(?*Node, &right_entry.node), last(&root));
    try std.testing.expectEqual(@as(?*Node, &replacement.node), next(&left_entry.node));
    try std.testing.expectEqual(@as(?*Node, &left_entry.node), prev(&replacement.node));
    try std.testing.expectEqual(@as(?*Node, &right_entry.node), next(&replacement.node));
}

test "rbtree replaceNodeCached keeps the cached leftmost stable when replacing the current root" {
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
    var right_entry = Entry{ .key = 20 };
    var replacement = Entry{ .key = 10 };
    var root = RootCached.init();

    _ = addCached(&root_entry.node, &root, less);
    _ = addCached(&left_entry.node, &root, less);
    _ = addCached(&right_entry.node, &root, less);

    replaceNodeCached(&root_entry.node, &replacement.node, &root);

    try std.testing.expectEqual(@as(?*Node, &replacement.node), root.root.node);
    try std.testing.expectEqual(@as(?*Node, &left_entry.node), firstCached(&root));
    try std.testing.expectEqual(first(&root.root), firstCached(&root));
    try std.testing.expectEqual(@as(?*Node, null), replacement.node.parent);
    try std.testing.expectEqual(@as(?*Node, &left_entry.node), replacement.node.left);
    try std.testing.expectEqual(@as(?*Node, &right_entry.node), replacement.node.right);
    try std.testing.expectEqual(@as(?*Node, &replacement.node), left_entry.node.parent);
    try std.testing.expectEqual(@as(?*Node, &replacement.node), right_entry.node.parent);
}

test "rbtree rb_find_add_cached keeps duplicate callers detached and rb_replace_node_cached keeps leftmost aligned" {
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

    const cmp = struct {
        fn compare(lhs: *const Node, rhs: *const Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    var root_entry = Entry{ .key = 10 };
    var leftmost_entry = Entry{ .key = 5 };
    var right_entry = Entry{ .key = 15 };
    var duplicate_entry = Entry{ .key = 10 };
    var replacement_entry = Entry{ .key = 5 };
    var root = RootCached.init();

    try std.testing.expectEqual(@as(?*Node, &root_entry.node), addCached(&root_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*Node, &leftmost_entry.node), rb_add_cached(&leftmost_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*Node, null), rb_add_cached(&right_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*Node, &leftmost_entry.node), rb_first_cached(&root));

    const existing = rb_find_add_cached(&duplicate_entry.node, &root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*Node, &root_entry.node), existing);
    try std.testing.expectEqual(@as(?*Node, &leftmost_entry.node), rb_first_cached(&root));
    try std.testing.expectEqual(@as(?*Node, null), duplicate_entry.node.parent);
    try std.testing.expectEqual(@as(?*Node, null), duplicate_entry.node.left);
    try std.testing.expectEqual(@as(?*Node, null), duplicate_entry.node.right);
    try std.testing.expectEqual(Color.red, duplicate_entry.node.color);

    rb_replace_node_cached(&leftmost_entry.node, &replacement_entry.node, &root);
    try std.testing.expectEqual(@as(?*Node, &replacement_entry.node), rb_first_cached(&root));
    try std.testing.expectEqual(first(&root.root), rb_first_cached(&root));
    try std.testing.expect(prev(&replacement_entry.node) == null);
    try std.testing.expectEqual(@as(?*Node, &root_entry.node), next(&replacement_entry.node));
}

test "rbtree rb_add mirrors add for ordered traversal" {
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
    var primary_root = Root.init();
    var alias_root = Root.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        add(&primary_entry.node, &primary_root, less);
        rb_add(&alias_entry.node, &alias_root, less);
    }

    var primary_order: [primary_entries.len]i32 = undefined;
    var alias_order: [alias_entries.len]i32 = undefined;
    var primary_count: usize = 0;
    var alias_count: usize = 0;

    var primary_current = first(&primary_root);
    while (primary_current) |node| : (primary_current = next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        primary_order[primary_count] = entry.key;
        primary_count += 1;
    }

    var alias_current = first(&alias_root);
    while (alias_current) |node| : (alias_current = next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        alias_order[alias_count] = entry.key;
        alias_count += 1;
    }

    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqualSlices(i32, primary_order[0..primary_count], alias_order[0..alias_count]);
    try std.testing.expectEqual(@as(usize, 4), alias_count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 10, 15, 20 }, alias_order[0..alias_count]);
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

    try std.testing.expectEqual(@as(?*Node, &entry.node), firstCached(&root));
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
