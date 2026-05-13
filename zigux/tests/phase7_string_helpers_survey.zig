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

test "phase 7 string helpers survey keeps the restored starter packet truthful" {
    const allocator = std.testing.allocator;

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-string-helpers-slice.md");
    defer allocator.free(slice_note);
    try expectContains(slice_note, "PHASE7_STATUS=starter_landed");
    try expectContains(slice_note, "current `master` now carries both `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`");
    try expectContains(slice_note, "keep the Phase 7 string-helpers lane limited to the restored starter packet");
    try expectContains(slice_note, "The restored starter packet on current `master` covers:");
    try expectContains(slice_note, "The next bounded follow-through should stay inside the restored starter packet");
    try expectNotContains(slice_note, "current `master` is missing both `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`");
    try expectNotContains(slice_note, "same-packet truthfulness repairs");

    const manifest = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_manifest.json");
    defer allocator.free(manifest);
    try expectContains(manifest, "\"current_master_state\": \"restored_starter_packet\"");
    try expectContains(manifest, "\"lib/string_helpers.zig\"");
    try expectContains(manifest, "\"zigux/tests/phase7_string_helpers.zig\"");
    try expectContains(manifest, "\"zigux/tests/phase7_string_helpers_sample_boundary.zig\"");
    try expectContains(manifest, "The helper pair `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig` is back on current master as a restored starter packet.");
    try expectNotContains(manifest, "missing_review_surfaces");
    try expectNotContains(manifest, "missing_on_master");

    const helper = try readRepoFile(allocator, "lib/string_helpers.zig");
    defer allocator.free(helper);
    try expectContains(helper, "pub fn skipSpaces");
    try expectContains(helper, "pub fn trimSpaces");
    try expectContains(helper, "pub fn sysfsStreq");
    try expectContains(helper, "pub fn matchString");
    try expectContains(helper, "pub fn strreplace");

    const helper_tests = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers.zig");
    defer allocator.free(helper_tests);
    try expectContains(helper_tests, "phase 7 string helpers starter covers whitespace trimming and prefix skipping");
    try expectContains(helper_tests, "phase 7 string helpers starter keeps sysfs matching newline aware");
    try expectContains(helper_tests, "phase 7 string helpers starter matches tables through the first null entry");
    try expectContains(helper_tests, "phase 7 string helpers starter replaces bytes only inside the exported c-string prefix");

    const docs_root = try readRepoFile(allocator, "Documentation/zigux/README.md");
    defer allocator.free(docs_root);
    try expectContains(docs_root, "restored starter packet");
    try expectContains(docs_root, "lib/string_helpers.zig");
    try expectContains(docs_root, "zigux/tests/phase7_string_helpers.zig");
    try expectContains(docs_root, "zigux/tests/phase7_string_helpers_sample_boundary.zig");

    const scripts_root = try readRepoFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_root);
    try expectContains(scripts_root, "current `master` still ships no standalone `samples/zigux/*string*` Phase 5 reference sample");
    try expectContains(scripts_root, "lib/string_helpers.zig");
    try expectContains(scripts_root, "zigux/tests/phase7_string_helpers.zig");
    try expectContains(scripts_root, "scripts/zigux/validate-phase7.py");
    try expectContains(scripts_root, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    try expectContains(scripts_root, "make -C zigux phase7-validate");

    const samples_root = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(samples_root);
    try expectContains(samples_root, "current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample;");
    try expectContains(samples_root, "treat any new `samples/zigux/*string*.zig` file as review-blocking");
    try expectContains(samples_root, "lib/string_helpers.zig");
    try expectContains(samples_root, "zigux/tests/phase7_string_helpers.zig");

    const tests_root = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_root);
    try expectContains(tests_root, "zigux/tests/phase7_string_helpers.zig");
    try expectContains(tests_root, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    try expectContains(tests_root, "zigux/tests/phase7_build.zig");

    const build_file = try readRepoFile(allocator, "zigux/tests/phase7_build.zig");
    defer allocator.free(build_file);
    try expectContains(build_file, "\"phase7_string_helpers.zig\"");
    try expectContains(build_file, "\"phase7_string_helpers_sample_boundary.zig\"");
    try expectContains(build_file, "phase7-string-helpers-tests");
    try expectContains(build_file, "phase7-string-helpers-sample-boundary-tests");

    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase7.py");
    defer allocator.free(validator);
    try expectContains(validator, "\"lib/string_helpers.zig\"");
    try expectContains(validator, "\"zigux/tests/phase7_string_helpers.zig\"");
    try expectContains(validator, "restored starter packet");
}
