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

test "phase 7 cmdline survey keeps the helper-plus-survey foothold truthful" {
    const allocator = std.testing.allocator;

    const sequencing_note = try readRepoFile(allocator, "Documentation/zigux/phase7-helper-lane-sequencing.md");
    defer allocator.free(sequencing_note);

    const helper = try readRepoFile(allocator, "lib/cmdline.zig");
    defer allocator.free(helper);

    const samples_readme = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(samples_readme);

    try expectContains(sequencing_note, "`cmdline` now survives through `lib/cmdline.zig` plus `zigux/tests/phase7_cmdline_survey.zig`.");
    try expectContains(sequencing_note, "the corresponding slice, dedicated test, manifest, and fixture packet still returned missing on current `master`.");
    try expectContains(sequencing_note, "That means `P7-L05` should keep same-lane follow-through limited to the returned helper plus survey foothold");
    try expectContains(sequencing_note, "because the current slot could directly reread `lib/cmdline.zig` plus `zigux/tests/phase7_cmdline_survey.zig`");
    try expectContains(sequencing_note, "If the drift is `cmdline`, first confirm whether the helper-plus-survey foothold");
    try expectContains(sequencing_note, "`Documentation/zigux/phase7-cmdline-slice.md`");
    try expectContains(sequencing_note, "`zigux/tests/phase7_cmdline.zig`");
    try expectContains(sequencing_note, "`zigux/tests/phase7_cmdline_manifest.json`");
    try expectContains(sequencing_note, "`zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`");
    try expectContains(sequencing_note, "keep same-lane work limited to that returned helper-plus-survey foothold or to reminder truthfulness");
    try expectNotContains(sequencing_note, "`cmdline` now survives only through a helper-only foothold in this environment.");

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
