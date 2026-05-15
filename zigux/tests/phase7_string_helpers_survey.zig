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
    try expectContains(slice_note, "string_get_size()");
    try expectContains(slice_note, "stringEscapeMem()");
    try expectContains(slice_note, "string_escape_mem()");
    try expectContains(slice_note, "stringEscapeMemAnyNp()");
    try expectContains(slice_note, "stringEscapeStr()");
    try expectContains(slice_note, "string_escape_str()");
    try expectContains(slice_note, "string_escape_str_any_np()");
    try expectContains(slice_note, "kasprintfStrarray()");
    try expectContains(slice_note, "kfreeStrarray()");
    try expectContains(slice_note, "memcpy_and_pad()");
    try expectContains(slice_note, "leading whitespace skipping that stops at the first NUL");
    try expectContains(slice_note, "newline-aware sysfs equality");
    try expectContains(slice_note, "bounded null-sentinel table matching through the first NULL entry");
    try expectContains(slice_note, "bounded string escaping across space, special, null, octal, hex, append-limited dictionary mode, and string-wrapper mode");
    try expectContains(slice_note, "bounded sequential string-array allocation with a NULL-terminated pointer view");
    try expectContains(slice_note, "exact-fit, terminator-only, and zero-capacity unescape destinations keep caller-owned output bounds explicit");
    try expectContains(slice_note, "in-place replacement behavior that stops at the first NUL");
    try expectContains(slice_note, "`stringEscapeMem()` keeps append-limited and dictionary-mode output accounting inside caller-owned storage");
    try expectContains(slice_note, "`stringEscapeMemAnyNp()`, `stringEscapeStr()`, and `stringEscapeStrAnyNp()` keep any-NP and first-NUL-bounded string-wrapper escaping inside caller-owned storage");
    try expectContains(slice_note, "`kstrdupAndReplace()` returns caller-owned duplicated storage, applies replacements only inside the duplicated exported prefix, and leaves the source slice unchanged");
    try expectContains(slice_note, "The next bounded follow-through should stay inside the helper-local packet");
    try expectNotContains(slice_note, "same-packet truthfulness repairs");

    const manifest = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_manifest.json");
    defer allocator.free(manifest);
    try expectContains(manifest, "\"lane_key\": \"P7-L04\"");
    try expectContains(manifest, "\"lane_key_note\": \"P7-L04 remains the packet-local helper-slice marker for the expanded string-helpers starter packet. Shared docs-root, validator, Makefile, workflow, and build-route reminders stay with the separate Phase 7 shared-control lanes.\"");
    try expectContains(manifest, "\"current_master_state\": \"expanded_starter_packet\"");
    try expectContains(manifest, "\"sysfsStreq\"");
    try expectContains(manifest, "\"sysfs_streq\"");
    try expectContains(manifest, "\"matchString\"");
    try expectContains(manifest, "\"match_string\"");
    try expectContains(manifest, "\"sysfsMatchString\"");
    try expectContains(manifest, "\"__sysfs_match_string\"");
    try expectContains(manifest, "\"string_get_size\"");
    try expectContains(manifest, "\"stringEscapeMem\"");
    try expectContains(manifest, "\"string_escape_mem\"");
    try expectContains(manifest, "\"stringEscapeMemAnyNp\"");
    try expectContains(manifest, "\"string_escape_mem_any_np\"");
    try expectContains(manifest, "\"stringEscapeStr\"");
    try expectContains(manifest, "\"string_escape_str\"");
    try expectContains(manifest, "\"string_escape_str_any_np\"");
    try expectContains(manifest, "\"kasprintfStrarray\"");
    try expectContains(manifest, "\"kfreeStrarray\"");
    try expectContains(manifest, "\"kstrdupAndReplace\"");
    try expectContains(manifest, "\"kstrdup_and_replace\"");
    try expectContains(manifest, "\"memcpyAndPad\"");
    try expectContains(manifest, "\"memcpy_and_pad\"");
    try expectContains(manifest, "\"strreplace\"");
    try expectContains(manifest, "newline-aware sysfs string equality");
    try expectContains(manifest, "null-sentinel table matching through the first NULL entry");
    try expectContains(manifest, "bounded sequential string-array allocation with NULL-terminated pointer views");
    try expectContains(manifest, "\"ownership_focus\": [");
    try expectContains(manifest, "exact-fit, terminator-only, and zero-capacity unescape destinations keep caller-owned output bounds explicit");
    try expectContains(manifest, "stringEscapeMem() keeps append-limited and dictionary-mode output accounting inside caller-owned storage");
    try expectContains(manifest, "stringEscapeMemAnyNp(), stringEscapeStr(), and stringEscapeStrAnyNp() keep any-NP and first-NUL-bounded string-wrapper escaping explicit without widening beyond caller-owned storage");
    try expectContains(manifest, "kasprintfStrarray() and kfreeStrarray() keep per-string ownership and teardown explicit and let callers tear down partially or fully consumed results without widening beyond the returned array packet");
    try expectContains(manifest, "kstrdupAndReplace() keeps returned storage caller-owned, rewrites only the duplicated exported prefix, and leaves the source buffer untouched");
    try expectContains(manifest, "in-place replacement inside the exported C-string prefix");
    try expectContains(manifest, "\"next_bounded_step\": \"Keep the expanded starter packet truthful across the slice note, helper-local manifest, dedicated survey, and dedicated no-string-sample boundary replay, then take the next helper-local string_helpers expansion only if the remaining non-goals still read the same way everywhere.\"");
    try expectNotContains(manifest, "missing_review_surfaces");
    try expectNotContains(manifest, "missing_on_master");

    const helper = try readRepoFile(allocator, "lib/string_helpers.zig");
    defer allocator.free(helper);
    try expectContains(helper, "pub fn sysfsStreq");
    try expectContains(helper, "pub fn sysfs_streq");
    try expectContains(helper, "pub fn matchString");
    try expectContains(helper, "pub fn match_string");
    try expectContains(helper, "pub fn sysfsMatchString");
    try expectContains(helper, "pub fn __sysfs_match_string");
    try expectContains(helper, "pub const KasprintfStrarrayResult = struct {");
    try expectContains(helper, "pub fn kasprintfStrarray");
    try expectContains(helper, "pub fn kasprintf_strarray");
    try expectContains(helper, "pub fn kfreeStrarray");
    try expectContains(helper, "pub fn kfree_strarray");
    try expectContains(helper, "fn allocKasprintfStrarrayNullTerminated");
    try expectContains(helper, "pub fn kstrdupAndReplace");
    try expectContains(helper, "pub fn kstrdup_and_replace");
    try expectContains(helper, "pub fn stringGetSize");
    try expectContains(helper, "pub fn string_get_size");
    try expectContains(helper, "pub fn stringEscapeMem");
    try expectContains(helper, "pub fn string_escape_mem");
    try expectContains(helper, "pub fn stringEscapeMemAnyNp");
    try expectContains(helper, "pub fn stringEscapeStr");
    try expectContains(helper, "pub fn string_escape_str");
    try expectContains(helper, "pub fn stringEscapeStrAnyNp");
    try expectContains(helper, "pub fn memcpyAndPad");
    try expectContains(helper, "pub fn memcpy_and_pad");
    try expectContains(helper, "pub fn strreplace");

    const helper_tests = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers.zig");
    defer allocator.free(helper_tests);
    try expectContains(helper_tests, "phase 7 string helpers starter covers whitespace trimming and prefix skipping");
    try expectContains(helper_tests, "phase 7 string helpers starter formats bounded sizes with three significant figures");
    try expectContains(helper_tests, "phase 7 string helpers starter keeps sysfs matching newline aware");
    try expectContains(helper_tests, "phase 7 string helpers starter matches tables through the first null entry");
    try expectContains(helper_tests, "phase 7 string helpers starter keeps exact-fit, terminator-only, and zero-capacity unescape destinations reviewable");
    try expectContains(helper_tests, "phase 7 string helpers starter escapes bounded memory across flag families and dictionary modes");
    try expectContains(helper_tests, "phase 7 string helpers starter builds sequential string arrays and sentinel views");
    try expectContains(helper_tests, "phase 7 string helpers starter reuses the blank string-array sentinel when no names are requested");
    try expectContains(helper_tests, "phase 7 string helpers starter keeps sibling zero-count results on the shared sentinel after one owner deinitializes");
    try expectContains(helper_tests, "phase 7 string helpers starter keeps sibling string arrays intact when one owner frees its result");
    try expectContains(helper_tests, "phase 7 string helpers starter mirrors kfree_strarray teardown and stays idempotent");
    try expectContains(helper_tests, "phase 7 string helpers starter frees partially built arrays when allocator failure interrupts setup");
    try expectContains(helper_tests, "phase 7 string helpers starter reports overflow before sizing the null-terminated string-array view");
    try expectContains(helper_tests, "phase 7 string helpers starter duplicates and replaces only the exported c-string prefix");
    try expectContains(helper_tests, "phase 7 string helpers starter pads bounded copies without reading past the provided source slice");
    try expectContains(helper_tests, "phase 7 string helpers starter replaces bytes only inside the exported c-string prefix");
    try expectContains(helper_tests, "const zero_written = string_helpers.string_get_size(42, 0, string_helpers.STRING_UNITS_10, &zero_buf, 0);");
    try expectContains(helper_tests, "const zero_capacity_len = string_helpers.stringUnescape(\"\\n\", &zero_capacity, 0, string_helpers.UNESCAPE_SPACE);");
    try expectContains(helper_tests, "const duplicated = try string_helpers.kstrdupAndReplace(std.testing.allocator, &source, '/', '_');");
    try expectContains(helper_tests, "const alias = try string_helpers.kstrdup_and_replace(std.testing.allocator, \"phase7-helper\", '-', '_');");
    try expectContains(helper_tests, "string_helpers.string_escape_mem_any_np(&[_]u8{ '\\n', 0x7f }, &alias_dst, 0, null);");
    try expectContains(helper_tests, "const string_written = string_helpers.stringEscapeStr(");
    try expectContains(helper_tests, "const any_np_written = string_helpers.string_escape_str_any_np(&[_]u8{ '\\n', 0 }, &any_np_dst, 0, null);");
    try expectContains(helper_tests, "string_helpers.kasprintfStrarray(std.testing.allocator, \"phase7-helper\", 3)");
    try expectContains(helper_tests, "string_helpers.kfreeStrarray(std.testing.allocator, &first);");
    try expectContains(helper_tests, "string_helpers.kfree_strarray(std.testing.allocator, &result);");
    try expectContains(helper_tests, "string_helpers.memcpy_and_pad(&truncated, \"alphabet\", 8, '.');");

    const sample_boundary = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    defer allocator.free(sample_boundary);
    try expectContains(sample_boundary, "phase 7 string helper boundary keeps the exact current sample inventory and no string sample");
    try expectContains(sample_boundary, "phase 7 string helper boundary keeps the lane-local helper packet aligned without claiming shared control surfaces");
    try expectNotContains(sample_boundary, "current shared reminders aligned");
}

