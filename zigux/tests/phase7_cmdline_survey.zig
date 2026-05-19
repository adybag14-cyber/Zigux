const std = @import("std");

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    verified_on_utc: []const u8,
    anchor: []const u8,
    current_master_state: []const u8,
    review_surfaces: []const []const u8,
    covered_helpers: []const []const u8,
    missing_paths: []const []const u8,
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

test "phase 7 cmdline survey keeps the returned helper-local packet truthful" {
    const allocator = std.testing.allocator;
    const checker_path = "scripts/zigux/check-phase7-cmdline-packet.py";

    const manifest_json = try readRepoFile(allocator, "zigux/tests/phase7_cmdline_manifest.json");
    defer allocator.free(manifest_json);

    const sequencing_note = try readRepoFile(allocator, "Documentation/zigux/phase7-helper-lane-sequencing.md");
    defer allocator.free(sequencing_note);

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-cmdline-slice.md");
    defer allocator.free(slice_note);

    const helper = try readRepoFile(allocator, "lib/cmdline.zig");
    defer allocator.free(helper);

    const helper_companion = try readRepoFile(allocator, "zigux/tests/phase7_cmdline.zig");
    defer allocator.free(helper_companion);

    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    const samples_readme = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(samples_readme);

    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P7-L10", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("lib/cmdline.c", manifest.anchor);
    try std.testing.expectEqualStrings("helper_slice_test_survey_manifest_anchor", manifest.current_master_state);
    try std.testing.expect(manifest.verified_on_utc.len != 0);
    try std.testing.expectEqual(@as(usize, 0), manifest.missing_paths.len);

    try expectStringSliceContains(manifest.review_surfaces, "Documentation/zigux/phase7-helper-lane-sequencing.md");
    try expectStringSliceContains(manifest.review_surfaces, "Documentation/zigux/phase7-cmdline-slice.md");
    try expectStringSliceContains(manifest.review_surfaces, "lib/cmdline.zig");
    try expectStringSliceContains(manifest.review_surfaces, "zigux/tests/phase7_cmdline.zig");
    try expectStringSliceContains(manifest.review_surfaces, "zigux/tests/phase7_cmdline_survey.zig");
    try expectStringSliceContains(manifest.review_surfaces, "zigux/tests/phase7_cmdline_manifest.json");
    try expectStringSliceContains(manifest.review_surfaces, checker_path);
    try expectStringSliceContains(manifest.review_surfaces, "samples/zigux/README.md");

    try expectStringSliceContains(manifest.covered_helpers, "parseOptionStr");
    try expectStringSliceContains(manifest.covered_helpers, "parse_option_str");
    try expectStringSliceContains(manifest.covered_helpers, "getOption");
    try expectStringSliceContains(manifest.covered_helpers, "get_option");
    try expectStringSliceContains(manifest.covered_helpers, "getOptions");
    try expectStringSliceContains(manifest.covered_helpers, "get_options");
    try expectStringSliceContains(manifest.covered_helpers, "nextArg");
    try expectStringSliceContains(manifest.covered_helpers, "next_arg");
    try expectStringSliceContains(manifest.covered_helpers, "memparse");

    try expectContains(checker, "PHASE7_CMDLINE_PACKET_SELF_TEST=pass");
    try expectContains(checker, "\"Documentation/zigux/phase7-cmdline-slice.md\",");
    try expectContains(checker, "\"lib/cmdline.zig\",");

    try expectContains(slice_note, "`PHASE7_STATUS=helper_local_test_survey_manifest_anchor`");
    try expectContains(slice_note, "`PHASE7_SLICE=cmdline-runtime-leaf`");
    try expectContains(slice_note, "Treat those surfaces as the current helper-local packet for this slice and keep same-lane follow-through inside that returned survey-backed packet.");
    try expectContains(slice_note, "Keep same-lane follow-through limited to the returned helper-local survey-manifest-checker truthfulness packet or one bounded parsing replay proof.");

    try expectContains(sequencing_note, "- cmdline packet, lane `P7-L10`:");
    try expectContains(sequencing_note, "  - `Documentation/zigux/phase7-cmdline-slice.md`");
    try expectContains(sequencing_note, "Fresh helper-local reread for this slot confirmed the dedicated cmdline slice, companion replay, survey, manifest, checker, and no-sample boundary now directly materialize on current `master`");
    try expectContains(sequencing_note, "`P7-L10` owns only cmdline helper-local parity, survey, manifest, checker, or reminder drift;");

    try expectContains(helper, "pub fn parseOptionStr");
    try expectContains(helper, "pub const parse_option_str = parseOptionStr;");
    try expectContains(helper, "pub fn getOption");
    try expectContains(helper, "pub const get_option = getOption;");
    try expectContains(helper, "pub fn getOptions");
    try expectContains(helper, "pub const get_options = getOptions;");
    try expectContains(helper, "pub fn nextArg");
    try expectContains(helper, "pub const next_arg = nextArg;");
    try expectContains(helper, "pub fn memparse");

    try expectContains(helper_companion, "const cmdline = @import(\"cmdline\");");
    try expectContains(helper_companion, "phase 7 cmdline companion replays exact bare-option matching boundaries");
    try expectContains(helper_companion, "phase 7 cmdline companion replays option decoding, ranges, and malformed-input posture");
    try expectContains(helper_companion, "phase 7 cmdline companion replays quoted argument splitting and memparse boundaries");
    try expectContains(helper_companion, "phase 7 cmdline companion replays leading-whitespace sentinels and quoted full-token boundaries");

    try expectStringSliceContains(manifest.ownership_focus, "parseOptionStr() stays bounded to exact comma-delimited bare options inside the exported C-string prefix");
    try expectStringSliceContains(manifest.ownership_focus, "getOption() and getOptions() keep caller-provided state explicit while preserving Linux-style malformed-input, range, and wraparound behavior");
    try expectStringSliceContains(manifest.ownership_focus, "nextArg() and next_arg() keep parameter, optional value, and remaining text borrowed from the caller slice without widening beyond the exported C-string boundary");
    try expectStringSliceContains(manifest.ownership_focus, "memparse() keeps no-conversion, suffix handling, and signed-clamp posture reviewable without widening into separate allocator-backed helper ownership");
    try expectContains(manifest.next_bounded_step, "helper-local survey-manifest-checker truthfulness packet");
    try expectContains(manifest.next_bounded_step, "bounded parsing replay proof");

    try expectContains(samples_readme, "Current `master` still ships no standalone Phase 5 sample-root files here for:");
    try expectContains(samples_readme, "* `*cmdline*`");
    try expectNotContains(samples_readme, "* `cmdline*`");
}
