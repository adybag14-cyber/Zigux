const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

test "phase 7 string helpers survey keeps the expanded starter packet truthful" {
    const allocator = std.testing.allocator;

    try std.testing.expectError(
        error.FileNotFound,
        std.Io.Dir.cwd().access(std.testing.io, "lib/string_helpers_parse_int_array.zig", .{}),
    );

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-string-helpers-slice.md");
    defer allocator.free(slice_note);
    try expectContains(slice_note, "PHASE7_STATUS=starter_landed");
    try expectContains(slice_note, "the shared no-sample boundary stays reviewable only while `samples/zigux/README.md` keeps the explicit `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*kasprintf*`, and `*strarray*` exclusions aligned with the helper-local boundary test");

    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase7-string-helpers-packet.py");
    defer allocator.free(checker);
    try expectContains(checker, "PHASE7_STRING_HELPERS_PACKET_SELF_TEST=pass");
    try expectContains(checker, "the explicit `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*kasprintf*`, and `*strarray*` exclusions aligned");
    try expectContains(checker, "* `*printf*`");
    try expectContains(checker, "* `*vsprintf*`");

    const helper = try readRepoFile(allocator, "lib/string_helpers.zig");
    defer allocator.free(helper);
    try expectContains(helper, "pub fn kstrdupQuotableCmdline(");
    try expectContains(helper, "pub fn kstrdup_quotable_cmdline(");
    try expectContains(helper, "pub fn stringUpper(");
    try expectContains(helper, "pub fn string_upper(");
    try expectContains(helper, "pub fn stringLower(");
    try expectContains(helper, "pub fn string_lower(");
    try expectNotContains(helper, "pub fn devmKasprintfStrarray");
    try expectNotContains(helper, "pub fn devm_kasprintf_strarray");

    const helper_tests = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers.zig");
    defer allocator.free(helper_tests);
    try expectContains(helper_tests, "test \"phase 7 string helpers starter quotes cmdlines after collapsing trailing NULs and replacing inter-argument separators\" {");
    try expectContains(helper_tests, "test \"phase 7 string helpers starter uppercases and lowercases only through the exported c-string boundary\" {");
    try expectNotContains(helper_tests, "devmKasprintfStrarray");
    try expectNotContains(helper_tests, "devm_kasprintf_strarray");

    const manifest = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_manifest.json");
    defer allocator.free(manifest);
    try expectContains(manifest, "\"scripts/zigux/check-phase7-string-helpers-packet.py\"");
    try expectContains(manifest, "quoted cmdline duplication that collapses trailing NULL separators into spaces before escaping special characters");
    try expectContains(manifest, "kstrdupQuotableCmdline() keeps returned storage caller-owned, leaves the caller source buffer untouched");
    try expectContains(manifest, "bounded uppercase and lowercase copies through the exported C-string boundary");
    try expectContains(manifest, "dedicated helper-local checker-backed packet reviewability");
    try expectContains(manifest, "\"next_bounded_step\": \"Keep the dedicated checker, survey, and sample-boundary replays fail-closed on the still-parked `devm_kasprintf_strarray()` follow-on");
    try expectContains(manifest, "the shared no-sample boundary stays reviewable only while `samples/zigux/README.md` keeps the explicit `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*kasprintf*`, and `*strarray*` exclusions aligned with the helper-local boundary test");
    try expectNotContains(manifest, "\"devmKasprintfStrarray\"");
    try expectNotContains(manifest, "\"devm_kasprintf_strarray\"");

    const sample_boundary = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    defer allocator.free(sample_boundary);
    try expectContains(sample_boundary, "Keep the dedicated checker, survey, and sample-boundary replays fail-closed on the still-parked `devm_kasprintf_strarray()` follow-on");
    try expectContains(sample_boundary, "the broader full-family packet that still leaves `devm_kasprintf_strarray()` outside the current `master` helper packet");
    try expectContains(sample_boundary, "Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here.");
    try expectContains(sample_boundary, "* `*printf*`");
    try expectContains(sample_boundary, "* `*vsprintf*`");
}