test "phase 7 string helper boundary keeps the lane-local helper packet aligned without claiming shared control surfaces" {
    const allocator = std.testing.allocator;

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-string-helpers-slice.md");
    defer allocator.free(slice_note);
    try expectContains(slice_note, "PHASE7_STATUS=starter_landed");
    try expectContains(slice_note, "expanded starter packet");
    try expectContains(slice_note, "leading whitespace skipping that stops at the first NUL");
    try expectContains(slice_note, "bounded size rendering with three significant figures, optional separator suppression, and truncation-safe output accounting");
    try expectContains(slice_note, "bounded sequential string-array allocation with a NULL-terminated pointer view");
    try expectContains(slice_note, "allocator-backed duplicate-and-replace behavior that rewrites only the exported C-string prefix and leaves the source buffer untouched");
    try expectNotContains(slice_note, "restored starter packet");
    try expectNotContains(slice_note, "missing both `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`");

    const helper = try readRepoFile(allocator, "lib/string_helpers.zig");
    defer allocator.free(helper);
    try expectContains(helper, "pub const KasprintfStrarrayResult = struct {");
    try expectContains(helper, "pub fn kasprintfStrarray");
    try expectContains(helper, "pub fn kfreeStrarray");
    try expectContains(helper, "pub fn kstrdupAndReplace");
    try expectContains(helper, "pub fn stringEscapeMem");
    try expectContains(helper, "pub fn stringEscapeStrAnyNp");
    try expectContains(helper, "pub fn memcpyAndPad");
    try expectContains(helper, "pub fn strreplace");

    const helper_tests = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers.zig");
    defer allocator.free(helper_tests);
    try expectContains(helper_tests, "phase 7 string helpers starter covers whitespace trimming and prefix skipping");
    try expectContains(helper_tests, "phase 7 string helpers starter formats bounded sizes with three significant figures");
    try expectContains(helper_tests, "phase 7 string helpers starter escapes bounded memory across flag families and dictionary modes");
    try expectContains(helper_tests, "phase 7 string helpers starter builds sequential string arrays and sentinel views");
    try expectContains(helper_tests, "phase 7 string helpers starter frees partially built arrays when allocator failure interrupts setup");
    try expectContains(helper_tests, "phase 7 string helpers starter reports overflow before sizing the null-terminated string-array view");
    try expectContains(helper_tests, "phase 7 string helpers starter mirrors kfree_strarray teardown and stays idempotent");
    try expectContains(helper_tests, "phase 7 string helpers starter duplicates and replaces only the exported c-string prefix");
    try expectContains(helper_tests, "phase 7 string helpers starter pads bounded copies without reading past the provided source slice");
    try expectContains(helper_tests, "phase 7 string helpers starter replaces bytes only inside the exported c-string prefix");

    const survey = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_survey.zig");
    defer allocator.free(survey);
    try expectContains(survey, "phase 7 string helpers survey keeps the expanded starter packet truthful");
    try expectContains(survey, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    try expectContains(survey, "leading whitespace skipping that stops at the first NUL");
    try expectContains(survey, "phase 7 string helpers starter formats bounded sizes with three significant figures");
    try expectContains(survey, "phase 7 string helpers starter builds sequential string arrays and sentinel views");
    try expectContains(survey, "phase 7 string helpers starter frees partially built arrays when allocator failure interrupts setup");
    try expectContains(survey, "phase 7 string helpers starter reports overflow before sizing the null-terminated string-array view");
    try expectContains(survey, "phase 7 string helpers starter duplicates and replaces only the exported c-string prefix");

    const manifest = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_manifest.json");
    defer allocator.free(manifest);
    try expectContains(manifest, "\"current_master_state\": \"expanded_starter_packet\"");
    try expectContains(manifest, "\"zigux/tests/phase7_string_helpers_sample_boundary.zig\"");
    try expectContains(manifest, "\"zigux/tests/phase7_string_helpers_survey.zig\"");
    try expectContains(manifest, "\"bounded sequential string-array allocation with NULL-terminated pointer views\"");
    try expectContains(manifest, "kasprintfStrarray() and kfreeStrarray() keep per-string ownership and teardown explicit and let callers tear down partially or fully consumed results without widening beyond the returned array packet");
    try expectContains(manifest, "kstrdupAndReplace() keeps returned storage caller-owned, rewrites only the duplicated exported prefix, and leaves the source buffer untouched");
    try expectNotContains(manifest, "missing_review_surfaces");
    try expectNotContains(manifest, "missing_on_master");
}
