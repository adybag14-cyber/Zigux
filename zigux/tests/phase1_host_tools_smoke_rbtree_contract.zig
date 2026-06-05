const std = @import("std");
const config = @import("config");

const allocator = std.testing.allocator;

fn readFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |index| {
        count += 1;
        cursor = index + needle.len;
    }
    return count;
}

test "phase1 host-tools smoke keeps rbtree import and build wiring" {
    const smoke = try readFile(config.smoke_path);
    defer allocator.free(smoke);
    const tests_build = try readFile(config.tests_build_path);
    defer allocator.free(tests_build);

    try requireContains(smoke, "const rbtree = @import(\"rbtree\");");
    try requireContains(smoke, "try std.testing.expect(@hasDecl(rbtree, \"find\"));");
    try requireContains(smoke, "try std.testing.expect(@hasDecl(rbtree, \"matchIterator\"));");
    try requireContains(smoke, "const RbtreeSmokeEntry = struct");
    try requireContains(smoke, "node: rbtree.Node = rbtree.Node.init()");
    try requireContains(smoke, "fn returnedSerial(node: ?*rbtree.Node) i32");
    try requireBefore(smoke, "const list_sort = @import(\"list_sort\");", "const rbtree = @import(\"rbtree\");");
    try requireBefore(smoke, "const rbtree = @import(\"rbtree\");", "const string = @import(\"string\");");

    try requireContains(tests_build, "const rbtree_module = b.createModule(.{");
    try requireContains(tests_build, ".root_source_file = b.path(\"../../tools/lib/rbtree.zig\")");
    try requireContains(tests_build, "root_module.addImport(\"rbtree\", rbtree_module);");
    try requireContains(tests_build, "phase1_host_tools_smoke");
    try requireContains(tests_build, "phase1-host-tools-smoke");
}

test "phase1 host-tools smoke keeps rbtree duplicate match replay" {
    const smoke = try readFile(config.smoke_path);
    defer allocator.free(smoke);

    try requireContains(smoke, "var tree_entries = [_]RbtreeSmokeEntry{");
    try requireContains(smoke, ".{ .key = 10, .serial = 0 }");
    try requireContains(smoke, ".{ .key = 20, .serial = 1 }");
    try requireContains(smoke, ".{ .key = 10, .serial = 4 }");
    try requireContains(smoke, "var tree_root = rbtree.Root.init();");
    try requireContains(smoke, "rbtree.add(&entry.node, &tree_root, RbtreeSmokeEntry.less);");
    try requireContains(smoke, "const found_duplicate = rbtree.find(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp) orelse return error.TestUnexpectedResult;");
    try requireContains(smoke, "try std.testing.expect(rbtree.find(&missing_key, &tree_root, RbtreeSmokeEntry.cmp) == null);");
    try requireContains(smoke, "const first_duplicate = rbtree.findFirst(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp) orelse return error.TestUnexpectedResult;");
    try requireContains(smoke, "const second_duplicate = rbtree.nextMatch(&duplicate_key, first_duplicate, RbtreeSmokeEntry.cmp) orelse return error.TestUnexpectedResult;");
    try requireContains(smoke, "const third_duplicate = rbtree.nextMatch(&duplicate_key, second_duplicate, RbtreeSmokeEntry.cmp) orelse return error.TestUnexpectedResult;");
    try requireContains(smoke, "try std.testing.expect(rbtree.nextMatch(&duplicate_key, third_duplicate, RbtreeSmokeEntry.cmp) == null);");
    try requireContains(smoke, "var iter = rbtree.matchIterator(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp);");
    try requireContains(smoke, "try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, duplicate_serials[0..duplicate_count]);");
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(smoke, "var iter = rbtree.matchIterator(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp);"));
}

test "phase1 host-tools smoke keeps rbtree cached leftmost and replace replay" {
    const smoke = try readFile(config.smoke_path);
    defer allocator.free(smoke);

    try requireContains(smoke, "var cached_leftmost_entries = [_]RbtreeSmokeEntry{");
    try requireContains(smoke, "var cached_leftmost_root = rbtree.RootCached.init();");
    try requireContains(smoke, "cached_leftmost_return_serials[0] = returnedSerial(rbtree.addCached(&cached_leftmost_entries[0].node, &cached_leftmost_root, RbtreeSmokeEntry.less));");
    try requireContains(smoke, "cached_leftmost_return_serials[3] = returnedSerial(rbtree.addCached(&cached_leftmost_entries[3].node, &cached_leftmost_root, RbtreeSmokeEntry.less));");
    try requireContains(smoke, "try std.testing.expectEqualSlices(i32, &.{ 0, -1, 2, -1 }, &cached_leftmost_return_serials);");
    try requireContains(smoke, "try std.testing.expectEqual(@as(?*rbtree.Node, &cached_leftmost_entries[2].node), rbtree.firstCached(&cached_leftmost_root));");

    try requireContains(smoke, "var cached_replacement = RbtreeSmokeEntry{ .key = 10, .serial = 4 };");
    try requireContains(smoke, "cached_root_transition_serials[0] = returnedSerial(rbtree.eraseCached(&cached_entries[1].node, &cached_root));");
    try requireContains(smoke, "rbtree.replaceNodeCached(&cached_entries[0].node, &cached_replacement.node, &cached_root);");
    try requireContains(smoke, "rbtree.eraseInitCached(&cached_replacement.node, &cached_root);");
    try requireContains(smoke, "try std.testing.expectEqualSlices(i32, &.{ 0, 0, 4, 2 }, &cached_root_transition_serials);");
    try requireContains(smoke, "try std.testing.expect(rbtree.emptyNode(&cached_replacement.node));");
    try requireAbsent(smoke, "rbtree.replaceNodeCached(&cached_entries[1].node, &cached_replacement.node, &cached_root);");
}
