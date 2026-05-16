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
        if (std.mem.indexOf(u8, entry.name, "string") != null) saw_string_file = true;
    }

    try std.testing.expect(!saw_string_file);
    try std.testing.expect(total_zig_files >= 1);
}

test "phase 7 string helper boundary keeps the lane-local helper packet aligned without claiming shared control surfaces" {
    const allocator = std.testing.allocator;
    const io = std.testing.io;

    try std.Io.Dir.cwd().access(io, "lib/string_helpers.zig", .{});
    try std.Io.Dir.cwd().access(io, "zigux/tests/phase7_string_helpers.zig", .{});
    try std.Io.Dir.cwd().access(io, "zigux/tests/phase7_string_helpers_survey.zig", .{});
    try std.Io.Dir.cwd().access(io, "zigux/tests/phase7_string_helpers_manifest.json", .{});
    try std.Io.Dir.cwd().access(io, "samples/zigux/README.md", .{});
    try std.Io.Dir.cwd().access(io, "scripts/zigux/validate-phase7.py", .{});
    try std.Io.Dir.cwd().access(io, "scripts/zigux/check-phase7-make-wrapper.py", .{});
    try std.Io.Dir.cwd().access(io, "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py", .{});
    try std.Io.Dir.cwd().access(io, "scripts/zigux/check-phase7-build-wiring.py", .{});

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
    try expectContains(helper_tests, "phase 7 string helpers starter keeps sibling zero-count results on the shared sentinel after one owner deinitializes");
    try expectContains(helper_tests, "phase 7 string helpers starter keeps sibling string arrays intact when one owner frees its result");
    try expectContains(helper_tests, "phase 7 string helpers starter frees partially built arrays when allocator failure interrupts setup");
    try expectContains(helper_tests, "phase 7 string helpers starter reports overflow before sizing the null-terminated string-array view");
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
    try expectContains(survey, "phase 7 string helpers starter keeps sibling zero-count results on the shared sentinel after one owner deinitializes");
    try expectContains(survey, "phase 7 string helpers starter keeps sibling string arrays intact when one owner frees its result");
    try expectContains(survey, "phase 7 string helpers starter frees partially built arrays when allocator failure interrupts setup");
    try expectContains(survey, "phase 7 string helpers starter reports overflow before sizing the null-terminated string-array view");
    try expectContains(survey, "phase 7 string helpers starter duplicates and replaces only the exported c-string prefix");
    try expectContains(survey, "phase 7 string helpers starter pads bounded copies without reading past the provided source slice");
    try expectContains(survey, "phase 7 string helpers starter replaces bytes only inside the exported c-string prefix");
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
    try expectContains(manifest, "memcpyAndPad() and strreplace() keep writes inside caller-provided destination and exported prefix boundaries");
    try expectNotContains(manifest, "missing_review_surfaces");
    try expectNotContains(manifest, "missing_on_master");

    const samples_readme = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(samples_readme);
    try expectContains(samples_readme, "current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample;");

    // Keep the expanded helper packet tied to the shared validator route without claiming those shared-control files as lane-owned.
    const shared_validator = try readRepoFile(allocator, "scripts/zigux/validate-phase7.py");
    defer allocator.free(shared_validator);
    try expectContains(shared_validator, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    try expectContains(shared_validator, "scripts/zigux/check-phase7-make-wrapper.py");
    try expectContains(shared_validator, "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py");
    try expectContains(shared_validator, "scripts/zigux/check-phase7-build-wiring.py");
    try expectContains(shared_validator, "zigux/tests/phase7_string_helpers_survey.zig");
    try expectContains(shared_validator, "zigux/tests/phase7_string_helpers_manifest.json");
}
