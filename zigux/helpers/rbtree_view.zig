const std = @import("std");

fn ptrFromRaw(raw: usize) ?*const RBNode {
    const aligned = raw & ~@as(usize, 0x3);
    if (aligned == 0) return null;
    return @ptrFromInt(aligned);
}

pub const Color = enum(u1) {
    red = 0,
    black = 1,
};

pub const RBNode = extern struct {
    __rb_parent_color: usize,
    rb_right: usize,
    rb_left: usize,

    pub fn parent(self: *const RBNode) ?*const RBNode {
        return ptrFromRaw(self.__rb_parent_color);
    }

    pub fn color(self: *const RBNode) Color {
        return @enumFromInt(@as(u1, @truncate(self.__rb_parent_color & 0x1)));
    }

    pub fn isRed(self: *const RBNode) bool {
        return self.color() == .red;
    }

    pub fn isBlack(self: *const RBNode) bool {
        return self.color() == .black;
    }

    pub fn parentTagBits(self: *const RBNode) usize {
        return self.__rb_parent_color & 0x3;
    }

    pub fn left(self: *const RBNode) ?*const RBNode {
        return ptrFromRaw(self.rb_left);
    }

    pub fn right(self: *const RBNode) ?*const RBNode {
        return ptrFromRaw(self.rb_right);
    }
};

pub const RBRoot = extern struct {
    rb_node: usize,
};

pub const RBTreeView = struct {
    root: *const RBRoot,

    pub fn init(root: *const RBRoot) RBTreeView {
        return .{ .root = root };
    }

    pub fn isEmpty(self: RBTreeView) bool {
        return self.root.rb_node == 0;
    }

    pub fn rootNode(self: RBTreeView) ?*const RBNode {
        return ptrFromRaw(self.root.rb_node);
    }

    pub fn leftmost(self: RBTreeView) ?*const RBNode {
        var cursor = self.rootNode() orelse return null;
        while (cursor.left()) |child| {
            cursor = child;
        }
        return cursor;
    }

    pub fn rightmost(self: RBTreeView) ?*const RBNode {
        var cursor = self.rootNode() orelse return null;
        while (cursor.right()) |child| {
            cursor = child;
        }
        return cursor;
    }
};

test "rbtree view treats a null root as empty" {
    const root = RBRoot{ .rb_node = 0 };
    const view = RBTreeView.init(&root);

    try std.testing.expect(view.isEmpty());
    try std.testing.expectEqual(@as(?*const RBNode, null), view.rootNode());
    try std.testing.expectEqual(@as(?*const RBNode, null), view.leftmost());
    try std.testing.expectEqual(@as(?*const RBNode, null), view.rightmost());
}

test "rbtree view keeps root color and missing parent explicit" {
    var node = RBNode{
        .__rb_parent_color = @intFromEnum(Color.red),
        .rb_right = 0,
        .rb_left = 0,
    };
    const root = RBRoot{ .rb_node = @intFromPtr(&node) };
    const view = RBTreeView.init(&root);

    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(?*const RBNode, &node), view.rootNode());
    try std.testing.expectEqual(Color.red, node.color());
    try std.testing.expect(node.isRed());
    try std.testing.expect(!node.isBlack());
    try std.testing.expectEqual(@as(?*const RBNode, null), node.parent());
}

test "rbtree view decodes parent pointers without losing the color bit" {
    var parent = RBNode{
        .__rb_parent_color = @intFromEnum(Color.black),
        .rb_right = 0,
        .rb_left = 0,
    };
    var child = RBNode{
        .__rb_parent_color = @intFromPtr(&parent) | @intFromEnum(Color.black),
        .rb_right = 0,
        .rb_left = 0,
    };

    try std.testing.expectEqual(@as(?*const RBNode, &parent), child.parent());
    try std.testing.expectEqual(Color.black, child.color());
    try std.testing.expect(child.isBlack());
    try std.testing.expectEqual(@as(usize, 0x1), child.parentTagBits());
}

test "rbtree view finds the leftmost and rightmost nodes of a bounded tree" {
    var root_node = RBNode{
        .__rb_parent_color = @intFromEnum(Color.black),
        .rb_right = 0,
        .rb_left = 0,
    };
    var left = RBNode{
        .__rb_parent_color = @intFromPtr(&root_node) | @intFromEnum(Color.red),
        .rb_right = 0,
        .rb_left = 0,
    };
    var right = RBNode{
        .__rb_parent_color = @intFromPtr(&root_node) | @intFromEnum(Color.red),
        .rb_right = 0,
        .rb_left = 0,
    };

    root_node.rb_left = @intFromPtr(&left);
    root_node.rb_right = @intFromPtr(&right);

    const root = RBRoot{ .rb_node = @intFromPtr(&root_node) };
    const view = RBTreeView.init(&root);

    try std.testing.expectEqual(@as(?*const RBNode, &left), view.leftmost());
    try std.testing.expectEqual(@as(?*const RBNode, &right), view.rightmost());
}
