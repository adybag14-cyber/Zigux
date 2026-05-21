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

    try std.testing.expectError(
        error.FileNotFound,
        std.Io.Dir.cwd().access(std.testing.io, "lib/string_helpers_parse_int_array.zig", .{}),
    );

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
    try expectContains(slice_note, "stringEscapeStrAnyNp()");
    try expectContains(slice_note, "string_escape_str_any_np()");
    try expectContains(slice_note, "kasprintfStrarray()");
    try expectContains(slice_note, "kfreeStrarray()");
    try expectContains(slice_note, "kstrdupQuotableCmdline()");
    try expectContains(slice_note, "kstrdup_quotable_cmdline()");
    try expectContains(slice_note, "parseIntArray()");
    try expectContains(slice_note, "parse_int_array()");
    try expectContains(slice_note, "stringUpper()");
    try expectContains(slice_note, "string_upper()");
    try expectContains(slice_note, "stringLower()");
    try expectContains(slice_note, "string_lower()");
    try expectContains(slice_note, "memcpy_and_pad()");
    try expectContains(slice_note, "leading whitespace skipping that stops at the first NUL");
    try expectContains(slice_note, "newline-aware sysfs equality");
    try expectContains(slice_note, "bounded null-sentinel table matching through the first NULL entry");
    try expectContains(slice_note, "bounded string escaping across space, special, null, octal, hex, append-limited dictionary mode, and string-wrapper mode");
    try expectContains(slice_note, "bounded sequential string-array allocation with a NULL-terminated pointer view, C-string prefix handling, zero-length sentinel reuse, and caller-driven teardown");
    try expectContains(slice_note, "bounded parse-int-array decoding for comma-separated lists, positive ranges, first-NUL and explicit-count limits, trailing-invalid-token stop behavior, and clean allocation-failure replay");
    try expectContains(slice_note, "uppercase and lowercase copying that stops at the exported C-string boundary and truncates to caller-owned destination storage");
    try expectContains(slice_note, "exact-fit, terminator-only, and zero-capacity unescape destinations keep caller-owned output bounds explicit");
    try expectContains(slice_note, "reject overflow before sizing the NULL-terminated pointer view");
    try expectContains(slice_note, "quoted file-path duplication that keeps an explicit `<unknown>` fallback for missing inputs while still escaping special characters through the same quotable path");
    try expectContains(slice_note, "quoted cmdline duplication that collapses trailing NULs, replaces inter-argument NULs with spaces, and then reuses the quotable escape path inside caller-owned output");
    try expectContains(slice_note, "`stringUpper()`, `string_upper()`, `stringLower()`, and `string_lower()` keep case-conversion writes inside caller-provided destination storage and stop at the exported C-string boundary");
    try expectContains(slice_note, "the broader full-family packet that still leaves `devm_kasprintf_strarray()` outside the current `master` helper packet");
    try expectContainsCount(slice_note, "the broader full-family packet that still leaves `devm_kasprintf_strarray()` outside the current `master` helper packet", 1);
    try expectContains(slice_note, "`scripts/zigux/check-phase7-string-helpers-packet.py`");
    try expectContains(slice_note, "Keep the dedicated checker, survey, and sample-boundary replays fail-closed on the still-parked `devm_kasprintf_strarray()` follow-on");
    try expectContainsCount(slice_note, "Keep the dedicated checker, survey, and sample-boundary replays fail-closed on the still-parked `devm_kasprintf_strarray()` follow-on", 1);
    try expectContains(slice_note, "Current `master` no longer carries a standalone `lib/string_helpers_parse_int_array.zig` sidecar");
    try expectContains(slice_note, "do not treat a standalone `lib/string_helpers_parse_int_array.zig` sidecar as part of the current helper-local packet");
    try expectNotContains(slice_note, "same-packet truthfulness repairs");

    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase7-string-helpers-packet.py");
    defer allocator.free(checker);
    try expectContains(checker, "PHASE7_STRING_HELPERS_PACKET_SELF_TEST=pass");
    try expectContains(checker, "\"Documentation/zigux/phase7-string-helpers-slice.md\"");
    try expectContains(checker, "\"zigux/tests/phase7_string_helpers_sample_boundary.zig\"");
    try expectContains(checker, "Keep the dedicated checker, survey, and sample-boundary replays fail-closed on the still-parked `devm_kasprintf_strarray()` follow-on");
    try expectContains(checker, "test \\\"phase 7 string helpers starter frees partially built arrays when allocator failure interrupts setup\\\" {");
    try expectContains(checker, "test \\\"phase 7 string helpers starter reports overflow before sizing the null-terminated string-array view\\\" {");

    const manifest = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_manifest.json");
    defer allocator.free(manifest);
    try expectContains(manifest, "\\\"lane_key\\\": \\\"helper-local\\\"");
    try expectContains(manifest, "\\\"lane_key_note\\\": \\\"helper-local keeps the expanded string-helpers starter packet separate from the Phase 7 shared-control lanes. Shared docs-root, validator, Makefile, workflow, and build-route reminders stay with those shared-control lanes.\\\"");
    try expectContains(manifest, "\\\"current_master_state\\\": \\\"expanded_starter_packet\\\"");
    try expectContains(manifest, "\\\"scripts/zigux/check-phase7-string-helpers-packet.py\\\"");
    try expectContains(manifest, "\\\"samples/zigux/README.md\\\"");
    try expectContains(manifest, "quoted cmdline duplication that collapses trailing NULL separators into spaces before escaping special characters");
    try expectContains(manifest, "shared no-sample boundary and helper-local reviewability");
    try expectContains(manifest, "dedicated helper-local checker-backed packet reviewability");
    try expectContains(manifest, "current `master` no longer carries a standalone `lib/string_helpers_parse_int_array.zig` sidecar");
    try expectContains(manifest, "should not drift back into a duplicate standalone `lib/string_helpers_parse_int_array.zig` sidecar");
    try expectContains(manifest, "\\\"next_bounded_step\\\": \\\"Keep the dedicated checker, survey, and sample-boundary replays fail-closed on the still-parked `devm_kasprintf_strarray()` follow-on");
    try expectContainsCount(manifest, "\\\"next_bounded_step\\\": \\\"Keep the dedicated checker, survey, and sample-boundary replays fail-closed on the still-parked `devm_kasprintf_strarray()` follow-on", 1);
    try expectNotContains(manifest, "missing_review_surfaces");
    try expectNotContains(manifest, "\\\"devmKasprintfStrarray\\\"");
    try expectNotContains(manifest, "\\\"devm_kasprintf_strarray\\\"");

    const helper = try readRepoFile(allocator, "lib/string_helpers.zig");
    defer allocator.free(helper);
    try expectContains(helper, "pub fn kstrdupQuotable(");
    try expectContains(helper, "pub fn kstrdupQuotableFile(");
    try expectContains(helper, "pub fn kstrdupQuotableCmdline(");
    try expectContains(helper, "pub fn parseIntArray(");
    try expectNotContains(helper, "pub fn devmKasprintfStrarray");
    try expectNotContains(helper, "pub fn devm_kasprintf_strarray");

    const helper_tests = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers.zig");
    defer allocator.free(helper_tests);
    try expectContains(helper_tests, "phase 7 string helpers starter quotes special log-hazard bytes without widening beyond the exported c-string prefix");
    try expectContains(helper_tests, "phase 7 string helpers starter quotes already-materialized file paths and keeps the missing-file fallback explicit");
    try expectContains(helper_tests, "phase 7 string helpers starter quotes cmdlines after collapsing trailing NULs and replacing inter-argument separators");
    try expectContains(helper_tests, "phase 7 string helpers starter frees partially built arrays when allocator failure interrupts setup");
    try expectContains(helper_tests, "phase 7 string helpers starter reports overflow before sizing the null-terminated string-array view");
    try expectContains(helper_tests, "phase 7 string helpers starter reports parse-int-array allocation failure cleanly");
    try expectContains(helper_tests, "phase 7 string helpers starter reports kstrdupQuotable allocation failure cleanly");
    try expectContains(helper_tests, "phase 7 string helpers starter reports kstrdupQuotableFile allocation failure cleanly");
    try expectContains(helper_tests, "phase 7 string helpers starter reports kstrdupQuotableCmdline allocation failure cleanly");
    try expectContains(helper_tests, "phase 7 string helpers starter reports duplicate-and-replace allocation failure cleanly");

    const samples_readme = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(samples_readme);
    try expectContains(samples_readme, "Current `master` still ships no standalone Phase 5 sample-root files here for:");
    try expectContainsCount(samples_readme, "Current `master` still ships no standalone Phase 5 sample-root files here for:", 1);
    try expectContains(samples_readme, "* `*string*`");
    try expectContains(samples_readme, "* `*cmdline*`");
    try expectContains(samples_readme, "* `*argv*`");
    try expectContains(samples_readme, "* `*rbtree*`");
    try expectContains(samples_readme, "* `*kasprintf*`");
    try expectContains(samples_readme, "* `*strarray*`");
    try expectContains(samples_readme, "Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here.");

    const sample_boundary = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    defer allocator.free(sample_boundary);
    try expectContains(sample_boundary, "phase 7 string helper boundary keeps the no-string-sample policy lane-local");
    try expectContains(sample_boundary, "the broader full-family packet that still leaves `devm_kasprintf_strarray()` outside the current `master` helper packet");
    try expectContains(sample_boundary, "Keep the dedicated checker, survey, and sample-boundary replays fail-closed on the still-parked `devm_kasprintf_strarray()` follow-on");
    try expectNotContains(sample_boundary, "The next bounded follow-through should realign the dedicated survey and sample-boundary replays");
}
