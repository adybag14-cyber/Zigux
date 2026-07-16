// Ported from check-phase1-rbtree-review-packet.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

const CLOSURE_NOTE_REL = "Documentation/zigux/phase1-closure.md";

const EXPECTED_CLOSURE_PARAGRAPH = "A second current helper-family tie-breaker inside that packet is the `rbtree` direct-anchor route: keep `tools/lib/rbtree.zig` parked unless a fresh reread finds drift in the helper-local ordered Linux-style alias proof, the dedicated manifest-backed `low_level_alias_anchor`, the dedicated manifest-backed `cached_root_alias_anchor`, the cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, or reseed anchors, or drift in the already-committed duplicate-search replay fields or exact `cached_leftmost_return_serials` witness. Current `master` still keeps both Linux-style alias proofs named explicitly in `zigux/tests/fixtures/phase1_helper_manifest.json`, while the shared host-tools smoke route and committed Phase 1 fixture already recheck duplicate-range iteration plus the exact cached-leftmost-return packet, so leave rbtree parked unless one of those helper-local anchors or committed replay fields drifts and do not batch a second cached-root widening into the same reopen step.";

const EXPECTED_DUPLICATE_SEARCH_ANCHORS = [_][]const u8{
    "test \"rbtree findAdd keeps the first duplicate and inserts new keys\"",
    "test \"rbtree nextMatch walks the duplicate range in order\"",
    "test \"rbtree matchIterator walks the duplicate range in order\"",
};

const EXPECTED_HELPER_TEST_ANCHORS = [_][]const u8{
    "test \"rbtree inserts and traverses in sorted order\"",
    "test \"rbtree erase and replace keep traversal consistent\"",
    "test \"rbtree ordered Linux-style aliases mirror traversal and replacement helpers\"",
    "test \"rbtree low-level Linux-style aliases mirror node-state helpers\"",
    "test \"rbtree eraseInit detaches erased node\"",
    "test \"rbtree eraseInit clears singleton roots before reseed\"",
    "test \"rbtree postorder and empty node helpers behave\"",
    "test \"rbtree findAdd keeps the first duplicate and inserts new keys\"",
    "test \"rbtree nextMatch walks the duplicate range in order\"",
    "test \"rbtree matchIterator walks the duplicate range in order\"",
    "test \"rbtree addCached returns the inserted node only when it becomes leftmost\"",
    "test \"rbtree findAddCached keeps cached leftmost stable while inserting misses\"",
    "test \"rbtree cached root keeps the leftmost pointer in sync\"",
    "test \"rbtree cached-root Linux-style aliases mirror the primary helpers\"",
    "test \"rbtree replaceNodeCached keeps non-leftmost leftmost unchanged\"",
    "test \"rbtree eraseCached returns null for a singleton cached tree\"",
    "test \"rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned\"",
    "test \"rbtree eraseInitCached clears singleton cached roots before reseed\"",
};

const EXPECTED_LANE_LINES = [_][]const u8{
    "- `PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors helper-local while the committed fixture still owns exact find(), findFirst(), nextMatch(), and matchIterator() duplicate-search fields and the shared host-tools smoke route keeps duplicate-range iteration plus the parked cached_leftmost_return_serials witness explicit`",
    "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local ordered Linux-style alias proof, dedicated low_level_alias_anchor, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`",
};

const EXPECTED_LANE_PARAGRAPH = "- `tools/lib/rbtree.zig` now keeps ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed coverage helper-local while the committed fixture still owns exact `find()`, `findFirst()`, `nextMatch()`, and `matchIterator()` duplicate-search fields and the shared host-tools smoke route already keeps duplicate-range iteration plus the parked `cached_leftmost_return_serials` witness explicit. The dedicated `low_level_alias_anchor` and `cached_root_alias_anchor` entries in `zigux/tests/fixtures/phase1_helper_manifest.json` keep both Linux-style alias proofs named explicitly inside that same helper-local packet instead of leaving either alias path implied only by the broader helper test list. Until another committed cached-root replay field lands, leave the remaining cached-root anchors helper-local and do not batch a second widening into the same reopen step.";

