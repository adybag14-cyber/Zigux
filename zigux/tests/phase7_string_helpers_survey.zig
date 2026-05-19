const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    if (needle.len == 0) return 0;

    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    return count;
}

fn expectContainsCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    try std.testing.expectEqual(expected, countOccurrences(haystack, needle));
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

test "phase 7 string helpers survey keeps the expanded starter packet truthful" {
    const allocator = std.testing.allocator;

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-string-helpers-slice.md");
    defer allocator.free(slice_note);
    try expectContains(slice_note, "PHASE7_STATUS=starter_landed");
    try expectContains(slice_note, "PHASE7_SLICE=string-helpers-runtime-leaf");
    try expectContains(slice_note, "expanded starter packet");
    try expectContains(slice_note, "`samples/zigux/README.md`");
    try expectContains(slice_note, "string_get_size()");
    try expectContains(slice_note, "stringEscapeMem()");
    try expectContains(slice_note, "string_escape_mem()");
    try expectContains(slice_note, "stringEscapeMemAnyNp()");
    try expectContains(slice_note, "stringEscapeStr()");
    try expectContains(slice_note, "string_escape_str()");
    try expectContains(slice_note, "string_escape_str_any_np()");
    try expectContains(slice_note, "kasprintfStrarray()");
    try expectContains(slice_note, "kfreeStrarray()");
    try expectContains(slice_note, "kstrdupQuotableCmdline()");
    try expectContains(slice_note, "kstrdup_quotable_cmdline()");
    try expectContains(slice_note, "parseIntArray()");
    try expectContains(slice_note, "parse_int_array()");
    try expectContains(slice_note, "memcpy_and_pad()");
    try expectContains(slice_note, "leading whitespace skipping that stops at the first NUL");
    try expectContains(slice_note, "newline-aware sysfs equality");
    try expectContains(slice_note, "bounded null-sentinel table matching through the first NULL entry");
    try expectContains(slice_note, "bounded string escaping across space, special, null, octal, hex, append-limited dictionary mode, and string-wrapper mode");
    try expectContains(slice_note, "bounded sequential string-array allocation with a NULL-terminated pointer view, C-string prefix handling, zero-length sentinel reuse, and caller-driven teardown");
    try expectContains(slice_note, "bounded parse-int-array decoding for comma-separated lists, positive ranges, first-NUL and explicit-count limits, trailing-invalid-token stop behavior, and clean allocation-failure replay");
    try expectContains(slice_note, "exact-fit, terminator-only, and zero-capacity unescape destinations keep caller-owned output bounds explicit");
    try expectContains(slice_note, "reject overflow before sizing the NULL-terminated pointer view");
    try expectContains(slice_note, "quoted file-path duplication that keeps an explicit `<unknown>` fallback for missing inputs while still escaping special characters through the same quotable path");
    try expectContains(slice_note, "quoted cmdline duplication that collapses trailing NULs, replaces inter-argument NULs with spaces, and then reuses the quotable escape path inside caller-owned output");
    try expectContains(slice_note, "the broader full-family packet that still leaves `devm_kasprintf_strarray()` outside the current `master` helper packet");
    try expectContainsCount(slice_note, "the broader full-family packet that still leaves `devm_kasprintf_strarray()` outside the current `master` helper packet", 1);
    try expectContains(slice_note, "Keep the dedicated survey and sample-boundary replays fail-closed on the still-parked `devm_kasprintf_strarray()` follow-on");
    try expectContainsCount(slice_note, "Keep the dedicated survey and sample-boundary replays fail-closed on the still-parked `devm_kasprintf_strarray()` follow-on", 1);
    try expectNotContains(slice_note, "same-packet truthfulness repairs");

    const manifest = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_manifest.json");
    defer allocator.free(manifest);
    try expectContains(manifest, "\"lane_key\": \"helper-local\"");
    try expectContains(manifest, "\"lane_key_note\": \"helper-local keeps the expanded string-helpers starter packet separate from the Phase 7 shared-control lanes. Shared docs-root, validator, Makefile, workflow, and build-route reminders stay with those shared-control lanes.\"");
    try expectContains(manifest, "\"current_master_state\": \"expanded_starter_packet\"");
    try expectContains(manifest, "\"samples/zigux/README.md\"");
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
    try expectContains(manifest, "\"stringEscapeStrAnyNp\"");
    try expectContains(manifest, "\"string_escape_str_any_np\"");
    try expectContains(manifest, "\"kasprintfStrarray\"");
    try expectContains(manifest, "\"kfreeStrarray\"");
    try expectContains(manifest, "\"kstrdupAndReplace\"");
    try expectContains(manifest, "\"kstrdup_and_replace\"");
    try expectContains(manifest, "\"kstrdupQuotable\"");
    try expectContains(manifest, "\"kstrdup_quotable\"");
    try expectContains(manifest, "\"kstrdupQuotableFile\"");
    try expectContains(manifest, "\"kstrdup_quotable_file\"");
    try expectContains(manifest, "\"kstrdupQuotableCmdline\"");
    try expectContains(manifest, "\"kstrdup_quotable_cmdline\"");
    try expectContains(manifest, "\"parseIntArray\"");
    try expectContains(manifest, "\"parse_int_array\"");
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
    try expectContains(manifest, "kstrdupQuotable() keeps returned storage caller-owned, hex-escapes special logging hazards and double quotes, and still stops at the duplicated exported prefix");
    try expectContains(manifest, "kstrdupQuotableFile() keeps returned storage caller-owned, uses an explicit `<unknown>` fallback for missing file inputs, and otherwise reuses quotable escaping for already-materialized path strings");
    try expectContains(manifest, "kstrdupQuotableCmdline() keeps returned storage caller-owned, collapses trailing and inter-argument NULL separators inside duplicated command-line storage, and only then applies quotable escaping");
    try expectContains(manifest, "parseIntArray() and parse_int_array() keep the returned storage caller-owned, prefix the parsed count, and stop cleanly at the first invalid token, first NUL, or explicit count bound without widening beyond the successful decode set");
    try expectContains(manifest, "the shared no-sample boundary stays reviewable only while `samples/zigux/README.md` keeps the explicit `*string*`, `*cmdline*`, `*argv*`, and `*rbtree*` exclusions aligned with the helper-local boundary test");
    try expectContains(manifest, "shared no-sample boundary and helper-local reviewability");
    try expectContains(manifest, "\"next_bounded_step\": \"Keep the dedicated survey and sample-boundary replays fail-closed on the still-parked `devm_kasprintf_strarray()` follow-on");
    try expectContainsCount(manifest, "\"next_bounded_step\": \"Keep the dedicated survey and sample-boundary replays fail-closed on the still-parked `devm_kasprintf_strarray()` follow-on", 1);
    try expectNotContains(manifest, "\"next_bounded_step\": \"Sync `zigux/tests/phase7_string_helpers_survey.zig` and `zigux/tests/phase7_string_helpers_sample_boundary.zig`\"");
    try expectNotContains(manifest, "validator-backed reviewability");
    try expectNotContains(manifest, "missing_review_surfaces");
    try expectNotContains(manifest, "missing_on_master");
    try expectContains(manifest, "\"anchor\": \"lib/string_helpers.c\"");
    try expectNotContains(manifest, "\"devmKasprintfStrarray\"");
    try expectNotContains(manifest, "\"devm_kasprintf_strarray\"");

    const helper = try readRepoFile(allocator, "lib/string_helpers.zig");
    defer allocator.free(helper);
    try expectContains(helper, "pub fn skipSpaces");
    try expectContains(helper, "pub fn skip_spaces");
    try expectContains(helper, "pub fn trimSpaces");
    try expectContains(helper, "pub fn strim");
    try expectContains(helper, "pub fn sysfsStreq");
    try expectContains(helper, "pub fn sysfs_streq");
    try expectContains(helper, "pub fn matchString");
    try expectContains(helper, "pub fn match_string");
    try expectContains(helper, "pub fn sysfsMatchString");
    try expectContains(helper, "pub fn __sysfs_match_string");
    try expectContains(helper, "pub fn stringGetSize");
    try expectContains(helper, "pub fn string_get_size");
    try expectContains(helper, "pub fn stringUnescape");
    try expectContains(helper, "pub fn string_unescape");
    try expectContains(helper, "pub fn stringUnescapeInplace");
    try expectContains(helper, "pub fn string_unescape_inplace");
    try expectContains(helper, "pub fn stringUnescapeAny");
    try expectContains(helper, "pub fn string_unescape_any");
    try expectContains(helper, "pub fn stringUnescapeAnyInplace");
    try expectContains(helper, "pub fn string_unescape_any_inplace");
    try expectContains(helper, "pub fn stringEscapeMem");
    try expectContains(helper, "pub fn string_escape_mem");
    try expectContains(helper, "pub fn stringEscapeMemAnyNp");
    try expectContains(helper, "pub fn string_escape_mem_any_np");
    try expectContains(helper, "pub fn stringEscapeStr");
    try expectContains(helper, "pub fn string_escape_str");
    try expectContains(helper, "pub fn stringEscapeStrAnyNp");
    try expectContains(helper, "pub fn string_escape_str_any_np");
    try expectContains(helper, "pub const KasprintfStrarrayResult = struct {");
    try expectContains(helper, "pub fn kasprintfStrarray");
    try expectContains(helper, "pub fn kasprintf_strarray");
    try expectContains(helper, "pub fn kfreeStrarray");
    try expectContains(helper, "pub fn kfree_strarray");
    try expectContains(helper, "pub fn parseIntArray");
    try expectContains(helper, "pub fn parse_int_array");
    try expectContains(helper, "pub fn kstrdupAndReplace");
    try expectContains(helper, "pub fn kstrdupQuotable");
    try expectContains(helper, "pub fn kstrdup_quotable");
    try expectContains(helper, "pub fn kstrdupQuotableCmdline");
    try expectContains(helper, "pub fn kstrdup_quotable_cmdline");
    try expectContains(helper, "pub fn memcpyAndPad");
    try expectContains(helper, "pub fn strreplace");
    try expectContains(helper, "pub fn stringUpper");
    try expectContains(helper, "pub fn string_upper");
    try expectContains(helper, "pub fn stringLower");
    try expectContains(helper, "pub fn string_lower");
    try expectContains(helper, "pub fn kstrdupQuotableFile");
    try expectContains(helper, "pub fn kstrdup_quotable_file");
    try expectNotContains(helper, "pub fn devmKasprintfStrarray");
    try expectNotContains(helper, "pub fn devm_kasprintf_strarray");

    const helper_tests = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers.zig");
    defer allocator.free(helper_tests);
    try expectContains(helper_tests, "phase 7 string helpers starter reuses the blank string-array sentinel when no names are requested");
    try expectContains(helper_tests, "phase 7 string helpers starter mirrors kfree_strarray teardown and stays idempotent");
    try expectContains(helper_tests, "phase 7 string helpers starter frees partially built arrays when allocator failure interrupts setup");
    try expectContains(helper_tests, "phase 7 string helpers starter reports overflow before sizing the null-terminated string-array view");
    try expectContains(helper_tests, "phase 7 string helpers starter reports empty parse-int-array input as no entry");
    try expectContains(helper_tests, "phase 7 string helpers starter reports duplicate-and-replace allocation failure cleanly");
    try expectContains(helper_tests, "phase 7 string helpers starter quotes already-materialized file paths and keeps the missing-file fallback explicit");
    try expectNotContains(helper_tests, "devmKasprintfStrarray");
    try expectNotContains(helper_tests, "devm_kasprintf_strarray");

    const samples_readme = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(samples_readme);
    try expectContains(samples_readme, "Current `master` still ships no standalone Phase 5 sample-root files here for:");
    try expectContainsCount(samples_readme, "Current `master` still ships no standalone Phase 5 sample-root files here for:", 1);
    try expectContains(samples_readme, "* `*string*`");
    try expectContainsCount(samples_readme, "* `*string*`", 1);
    try expectContains(samples_readme, "* `*cmdline*`");
    try expectContainsCount(samples_readme, "* `*cmdline*`", 1);
    try expectContains(samples_readme, "* `*argv*`");
    try expectContainsCount(samples_readme, "* `*argv*`", 1);
    try expectContains(samples_readme, "* `*rbtree*`");
    try expectContainsCount(samples_readme, "* `*rbtree*`", 1);
    try expectContains(samples_readme, "* `*kasprintf*`");
    try expectContainsCount(samples_readme, "* `*kasprintf*`", 1);
    try expectContains(samples_readme, "* `*strarray*`");
    try expectContainsCount(samples_readme, "* `*strarray*`", 1);

    try expectContains(slice_note, "do not count `scripts/zigux/validate-phase7.py`");
    try expectContains(slice_note, "do not count `zigux/tests/phase7_build.zig`");

    const sample_boundary = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    defer allocator.free(sample_boundary);
    try expectContains(sample_boundary, "phase 7 string helper boundary keeps the no-string-sample policy lane-local");
    try expectContains(sample_boundary, "phase 7 string helper boundary stays on sample-boundary surfaces only");
    try expectContains(sample_boundary, "the broader full-family packet that still leaves `devm_kasprintf_strarray()` outside the current `master` helper packet");
    try expectContainsCount(sample_boundary, "the broader full-family packet that still leaves `devm_kasprintf_strarray()` outside the current `master` helper packet", 1);
    try expectContains(sample_boundary, "Keep the dedicated survey and sample-boundary replays fail-closed on the still-parked `devm_kasprintf_strarray()` follow-on");
    try expectContainsCount(sample_boundary, "Keep the dedicated survey and sample-boundary replays fail-closed on the still-parked `devm_kasprintf_strarray()` follow-on", 1);
    try expectNotContains(sample_boundary, "The next bounded follow-through should realign the dedicated survey and sample-boundary replays");
}
