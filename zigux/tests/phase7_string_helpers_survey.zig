const std = @import("std");

const Manifest = struct {
    lane_key: []const u8,
    lane_key_note: []const u8,
    phase: []const u8,
    anchor: []const u8,
    direct_repo_anchor: []const u8,
    anchor_state_note: []const u8,
    current_master_state: []const u8,
    review_surfaces: []const []const u8,
    covered_helpers: []const []const u8,
    current_master_truthfulness: []const u8,
    starter_packet_focus: []const []const u8,
    ownership_focus: []const []const u8,
    next_bounded_step: []const u8,
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn stringSliceContains(haystack: []const []const u8, needle: []const u8) bool {
    for (haystack) |item| {
        if (std.mem.eql(u8, item, needle)) return true;
    }
    return false;
}

fn expectStringSliceContains(haystack: []const []const u8, needle: []const u8) !void {
    try std.testing.expect(stringSliceContains(haystack, needle));
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
    try expectContains(slice_note, "`zigux/tests/phase7_string_helpers_format_boundary.zig`");
    try expectContains(slice_note, "the shared no-sample boundary stays reviewable only while `samples/zigux/README.md` keeps the explicit `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*kasprintf*`, and `*strarray*` exclusions aligned with the helper-local boundary test");
    try expectContains(slice_note, "the broader full-family packet that still leaves `parse_int_array_user()` and `devm_kasprintf_strarray()` outside the current `master` helper packet");
    try expectContains(slice_note, "Keep the dedicated checkers, survey, sample-boundary, and format-boundary replays fail-closed on the still-parked `parse_int_array_user()` and `devm_kasprintf_strarray()` follow-ons");

    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase7-string-helpers-packet.py");
    defer allocator.free(checker);
    try expectContains(checker, "PHASE7_STRING_HELPERS_PACKET_SELF_TEST=pass");
    try expectContains(checker, "the explicit `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*kasprintf*`, and `*strarray*` exclusions aligned");
    try expectContains(checker, "* `*printf*`");
    try expectContains(checker, "* `*vsprintf*`");
    try expectContains(checker, "the broader full-family packet that still leaves `parse_int_array_user()` and `devm_kasprintf_strarray()` outside the current `master` helper packet");
    try expectContains(checker, "Keep the dedicated checker, survey, and sample-boundary replays fail-closed on the still-parked `parse_int_array_user()` and `devm_kasprintf_strarray()` follow-ons");
    try expectContains(checker, "Keep the dedicated checkers, survey, sample-boundary, and format-boundary replays fail-closed on the still-parked `parse_int_array_user()` and `devm_kasprintf_strarray()` follow-ons");
    try expectContains(checker, "try expectContains(helper, \\\"pub fn stringIsTerminated(\\\");");
    try expectContains(checker, "try expectContains(helper, \\\"pub fn string_is_terminated(\\\");");
    try expectContains(checker, "try expectContains(helper_tests, \\\"test \\\\\\\"phase 7 string helpers starter keeps termination checks bounded by the caller limit\\\\\\\" {\\\");");
    try expectContains(checker, "try expectContains(manifest, \\\"stringIsTerminated() and string_is_terminated() keep caller-provided bounds explicit and only scan inside the requested prefix\\\");");

    const format_boundary_checker = try readRepoFile(allocator, "scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py");
    defer allocator.free(format_boundary_checker);
    try expectContains(format_boundary_checker, "PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET_SELF_TEST=pass");
    try expectContains(format_boundary_checker, "\"zigux/tests/phase7_string_helpers_format_boundary.zig\",");

    const helper = try readRepoFile(allocator, "lib/string_helpers.zig");
    defer allocator.free(helper);
    try expectContains(helper, "pub fn kstrdupQuotableCmdline(");
    try expectContains(helper, "pub fn kstrdup_quotable_cmdline(");
    try expectContains(helper, "pub fn stringIsTerminated(");
    try expectContains(helper, "pub fn string_is_terminated(");
    try expectContains(helper, "pub fn stringUpper(");
    try expectContains(helper, "pub fn string_upper(");
    try expectContains(helper, "pub fn stringLower(");
    try expectContains(helper, "pub fn string_lower(");
    try expectNotContains(helper, "pub fn devmKasprintfStrarray");
    try expectNotContains(helper, "pub fn devm_kasprintf_strarray");
    try expectNotContains(helper, "pub fn parseIntArrayUser(");
    try expectNotContains(helper, "pub fn parse_int_array_user(");

    const helper_tests = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers.zig");
    defer allocator.free(helper_tests);
    try expectContains(helper_tests, "test \\\"phase 7 string helpers starter quotes cmdlines after collapsing trailing NULs and replacing inter-argument separators\\\" {");
    try expectContains(helper_tests, "test \\\"phase 7 string helpers starter keeps termination checks bounded by the caller limit\\\" {");
    try expectContains(helper_tests, "test \\\"phase 7 string helpers starter uppercases and lowercases only through the exported c-string boundary\\\" {");
    try expectContains(helper_tests, "test \\\"phase 7 string helpers starter reports duplicate-and-replace allocation failure cleanly\\\" {");
    try expectContains(helper_tests, "test \\\"phase 7 string helpers starter keeps rendered size accounting explicit when no payload bytes can be written\\\" {");
    try expectContains(helper_tests, "test \\\"phase 7 string helpers starter keeps exact-fit, terminator-only, and zero-capacity unescape destinations reviewable\\\" {");
    try expectContains(helper_tests, "test \\\"phase 7 string helpers starter keeps zero-capacity and exact-fit escape accounting explicit\\\" {");
    try expectNotContains(helper_tests, "devmKasprintfStrarray");
    try expectNotContains(helper_tests, "devm_kasprintf_strarray");
    try expectNotContains(helper_tests, "parseIntArrayUser");
    try expectNotContains(helper_tests, "parse_int_array_user");

    const manifest_json = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_manifest.json");
    defer allocator.free(manifest_json);
    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;
    try std.testing.expectEqualStrings("helper-local", manifest.lane_key);
    try expectContains(manifest.lane_key_note, "helper-local keeps the expanded string-helpers starter packet separate");
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("lib/string_helpers.c", manifest.anchor);
    try std.testing.expectEqualStrings("lib/string_helpers.zig", manifest.direct_repo_anchor);
    try expectContains(manifest.anchor_state_note, "directly readable current-master helper-local anchor");
    try std.testing.expectEqualStrings("expanded_starter_packet", manifest.current_master_state);

    try expectStringSliceContains(manifest.review_surfaces, "Documentation/zigux/phase7-string-helpers-slice.md");
    try expectStringSliceContains(manifest.review_surfaces, "scripts/zigux/check-phase7-string-helpers-packet.py");
    try expectStringSliceContains(manifest.review_surfaces, "scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py");
    try expectStringSliceContains(manifest.review_surfaces, "lib/string_helpers.zig");
    try expectStringSliceContains(manifest.review_surfaces, "zigux/tests/phase7_string_helpers.zig");
    try expectStringSliceContains(manifest.review_surfaces, "zigux/tests/phase7_string_helpers_survey.zig");
    try expectStringSliceContains(manifest.review_surfaces, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    try expectStringSliceContains(manifest.review_surfaces, "zigux/tests/phase7_string_helpers_format_boundary.zig");
    try expectStringSliceContains(manifest.review_surfaces, "zigux/tests/phase7_string_helpers_manifest.json");
    try expectStringSliceContains(manifest.review_surfaces, "samples/zigux/README.md");

    try expectStringSliceContains(manifest.covered_helpers, "stringIsTerminated");
    try expectStringSliceContains(manifest.covered_helpers, "string_is_terminated");
    try expectStringSliceContains(manifest.covered_helpers, "stringEscapeStrAnyNp");
    try expectStringSliceContains(manifest.covered_helpers, "string_escape_str_any_np");
    try expectStringSliceContains(manifest.covered_helpers, "kstrdupQuotableCmdline");
    try expectStringSliceContains(manifest.covered_helpers, "kstrdup_quotable_cmdline");
    try expectStringSliceContains(manifest.covered_helpers, "parseIntArray");
    try expectStringSliceContains(manifest.covered_helpers, "parse_int_array");
    try expectStringSliceContains(manifest.covered_helpers, "stringUpper");
    try expectStringSliceContains(manifest.covered_helpers, "stringLower");

    try expectContains(manifest.current_master_truthfulness, "still-parked `parse_int_array_user()` user-buffer follow-on");
    try expectContains(manifest.current_master_truthfulness, "`devm_kasprintf_strarray()` follow-on");

    try expectStringSliceContains(manifest.starter_packet_focus, "dedicated helper-local checker-backed packet reviewability");
    try expectStringSliceContains(manifest.starter_packet_focus, "dedicated format-boundary replay for the trace-events formatting companion and broad-format exclusion");

    try expectStringSliceContains(manifest.ownership_focus, "stringIsTerminated() and string_is_terminated() keep caller-provided bounds explicit and only scan inside the requested prefix");
    try expectStringSliceContains(manifest.ownership_focus, "kstrdupQuotableCmdline() keeps returned storage caller-owned, leaves the caller source buffer untouched, collapses trailing and inter-argument NULL separators only inside duplicated command-line storage, and only then applies quotable escaping");
    try expectStringSliceContains(manifest.ownership_focus, "the shared no-sample boundary stays reviewable only while `samples/zigux/README.md` keeps the explicit `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*kasprintf*`, and `*strarray*` exclusions aligned with the helper-local boundary test");
    try std.testing.expectEqualStrings(
        "Keep the dedicated checkers, survey, sample-boundary, and format-boundary replays fail-closed on the still-parked `parse_int_array_user()` and `devm_kasprintf_strarray()` follow-ons, and reopen only when one of those helper-local non-goals lands or the no-sample boundary drifts on current `master`.",
        manifest.next_bounded_step,
    );

    try expectNotContains(manifest_json, "\"devmKasprintfStrarray\"");
    try expectNotContains(manifest_json, "\"devm_kasprintf_strarray\"");
    try expectNotContains(manifest_json, "\"parseIntArrayUser\"");
    try expectNotContains(manifest_json, "\"parse_int_array_user\"");

    const sample_boundary = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    defer allocator.free(sample_boundary);
    try expectContains(sample_boundary, "Keep the dedicated checkers, survey, sample-boundary, and format-boundary replays fail-closed on the still-parked `parse_int_array_user()` and `devm_kasprintf_strarray()` follow-ons");
    try expectContains(sample_boundary, "scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py");
    try expectContains(sample_boundary, "zigux/tests/phase7_string_helpers_format_boundary.zig");
    try expectContains(sample_boundary, "the broader full-family packet that still leaves `parse_int_array_user()` and `devm_kasprintf_strarray()` outside the current `master` helper packet");
    try expectContains(sample_boundary, "Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here.");
    try expectContains(sample_boundary, "kstrdupQuotableFile");
    try expectContains(sample_boundary, "kstrdup_quotable_file");
    try expectContains(sample_boundary, "* `*bitmap*`");
    try expectContains(sample_boundary, "* `*printf*`");
    try expectContains(sample_boundary, "* `*vsprintf*`");

    const format_boundary = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_format_boundary.zig");
    defer allocator.free(format_boundary);
    try expectContains(format_boundary, "phase 7 string helper format boundary keeps the trace-events formatting companion as the only sample-root exception");
    try expectContains(format_boundary, "phase 7 string helper format boundary stays on sample-boundary review surfaces only");
    try expectContains(format_boundary, "Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here.");
    try expectContains(format_boundary, "* `*printf*`");
    try expectContains(format_boundary, "* `*vsprintf*`");
}
