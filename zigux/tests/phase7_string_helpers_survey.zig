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
    try expectContains(slice_note, "kasprintfStrarray()");
    try expectContains(slice_note, "kfreeStrarray()");
    try expectContains(slice_note, "leading whitespace skipping that stops at the first NUL");
    try expectContains(slice_note, "bounded sequential string-array allocation with a NULL-terminated pointer view");
    try expectContains(slice_note, "The next bounded follow-through should stay inside the helper-local packet");
    try expectNotContains(slice_note, "same-packet truthfulness repairs");

    const shared_note = try readRepoFile(allocator, "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md");
    defer allocator.free(shared_note);
    try expectContains(shared_note, "shared docs-root and scripts-root");
    try expectContains(shared_note, "ownership-focus packet explicit");
    try expectContains(shared_note, "first-NUL trimming and prefix skipping stop at the exported C-string boundary");
    try expectContains(shared_note, "exact-fit and zero-capacity unescape destinations stay caller-owned");
    try expectContains(shared_note, "append-limited escape accounting stays inside caller storage");
    try expectContains(shared_note, "`memcpyAndPad()` plus `strreplace()` stay bounded by caller-provided destinations");

    const manifest = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_manifest.json");
    defer allocator.free(manifest);
    try expectContains(manifest, "\"current_master_state\": \"expanded_starter_packet\"");
    try expectContains(manifest, "\"stringEscapeMem\"");
    try expectContains(manifest, "\"string_escape_mem_any_np\"");
    try expectContains(manifest, "\"stringEscapeStr\"");
    try expectContains(manifest, "\"string_escape_str_any_np\"");
    try expectContains(manifest, "\"kasprintfStrarray\"");
    try expectContains(manifest, "\"kfreeStrarray\"");
    try expectContains(manifest, "\"memcpyAndPad\"");
    try expectContains(manifest, "\"strreplace\"");
    try expectContains(manifest, "bounded sequential string-array allocation with NULL-terminated pointer views");
    try expectContains(manifest, "per-string ownership and teardown");
    try expectContains(manifest, "\"ownership_focus\": [");
    try expectContains(manifest, "kasprintfStrarray() and kfreeStrarray() keep per-string ownership and teardown explicit and let callers tear down partially or fully consumed results without widening beyond the returned array packet");
    try expectNotContains(manifest, "missing_review_surfaces");
    try expectNotContains(manifest, "missing_on_master");

    const helper = try readRepoFile(allocator, "lib/string_helpers.zig");
    defer allocator.free(helper);
    try expectContains(helper, "pub const KasprintfStrarrayResult = struct {");
    try expectContains(helper, "pub fn kasprintfStrarray");
    try expectContains(helper, "pub fn kasprintf_strarray");
    try expectContains(helper, "pub fn kfreeStrarray");
    try expectContains(helper, "pub fn kfree_strarray");
    try expectContains(helper, "fn allocKasprintfStrarrayNullTerminated");
    try expectContains(helper, "pub fn stringEscapeMem");
    try expectContains(helper, "pub fn stringEscapeStrAnyNp");
    try expectContains(helper, "pub fn memcpyAndPad");
    try expectContains(helper, "pub fn strreplace");

    const helper_tests = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers.zig");
    defer allocator.free(helper_tests);
    try expectContains(helper_tests, "phase 7 string helpers starter escapes bounded memory across flag families and dictionary modes");
    try expectContains(helper_tests, "phase 7 string helpers starter builds sequential string arrays and sentinel views");
    try expectContains(helper_tests, "phase 7 string helpers starter reuses the blank string-array sentinel when no names are requested");
    try expectContains(helper_tests, "phase 7 string helpers starter keeps sibling string arrays intact when one owner frees its result");
    try expectContains(helper_tests, "phase 7 string helpers starter mirrors kfree_strarray teardown and stays idempotent");
    try expectContains(helper_tests, "phase 7 string helpers starter frees partially built arrays when allocator failure interrupts setup");
    try expectContains(helper_tests, "phase 7 string helpers starter reports overflow before sizing the null-terminated string-array view");
    try expectContains(helper_tests, "string_helpers.kasprintfStrarray(std.testing.allocator, \"phase7-helper\", 3)");
    try expectContains(helper_tests, "string_helpers.kfreeStrarray(std.testing.allocator, &first);");
    try expectContains(helper_tests, "string_helpers.kfree_strarray(std.testing.allocator, &result);");

    const build_file = try readRepoFile(allocator, "zigux/tests/phase7_build.zig");
    defer allocator.free(build_file);
    try expectContains(build_file, "\"phase7_string_helpers.zig\"");
    try expectContains(build_file, "phase7-string-helpers-tests");
    try expectContains(build_file, "\"phase7_string_helpers_survey.zig\"");
    try expectContains(build_file, "phase7-string-helpers-survey-tests");
}
