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

fn isStandaloneStringSample(name: []const u8) bool {
    if (!std.mem.endsWith(u8, name, ".zig")) return false;
    if (std.mem.eql(u8, name, "trace_events_string_formatting_sample.zig")) return false;
    if (std.mem.startsWith(u8, name, "string")) return true;
    if (std.mem.indexOf(u8, name, "string_helper") != null) return true;
    if (std.mem.indexOf(u8, name, "string_helpers") != null) return true;
    return false;
}

test "phase 7 string helper boundary keeps the no-string-sample policy lane-local" {
    const io = std.testing.io;
    try std.testing.expectError(error.FileNotFound, std.Io.Dir.cwd().access(io, "samples/zigux/string_helpers_sample.zig", .{}));

    var dir = try std.Io.Dir.cwd().openDir(io, "samples/zigux", .{ .iterate = true });
    defer dir.close(io);

    var saw_string_file = false;
    var total_zig_files: usize = 0;

    var iterator = dir.iterate();
    while (try iterator.next(io)) |entry| {
        if (entry.kind != .file) continue;
        if (!std.mem.endsWith(u8, entry.name, ".zig")) continue;

        total_zig_files += 1;
        if (isStandaloneStringSample(entry.name)) saw_string_file = true;
    }

    try std.testing.expect(!saw_string_file);
    try std.testing.expect(total_zig_files >= 1);
}

