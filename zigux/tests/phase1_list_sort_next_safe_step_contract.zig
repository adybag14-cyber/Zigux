const std = @import("std");
const testing = std.testing;

const helper_manifest = @embedFile("fixtures/phase1_helper_manifest.json");

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "closure note keeps the shared reminder packet and manifest authority visible" {
    const closure_note = try readRepoFile(testing.allocator, "Documentation/zigux/phase1-closure.md");
    defer testing.allocator.free(closure_note);

    try expectContains(closure_note, "PHASE1_HELPER_COUNT=13");
    try expectContains(closure_note, "Documentation/zigux/phase1-host-helper-lane-sequencing.md");
    try expectContains(closure_note, "zigux/tests/fixtures/phase1_helper_manifest.json");
    try expectContains(closure_note, "PHASE1_CURRENT_REMINDER_PACKET=");
    try expectContains(closure_note, "PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker");
}

test "list_sort stays in the parked shared replay family" {
    const lane_note = try readRepoFile(testing.allocator, "Documentation/zigux/phase1-host-helper-lane-sequencing.md");
    defer testing.allocator.free(lane_note);

    try expectContains(lane_note, "tools/lib/list_sort.zig");
    try expectContains(lane_note, "PHASE1_SHARED_REPLAY_PARKED_HELPERS=tools/lib/argv_split.zig,tools/lib/cmdline.zig,tools/lib/ctype.zig,tools/lib/hweight.zig,tools/lib/list_sort.zig");
    try expectContains(lane_note, "list_sort reopens only for shared replay or reminder-surface drift");
    try expectContains(lane_note, "do not widen into neighboring shared-replay parked helpers by default");
}

test "manifest keeps list_sort parity keys and helper-local anchors separate" {
    try expectContains(helper_manifest, "\"tools/lib/list_sort.zig\"");
    try expectContains(helper_manifest, "\"tri_sorted_keys\"");
    try expectContains(helper_manifest, "\"tri_sorted_ordinals\"");
    try expectContains(helper_manifest, "\"bool_sorted_keys\"");
    try expectContains(helper_manifest, "\"bool_sorted_ordinals\"");
    try expectContains(helper_manifest, "test \\\"list sort honors comparator context\\\"");
    try expectContains(helper_manifest, "test \\\"list sort keeps reverse links aligned after reordering\\\"");
    try expectContains(helper_manifest, "test \\\"list sort preserves input order when every comparison ties\\\"");
    try expectContains(helper_manifest, "keep list_sort parked unless a fresh reread finds drift in the committed `tri_sorted_*` or `bool_sorted_*` fixture keys");
}
