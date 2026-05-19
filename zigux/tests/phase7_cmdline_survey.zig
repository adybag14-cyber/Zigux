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

test "phase 7 cmdline survey keeps the helper-local packet truthful" {
    const allocator = std.testing.allocator;

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-cmdline-slice.md");
    defer allocator.free(slice_note);
    try expectContains(slice_note, "PHASE7_STATUS=helper_local_packet_landed");
    try expectContains(slice_note, "PHASE7_SLICE=cmdline-runtime-leaf");
    try expectContains(slice_note, "PHASE7_LANE_KEY=helper-local");
    try expectContains(slice_note, "`lib/cmdline.zig`");
    try expectContains(slice_note, "`zigux/tests/phase7_cmdline.zig`");
    try expectContains(slice_note, "`samples/zigux/README.md`");
    try expectContains(slice_note, "`parseOptionStr()` and `parse_option_str`");
    try expectContains(slice_note, "`getOption()` and `get_option`");
    try expectContains(slice_note, "`getOptions()` and `get_options`");
    try expectContains(slice_note, "`nextArg()` and `next_arg`");
    try expectContains(slice_note, "`memparse()`");
    try expectContains(slice_note, "Current `master` still ships no standalone `samples/zigux/*cmdline*` reference sample");
    try expectContains(slice_note, "dedicated helper-local replay coverage rooted at `zigux/tests/phase7_cmdline.zig`");
    try expectContains(slice_note, "Keep the dedicated cmdline helper replay, survey, manifest, and no-standalone-cmdline-sample boundary fail-closed on the current helper-local packet");
    try expectContains(slice_note, "Route adjacent `argv_split`, `string_helpers`, and `rbtree` follow-through to their own Phase 7 helper-local packets.");
    try expectContains(slice_note, "do not count `Documentation/zigux/phase7-rbtree-slice.md`");
    try expectContains(slice_note, "do not count `lib/rbtree.zig`");
    try expectContains(slice_note, "the separate `rbtree` helper-local packet under `lib/`");
    try expectNotContains(slice_note, "Build the matching helper-local review packet for `lib/argv_split.zig`");
    try expectNotContains(slice_note, "do not count missing `lib/rbtree.zig`");
    try expectNotContains(slice_note, "a returned `rbtree` helper-local packet under `lib/`");
    try expectNotContains(slice_note, "standalone string-helper delivery");

    const manifest = try readRepoFile(allocator, "zigux/tests/phase7_cmdline_manifest.json");
    defer allocator.free(manifest);
    try expectContains(manifest, "\"lane_key\": \"helper-local\"");
    try expectContains(manifest, "\"anchor\": \"lib/cmdline.c\"");
    try expectContains(manifest, "\"current_master_state\": \"helper_local_packet\"");
    try expectContains(manifest, "\"lib/cmdline.zig\"");
    try expectContains(manifest, "\"zigux/tests/phase7_cmdline.zig\"");
    try expectContains(manifest, "\"zigux/tests/phase7_cmdline_sample_boundary.zig\"");
    try expectContains(manifest, "\"samples/zigux/README.md\"");
    try expectContains(manifest, "\"parseOptionStr\"");
    try expectContains(manifest, "\"getOption\"");
    try expectContains(manifest, "\"getOptions\"");
    try expectContains(manifest, "\"nextArg\"");
    try expectContains(manifest, "\"memparse\"");
    try expectContains(manifest, "\"next_bounded_step\": \"Keep the dedicated cmdline helper replay, survey, manifest, and no-standalone-cmdline-sample boundary fail-closed on the current helper-local packet");
    try expectNotContains(manifest, "\"next_bounded_step\": \"Build the matching helper-local review packet for `lib/argv_split.zig` while keeping `rbtree` parked");
    try expectNotContains(manifest, "\"stringEscapeMem\"");
    try expectNotContains(manifest, "\"devm_kasprintf_strarray\"");

    const helper = try readRepoFile(allocator, "lib/cmdline.zig");
    defer allocator.free(helper);
    try expectContains(helper, "pub fn parseOptionStr");
    try expectContains(helper, "pub const parse_option_str = parseOptionStr;");
    try expectContains(helper, "pub fn getOption");
    try expectContains(helper, "pub const get_option = getOption;");
    try expectContains(helper, "pub fn getOptions");
    try expectContains(helper, "pub const get_options = getOptions;");
    try expectContains(helper, "pub fn nextArg");
    try expectContains(helper, "pub const next_arg = nextArg;");
    try expectContains(helper, "pub fn memparse");
    try expectContains(helper, "test \"nextArg parses key value pairs and quoted values\"");
    try expectContains(helper, "test \"memparse handles decimal hexadecimal octal and suffixes\"");
    try expectNotContains(helper, "pub fn argvSplit");
    try expectNotContains(helper, "pub fn kstrdupQuotable");

    const helper_companion = try readRepoFile(allocator, "zigux/tests/phase7_cmdline.zig");
    defer allocator.free(helper_companion);
    try expectContains(helper_companion, "const cmdline = @import(\"cmdline\");");
    try expectContains(helper_companion, "phase 7 cmdline companion replays bare-option and integer option boundaries");
    try expectContains(helper_companion, "phase 7 cmdline companion replays nextArg borrowed-slice boundaries");
    try expectContains(helper_companion, "phase 7 cmdline companion replays memparse suffix and unchanged-rest behavior");

    const sample_boundary = try readRepoFile(allocator, "zigux/tests/phase7_cmdline_sample_boundary.zig");
    defer allocator.free(sample_boundary);
    try expectContains(sample_boundary, "phase 7 cmdline boundary keeps the no-standalone-cmdline-sample policy helper-local");
    try expectContains(sample_boundary, "phase 7 cmdline boundary stays rooted in the helper-local packet");
    try expectContains(sample_boundary, "no-standalone-cmdline-sample boundary");
    try expectContains(sample_boundary, "\"samples/zigux/README.md\"");
    try expectContains(sample_boundary, "* `*cmdline*`");

    const samples_readme = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(samples_readme);
    try expectContains(samples_readme, "Current `master` still ships no standalone Phase 5 sample-root files here for:");
    try expectContains(samples_readme, "* `*cmdline*`");
}
