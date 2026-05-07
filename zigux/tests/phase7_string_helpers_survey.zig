const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

test "phase 7 string helpers survey keeps the roadmap-backed helper packet reviewable" {
    const allocator = std.testing.allocator;

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-string-helpers-slice.md");
    defer allocator.free(slice_note);
    try expectContains(slice_note, "lib/string_helpers.c");
    try expectContains(slice_note, "lib/string_helpers.zig");
    try expectContains(slice_note, "zigux/tests/phase7_string_helpers.zig");
    try expectContains(slice_note, "zigux/tests/phase7_string_helpers_survey.zig");
    try expectContains(slice_note, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    try expectContains(slice_note, "zig build test --build-file zigux/tests/phase7_build.zig");
    try expectContains(slice_note, "python3 scripts/zigux/validate-phase7.py");
    try expectContains(slice_note, "make -C zigux phase7-validate");
    try expectContains(slice_note, "make -C zigux phase7");
    try expectContains(slice_note, "This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.");
    try expectContains(slice_note, "started as a small runtime-safe leaf batch and now keeps its landed formatting, escaping, and allocator-backed helpers reviewable through the same bounded Zig gates instead of widening into broader ownership families");
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "before deeper formatting, escaping, or allocation-backed helpers are attempted") == null);
    try expectContains(slice_note, "The current bounded slice covers:");
    try expectContains(slice_note, "`kasprintf_strarray()` over the bounded sequential prefix-index ownership path");
    try expectContains(slice_note, "`kfree_strarray()` over the bounded repeated-teardown-safe release path");
    try expectContains(slice_note, "one allocator-backed `kasprintf_strarray()` proof that returns sequential `prefix-index` owned strings together with a trailing null-pointer view for C-style callers");
    try expectContains(slice_note, "one `kfree_strarray()` proof that keeps first-NUL prefix handling, zero-count sentinel reuse, repeated teardown, and setup-failure cleanup safe");
    try expectContains(slice_note, "one allocator-backed quotable duplication proof that hex-escapes control bytes, quotes, and backslashes for log-safe callers while preserving null-input, first-NUL bounds, and allocation-failure cleanup");
    try expectContains(slice_note, "exact-fit, terminator-only, and zero-capacity destination handling for `string_unescape()` so the helper's bounded write discipline stays reviewable");
    try expectContains(slice_note, "zero-capacity escape-destination accounting that still reports the full would-be escaped length without promising an appended terminator");
    try expectContains(slice_note, "If the string-helper family reopens, prefer one tiny helper-local parity, survey, or validation sync around the now-landed `kstrdup_quotable()` path before widening into task-owned, file-owned, or device-managed follow-on work.");

    const docs_root = try readRepoFile(allocator, "Documentation/zigux/README.md");
    defer allocator.free(docs_root);
    try expectContains(docs_root, "Documentation/zigux/phase7-string-helpers-slice.md");
    try expectContains(docs_root, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    try expectContains(docs_root, "current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample");
    try expectContains(docs_root, "lib/string_helpers.zig");
    try expectContains(docs_root, "scripts/zigux/check-phase7-build-wiring.py");

    const tests_root = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_root);
    try expectContains(tests_root, "scripts/zigux/validate-phase7.py");
    try expectContains(tests_root, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    try expectContains(tests_root, "zigux/tests/phase7_build.zig");
    try expectContains(tests_root, "the dedicated `zigux/tests/phase7_string_helpers_sample_boundary.zig` boundary replay");

    const samples_root = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(samples_root);
    try expectContains(samples_root, "current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample;");
    try expectContains(samples_root, "treat any new `samples/zigux/*string*.zig` file as review-blocking");
    try expectContains(samples_root, "Documentation/zigux/phase7-string-helpers-slice.md");
    try expectContains(samples_root, "lib/string_helpers.zig");

    const scripts_root = try readRepoFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_root);
    try expectContains(scripts_root, "validate-phase7.py");
    try expectContains(scripts_root, "check-phase7-build-wiring.py");
    try expectContains(scripts_root, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    try expectContains(scripts_root, "make -C zigux phase7-validate");

    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);
    try expectContains(makefile, "phase7-validate:");
    try expectContains(makefile, "scripts/zigux/validate-phase7.py --self-test");
    try expectContains(makefile, "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py");
    try expectContains(makefile, "phase7: phase7-validate phase7-test");

    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase7.py");
    defer allocator.free(validator);
    try expectContains(validator, "\"zigux/tests/phase7_string_helpers_survey.zig\"");

    const build_file = try readRepoFile(allocator, "zigux/tests/phase7_build.zig");
    defer allocator.free(build_file);
    try expectContains(build_file, "\"phase7_string_helpers.zig\"");
    try expectContains(build_file, "\"phase7_string_helpers_survey.zig\"");
    try expectContains(build_file, "\"phase7-string-helpers-tests\"");
    try expectContains(build_file, "\"phase7-string-helpers-survey-tests\"");
    try expectContains(build_file, "run_string_helpers_survey_tests.setCwd(b.path(\"../..\"));");
    try expectContains(build_file, "\"phase7_string_helpers_sample_boundary.zig\"");
    try expectContains(build_file, "\"phase7-string-helpers-sample-boundary-tests\"");
    try expectContains(build_file, "run_string_helpers_sample_boundary_tests.setCwd(b.path(\"../..\"));");

    const helper_tests = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers.zig");
    defer allocator.free(helper_tests);
    try expectContains(helper_tests, "phase 7 string matching preserves null-terminated search semantics");
    try expectContains(helper_tests, "phase 7 match helpers accept Linux-style all-entries search bounds");
    try expectContains(helper_tests, "phase 7 parseIntArray keeps base and sign parsing explicit");
    try expectContains(helper_tests, "phase 7 parseIntArray respects first-NUL and no-entry behavior");
    try expectContains(helper_tests, "phase 7 parseIntArrayUser copies a bounded user buffer before parsing");
    try expectContains(helper_tests, "phase 7 parseIntArrayUser fails closed on short buffers and empty copied input");
    try expectContains(helper_tests, "phase 7 stringUnescape covers deterministic Linux escape fixtures");
    try expectContains(helper_tests, "phase 7 stringEscapeMem covers the bounded escape subset");
    try expectContains(helper_tests, "phase 7 kstrdupQuotable escapes special log bytes and preserves first-NUL bounds");
    try expectContains(helper_tests, "phase 7 kstrdupQuotable returns null for null inputs and keeps empty results owned");
    try expectContains(helper_tests, "phase 7 kstrdupQuotable frees the owned copy when allocation fails");
    try expectContains(helper_tests, "phase 7 kasprintfStrarray returns sequential owned strings with a null-pointer terminator");
    try expectContains(helper_tests, "phase 7 kasprintfStrarray deinit resets exported views to the zero-count sentinel state");
    try expectContains(helper_tests, "phase 7 kasprintfStrarray frees intermediate allocations when setup fails");
    try expectContains(helper_tests, "phase 7 kfreeStrarray keeps first-NUL prefixes, zero-count reuse, and repeated teardown safe");
    try expectContains(helper_tests, "phase 7 skipSpaces and strim honor C-string whitespace bounds");

    const helper_impl = try readRepoFile(allocator, "lib/string_helpers.zig");
    defer allocator.free(helper_impl);
    try expectContains(helper_impl, "pub fn stringGetSize");
    try expectContains(helper_impl, "pub fn stringUnescape");
    try expectContains(helper_impl, "pub fn stringEscapeMem");
    try expectContains(helper_impl, "pub fn kstrdupQuotable");
    try expectContains(helper_impl, "pub fn kasprintfStrarray");
    try expectContains(helper_impl, "pub fn skipSpaces");
    try expectContains(helper_impl, "pub fn strim");
    try expectContains(helper_impl, "test \"matchString stops at null sentinels and returns -EINVAL on miss\"");
    try expectContains(helper_impl, "test \"sysfsMatchString reuses sysfs newline semantics\"");
    try expectContains(helper_impl, "test \"stringGetSize formats decimal and binary units with Linux-style rounding\"");
    try expectContains(helper_impl, "test \"stringGetSize respects no-space and no-bytes modifiers\"");
    try expectContains(helper_impl, "test \"stringGetSize reports truncated output length without losing termination\"");
    try expectContains(helper_impl, "test \"stringGetSize handles zero block size and zero-length outputs safely\"");
    try expectContains(helper_impl, "test \"stringUnescape exact-fit destination still decodes an escape\"");
    try expectContains(helper_impl, "test \"stringUnescape keeps terminator-only and zero-capacity destinations bounded\"");
    try expectContains(helper_impl, "test \"kstrdupQuotable frees the owned copy when allocation fails\"");
    try expectContains(helper_impl, "test \"kasprintfStrarray frees intermediate allocations when setup fails\"");
    try expectContains(helper_impl, "std.testing.checkAllAllocationFailures");
}
