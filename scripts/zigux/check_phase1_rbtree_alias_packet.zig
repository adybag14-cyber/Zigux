// Ported from check-phase1-rbtree-alias-packet.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_RBTREE_ALIAS_PACKET_SELF_TEST=pass";

const EXPECTED_RBTREE_SOURCE_SYMBOLS = [_][]const u8{
    "pub fn rb_add_cached(node: *Node, root: *RootCached, less: LessFn) ?*Node {",
    "pub fn rb_find_add(node: *Node, root: *Root, cmp: CmpNodeFn) ?*Node {",
    "pub fn rb_find_add_cached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {",
    "pub fn rb_find(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) ?*Node {",
    "pub fn rb_find_first(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) ?*Node {",
    "pub fn rb_next_match(key: *const anyopaque, node: *const Node, cmp: CmpKeyFn) ?*Node {",
    "pub fn rb_match_iterator(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) MatchIterator {",
    "pub fn rb_insert_color_cached(node: *Node, root: *RootCached, leftmost: bool) void {",
    "pub fn rb_erase_cached(node: *Node, root: *RootCached) ?*Node {",
    "pub fn rb_erase_init_cached(node: *Node, root: *RootCached) void {",
    "pub fn rb_first(root: *const Root) ?*Node {",
    "pub fn rb_first_cached(root: *const RootCached) ?*Node {",
    "pub fn rb_last(root: *const Root) ?*Node {",
    "pub fn rb_next(node: *const Node) ?*Node {",
    "pub fn rb_prev(node: *const Node) ?*Node {",
    "pub fn rb_replace_node(victim: *Node, new: *Node, root: *Root) void {",
    "pub fn rb_replace_node_cached(victim: *Node, new: *Node, root: *RootCached) void {",
    "pub fn rb_first_postorder(root: *const Root) ?*Node {",
    "pub fn rb_next_postorder(node: ?*const Node) ?*Node {",
};

const LANE_NOTE_REL = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";

const LIST_FIELDS = [_][]const u8{
    "helper_test_anchors",
    "parity_fixture_keys",
    "cached_leftmost_fixture_keys",
    "traversal_replay_keys",
    "duplicate_search_replay_keys",
    "duplicate_search_anchors",
    "cached_root_followup_anchors",
};

const MANIFEST_REL = "zigux/tests/fixtures/phase1_helper_manifest.json";

const RBTREE_DIRECT_OWNER_LINE = "- `PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors helper-local while the committed shared replay already owns duplicate-search parity through find(), findFirst(), nextMatch(), and matchIterator() plus the parked cached_leftmost_return_serials witness`";

const RBTREE_HELPER_REL = "tools/lib/rbtree.zig";

const RBTREE_NEXT_SAFE_STEP_LINE = "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`";

const SCALAR_FIELDS = [_][]const u8{
    "phase1_helper_replay_anchor",
    "shared_replay_summary",
    "cached_root_direct_review_summary",
    "ordered_alias_anchor",
    "low_level_alias_anchor",
    "cached_root_alias_anchor",
    "review_packet_summary",
    "next_safe_step_note",
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
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

    {
        const relative_path = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";
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
        const marker = "- `PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors helper-local while the committed shared replay already owns duplicate-search parity through find(), findFirst(), nextMatch(), and matchIterator() plus the parked cached_leftmost_return_serials witness`";
        const count = guard.countOccurrences(text, marker);
        if (count != 1) {
            const issue = try std.fmt.allocPrint(allocator, "lane_note:rbtree_direct_owner:expected=1:actual={d}", .{count});
            try failures.append(allocator, issue);
        }
    }

    {
        const relative_path = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";
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
        const marker = "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`";
        const count = guard.countOccurrences(text, marker);
        if (count != 1) {
            const issue = try std.fmt.allocPrint(allocator, "lane_note:rbtree_next_safe_step:expected=1:actual={d}", .{count});
            try failures.append(allocator, issue);
        }
    }

    return failures;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    {
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, "\n");
    }
    {
        const relative_path = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, "\n");
    }
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    try guard.expectSelfTest(failures.items.len == 0);
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_RBTREE_ALIAS_PACKET_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_RBTREE_ALIAS_PACKET_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
