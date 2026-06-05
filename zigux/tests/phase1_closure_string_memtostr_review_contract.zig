const std = @import("std");
const testing = std.testing;

const closure_path = "Documentation/zigux/phase1-closure.md";
const lane_note_path = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";
const manifest_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
const string_checker_path = "scripts/zigux/check-phase1-string-review-packet.py";
const validator_path = "scripts/zigux/validate-phase1-closure.py";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

test "closure note keeps string memtostr review parked in helper-local evidence" {
    const allocator = testing.allocator;
    const closure = try readFile(allocator, closure_path);
    defer allocator.free(closure);

    try expectContains(closure, "`PHASE1_STRING_REVIEW_GUARD=python3 scripts/zigux/check-phase1-string-review-packet.py");
    try expectContains(closure, "helper-local `memtostr()`, `memtostrPad()`, and `memtostr_pad()` anchors");
    try expectContains(closure, "beside the `memcpyAndPad()`, `memcpy_and_pad()`, `strtomem()`, and `strtomem_pad()` byte-copy anchors");
    try expectContains(closure, "rather than shared-fixture or validator-owned requirements until dedicated fixture keys land");
    try expectOrdered(
        closure,
        "`PHASE1_STRING_REVIEW_GUARD=python3 scripts/zigux/check-phase1-string-review-packet.py",
        "helper-local `memtostr()`, `memtostrPad()`, and `memtostr_pad()` anchors",
    );
}

test "lane note and manifest keep byte-copy anchors inside the string direct-owner packet" {
    const allocator = testing.allocator;
    const lane_note = try readFile(allocator, lane_note_path);
    defer allocator.free(lane_note);
    const manifest = try readFile(allocator, manifest_path);
    defer allocator.free(manifest);

    try expectContains(lane_note, "the same string-local packet also keeps helper-local byte-copy and pad coverage explicit");
    try expectContains(lane_note, "`memcpyAndPad()`, `memcpy_and_pad()`, `strtomem()`, `strtomem_pad()`, `memtostr()`, `memtostrPad()`, and `memtostr_pad()`");
    try expectContains(lane_note, "until dedicated shared fixture keys land");
    try expectContains(lane_note, "`PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics");
    try expectContains(lane_note, "moving-earliest-dirty-byte memchrInv coverage helper-local");

    try expectContains(manifest, "\"memtostr_review_anchors\"");
    try expectContains(manifest, "test \\\"memtostr copies a bounded non-NUL source and adds one terminator\\\"");
    try expectContains(manifest, "test \\\"memtostr stops at embedded NUL without padding the tail\\\"");
    try expectContains(manifest, "test \\\"memtostrPad zero-pads the remaining tail after copying\\\"");
    try expectContains(manifest, "test \\\"memtostr helpers keep one-byte destinations terminated\\\"");
    try expectContains(manifest, "\"memtostr_review_summary\"");
    try expectContains(manifest, "shared Phase 1 replay still does not carry dedicated memtostr(), memtostrPad(), or memtostr_pad() fixture keys");
}

test "string review checker exact-checks memtostr and byte-copy source anchors" {
    const allocator = testing.allocator;
    const checker = try readFile(allocator, string_checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "\"pub fn memtostr(dest: []u8, src: []const u8) void {\"");
    try expectContains(checker, "\"pub fn memtostrPad(dest: []u8, src: []const u8) void {\"");
    try expectContains(checker, "\"pub fn memtostr_pad(dest: []u8, src: []const u8) void {\"");
    try expectContains(checker, "\"memtostr_review_anchors\"");
    try expectContains(checker, "\"copy_fill_review_anchors\"");
    try expectContains(checker, "helper-local memtostr boundary and tail-padding anchors stay explicit");
    try expectContains(checker, "helper-local raw-copy and pad anchors stay explicit");
    try expectOrdered(checker, "\"copy_fill_review_anchors\"", "\"memtostr_review_anchors\"");
}

test "closure validator keeps memtostr marker current and avoids old string validator promotion" {
    const allocator = testing.allocator;
    const validator = try readFile(allocator, validator_path);
    defer allocator.free(validator);

    try expectContains(validator, "\"string_review_guard\"");
    try expectContains(validator, "\"string_memtostr_review\"");
    try expectContains(validator, "Current `master` now also spells the helper-local `memtostr()`, `memtostrPad()`, and `memtostr_pad()` anchors");
    try expectContains(validator, "Keep those byte-copy and pad tests helper-local review evidence rather than shared-fixture or validator-owned requirements");
    try expectNotContains(validator, "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`");
    try expectNotContains(validator, "`PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first`");
}
