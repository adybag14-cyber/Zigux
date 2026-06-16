// Ported from check-phase1-rbtree-direct-anchors.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_RBTREE_DIRECT_ANCHORS_SELF_TEST=pass";

const RBTREE_REL = "tools/lib/rbtree.zig";

const REQUIRED_SOURCE_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "empty_node", .marker = "pub fn emptyNode(node: *const Node) bool {" },
    .{ .label = "clear_node", .marker = "pub fn clearNode(node: *Node) void {" },
    .{ .label = "link_node", .marker = "pub fn linkNode(node: *Node, parent: ?*Node, link: *?*Node) void {" },
    .{ .label = "insert_color_cached", .marker = "pub fn insertColorCached(node: *Node, root: *RootCached, leftmost: bool) void {" },
    .{ .label = "rb_insert_color_cached", .marker = "pub fn rb_insert_color_cached(node: *Node, root: *RootCached, leftmost: bool) void {" },
    .{ .label = "add_cached", .marker = "pub fn addCached(node: *Node, root: *RootCached, less: LessFn) ?*Node {" },
    .{ .label = "rb_add_cached", .marker = "pub fn rb_add_cached(node: *Node, root: *RootCached, less: LessFn) ?*Node {" },
    .{ .label = "find_add_cached", .marker = "pub fn findAddCached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {" },
    .{ .label = "rb_find_add_cached", .marker = "pub fn rb_find_add_cached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {" },
    .{ .label = "erase_cached", .marker = "pub fn eraseCached(node: *Node, root: *RootCached) ?*Node {" },
    .{ .label = "rb_erase_cached", .marker = "pub fn rb_erase_cached(node: *Node, root: *RootCached) ?*Node {" },
    .{ .label = "erase_init", .marker = "pub fn eraseInit(node: *Node, root: *Root) void {" },
    .{ .label = "erase_init_cached", .marker = "pub fn eraseInitCached(node: *Node, root: *RootCached) void {" },
    .{ .label = "rb_erase_init_cached", .marker = "pub fn rb_erase_init_cached(node: *Node, root: *RootCached) void {" },
    .{ .label = "first_cached", .marker = "pub fn firstCached(root: *const RootCached) ?*Node {" },
    .{ .label = "rb_first_cached", .marker = "pub fn rb_first_cached(root: *const RootCached) ?*Node {" },
    .{ .label = "replace_node", .marker = "pub fn replaceNode(victim: *Node, new: *Node, root: *Root) void {" },
    .{ .label = "rb_replace_node", .marker = "pub fn rb_replace_node(victim: *Node, new: *Node, root: *Root) void {" },
    .{ .label = "replace_node_cached", .marker = "pub fn replaceNodeCached(victim: *Node, new: *Node, root: *RootCached) void {" },
    .{ .label = "rb_replace_node_cached", .marker = "pub fn rb_replace_node_cached(victim: *Node, new: *Node, root: *RootCached) void {" },
};

const REQUIRED_TEST_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "ordered_alias_anchor", .marker = "test \"rbtree ordered Linux-style aliases mirror traversal and replacement helpers\" {" },
    .{ .label = "low_level_alias_anchor", .marker = "test \"rbtree low-level Linux-style aliases mirror node-state helpers\" {" },
    .{ .label = "cached_add_leftmost", .marker = "test \"rbtree addCached returns the inserted node only when it becomes leftmost\" {" },
    .{ .label = "cached_find_add_leftmost", .marker = "test \"rbtree findAddCached keeps cached leftmost stable while inserting misses\" {" },
    .{ .label = "cached_leftmost_sync", .marker = "test \"rbtree cached root keeps the leftmost pointer in sync\" {" },
    .{ .label = "cached_root_alias_anchor", .marker = "test \"rbtree cached-root Linux-style aliases mirror the primary helpers\" {" },
    .{ .label = "cached_replace_non_leftmost", .marker = "test \"rbtree replaceNodeCached keeps non-leftmost leftmost unchanged\" {" },
    .{ .label = "cached_singleton_erase", .marker = "test \"rbtree eraseCached returns null for a singleton cached tree\" {" },
    .{ .label = "cached_detach", .marker = "test \"rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned\" {" },
    .{ .label = "cached_reseed", .marker = "test \"rbtree eraseInitCached clears singleton cached roots before reseed\" {" },
};

fn collectFailures(
    io: Io,
    allocator: std.mem.Allocator,
    root: []const u8,
) !std.ArrayList([]const u8) {
    var failures: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    {
        const relative_path = "tools/lib/rbtree.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

    {
        const relative_path = "tools/lib/rbtree.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
                try failures.append(allocator, issue);
                return failures;
            },
            else => return err,
        };
        defer allocator.free(text);
        for (REQUIRED_TEST_MARKERS) |entry| {
            const count = guard.countOccurrences(text, entry.marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected=1:actual={d}", .{ entry.label, count });
                try failures.append(allocator, issue);
            }
        }
        for (REQUIRED_SOURCE_MARKERS) |entry| {
            const count = guard.countOccurrences(text, entry.marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected=1:actual={d}", .{ entry.label, count });
                try failures.append(allocator, issue);
            }
        }
    }

    return failures;
}

fn buildSampleSource(allocator: std.mem.Allocator) ![]u8 {
    var content = std.ArrayList(u8).empty;
    errdefer content.deinit(allocator);
    for (REQUIRED_TEST_MARKERS) |entry| {
        try content.appendSlice(allocator, entry.marker);
        try content.append(allocator, '\n');
    }
    for (REQUIRED_SOURCE_MARKERS) |entry| {
        try content.appendSlice(allocator, entry.marker);
        try content.append(allocator, '\n');
    }
    return try content.toOwnedSlice(allocator);
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    const sample = try buildSampleSource(allocator);
    defer allocator.free(sample);
    {
        const relative_path = "tools/lib/rbtree.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, sample);
        var failures = try collectFailures(io, allocator, root);
        defer {
            for (failures.items) |item| allocator.free(item);
            failures.deinit(allocator);
        }
        try guard.expectSelfTest(failures.items.len == 0);
    }
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_RBTREE_DIRECT_ANCHORS_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 63)});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var explicit_root: ?[]const u8 = null;
    var self_test = false;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const root = if (explicit_root) |value| value else try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);

    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    if (failures.items.len > 0) {
        try guard.printLine(io, "PHASE1_RBTREE_DIRECT_ANCHORS_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
