const std = @import("std");
const testing = std.testing;

const rbtree_view = @import("rbtree_view");

test "rbtree view keeps empty roots explicit" {
    const root = rbtree_view.RBRoot{ .rb_node = 0 };
    const view = rbtree_view.RBTreeView.init(&root);

    try testing.expect(view.isEmpty());
    try testing.expectEqual(@as(?*const rbtree_view.RBNode, null), view.rootNode());
}

test "rbtree view preserves root color without inventing a parent" {
    var node = rbtree_view.RBNode{
        .__rb_parent_color = @intFromEnum(rbtree_view.Color.red),
        .rb_right = 0,
        .rb_left = 0,
    };
    const root = rbtree_view.RBRoot{ .rb_node = @intFromPtr(&node) };
    const view = rbtree_view.RBTreeView.init(&root);

    try testing.expectEqual(@as(?*const rbtree_view.RBNode, &node), view.rootNode());
    try testing.expectEqual(rbtree_view.Color.red, node.color());
    try testing.expectEqual(@as(?*const rbtree_view.RBNode, null), node.parent());
}

test "rbtree view keeps parent pointers and black color bits aligned" {
    var parent = rbtree_view.RBNode{
        .__rb_parent_color = @intFromEnum(rbtree_view.Color.black),
        .rb_right = 0,
        .rb_left = 0,
    };
    var child = rbtree_view.RBNode{
        .__rb_parent_color = @intFromPtr(&parent) | @intFromEnum(rbtree_view.Color.black),
        .rb_right = 0,
        .rb_left = 0,
    };

    try testing.expectEqual(@as(?*const rbtree_view.RBNode, &parent), child.parent());
    try testing.expectEqual(rbtree_view.Color.black, child.color());
    try testing.expect(child.isBlack());
    try testing.expectEqual(@as(usize, 0x1), child.parentTagBits());
}

test "rbtree view keeps leftmost and rightmost traversal reviewable" {
    var root_node = rbtree_view.RBNode{
        .__rb_parent_color = @intFromEnum(rbtree_view.Color.black),
        .rb_right = 0,
        .rb_left = 0,
    };
    var left = rbtree_view.RBNode{
        .__rb_parent_color = @intFromPtr(&root_node) | @intFromEnum(rbtree_view.Color.red),
        .rb_right = 0,
        .rb_left = 0,
    };
    var right = rbtree_view.RBNode{
        .__rb_parent_color = @intFromPtr(&root_node) | @intFromEnum(rbtree_view.Color.red),
        .rb_right = 0,
        .rb_left = 0,
    };

    root_node.rb_left = @intFromPtr(&left);
    root_node.rb_right = @intFromPtr(&right);

    const root = rbtree_view.RBRoot{ .rb_node = @intFromPtr(&root_node) };
    const view = rbtree_view.RBTreeView.init(&root);

    try testing.expectEqual(@as(?*const rbtree_view.RBNode, &left), view.leftmost());
    try testing.expectEqual(@as(?*const rbtree_view.RBNode, &right), view.rightmost());
}

test "rbtree view keeps inorder successors reviewable" {
    var root_node = rbtree_view.RBNode{
        .__rb_parent_color = @intFromEnum(rbtree_view.Color.black),
        .rb_right = 0,
        .rb_left = 0,
    };
    var left = rbtree_view.RBNode{
        .__rb_parent_color = @intFromPtr(&root_node) | @intFromEnum(rbtree_view.Color.red),
        .rb_right = 0,
        .rb_left = 0,
    };
    var right = rbtree_view.RBNode{
        .__rb_parent_color = @intFromPtr(&root_node) | @intFromEnum(rbtree_view.Color.red),
        .rb_right = 0,
        .rb_left = 0,
    };

    root_node.rb_left = @intFromPtr(&left);
    root_node.rb_right = @intFromPtr(&right);

    try testing.expectEqual(@as(?*const rbtree_view.RBNode, &root_node), left.next());
    try testing.expectEqual(@as(?*const rbtree_view.RBNode, &right), root_node.next());
    try testing.expectEqual(@as(?*const rbtree_view.RBNode, null), right.next());
}

test "rbtree view keeps inorder predecessors reviewable" {
    var root_node = rbtree_view.RBNode{
        .__rb_parent_color = @intFromEnum(rbtree_view.Color.black),
        .rb_right = 0,
        .rb_left = 0,
    };
    var left = rbtree_view.RBNode{
        .__rb_parent_color = @intFromPtr(&root_node) | @intFromEnum(rbtree_view.Color.red),
        .rb_right = 0,
        .rb_left = 0,
    };
    var right = rbtree_view.RBNode{
        .__rb_parent_color = @intFromPtr(&root_node) | @intFromEnum(rbtree_view.Color.red),
        .rb_right = 0,
        .rb_left = 0,
    };

    root_node.rb_left = @intFromPtr(&left);
    root_node.rb_right = @intFromPtr(&right);

    try testing.expectEqual(@as(?*const rbtree_view.RBNode, null), left.prev());
    try testing.expectEqual(@as(?*const rbtree_view.RBNode, &left), root_node.prev());
    try testing.expectEqual(@as(?*const rbtree_view.RBNode, &root_node), right.prev());
}