const EXPECTED_PARITY_FIXTURE_KEYS = [_][]const u8{
    "empty_root",
    "insert_order",
    "reverse_order",
    "replace_order",
    "erase_init_order",
    "postorder_count",
    "erase_init_node_empty",
    "cleared_node_empty",
    "find_found_key",
    "find_missing",
    "find_first_serial",
    "next_match_serials",
    "match_iterator_serials",
    "next_match_terminal_null",
};

const EXPECTED_SMOKE_MARKERS = [_][]const u8{
    "const rbtree = @import(\"rbtree\");",
    "try std.testing.expect(@hasDecl(rbtree, \"find\"));",
    "try std.testing.expect(@hasDecl(rbtree, \"matchIterator\"));",
    "const found_duplicate = rbtree.find(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp) orelse return error.TestUnexpectedResult;",
    "const first_duplicate = rbtree.findFirst(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp) orelse return error.TestUnexpectedResult;",
    "const second_duplicate = rbtree.nextMatch(&duplicate_key, first_duplicate, RbtreeSmokeEntry.cmp) orelse return error.TestUnexpectedResult;",
    "try std.testing.expect(rbtree.nextMatch(&duplicate_key, third_duplicate, RbtreeSmokeEntry.cmp) == null);",
    "var iter = rbtree.matchIterator(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp);",
    "var cached_leftmost_return_serials: [4]i32 = undefined;",
    "try std.testing.expectEqualSlices(i32, &.{ 0, -1, 2, -1 }, &cached_leftmost_return_serials);",
    "var cached_root_transition_serials: [4]i32 = undefined;",
    "try std.testing.expectEqualSlices(i32, &.{ 0, 0, 4, 2 }, &cached_root_transition_serials);",
};

const EXPECTED_SOURCE_SYMBOLS = [_][]const u8{
    "pub fn insertColorCached(node: *Node, root: *RootCached, leftmost: bool) void {",
    "pub fn rb_insert_color_cached(node: *Node, root: *RootCached, leftmost: bool) void {",
    "pub fn addCached(node: *Node, root: *RootCached, less: LessFn) ?*Node {",
    "pub fn rb_add_cached(node: *Node, root: *RootCached, less: LessFn) ?*Node {",
    "pub fn findAddCached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {",
    "pub fn rb_find_add_cached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {",
    "pub fn eraseCached(node: *Node, root: *RootCached) ?*Node {",
    "pub fn rb_erase_cached(node: *Node, root: *RootCached) ?*Node {",
    "pub fn eraseInitCached(node: *Node, root: *RootCached) void {",
    "pub fn rb_erase_init_cached(node: *Node, root: *RootCached) void {",
    "pub fn firstCached(root: *const RootCached) ?*Node {",
    "pub fn rb_first_cached(root: *const RootCached) ?*Node {",
    "pub fn replaceNodeCached(victim: *Node, new: *Node, root: *RootCached) void {",
    "pub fn rb_replace_node_cached(victim: *Node, new: *Node, root: *RootCached) void {",
    "pub fn nextMatch(key: *const anyopaque, node: *const Node, cmp: CmpKeyFn) ?*Node {",
    "pub fn rb_next_match(key: *const anyopaque, node: *const Node, cmp: CmpKeyFn) ?*Node {",
    "pub fn matchIterator(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) MatchIterator {",
    "pub fn rb_match_iterator(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) MatchIterator {",
};

const FIXTURE_REL = "zigux/tests/fixtures/phase1_helpers.json";

const HELPER_REL = "tools/lib/rbtree.zig";

const LANE_NOTE_REL = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";

const MANIFEST_REL = "zigux/tests/fixtures/phase1_helper_manifest.json";

