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

test "phase1 host-tools smoke keeps list_sort import and build wiring" {
    const smoke = try readFile(config.smoke_path);
    defer allocator.free(smoke);
    const tests_build = try readFile(config.tests_build_path);
    defer allocator.free(tests_build);

    try requireContains(smoke, "const list_sort = @import(\"list_sort\");");
    try requireContains(smoke, "try std.testing.expect(@hasDecl(list_sort, \"listSort\"));");
    try requireContains(smoke, "const ListSortSmokeEntry = struct");
    try requireContains(smoke, "node: list_sort.ListHead = .{}");
    try requireBefore(smoke, "const hweight = @import(\"hweight\");", "const list_sort = @import(\"list_sort\");");
    try requireBefore(smoke, "const list_sort = @import(\"list_sort\");", "const rbtree = @import(\"rbtree\");");

    try requireContains(tests_build, "const list_sort_module = b.createModule(.{");
    try requireContains(tests_build, ".root_source_file = b.path(\"../../tools/lib/list_sort.zig\")");
    try requireContains(tests_build, "root_module.addImport(\"list_sort\", list_sort_module);");
    try requireContains(tests_build, "phase1_host_tools_smoke");
    try requireContains(tests_build, "phase1-host-tools-smoke");
}

test "phase1 host-tools smoke keeps list_sort stable tri-state replay" {
    const smoke = try readFile(config.smoke_path);
    defer allocator.free(smoke);

    try requireContains(smoke, "var list_head: list_sort.ListHead = .{};");
    try requireContains(smoke, "list_head.init();");
    try requireContains(smoke, ".{ .key = 2, .ordinal = 0 }");
    try requireContains(smoke, ".{ .key = 1, .ordinal = 1 }");
    try requireContains(smoke, ".{ .key = 3, .ordinal = 4 }");
    try requireContains(smoke, "fn less(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32");
    try requireContains(smoke, "if (lhs.key < rhs.key) return -1;");
    try requireContains(smoke, "if (lhs.key > rhs.key) return 1;");
    try requireContains(smoke, "list_sort.listSort(null, &list_head, list_cmp);");
    try requireContains(smoke, "try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 3, 3 }, sorted_keys[0..sorted_count]);");
    try requireContains(smoke, "try std.testing.expectEqualSlices(usize, &.{ 1, 3, 0, 2, 4 }, sorted_ordinals[0..sorted_count]);");
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(smoke, "list_sort.listSort(null, &list_head, list_cmp);"));
}

test "phase1 host-tools smoke keeps list_sort boolean comparator replay" {
    const smoke = try readFile(config.smoke_path);
    defer allocator.free(smoke);

    try requireContains(smoke, "var bool_head: list_sort.ListHead = .{};");
    try requireContains(smoke, "bool_head.init();");
    try requireContains(smoke, "const bool_cmp = struct");
    try requireContains(smoke, "return @intFromBool(lhs.key > rhs.key);");
    try requireContains(smoke, "list_sort.listSort(null, &bool_head, bool_cmp);");
    try requireContains(smoke, "sorted_count = 0;");
    try requireContains(smoke, "sorted_node = bool_head.next;");
    try requireContains(smoke, "try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 3, 3 }, sorted_keys[0..sorted_count]);");
    try requireContains(smoke, "try std.testing.expectEqualSlices(usize, &.{ 1, 3, 0, 2, 4 }, sorted_ordinals[0..sorted_count]);");
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(smoke, "list_sort.listSort(null, &bool_head, bool_cmp);"));
    try requireAbsent(smoke, "list_sort.listSort(null, &bool_head, list_cmp);");
}
