const std = @import("std");

const checker_path = "scripts\zigux/check_phase1_string_review_packet.zig";
const closure_path = "Documentation/zigux/phase1-closure.md";
const lane_note_path = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";

fn readFile(path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectInOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "phase1 string review checker keeps the direct string packet catalog" {
    const checker = try readFile(checker_path);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "EXPECTED_STRING_PACKET = {");
    try expectContains(checker, "\"memparse_review_anchors\"");
    try expectContains(checker, "\"strscpy_review_anchors\"");
    try expectContains(checker, "\"sysfs_review_anchors\"");
    try expectContains(checker, "\"counted_search_review_anchors\"");
    try expectContains(checker, "\"strnchrnul_review_anchor\"");
    try expectContains(checker, "\"parity_fixture_keys\"");
    try expectContains(checker, "\"next_safe_step_note\"");

    try expectInOrder(checker, "\"memparse_review_anchors\"", "\"sysfs_review_anchors\"");
    try expectInOrder(checker, "\"sysfs_review_anchors\"", "\"counted_search_review_anchors\"");
    try expectInOrder(checker, "\"counted_search_review_anchors\"", "\"parity_fixture_keys\"");
}

test "phase1 string review checker keeps fixture and lane-note enforcement surfaces" {
    const checker = try readFile(checker_path);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "STRING_HELPER_REL = Path(\"tools/lib/string.zig\")");
    try expectContains(checker, "STRING_MANIFEST_REL = Path(\"zigux/tests/fixtures/phase1_helper_manifest.json\")");
    try expectContains(checker, "STRING_FIXTURE_REL = Path(\"zigux/tests/fixtures/phase1_helpers.json\")");
    try expectContains(checker, "STRING_LANE_NOTE_REL = Path(\"Documentation/zigux/phase1-host-helper-lane-sequencing.md\")");
    try expectContains(checker, "EXPECTED_STRING_FIXTURE_VALUES = {");
    try expectContains(checker, "EXPECTED_STRING_LANE_MARKERS = [");
    try expectContains(checker, "\"lane_direct_owner\"");
    try expectContains(checker, "\"lane_next_safe_step\"");
    try expectContains(checker, "collect_duplicate_json_key_paths");
}

test "phase1 closure note advertises the string review guard as current reminder evidence" {
    const closure = try readFile(closure_path);
    defer std.testing.allocator.free(closure);

    try expectContains(closure, "`scripts\zigux/check_phase1_string_review_packet.zig`");
    try expectContains(closure, "PHASE1_STRING_REVIEW_GUARD=zig run scripts/zigux/check_phase1_string_review_packet.zig");
    try expectContains(closure, "helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit");
    try expectContains(closure, "`memtostr()`, `memtostrPad()`, and `memtostr_pad()`");
}

test "phase1 lane note keeps string inside the direct-anchor owner map" {
    const lane_note = try readFile(lane_note_path);
    defer std.testing.allocator.free(lane_note);

    try expectContains(lane_note, "`tools/lib/string.zig`");
    try expectContains(lane_note, "PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig");
    try expectContains(lane_note, "PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics");
    try expectContains(lane_note, "PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift");
    try expectContains(lane_note, "keep the helper-local sysfs review anchors aligned across the string review packet and this lane note");
}
