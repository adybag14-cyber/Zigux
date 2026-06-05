const std = @import("std");
const testing = std.testing;

const closure_path = "Documentation/zigux/phase1-closure.md";
const lane_note_path = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";
const manifest_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
const string_checker_path = "scripts/zigux/check-phase1-string-review-packet.py";
const string_helper_path = "tools/lib/string.zig";

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

test "closure note keeps counted search under the string review guard" {
    const allocator = testing.allocator;
    const closure = try readFile(allocator, closure_path);
    defer allocator.free(closure);

    try expectContains(closure, "`PHASE1_STRING_REVIEW_GUARD=python3 scripts/zigux/check-phase1-string-review-packet.py");
    try expectContains(closure, "helper-local string anchors plus the committed replaceChar and current string fixture packet");
    try expectContains(closure, "rather than shared-fixture or validator-owned requirements until dedicated fixture keys land");
    try expectNotContains(closure, "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`");
    try expectNotContains(closure, "`PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first`");
}

test "lane note keeps counted search as one helper-local string packet" {
    const allocator = testing.allocator;
    const lane_note = try readFile(allocator, lane_note_path);
    defer allocator.free(lane_note);

    try expectContains(lane_note, "counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen()");
    try expectContains(lane_note, "the current `strnchrNul()` and `strnchrnul()` match-or-NUL boundary anchor");
    try expectContains(lane_note, "the same counted-search packet now also keeps the direct `strspn()` accepted-prefix anchor review-visible");
    try expectContains(lane_note, "`PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift");
    try expectOrdered(
        lane_note,
        "`PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics",
        "the current `strnchrNul()` and `strnchrnul()` match-or-NUL boundary anchor",
    );
}

test "manifest and checker exact-check the counted search anchor roster" {
    const allocator = testing.allocator;
    const manifest = try readFile(allocator, manifest_path);
    defer allocator.free(manifest);
    const checker = try readFile(allocator, string_checker_path);
    defer allocator.free(checker);

    const manifest_anchors = [_][]const u8{
        "test \\\"strchr mirrors full-length C-string searches\\\"",
        "test \\\"strrchr finds the last in-range match with C-string semantics\\\"",
        "test \\\"strpbrk finds the first accepted byte with C-string semantics\\\"",
        "test \\\"strspn counts the accepted prefix with C-string semantics\\\"",
        "test \\\"strcspn counts until the first rejected byte with C-string semantics\\\"",
        "test \\\"strnchr honors count and C-string boundaries\\\"",
        "test \\\"strnlen honors count and C-string boundaries\\\"",
        "test \\\"strnchrNul returns the first match, NUL, or count boundary\\\"",
        "test \\\"strchrNul and strchrnul return the first match or terminator boundary\\\"",
    };
    const checker_anchors = [_][]const u8{
        "test \"strchr mirrors full-length C-string searches\"",
        "test \"strrchr finds the last in-range match with C-string semantics\"",
        "test \"strpbrk finds the first accepted byte with C-string semantics\"",
        "test \"strspn counts the accepted prefix with C-string semantics\"",
        "test \"strcspn counts until the first rejected byte with C-string semantics\"",
        "test \"strnchr honors count and C-string boundaries\"",
        "test \"strnlen honors count and C-string boundaries\"",
        "test \"strnchrNul returns the first match, NUL, or count boundary\"",
        "test \"strchrNul and strchrnul return the first match or terminator boundary\"",
    };

    try expectContains(manifest, "\"counted_search_review_anchors\"");
    try expectContains(checker, "\"counted_search_review_anchors\"");
    try expectContains(checker, "\"strnchrnul_review_anchor\"");
    try expectContains(checker, "\"strchrnul_review_anchor\"");
    try expectContains(checker, "remain owned by the helper-local anchors");
    try expectOrdered(checker, "\"search_length_review_summary\"", "\"counted_search_review_anchors\"");

    for (manifest_anchors) |anchor| {
        try expectContains(manifest, anchor);
    }
    for (checker_anchors) |anchor| {
        try expectContains(checker, anchor);
    }
}

test "string helper keeps counted search functions and direct tests live" {
    const allocator = testing.allocator;
    const helper = try readFile(allocator, string_helper_path);
    defer allocator.free(helper);

    const symbols = [_][]const u8{
        "pub fn strchr(buf: []const u8, needle: u8) ?usize {",
        "pub fn strrchr(buf: []const u8, needle: u8) ?usize {",
        "pub fn strpbrk(buf: []const u8, accept: []const u8) ?usize {",
        "pub fn strspn(buf: []const u8, accept: []const u8) usize {",
        "pub fn strcspn(buf: []const u8, reject: []const u8) usize {",
        "pub fn strnchr(buf: []const u8, count: usize, needle: u8) ?usize {",
        "pub fn strlen(buf: []const u8) usize {",
        "pub fn strnlen(buf: []const u8, count: usize) usize {",
        "pub fn strnchrNul(buf: []const u8, count: usize, needle: u8) usize {",
        "pub fn strnchrnul(buf: []const u8, count: usize, needle: u8) usize {",
        "pub fn strchrNul(buf: []const u8, needle: u8) usize {",
        "pub fn strchrnul(buf: []const u8, needle: u8) usize {",
    };
    const tests = [_][]const u8{
        "test \"strchr mirrors full-length C-string searches\"",
        "test \"strrchr finds the last in-range match with C-string semantics\"",
        "test \"strpbrk finds the first accepted byte with C-string semantics\"",
        "test \"strspn counts the accepted prefix with C-string semantics\"",
        "test \"strcspn counts until the first rejected byte with C-string semantics\"",
        "test \"strnchr honors count and C-string boundaries\"",
        "test \"strlen honors C-string boundaries\"",
        "test \"strnlen honors count and C-string boundaries\"",
        "test \"strnchrNul returns the first match, NUL, or count boundary\"",
        "test \"strchrNul and strchrnul return the first match or terminator boundary\"",
    };

    for (symbols) |symbol| {
        try expectContains(helper, symbol);
    }
    for (tests) |direct_test| {
        try expectContains(helper, direct_test);
    }
    try expectOrdered(helper, "pub fn strnchr(buf: []const u8, count: usize, needle: u8) ?usize {", "pub fn strnchrNul(buf: []const u8, count: usize, needle: u8) usize {");
}
