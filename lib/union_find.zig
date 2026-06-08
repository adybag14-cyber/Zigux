// SPDX-License-Identifier: GPL-2.0
const std = @import("std");

pub const UfNode = struct {
    parent: *UfNode,
    rank: u32,
};

pub fn init(node: *UfNode) void {
    node.* = .{ .parent = node, .rank = 0 };
}

pub fn ufFind(node: *UfNode) *UfNode {
    var cur = node;
    while (cur.parent != cur) {
        cur.parent = cur.parent.parent;
        cur = cur.parent;
    }
    return cur;
}

pub fn ufUnion(node1: *UfNode, node2: *UfNode) void {
    const root1 = ufFind(node1);
    const root2 = ufFind(node2);

    if (root1 == root2) return;

    if (root1.rank < root2.rank) {
        root1.parent = root2;
    } else if (root1.rank > root2.rank) {
        root2.parent = root1;
    } else {
        root2.parent = root1;
        root1.rank += 1;
    }
}

pub const uf_find = ufFind;
pub const uf_union = ufUnion;

test "union find compresses parent pointers" {
    var root: UfNode = undefined;
    var mid: UfNode = undefined;
    var leaf: UfNode = undefined;

    init(&root);
    init(&mid);
    init(&leaf);

    mid.parent = &root;
    leaf.parent = &mid;

    try std.testing.expect(ufFind(&leaf) == &root);
    try std.testing.expect(leaf.parent == &root);
}

test "union find equal rank union attaches second root to first" {
    var a: UfNode = undefined;
    var b: UfNode = undefined;

    init(&a);
    init(&b);
    ufUnion(&a, &b);

    try std.testing.expect(a.parent == &a);
    try std.testing.expect(b.parent == &a);
    try std.testing.expectEqual(@as(u32, 1), a.rank);
    try std.testing.expectEqual(@as(u32, 0), b.rank);
}

test "union find repeated union is a no-op" {
    var a: UfNode = undefined;
    var b: UfNode = undefined;

    init(&a);
    init(&b);
    ufUnion(&a, &b);
    const rank_after_first = a.rank;

    ufUnion(&a, &b);
    ufUnion(&b, &a);

    try std.testing.expect(a.parent == &a);
    try std.testing.expect(b.parent == &a);
    try std.testing.expectEqual(rank_after_first, a.rank);
}
