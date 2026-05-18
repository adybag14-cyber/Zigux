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

fn expectStringSliceContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |item| {
        if (std.mem.eql(u8, item, needle)) return;
    }
    try std.testing.expect(false);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

test "phase 7 cmdline survey keeps the helper-plus-survey-manifest foothold truthful" {
    const allocator = std.testing.allocator;

    const manifest_json = try readRepoFile(allocator, "zigux/tests/phase7_cmdline_manifest.json");
    defer allocator.free(manifest_json);

    const sequencing_note = try readRepoFile(allocator, "Documentation/zigux/phase7-helper-lane-sequencing.md");
    defer allocator.free(sequencing_note);

    const helper = try readRepoFile(allocator, "lib/cmdline.zig");
    defer allocator.free(helper);

    const samples_readme = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(samples_readme);

    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P7-L05", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("lib/cmdline.c", manifest.anchor);
    try std.testing.expectEqualStrings("helper_survey_manifest_foothold", manifest.current_master_state);
    try std.testing.expect(manifest.verified_on_utc.len != 0);

    try expectStringSliceContains(manifest.review_surfaces, "Documentation/zigux/phase7-helper-lane-sequencing.md");
    try expectStringSliceContains(manifest.review_surfaces, "lib/cmdline.zig");
    try expectStringSliceContains(manifest.review_surfaces, "zigux/tests/phase7_cmdline_survey.zig");
    try expectStringSliceContains(manifest.review_surfaces, "zigux/tests/phase7_cmdline_manifest.json");
    try expectStringSliceContains(manifest.review_surfaces, "samples/zigux/README.md");

    try expectStringSliceContains(manifest.covered_helpers, "parseOptionStr");
    try expectStringSliceContains(manifest.covered_helpers, "parse_option_str");
    try expectStringSliceContains(manifest.covered_helpers, "nextArg");
    try expectStringSliceContains(manifest.covered_helpers, "next_arg");
    try expectStringSliceContains(manifest.covered_helpers, "memparse");

    try expectStringSliceContains(manifest.missing_paths, "Documentation/zigux/phase7-cmdline-slice.md");
    try expectStringSliceContains(manifest.missing_paths, "zigux/tests/phase7_cmdline.zig");
    try expectStringSliceContains(manifest.missing_paths, "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig");
    try expectStringSliceContains(manifest.missing_paths, "zigux/tests/phase7_build.zig");
    try expectStringSliceContains(manifest.missing_paths, "scripts/zigux/validate-phase7.py");

    try expectStringSliceContains(manifest.ownership_focus, "parseOptionStr() keeps exact bare-option matching bounded to the exported option-string prefix");
    try expectStringSliceContains(manifest.ownership_focus, "nextArg() and next_arg() keep quoted and unquoted argument parsing bounded to the first NUL while preserving the remaining tail for the caller");
    try expectStringSliceContains(manifest.ownership_focus, "memparse() keeps signed-prefix handling, suffix scaling, and saturation bounded to the caller-provided input slice");
    try expectStringSliceContains(manifest.ownership_focus, "same-lane follow-through stays inside the returned helper, survey, and manifest foothold until a fresh reread proves the slice, dedicated test, fixture, or shared Phase 7 build route returned on current master");
    try expectContains(manifest.next_bounded_step, "helper-local survey-or-manifest truthfulness");

    try expectContains(sequencing_note, "`cmdline` now survives through `lib/cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, and `zigux/tests/phase7_cmdline_manifest.json`.");
    try expectContains(sequencing_note, "the corresponding slice, dedicated test, and fixture packet still returned missing on current `master`.");
    try expectContains(sequencing_note, "That means `P7-L05` should keep same-lane follow-through limited to the returned helper-plus-survey-manifest foothold");
    try expectContains(sequencing_note, "because the current slot could directly reread `lib/cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, and `zigux/tests/phase7_cmdline_manifest.json`");
    try expectContains(sequencing_note, "If the drift is `cmdline`, first confirm whether the helper-plus-survey-manifest foothold");

    try expectContains(helper, "pub fn parseOptionStr");
    try expectContains(helper, "pub const parse_option_str = parseOptionStr;");
    try expectContains(helper, "pub fn nextArg");
    try expectContains(helper, "pub const next_arg = nextArg;");
    try expectContains(helper, "pub fn memparse");
    try expectContains(helper, "test \"memparse applies suffixes before signed clamping\"");
    try expectContains(helper, "test \"memparse keeps signed non-decimal prefixes aligned with suffix handling\"");
    try expectContains(helper, "test \"parseOptionStr matches only exact bare options\"");
    try expectContains(helper, "test \"nextArg stays inside the first NUL for bare and key value tokens\"");
    try expectContains(helper, "test \"nextArg keeps quoted empty values explicit without swallowing the next token\"");

    try expectContains(samples_readme, "Current `master` still ships no standalone Phase 5 sample-root files here for:");
    try expectContains(samples_readme, "* `*cmdline*`");
}
