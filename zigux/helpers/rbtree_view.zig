const std = @import("std");
const rbtree = @import("rbtree");

pub const EMPTY_FLAG: u32 = 1;
pub const TRUNCATED_FLAG: u32 = 2;
pub const ROOT_BLACK_FLAG: u32 = 4;

pub const Summary = struct {
    node_count: u32,
    flags: u32,
    first_addr: usize,
    last_addr: usize,
};

pub fn isEmpty(root: *const rbtree.Root) bool {
    return rbtree.emptyRoot(root);
}

pub fn firstAddr(root: *const rbtree.Root) usize {
    const node = rbtree.first(root) orelse return 0;
    return @intFromPtr(node);
}

pub fn lastAddr(root: *const rbtree.Root) usize {
    const node = rbtree.last(root) orelse return 0;
    return @intFromPtr(node);
}

pub fn countBounded(root: *const rbtree.Root, max_nodes: u32) u32 {
    if (max_nodes == 0 or isEmpty(root)) return 0;

    var count: u32 = 0;
    var current = rbtree.first(root);
    while (current != null and count < max_nodes) : (current = rbtree.next(current.?)) {
        count += 1;
    }
    return count;
}

pub fn containsNode(root: *const rbtree.Root, target: *const rbtree.Node, max_nodes: u32) bool {
    if (max_nodes == 0 or isEmpty(root)) return false;

    var seen: u32 = 0;
    var current = rbtree.first(root);
    while (current != null and seen < max_nodes) : (current = rbtree.next(current.?)) {
        if (current.? == target) return true;
        seen += 1;
    }
    return false;
}

pub fn summarize(root: *const rbtree.Root, max_nodes: u32) Summary {
    if (isEmpty(root)) {
        return .{
            .node_count = 0,
            .flags = EMPTY_FLAG,
            .first_addr = 0,
            .last_addr = 0,
        };
    }

    var flags: u32 = 0;
    if (root.node.?.color == .black) flags |= ROOT_BLACK_FLAG;

    const first = rbtree.first(root).?;
    const last = rbtree.last(root).?;
    const count = countBounded(root, max_nodes);
    if (max_nodes != 0 and count == max_nodes and !containsNode(root, last, max_nodes)) {
        flags |= TRUNCATED_FLAG;
    }

    return .{
        .node_count = count,
        .flags = flags,
        .first_addr = @intFromPtr(first),
        .last_addr = @intFromPtr(last),
    };
}

test "phase3 rbtree view summarizes ordered traversal" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
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
    var root = rbtree.Root.init();
    for (&entries) |*entry| rbtree.add(&entry.node, &root, less);

    const summary = summarize(&root, 8);
    try std.testing.expectEqual(@as(u32, 4), summary.node_count);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&entries[2].node)), summary.first_addr);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&entries[1].node)), summary.last_addr);
    try std.testing.expect((summary.flags & ROOT_BLACK_FLAG) != 0);
    try std.testing.expect((summary.flags & TRUNCATED_FLAG) == 0);
}

test "phase3 rbtree view marks bounded traversal as truncated" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 8 },
        .{ .key = 4 },
        .{ .key = 12 },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| rbtree.add(&entry.node, &root, less);

    const summary = summarize(&root, 2);
    try std.testing.expectEqual(@as(u32, 2), summary.node_count);
    try std.testing.expect((summary.flags & TRUNCATED_FLAG) != 0);
}

test "phase3 rbtree view keeps empty roots explicit" {
    var root = rbtree.Root.init();
    const summary = summarize(&root, 4);

    try std.testing.expect(isEmpty(&root));
    try std.testing.expectEqual(@as(u32, 0), summary.node_count);
    try std.testing.expectEqual(@as(usize, 0), summary.first_addr);
    try std.testing.expectEqual(@as(usize, 0), summary.last_addr);
    try std.testing.expectEqual(@as(u32, EMPTY_FLAG), summary.flags);
}
