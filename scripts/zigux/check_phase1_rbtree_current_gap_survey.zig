// Ported from check-phase1-rbtree-current-gap-survey.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_RBTREE_CURRENT_GAP_SURVEY.PY_SELF_TEST=pass";

const MISSING_ALIAS_MARKERS = [_][]const u8{
    "pub fn rb_link_node(",
    "pub fn rb_insert_color(node: *Node, root: *Root) void {",
    "pub fn rb_erase(node: *Node, root: *Root) void {",
    "pub fn rb_erase_init(node: *Node, root: *Root) void {",
};
const REQUIRED_HELPER_MARKERS = [_][]const u8{
    "pub fn rb_add(node: *Node, root: *Root, less: LessFn) void {",
    "pub fn rb_find_add(node: *Node, root: *Root, cmp: CmpNodeFn) ?*Node {",
    "pub fn rb_replace_node(victim: *Node, new: *Node, root: *Root) void {",
    "pub fn rb_insert_color_cached(node: *Node, root: *RootCached, leftmost: bool) void {",
    "pub fn rb_erase_cached(node: *Node, root: *RootCached) ?*Node {",
    "pub fn rb_erase_init_cached(node: *Node, root: *RootCached) void {",
    "test \"rbtree ordered Linux-style aliases mirror traversal and replacement helpers\"",
    "test \"rbtree cached-root Linux-style aliases mirror the primary helpers\"",
};
const REQUIRED_SURVEY_MARKERS = [_][]const u8{
    "PHASE1_RBTREE_CURRENT_SURVEY_STATUS=helper_gap_open",
    "PHASE1_RBTREE_CURRENT_HELPER_BLOB=b8cc3d811028922be412f40cfddfd8da82ea6d8c",
    "PHASE1_RBTREE_MISSING_LOW_LEVEL_ALIASES=rb_link_node,rb_insert_color,rb_erase,rb_erase_init",
    "PHASE1_RBTREE_MISSING_TEST_ANCHOR=test \"rbtree low-level Linux-style aliases mirror node-state helpers\"",
    "PHASE1_RBTREE_EXISTING_HELPER_ANCHORS=ordered_linux_style_aliases,cached_root_aliases,cached_root_insert_miss,leftmost_sync,singleton_erase,replacement,detach,reseed",
    "PHASE1_RBTREE_NEXT_BOUNDED_STEP=apply the already-scoped non-cached low-level alias helper patch for rb_link_node, rb_insert_color, rb_erase, and rb_erase_init plus the direct low-level alias test once a trustworthy patch-capable current-head write path is available; otherwise keep this survey and its checker aligned with current helper reality",
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

    const helper_rel = "tools/lib/rbtree.zig";
    const survey_rel = "Documentation/zigux/phase1-rbtree-current-gap-survey.md";
    const helper_path = try guard.joinPath(allocator, root, helper_rel);
    defer allocator.free(helper_path);
    const survey_path = try guard.joinPath(allocator, root, survey_rel);
    defer allocator.free(survey_path);

    var helper_text_owned: ?[]u8 = null;
    defer if (helper_text_owned) |owned| allocator.free(owned);
    var survey_text_owned: ?[]u8 = null;
    defer if (survey_text_owned) |owned| allocator.free(owned);

    if (!guard.pathExists(io, helper_path)) {
        const issue = try std.fmt.allocPrint(allocator, "missing:{s}", .{helper_rel});
        try failures.append(allocator, issue);
    } else {
        helper_text_owned = try guard.readUtf8File(io, allocator, helper_path);
    }
    if (!guard.pathExists(io, survey_path)) {
        const issue = try std.fmt.allocPrint(allocator, "missing:{s}", .{survey_rel});
        try failures.append(allocator, issue);
    } else {
        survey_text_owned = try guard.readUtf8File(io, allocator, survey_path);
    }

    const helper_text = helper_text_owned orelse "";
    const survey_text = survey_text_owned orelse "";

    for (REQUIRED_HELPER_MARKERS) |marker| {
        const count = guard.countOccurrences(helper_text, marker);
        if (count != 1) {
            const issue = try std.fmt.allocPrint(allocator, "helper-marker-count:{s}:{d}", .{ marker, count });
            try failures.append(allocator, issue);
        }
    }
    for (MISSING_ALIAS_MARKERS) |marker| {
        if (std.mem.indexOf(u8, helper_text, marker) != null) {
            const issue = try std.fmt.allocPrint(allocator, "missing-alias-now-present:{s}", .{marker});
            try failures.append(allocator, issue);
        }
    }
    for (REQUIRED_SURVEY_MARKERS) |marker| {
        const count = guard.countOccurrences(survey_text, marker);
        if (count != 1) {
            const issue = try std.fmt.allocPrint(allocator, "survey-marker-count:{s}:{d}", .{ marker, count });
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
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    try guard.expectSelfTest(failures.items.len == 0);
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_GUARD_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "phase1-rbtree-current-gap-survey:ok", .{});
    std.process.exit(0);
}

