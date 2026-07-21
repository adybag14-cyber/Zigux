const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_RBTREE_STARTER_PACKET=pass";
pub const self_test_pass_marker = "PHASE3_RBTREE_STARTER_PACKET_SELF_TEST=pass";

const CURRENT_NEXT_SAFE_STEP = [_][]const u8{
    "keep the helper-local rbtree starter packet aligned with its checker and focused build replay without widening into mutation or shared ABI catalog work",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-rbtree-slice_md = [_][]const u8{
    "# Phase 3 rbtree Slice",
    "- `zigux/helpers/rbtree_view.zig`",
    "- `zigux/tests/phase3_rbtree_starter_packet.zig`",
    "This packet stays intentionally small:",
    "inorder successor, inorder predecessor, and empty-root decoding explicit",
    "leftmost/rightmost traversal, and inorder successor/predecessor traversal visible",
    "child-subtree descent, and empty-root decoding explicit",
    "child-subtree successor/predecessor descent visible",
};

const REQUIRED_MARKERS__zigux_helpers_rbtree_view_zig = [_][]const u8{
    "pub const Color = enum(u1) {",
    "pub const RBNode = extern struct {",
    "pub fn parent(self: *const RBNode) ?*const RBNode {",
    "pub fn color(self: *const RBNode) Color {",
    "pub fn parentTagBits(self: *const RBNode) usize {",
    "pub const RBTreeView = struct {",
    "pub fn leftmost(self: RBTreeView) ?*const RBNode {",
    "pub fn rightmost(self: RBTreeView) ?*const RBNode {",
    "pub fn next(self: *const RBNode) ?*const RBNode {",
    "pub fn prev(self: *const RBNode) ?*const RBNode {",
    "test \"rbtree view treats a null root as empty\" {",
    "test \"rbtree view decodes parent pointers without losing the color bit\" {",
    "test \"rbtree view walks inorder successors across a bounded tree\" {",
    "test \"rbtree view walks inorder predecessors across a bounded tree\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_rbtree_starter_packet_zig = [_][]const u8{
    "test \"rbtree view keeps empty roots explicit\" {",
    "test \"rbtree view preserves root color without inventing a parent\" {",
    "test \"rbtree view keeps parent pointers and black color bits aligned\" {",
    "test \"rbtree view keeps leftmost and rightmost traversal reviewable\" {",
    "test \"rbtree view keeps inorder successors reviewable\" {",
    "test \"rbtree view keeps inorder predecessors reviewable\" {",
    "test \"rbtree view descends into the right subtree for the next inorder node\" {",
    "test \"rbtree view descends into the left subtree for the previous inorder node\" {",
    "try testing.expectEqual(@as(usize, 0x1), child.parentTagBits());",
    "try testing.expectEqual(@as(?*const rbtree_view.RBNode, &root_node), left.next());",
    "try testing.expectEqual(@as(?*const rbtree_view.RBNode, &root_node), right.prev());",
    "try testing.expectEqual(@as(?*const rbtree_view.RBNode, &right_left), root_node.next());",
    "try testing.expectEqual(@as(?*const rbtree_view.RBNode, &left_right), root_node.prev());",
};

const REQUIRED_MARKERS__zigux_tests_phase3_rbtree_starter_packet_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/rbtree_view.zig\"),",
    ".root_source_file = b.path(\"phase3_rbtree_starter_packet.zig\"),",
    "root_module.addImport(\"rbtree_view\", rbtree_view);",
    "\"phase3-rbtree-starter-packet-test\"",
};

const REQUIRED_REPLAY_ROUTES = [_][]const u8{
    "zig run scripts\\zigux/check_phase3_rbtree_starter_packet.zig -- --self-test",
    "zig run scripts\\zigux/check_phase3_rbtree_starter_packet.zig -- --repo-root .",
    "zig build phase3-rbtree-starter-packet-test --build-file zigux/tests/phase3_rbtree_starter_packet_build.zig",
};

const SELF_TEST_CASES = [_][]const u8{
    "pub const RBTreeView = struct {",
    "test \"rbtree view keeps inorder successors reviewable\" {",
    "test \"rbtree view keeps inorder predecessors reviewable\" {",
    "test \"rbtree view descends into the right subtree for the next inorder node\" {",
    "test \"rbtree view descends into the left subtree for the previous inorder node\" {",
    "\"phase3-rbtree-starter-packet-test\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_current_next_safe_step_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-rbtree-slice.md");
    defer allocator.free(text_current_next_safe_step_path);
    const text_current_next_safe_step = try guard.readUtf8File(io, allocator, text_current_next_safe_step_path);
    defer allocator.free(text_current_next_safe_step);
    for (CURRENT_NEXT_SAFE_STEP) |marker| try guard.requireMarker(text_current_next_safe_step, marker);
    const text_required_markers__documentation_zigux_phase3-rbtree-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-rbtree-slice/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-rbtree-slice_md_path);
    const text_required_markers__documentation_zigux_phase3-rbtree-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-rbtree-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-rbtree-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-rbtree-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-rbtree-slice_md, marker);
    const text_required_markers__zigux_helpers_rbtree_view_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/rbtree/view/zig");
    defer allocator.free(text_required_markers__zigux_helpers_rbtree_view_zig_path);
    const text_required_markers__zigux_helpers_rbtree_view_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_rbtree_view_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_rbtree_view_zig);
    for (REQUIRED_MARKERS__zigux_helpers_rbtree_view_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_rbtree_view_zig, marker);
    const text_required_markers__zigux_tests_phase3_rbtree_starter_packet_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/rbtree/starter/packet/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_rbtree_starter_packet_zig_path);
    const text_required_markers__zigux_tests_phase3_rbtree_starter_packet_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_rbtree_starter_packet_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_rbtree_starter_packet_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_rbtree_starter_packet_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_rbtree_starter_packet_zig, marker);
    const text_required_markers__zigux_tests_phase3_rbtree_starter_packet_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/rbtree/starter/packet/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_rbtree_starter_packet_build_zig_path);
    const text_required_markers__zigux_tests_phase3_rbtree_starter_packet_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_rbtree_starter_packet_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_rbtree_starter_packet_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_rbtree_starter_packet_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_rbtree_starter_packet_build_zig, marker);
    const text_required_replay_routes_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-rbtree-slice.md");
    defer allocator.free(text_required_replay_routes_path);
    const text_required_replay_routes = try guard.readUtf8File(io, allocator, text_required_replay_routes_path);
    defer allocator.free(text_required_replay_routes);
    for (REQUIRED_REPLAY_ROUTES) |marker| try guard.requireMarker(text_required_replay_routes, marker);
    const text_self_test_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_self_test_cases_path);
    const text_self_test_cases = try guard.readUtf8File(io, allocator, text_self_test_cases_path);
    defer allocator.free(text_self_test_cases);
    for (SELF_TEST_CASES) |marker| try guard.requireMarker(text_self_test_cases, marker);
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
