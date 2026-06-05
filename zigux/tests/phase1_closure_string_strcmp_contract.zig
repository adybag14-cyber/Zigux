const std = @import("std");

const max_file_size = 1024 * 1024;

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(max_file_size));
}

fn expectContainsOnce(haystack: []const u8, needle: []const u8) !void {
    const first = std.mem.indexOf(u8, haystack, needle) orelse {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    };
    if (std.mem.indexOf(u8, haystack[first + needle.len ..], needle) != null) {
        std.debug.print("duplicate marker: {s}\n", .{needle});
        return error.DuplicateMarker;
    }
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) == null) {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    }
}

const strcmp_anchor =
    \\test "strcmp mirrors C-string lexical ordering"
;

const strcmp_nul_anchor =
    \\test "strcmp stops at embedded NULs and length mismatches"
;

const strncmp_anchor =
    \\test "strncmp honors the count limit before later mismatches"
;

const strncmp_nul_anchor =
    \\test "strncmp stops at embedded NULs and shorter prefixes"
;

const strcmp_summary =
    \\helper-local lexical-compare anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated strcmp() fixture keys
;

test "string strcmp closure packet keeps review markers helper-local" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    const closure = try readFile(allocator, "Documentation/zigux/phase1-closure.md");
    const validator = try readFile(allocator, "scripts/zigux/validate-phase1-closure.py");
    const checker = try readFile(allocator, "scripts/zigux/check-phase1-string-review-packet.py");

    try expectContainsOnce(
        closure,
        "`PHASE1_STRING_REVIEW_GUARD=python3 scripts/zigux/check-phase1-string-review-packet.py exact-checks helper-local string anchors plus the committed replaceChar and current string fixture packet across the helper, closure note, lane note, manifest, and fixture`",
    );

    try expectContainsOnce(validator, "\"strcmp_review_anchors\": [");
    try expectContainsOnce(validator, strcmp_anchor);
    try expectContainsOnce(validator, strcmp_nul_anchor);
    try expectContainsOnce(validator, "\"strcmp_review_summary\":");
    try expectContains(validator, strcmp_summary);

    try expectContainsOnce(checker, "\"strcmp_review_anchors\": [");
    try expectContains(checker, strcmp_anchor);
    try expectContains(checker, strcmp_nul_anchor);
    try expectContains(checker, strncmp_anchor);
    try expectContains(checker, strncmp_nul_anchor);
    try expectContainsOnce(checker, "\"strcmp_review_summary\":");
    try expectContains(checker, strcmp_summary);
}

test "manifest and lane note keep string compare in the direct-anchor family" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    const lane_note = try readFile(allocator, "Documentation/zigux/phase1-host-helper-lane-sequencing.md");
    const manifest = try readFile(allocator, "zigux/tests/fixtures/phase1_helper_manifest.json");

    try expectContainsOnce(
        lane_note,
        "`PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig`",
    );
    try expectContainsOnce(
        lane_note,
        "`PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen(), embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`",
    );

    try expectContainsOnce(manifest, "\"strcmp_review_anchors\"");
    try expectContains(manifest, "strcmp mirrors C-string lexical ordering");
    try expectContains(manifest, "strcmp stops at embedded NULs and length mismatches");
    try expectContains(manifest, "strncmp honors the count limit before later mismatches");
    try expectContains(manifest, "strncmp stops at embedded NULs and shorter prefixes");
    try expectContainsOnce(manifest, "\"strcmp_review_summary\"");
    try expectContains(manifest, strcmp_summary);
    try expectContains(manifest, "\"parity_fixture_keys\"");
    try expectContains(manifest, "\"replace_char_cstr_bytes\"");
}

test "string helper source still exposes the lexical compare entrypoints and anchors" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    const helper = try readFile(allocator, "tools/lib/string.zig");

    try expectContainsOnce(helper, "pub fn strcmp(lhs: []const u8, rhs: []const u8) i32 {");
    try expectContainsOnce(helper, "pub fn strncmp(lhs: []const u8, rhs: []const u8, count: usize) i32 {");
    try expectContainsOnce(helper, strcmp_anchor);
    try expectContainsOnce(helper, strcmp_nul_anchor);
    try expectContainsOnce(helper, strncmp_anchor);
    try expectContainsOnce(helper, strncmp_nul_anchor);
}
