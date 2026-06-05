const std = @import("std");

const testing = std.testing;

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        path,
        testing.allocator,
        .limited(512 * 1024),
    );
}

test "closure note keeps string review helpers helper-local" {
    const closure_note = try readRepoFile("Documentation/zigux/phase1-closure.md");
    defer testing.allocator.free(closure_note);

    try expectContains(closure_note, "PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit");
    try expectContains(closure_note, "PHASE1_STRING_REVIEW_GUARD=python3 scripts/zigux/check-phase1-string-review-packet.py");
    try expectContains(closure_note, "helper-local `memtostr()`, `memtostrPad()`, and `memtostr_pad()` anchors");
    try expectContains(closure_note, "`memcpyAndPad()`, `memcpy_and_pad()`, `strtomem()`, and `strtomem_pad()` byte-copy anchors");
    try expectContains(closure_note, "Keep those byte-copy and pad tests helper-local review evidence");
    try expectNotContains(closure_note, "PHASE1_STRING_SYSFS_REVIEW=validator-owned");
    try expectNotContains(closure_note, "PHASE1_STRING_REVIEW_GUARD=missing");
}

test "string helper exposes the direct review anchor tests" {
    const string_helper = try readRepoFile("tools/lib/string.zig");
    defer testing.allocator.free(string_helper);

    try expectContains(string_helper, "pub fn strlcat");
    try expectContains(string_helper, "pub fn memcpyAndPad");
    try expectContains(string_helper, "pub fn memcpy_and_pad");
    try expectContains(string_helper, "pub fn strtomem");
    try expectContains(string_helper, "pub fn strtomem_pad");
    try expectContains(string_helper, "pub fn memtostr");
    try expectContains(string_helper, "pub fn memtostrPad");
    try expectContains(string_helper, "pub fn memtostr_pad");
    try expectContains(string_helper, "pub fn sysfsStreq");
    try expectContains(string_helper, "pub fn sysfs_streq");
    try expectContains(string_helper, "pub fn sysfsMatchString");
    try expectContains(string_helper, "pub fn sysfs_match_string");
    try expectContains(string_helper, "pub fn strcmp");
    try expectContains(string_helper, "pub fn strcasecmp");
    try expectContains(string_helper, "pub fn strncasecmp");
    try expectContains(string_helper, "pub fn strchrNul");
    try expectContains(string_helper, "pub fn strchrnul");

    try expectContains(string_helper, "test \"strlcat truncates with a terminator and keeps the full attempted length\"");
    try expectContains(string_helper, "test \"memtostr stops at embedded NUL without padding the tail\"");
    try expectContains(string_helper, "test \"memtostr helpers keep one-byte destinations terminated\"");
    try expectContains(string_helper, "test \"sysfsMatchString finds newline-aware matches and preserves first-match order\"");
    try expectContains(string_helper, "test \"strcmp stops at embedded NULs and length mismatches\"");
    try expectContains(string_helper, "test \"strchrNul and strchrnul return the first match or terminator boundary\"");
}

test "manifest keeps string helper follow-up owned by direct anchors" {
    const manifest = try readRepoFile("zigux/tests/fixtures/phase1_helper_manifest.json");
    defer testing.allocator.free(manifest);

    try expectContains(manifest, "\"tools/lib/string.zig\"");
    try expectContains(manifest, "\"strlcat_review_summary\"");
    try expectContains(manifest, "\"copy_fill_review_anchors\"");
    try expectContains(manifest, "\"memtostr_review_anchors\"");
    try expectContains(manifest, "\"memtostr_review_summary\"");
    try expectContains(manifest, "\"sysfs_review_summary\"");
    try expectContains(manifest, "\"strcmp_review_summary\"");
    try expectContains(manifest, "\"casecmp_review_summary\"");
    try expectContains(manifest, "\"search_length_review_summary\"");
    try expectContains(manifest, "\"strnchr_review_summary\"");
    try expectContains(manifest, "helper-local strlcat, sysfs, case-insensitive compare, and match-or-terminator review anchors");
    try expectContains(manifest, "shared Phase 1 replay still does not carry dedicated memtostr(), memtostrPad(), or memtostr_pad() fixture keys");
    try expectNotContains(manifest, "\"sysfs_fixture_keys\"");
    try expectNotContains(manifest, "\"memtostr_fixture_keys\"");
}
