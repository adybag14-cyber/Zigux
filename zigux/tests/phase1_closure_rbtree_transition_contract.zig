const std = @import("std");

const allocator = std.testing.allocator;

const closure_note_path = "Documentation/zigux/phase1-closure.md";
const manifest_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
const fixture_path = "zigux/tests/fixtures/phase1_helpers.json";
const smoke_path = "zigux/tests/phase1_host_tools_smoke.zig";

fn readFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectContainsOnce(haystack: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

fn expectContainsAny(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        if (std.mem.indexOf(u8, haystack, needle) != null) {
            return;
        }
    }
    return error.TestUnexpectedResult;
}

test "closure note keeps rbtree cached-root transition shared evidence explicit" {
    const closure_note = try readFile(closure_note_path);
    defer allocator.free(closure_note);

    try expectContains(closure_note, "Current `master` also keeps the companion `cached_root_transition_serials` witness shared instead of helper-local only");
    try expectContains(closure_note, "`zigux/tests/fixtures/phase1_helpers.json` still records the exact cached-root erase, replacement, and detach transition packet");
    try expectContains(closure_note, "`zigux/tests/phase1_host_tools_smoke.zig` already rechecks the same `[0, 0, 4, 2]` sequence");
    try expectContains(closure_note, "Treat that transition packet as landed shared closure evidence");
    try expectContains(closure_note, "while still leaving the remaining insert-miss, leftmost-sync, alias, singleton-erase, replacement, detach, and reseed anchors helper-local");
}

test "manifest names cached-root transition fixture as shared replay evidence" {
    const manifest = try readFile(manifest_path);
    defer allocator.free(manifest);

    try expectContains(manifest, "\"cached_root_transition_fixture_keys\": [");
    try expectContains(manifest, "\"cached_root_transition_serials\"");
    try expectContains(manifest, "the committed Phase 1 fixture and the shared host-tools smoke route also keep the exact `cached_root_transition_serials` cached-root erase, replacement, and detach sequence aligned on current master");
    try expectContains(manifest, "If this helper lane reopens, keep the already-landed shared-replay promotion for `cached_leftmost_return_serials` aligned");
}

test "fixture records the exact cached-root transition witness once" {
    const fixture = try readFile(fixture_path);
    defer allocator.free(fixture);

    try expectContainsOnce(fixture, "\"cached_root_transition_serials\"");
    try expectContainsAny(fixture, &.{
        "\"cached_root_transition_serials\": [0, 0, 4, 2]",
        "\"cached_root_transition_serials\":[0,0,4,2]",
    });
}

test "shared host-tools smoke replays the cached-root transition sequence" {
    const smoke = try readFile(smoke_path);
    defer allocator.free(smoke);

    try expectContains(smoke, "var cached_root_transition_serials: [4]i32 = undefined;");
    try expectContains(smoke, "cached_root_transition_serials[0] = returnedSerial(rbtree.eraseCached(&cached_entries[1].node, &cached_root));");
    try expectContains(smoke, "rbtree.replaceNodeCached(&cached_entries[0].node, &cached_replacement.node, &cached_root);");
    try expectContains(smoke, "rbtree.eraseInitCached(&cached_replacement.node, &cached_root);");
    try expectContains(smoke, "try std.testing.expectEqualSlices(i32, &.{ 0, 0, 4, 2 }, &cached_root_transition_serials);");
    try expectContains(smoke, "try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[2].node), rbtree.firstCached(&cached_root));");
}
