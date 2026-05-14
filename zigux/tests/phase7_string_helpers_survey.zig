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

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-string-helpers-slice.md");
    defer allocator.free(slice_note);
    try expectContains(slice_note, "PHASE7_STATUS=starter_landed");
    try expectContains(slice_note, "expanded starter packet");
    try expectContains(slice_note, "stringEscapeMem()");
    try expectContains(slice_note, "string_escape_str_any_np()");
    try expectContains(slice_note, "leading whitespace skipping that stops at the first NUL");
    try expectContains(slice_note, "bounded memcpy-and-pad behavior that truncates long copies, pads short ones, and stays inside the provided source slice");
    try expectContains(slice_note, "in-place replacement behavior that stops at the first NUL");
    try expectContains(slice_note, "The next bounded follow-through should keep the expanded starter packet truthful");
    try expectNotContains(slice_note, "same-packet truthfulness repairs");

    const manifest = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_manifest.json");
    defer allocator.free(manifest);
    try expectContains(manifest, "\"current_master_state\": \"expanded_starter_packet\"");
    try expectContains(manifest, "\"stringEscapeMem\"");
    try expectContains(manifest, "\"string_escape_mem_any_np\"");
    try expectContains(manifest, "\"stringEscapeStr\"");
    try expectContains(manifest, "\"string_escape_str_any_np\"");
    try expectContains(manifest, "\"memcpyAndPad\"");
    try expectContains(manifest, "\"memcpy_and_pad\"");
    try expectContains(manifest, "\"strreplace\"");
    try expectContains(manifest, "first-NUL-bounded whitespace trimming and prefix skipping");
    try expectContains(manifest, "bounded memcpy-and-pad copy semantics");
    try expectContains(manifest, "in-place replacement inside the exported C-string prefix");
    try expectContains(manifest, "expanded starter packet");
    try expectNotContains(manifest, "missing_review_surfaces");
    try expectNotContains(manifest, "missing_on_master");

    const helper = try readRepoFile(allocator, "lib/string_helpers.zig");
    defer allocator.free(helper);
    try expectContains(helper, "pub const ESCAPE_SPACE");
    try expectContains(helper, "pub const ESCAPE_APPEND");
    try expectContains(helper, "pub fn stringEscapeMem");
    try expectContains(helper, "pub fn string_escape_mem");
    try expectContains(helper, "pub fn stringEscapeMemAnyNp");
    try expectContains(helper, "pub fn string_escape_mem_any_np");
    try expectContains(helper, "pub fn stringEscapeStr");
    try expectContains(helper, "pub fn string_escape_str");
    try expectContains(helper, "pub fn stringEscapeStrAnyNp");
    try expectContains(helper, "pub fn string_escape_str_any_np");
    try expectContains(helper, "pub fn stringUnescapeInplace");
    try expectContains(helper, "pub fn memcpyAndPad");
    try expectContains(helper, "pub fn strreplace");

    const helper_tests = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers.zig");
    defer allocator.free(helper_tests);
    try expectContains(helper_tests, "phase 7 string helpers starter escapes bounded memory across flag families and dictionary modes");
    try expectContains(helper_tests, "string_helpers.stringEscapeMem(");
    try expectContains(helper_tests, "string_helpers.string_escape_mem_any_np");
    try expectContains(helper_tests, "string_helpers.stringEscapeStr(");
    try expectContains(helper_tests, "string_helpers.string_escape_str_any_np");
    try expectContains(helper_tests, "phase 7 string helpers starter keeps exact-fit, terminator-only, and zero-capacity unescape destinations reviewable");
    try expectContains(helper_tests, "const exact_fit_len = string_helpers.stringUnescape(\"\\n\\r\", &exact_fit, exact_fit.len, string_helpers.UNESCAPE_SPACE);");
    try expectContains(helper_tests, "const terminator_only_len = string_helpers.stringUnescape(\"\\n\\r\", &terminator_only, 1, string_helpers.UNESCAPE_SPACE);");
    try expectContains(helper_tests, "const zero_capacity_len = string_helpers.stringUnescape(\"\\n\", &zero_capacity, 0, string_helpers.UNESCAPE_SPACE);");
    try expectContains(helper_tests, "phase 7 string helpers starter pads bounded copies without reading past the provided source slice");
    try expectContains(helper_tests, "string_helpers.memcpyAndPad(&requested_beyond_source, \"go\", 8, '!');");
    try expectContains(helper_tests, "phase 7 string helpers starter replaces bytes only inside the exported c-string prefix");
    try expectContains(helper_tests, "string_helpers.strreplace(&replace_buf, '-', '_')");
    try expectContains(helper_tests, "string_helpers.stringUnescapeInplace(&selective, string_helpers.UNESCAPE_HEX);");

    const build_file = try readRepoFile(allocator, "zigux/tests/phase7_build.zig");
    defer allocator.free(build_file);
    try expectContains(build_file, "\"phase7_string_helpers.zig\"");
    try expectContains(build_file, "phase7-string-helpers-tests");
}
