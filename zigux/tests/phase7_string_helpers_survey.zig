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

test "phase 7 string helpers survey keeps the current missing-helper packet truthful" {
    const allocator = std.testing.allocator;

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-string-helpers-slice.md");
    defer allocator.free(slice_note);
    try expectContains(slice_note, "PHASE7_STATUS=parked");
    try expectContains(slice_note, "current `master` is missing both `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`");
    try expectContains(slice_note, "The most recently described bounded slice covers:");
    try expectContains(slice_note, "The parked review packet still describes tests for:");
    try expectContains(slice_note, "The parked string-helper packet remains recorded in `zigux/tests/phase7_string_helpers_manifest.json`");
    try expectContains(slice_note, "The next honest reopen step is to restore `lib/string_helpers.zig` together with `zigux/tests/phase7_string_helpers.zig`");
    try expectContains(slice_note, "Until those files are back on current `master`, keep this lane limited to same-packet truthfulness repairs");
    try expectNotContains(slice_note, "If the string-helper family reopens, prefer one tiny helper-local parity, survey, or validation sync around the now-landed `kstrdup_quotable()` path before widening into task-owned, file-owned, or device-managed follow-on work.");

    const manifest = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_manifest.json");
    defer allocator.free(manifest);
    try expectContains(manifest, "\"missing_review_surfaces\": [");
    try expectContains(manifest, "\"lib/string_helpers.zig\"");
    try expectContains(manifest, "\"zigux/tests/phase7_string_helpers.zig\"");
    try expectContains(manifest, "\"current_master_truthfulness\":");
    try expectContains(manifest, "\"phase7-string-helpers-helper\"");
    try expectContains(manifest, "\"phase7-string-helpers-dedicated-tests\"");
    try expectContains(manifest, "\"phase7-string-helpers-docs-root-summary\"");
    try expectContains(manifest, "docs-root shared Phase 7 summary still needs a separate same-packet truthfulness refresh");
    try expectContains(manifest, "the shared validate-phase7 surface plus the scripts-root and sample-root Phase 5 no-string-sample reminders still align with the parked slice note, survey gate, and no-sample boundary packet");
    try expectContains(manifest, "\"status\": \"missing_on_master\"");
    try expectNotContains(manifest, "\"phase7-string-helpers-validator-truthfulness\"");
    try expectNotContains(manifest, "\"phase7-string-helpers-scripts-readme-boundary\"");
    try expectNotContains(manifest, "still reads narrower");
    try expectNotContains(manifest, "synced docs-root parked packet");

    const docs_root = try readRepoFile(allocator, "Documentation/zigux/README.md");
    defer allocator.free(docs_root);
    try expectContains(docs_root, "Documentation/zigux/phase7-string-helpers-slice.md");
    try expectContains(docs_root, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    try expectContains(docs_root, "current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample");
    try expectContains(docs_root, "lib/string_helpers.zig");

    const tests_root = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_root);
    try expectContains(tests_root, "scripts/zigux/validate-phase7.py");
    try expectContains(tests_root, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    try expectContains(tests_root, "zigux/tests/phase7_build.zig");

    const samples_root = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(samples_root);
    try expectContains(samples_root, "current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample;");
    try expectContains(samples_root, "treat any new `samples/zigux/*string*.zig` file as review-blocking");
    try expectContains(samples_root, "Documentation/zigux/phase7-string-helpers-slice.md");

    const scripts_root = try readRepoFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_root);
    try expectContains(scripts_root, "validate-phase7.py");
    try expectContains(scripts_root, "Documentation/zigux/review-checklist.md");
    try expectContains(scripts_root, "Documentation/zigux/phase7-string-helpers-slice.md");
    try expectContains(scripts_root, "check-phase7-build-wiring.py");
    try expectContains(scripts_root, "check-phase7-make-wrapper-selftest-alignment.py");
    try expectContains(scripts_root, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    try expectContains(scripts_root, "make -C zigux phase7-validate");
    try expectContains(scripts_root, "current `master` also still ships no standalone `samples/zigux/*string*` Phase 5 reference sample");
    try expectNotContains(scripts_root, "current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample");

    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);
    try expectContains(makefile, "phase7-validate:");
    try expectContains(makefile, "scripts/zigux/validate-phase7.py --self-test");
    try expectContains(makefile, "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py");
    try expectContains(makefile, "phase7: phase7-validate phase7-test");

    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase7.py");
    defer allocator.free(validator);
    try expectContains(validator, "\"zigux/tests/phase7_string_helpers_survey.zig\"");
    try expectContains(validator, "\"scripts/zigux/check-phase7-build-wiring.py\"");

    const alignment_note = try readRepoFile(allocator, "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md");
    defer allocator.free(alignment_note);
    try expectContains(alignment_note, "PHASE7_LANE_KEY=P7-Y05");
    try expectContains(alignment_note, "`scripts/zigux/check-phase7-make-wrapper.py`");
    try expectContains(alignment_note, "`scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`");
    try expectContains(alignment_note, "this note does not reopen `lib/string_helpers.zig`, `lib/cmdline.zig`, `lib/argv_split.zig`, or `lib/rbtree.zig`");

    const alignment_checker = try readRepoFile(allocator, "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py");
    defer allocator.free(alignment_checker);
    try expectContains(alignment_checker, "scripts/zigux/check-phase7-make-wrapper.py");
    try expectContains(alignment_checker, "zigux/Makefile");

    const build_file = try readRepoFile(allocator, "zigux/tests/phase7_build.zig");
    defer allocator.free(build_file);
    try expectContains(build_file, "\"phase7_string_helpers.zig\"");
    try expectContains(build_file, "\"phase7_string_helpers_survey.zig\"");
    try expectContains(build_file, "\"phase7_string_helpers_sample_boundary.zig\"");
}