test "phase 7 string helper boundary stays on sample-boundary surfaces only" {
    const allocator = std.testing.allocator;
    const io = std.testing.io;

    try std.Io.Dir.cwd().access(io, "lib/string_helpers.zig", .{});
    try std.Io.Dir.cwd().access(io, "zigux/tests/phase7_string_helpers.zig", .{});
    try std.Io.Dir.cwd().access(io, "zigux/tests/phase7_string_helpers_survey.zig", .{});
    try std.Io.Dir.cwd().access(io, "zigux/tests/phase7_string_helpers_manifest.json", .{});
    try std.Io.Dir.cwd().access(io, "samples/zigux/README.md", .{});

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-string-helpers-slice.md");
    defer allocator.free(slice_note);
    try expectContains(slice_note, "PHASE7_STATUS=starter_landed");
    try expectContains(slice_note, "expanded starter packet");
    try expectContains(slice_note, "Current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample");
    try expectContains(slice_note, "leading whitespace skipping that stops at the first NUL");
    try expectContains(slice_note, "bounded size rendering with three significant figures, optional separator suppression, and truncation-safe output accounting");
    try expectContains(slice_note, "bounded sequential string-array allocation with a NULL-terminated pointer view, C-string prefix handling, zero-length sentinel reuse, and caller-driven teardown");
    try expectContains(slice_note, "allocator-backed duplicate-and-replace behavior that rewrites only the exported C-string prefix and leaves the source buffer untouched");
    try expectContains(slice_note, "`memcpyAndPad()` and `strreplace()` keep writes inside caller-provided destination and exported prefix boundaries");
    try expectContains(slice_note, "the broader full-family packet that still leaves `kstrdup_quotable_file()` and `devm_kasprintf_strarray()` outside the current `master` helper packet");
    try expectContains(slice_note, "The next bounded follow-through should realign the dedicated survey and sample-boundary replays so they treat `parse_int_array()` as landed and keep only `kstrdup_quotable_file()` plus `devm_kasprintf_strarray()` parked as the remaining helper-local non-goals.");
    try expectNotContains(slice_note, "restored starter packet");
    try expectNotContains(slice_note, "missing both `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`");

    const helper = try readRepoFile(allocator, "lib/string_helpers.zig");
    defer allocator.free(helper);
    try expectContains(helper, "pub const KasprintfStrarrayResult = struct {");
    try expectContains(helper, "pub fn kasprintfStrarray");
    try expectContains(helper, "pub fn kfreeStrarray");
    try expectContains(helper, "pub fn kstrdupAndReplace");
    try expectContains(helper, "pub fn kstrdupQuotable");
    try expectContains(helper, "pub fn kstrdup_quotable");
    try expectContains(helper, "pub fn kstrdupQuotableCmdline");
    try expectContains(helper, "pub fn kstrdup_quotable_cmdline");
    try expectContains(helper, "pub fn parseIntArray");
    try expectContains(helper, "pub fn parse_int_array");
    try expectContains(helper, "pub fn stringEscapeMem");
    try expectContains(helper, "pub fn stringEscapeStrAnyNp");
    try expectContains(helper, "pub fn memcpyAndPad");
    try expectContains(helper, "pub fn strreplace");
    try expectContains(helper, "pub fn stringUpper");
    try expectContains(helper, "pub fn string_upper");
    try expectContains(helper, "pub fn stringLower");
    try expectContains(helper, "pub fn string_lower");

    const helper_tests = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers.zig");
    defer allocator.free(helper_tests);
    try expectContains(helper_tests, "phase 7 string helpers starter covers whitespace trimming and prefix skipping");
    try expectContains(helper_tests, "phase 7 string helpers starter formats bounded sizes with three significant figures");
    try expectContains(helper_tests, "phase 7 string helpers starter escapes bounded memory across flag families and dictionary modes");
    try expectContains(helper_tests, "phase 7 string helpers starter builds sequential string arrays and sentinel views");
    try expectContains(helper_tests, "phase 7 string helpers starter keeps sibling zero-count results on the shared sentinel after one owner deinitializes");
    try expectContains(helper_tests, "phase 7 string helpers starter keeps sibling string arrays intact when one owner frees its result");
    try expectContains(helper_tests, "phase 7 string helpers starter frees partially built arrays when allocator failure interrupts setup");
    try expectContains(helper_tests, "phase 7 string helpers starter reports overflow before sizing the null-terminated string-array view");
    try expectContains(helper_tests, "phase 7 string helpers starter duplicates and replaces only the exported c-string prefix");
    try expectContains(helper_tests, "phase 7 string helpers starter quotes special log-hazard bytes without widening beyond the exported c-string prefix");
    try expectContains(helper_tests, "phase 7 string helpers starter quotes cmdlines after collapsing trailing NULs and replacing inter-argument separators");
    try expectContains(helper_tests, "phase 7 string helpers starter reports kstrdupQuotable allocation failure cleanly");
    try expectContains(helper_tests, "phase 7 string helpers starter reports kstrdupQuotableCmdline allocation failure cleanly");
    try expectContains(helper_tests, "phase 7 string helpers starter reports duplicate-and-replace allocation failure cleanly");
    try expectContains(helper_tests, "parseIntArray parses bounded comma lists and positive ranges");
    try expectContains(helper_tests, "parseIntArray stops at invalid trailing tokens while respecting count and first NUL");
    try expectContains(helper_tests, "parseIntArray reports NoEntry when no integers are available");
    try expectContains(helper_tests, "phase 7 string helpers starter pads bounded copies without reading past the provided source slice");
    try expectContains(helper_tests, "phase 7 string helpers starter replaces bytes only inside the exported c-string prefix");
    try expectContains(helper_tests, "phase 7 string helpers starter uppercases and lowercases only through the exported c-string boundary");

    const survey = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_survey.zig");
    defer allocator.free(survey);
    try expectContains(survey, "phase 7 string helpers survey keeps the helper-local packet truthful");
    try expectContains(survey, "`parseIntArray()` and `parse_int_array()`");
    try expectContains(survey, "bounded parse-int-array helper pair");
    try expectContains(survey, "runParseIntArrayWithFailingAllocator");
    try expectNotContains(survey, "phase 7 string helpers survey keeps the expanded starter packet truthful");
    try expectNotContains(survey, "Documentation/zigux/review-checklist.md");
    try expectNotContains(survey, "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md");
    try expectNotContains(survey, "zigux/tests/phase7_build.zig");

    const manifest = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_manifest.json");
    defer allocator.free(manifest);
    try expectContains(manifest, "\"current_master_state\": \"expanded_starter_packet\"");
    try expectContains(manifest, "\"zigux/tests/phase7_string_helpers_sample_boundary.zig\"");
    try expectContains(manifest, "\"zigux/tests/phase7_string_helpers_survey.zig\"");
    try expectContains(manifest, "\"bounded sequential string-array allocation with NULL-terminated pointer views\"");
    try expectContains(manifest, "kasprintfStrarray() and kfreeStrarray() keep per-string ownership and teardown explicit and let callers tear down partially or fully consumed results without widening beyond the returned array packet");
    try expectContains(manifest, "kstrdupAndReplace() keeps returned storage caller-owned, rewrites only the duplicated exported prefix, and leaves the source buffer untouched");
    try expectContains(manifest, "without overstating the file-path or device-managed follow-ons as landed");
    try expectContains(manifest, "treats `parse_int_array()` as landed and keeps only `kstrdup_quotable_file()` plus `devm_kasprintf_strarray()` outside the current packet");
    try expectContains(manifest, "\"stringEscapeStrAnyNp\"");
    try expectContains(manifest, "\"stringUpper\"");
    try expectContains(manifest, "\"string_upper\"");
    try expectContains(manifest, "\"stringLower\"");
    try expectContains(manifest, "\"string_lower\"");
    try expectContains(manifest, "bounded uppercase and lowercase copies through the exported C-string boundary");
    try expectNotContains(manifest, "missing_review_surfaces");
    try expectNotContains(manifest, "missing_on_master");

    const samples_readme = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(samples_readme);
    try expectContains(samples_readme, "Current `master` still ships no standalone Phase 5 sample-root files here for:");
    try expectContains(samples_readme, "* `*string*`");
    try expectContains(samples_readme, "* `*cmdline*`");
    try expectContains(samples_readme, "* `*argv*`");
    try expectContains(samples_readme, "* `*rbtree*`");

    const sample_boundary = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    defer allocator.free(sample_boundary);
    try expectContains(sample_boundary, "phase 7 string helper boundary keeps the no-string-sample policy lane-local");
    try expectContains(sample_boundary, "phase 7 string helper boundary stays on sample-boundary surfaces only");
}
