const std = @import("std");
const testing = std.testing;

const helper_fixture = @embedFile("fixtures/phase1_helpers.json");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAnyContains(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        if (std.mem.indexOf(u8, haystack, needle) != null) return;
    }

    try testing.expect(false);
}

fn readClosureNote() ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        "Documentation/zigux/phase1-closure.md",
        testing.allocator,
        .limited(128 * 1024),
    );
}

test "phase1 closure note keeps rbtree cached transition evidence shared" {
    const closure_note = try readClosureNote();
    defer testing.allocator.free(closure_note);

    try expectContains(closure_note, "cached_root_transition_serials");
    try expectContains(closure_note, "[0, 0, 4, 2]");
    try expectContains(closure_note, "landed shared closure evidence");
    try expectContains(closure_note, "future cached-root rereads");
}

test "phase1 closure note keeps remaining rbtree cached-root anchors helper local" {
    const closure_note = try readClosureNote();
    defer testing.allocator.free(closure_note);

    try expectContains(closure_note, "insert-miss, leftmost-sync, alias, singleton-erase, replacement, detach, and reseed anchors");
    try expectContains(closure_note, "helper-local until another broader replay field lands");
    try expectContains(closure_note, "do not batch a second cached-root widening");
}

test "phase1 helper fixture pins the rbtree cached transition witness" {
    try expectContains(helper_fixture, "\"rbtree\"");
    try expectAnyContains(helper_fixture, &.{
        "\"cached_root_transition_serials\":[0,0,4,2]",
        "\"cached_root_transition_serials\": [0,0,4,2]",
        "\"cached_root_transition_serials\":[0, 0, 4, 2]",
        "\"cached_root_transition_serials\": [0, 0, 4, 2]",
    });
}