const SMOKE_REL = "zigux/tests/phase1_host_tools_smoke.zig";

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
        const relative_path = "zigux/tests/phase1_host_tools_smoke.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
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
    {
        const relative_path = "Documentation/zigux/phase1-closure.md";
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
        const marker = "- `tools/lib/rbtree.zig` now keeps ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed coverage helper-local while the committed fixture still owns exact `find()`, `findFirst()`, `nextMatch()`, and `matchIterator()` duplicate-search fields and the shared host-tools smoke route already keeps duplicate-range iteration plus the parked `cached_leftmost_return_serials` witness explicit. The dedicated `low_level_alias_anchor` and `cached_root_alias_anchor` entries in `zigux/tests/fixtures/phase1_helper_manifest.json` keep both Linux-style alias proofs named explicitly inside that same helper-local packet instead of leaving either alias path implied only by the broader helper test list. Until another committed cached-root replay field lands, leave the remaining cached-root anchors helper-local and do not batch a second widening into the same reopen step.";
        const count = guard.countOccurrences(text, marker);
        if (count != 1) {
            const issue = try std.fmt.allocPrint(allocator, "lane_paragraph:expected=1:actual={d}", .{count});
            try failures.append(allocator, issue);
        }
    }

    {
        const relative_path = "Documentation/zigux/phase1-closure.md";
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
        const marker = "A second current helper-family tie-breaker inside that packet is the `rbtree` direct-anchor route: keep `tools/lib/rbtree.zig` parked unless a fresh reread finds drift in the helper-local ordered Linux-style alias proof, the dedicated manifest-backed `low_level_alias_anchor`, the dedicated manifest-backed `cached_root_alias_anchor`, the cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, or reseed anchors, or drift in the already-committed duplicate-search replay fields or exact `cached_leftmost_return_serials` witness. Current `master` still keeps both Linux-style alias proofs named explicitly in `zigux/tests/fixtures/phase1_helper_manifest.json`, while the shared host-tools smoke route and committed Phase 1 fixture already recheck duplicate-range iteration plus the exact cached-leftmost-return packet, so leave rbtree parked unless one of those helper-local anchors or committed replay fields drifts and do not batch a second cached-root widening into the same reopen step.";
        const count = guard.countOccurrences(text, marker);
        if (count != 1) {
            const issue = try std.fmt.allocPrint(allocator, "closure_paragraph:expected=1:actual={d}", .{count});
            try failures.append(allocator, issue);
        }
    }

    {
        const relative_path = LANE_NOTE_REL;
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                try guard.appendMissingFileIssue(allocator, &failures, relative_path);
                return failures;
            },
            else => return err,
        };
        defer allocator.free(text);
        for (EXPECTED_LANE_LINES) |marker| {
            const label = try std.fmt.allocPrint(allocator, "lane_line:{s}", .{marker});
            defer allocator.free(label);
            try guard.appendExactOccurrenceIssue(allocator, &failures, text, label, marker);
        }
    }

    {
        const relative_path = "zigux/tests/phase1_host_tools_smoke.zig";
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
        for (EXPECTED_SMOKE_MARKERS) |marker| {
            if (std.mem.indexOf(u8, text, marker) == null) {
                const issue = try std.fmt.allocPrint(allocator, "missing_marker:{s}", .{marker});
                try failures.append(allocator, issue);
            }
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
        const full_path = try guard.joinPath(allocator, root, LANE_NOTE_REL);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        try content.appendSlice(allocator, EXPECTED_LANE_PARAGRAPH);
        try content.append(allocator, '\n');
        for (EXPECTED_LANE_LINES) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    {
        const full_path = try guard.joinPath(allocator, root, CLOSURE_NOTE_REL);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, EXPECTED_CLOSURE_PARAGRAPH);
    }
    {
        const full_path = try guard.joinPath(allocator, root, MANIFEST_REL);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, "{}\n");
    }
    {
        const full_path = try guard.joinPath(allocator, root, SMOKE_REL);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (EXPECTED_SMOKE_MARKERS) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }

    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    if (failures.items.len != 0) {
        try guard.printLine(io, "PHASE1_RBTREE_REVIEW_PACKET_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        return guard.GuardError.SelfTestFailed;
    }
    try guard.printLine(io, "PHASE1_RBTREE_REVIEW_PACKET_SELF_TEST=pass", .{});
    try guard.printLine(io, "SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

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
        try guard.printLine(io, "PHASE1_GUARD=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "PHASE1_GUARD=pass", .{});
    std.process.exit(0);
}
