const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_RBTREE_OWNERSHIP_FOCUS=pass";
pub const self_test_pass_marker = "PHASE7_RBTREE_OWNERSHIP_FOCUS_SELF_TEST=pass";

const REQUIRED_MARKERS__zigux_tests_phase7_rbtree_manifest_json = [_][]const u8{
    "\"linked-node teardown reconnects prev and next ownership together with leftmost continuity during eraseLinked()\"",
    "\"replaceNode() copies victim links onto replacement nodes before reconnecting parent and child ownership\"",
    "\"postorder traversal helpers treat cleared detached nodes as empty so stale parent walks do not leak past the reusable leaf packet\"",
};

const REQUIRED_MARKERS__lib_rbtree_zig = [_][]const u8{
    "pub fn eraseLinked(node: *NodeLinked, root: *RootLinked) bool {",
    "prev_link.next = node.next;",
    "root.leftmost = node.next;",
    "next_link.prev = node.prev;",
    "clearLinkedNode(node);",
    "test \"rbtree linked helpers track leftmost and neighbour links\" {",
    "try std.testing.expectEqual(@as(?*NodeLinked, &entries[2].linked), root.leftmost);",
    "try std.testing.expectEqual(@as(?*NodeLinked, &entries[0].linked), entries[2].linked.next);",
    "try std.testing.expectEqual(@as(?*NodeLinked, &entries[2].linked), entries[0].linked.prev);",
    "pub fn replaceNode(victim: *Node, new: *Node, root: *Root) void {",
    "new.* = victim.*;",
    "left.parent = new;",
    "right.parent = new;",
    "pub fn replaceNodeCached(victim: *Node, new: *Node, root: *RootCached) void {",
    "if (root.leftmost == victim) {",
    "root.leftmost = new;",
    "test \"rbtree replaceNode copies victim links over dirty replacement nodes\" {",
    "try std.testing.expectEqual(@as(?*Node, &replacement.node), prev(&root_entry.node));",
    "try std.testing.expectEqual(@as(?*Node, &root_entry.node), next(&replacement.node));",
    "test \"rbtree replaceNodeCached keeps singleton cached roots aligned over dirty replacement nodes\" {",
    "pub fn firstPostorder(root: *const Root) ?*Node {",
    "pub fn nextPostorder(node: ?*const Node) ?*Node {",
    "if (emptyNode(current)) {",
    "return leftDeepestNode(parent.?.right.?);",
    "return parent;",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers__zigux_tests_phase7_rbtree_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_rbtree_manifest.json");
    defer allocator.free(text_required_markers__zigux_tests_phase7_rbtree_manifest_json_path);
    const text_required_markers__zigux_tests_phase7_rbtree_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_rbtree_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_rbtree_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_phase7_rbtree_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_rbtree_manifest_json, marker);
    const text_required_markers__lib_rbtree_zig_path = try guard.joinPath(allocator, root, "lib/rbtree.zig");
    defer allocator.free(text_required_markers__lib_rbtree_zig_path);
    const text_required_markers__lib_rbtree_zig = try guard.readUtf8File(io, allocator, text_required_markers__lib_rbtree_zig_path);
    defer allocator.free(text_required_markers__lib_rbtree_zig);
    for (REQUIRED_MARKERS__lib_rbtree_zig) |marker| try guard.requireMarker(text_required_markers__lib_rbtree_zig, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
