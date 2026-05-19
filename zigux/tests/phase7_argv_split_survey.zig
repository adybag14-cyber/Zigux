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

fn expectStringSliceNotContains(haystack: []const []const u8, needle: []const u8) !void {
    try std.testing.expect(!stringSliceContains(haystack, needle));
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

test "phase 7 argv split survey keeps the returned helper-local packet truthful" {
    const allocator = std.testing.allocator;
    const checker_path = "scripts/zigux/check-phase7-argv-split-packet.py";

    const manifest_json = try readRepoFile(allocator, "zigux/tests/phase7_argv_split_manifest.json");
    defer allocator.free(manifest_json);

    const sequencing_note = try readRepoFile(allocator, "Documentation/zigux/phase7-helper-lane-sequencing.md");
    defer allocator.free(sequencing_note);

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-argv-split-slice.md");
    defer allocator.free(slice_note);

    const helper = try readRepoFile(allocator, "lib/argv_split.zig");
    defer allocator.free(helper);

    const helper_companion = try readRepoFile(allocator, "zigux/tests/phase7_argv_split.zig");
    defer allocator.free(helper_companion);

    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    const samples_readme = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(samples_readme);

    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P7-L09", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("lib/argv_split.c", manifest.anchor);
    try std.testing.expectEqualStrings("helper_slice_test_survey_manifest_anchor", manifest.current_master_state);
    try std.testing.expect(manifest.verified_on_utc.len != 0);

    try expectStringSliceContains(manifest.review_surfaces, "Documentation/zigux/phase7-argv-split-slice.md");
    try expectStringSliceContains(manifest.review_surfaces, "Documentation/zigux/phase7-helper-lane-sequencing.md");
    try expectStringSliceContains(manifest.review_surfaces, "lib/argv_split.zig");
    try expectStringSliceContains(manifest.review_surfaces, "zigux/tests/phase7_argv_split.zig");
    try expectStringSliceContains(manifest.review_surfaces, "zigux/tests/phase7_argv_split_survey.zig");
    try expectStringSliceContains(manifest.review_surfaces, "zigux/tests/phase7_argv_split_manifest.json");
    try expectStringSliceContains(manifest.review_surfaces, checker_path);
    try expectStringSliceContains(manifest.review_surfaces, "samples/zigux/README.md");

    try expectStringSliceContains(manifest.covered_helpers, "countArgc");
    try expectStringSliceContains(manifest.covered_helpers, "argvSplit");
    try expectStringSliceContains(manifest.covered_helpers, "argvSplitWithArgc");
    try expectStringSliceContains(manifest.covered_helpers, "argvFree");
    try expectStringSliceContains(manifest.covered_helpers, "ArgvSplitResult.deinit");
    try expectStringSliceContains(manifest.covered_helpers, "ArgvSplitResult.cArgv");

    try expectStringSliceContains(manifest.missing_paths, "zigux/tests/fixtures/phase7_argv_split_vectors.zig");
    try expectStringSliceNotContains(manifest.missing_paths, "zigux/tests/phase7_argv_split.zig");

    try expectContains(checker, "\"zigux/tests/phase7_argv_split.zig\",");
    try expectContains(checker, "\"PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass\",");
    try expectContains(checker, "phase 7 argv split companion replays copied-storage token ownership");

    try expectStringSliceContains(manifest.ownership_focus, "argvSplit() duplicates the caller input before tokenizing so returned tokens stay inside helper-owned storage");
    try expectStringSliceContains(manifest.ownership_focus, "countArgc(), cStringPrefix(), nextArgSpan(), and nextSplitArgSpan() keep token counting and separator zeroing bounded to the exported C-string prefix");
    try expectStringSliceContains(manifest.ownership_focus, "blank-input results reuse exported empty storage and argv sentinel views without widening beyond the returned packet");
    try expectStringSliceContains(manifest.ownership_focus, "deinit(), argvFree(), allocator-failure cleanup, and overflow rejection keep release ownership explicit without widening beyond the returned argv packet");
    try expectStringSliceContains(manifest.ownership_focus, "the no-standalone-argv sample boundary stays explicit only while `samples/zigux/README.md` keeps `*argv*` listed among the no-extra-sample reminders");
    try expectContains(manifest.next_bounded_step, "fixture vectors");
    try expectContains(manifest.next_bounded_step, "helper-local survey-manifest-checker truthfulness");

    try expectContains(sequencing_note, "- argv-split packet, lane `P7-L09`:");
    try expectContains(sequencing_note, "  - `zigux/tests/phase7_argv_split.zig`");
    try expectContains(sequencing_note, "`P7-L09` owns only argv-split helper-local parity, survey, manifest, fixture, checker, or reminder drift;");

    try expectContains(slice_note, "`PHASE7_STATUS=helper_local_test_packet_landed`");
    try expectContains(slice_note, "`PHASE7_SLICE=argv-split-runtime-leaf`");
    try expectContains(slice_note, "`Documentation/zigux/phase7-argv-split-slice.md`, `lib/argv_split.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `scripts/zigux/check-phase7-argv-split-packet.py`, and `samples/zigux/README.md`.");
    try expectContains(slice_note, "`zigux/tests/fixtures/phase7_argv_split_vectors.zig` explicit as the remaining same-lane follow-on");
    try expectContains(slice_note, "Keep the dedicated argv_split replay, survey, manifest, checker, and no-standalone-argv-sample boundary fail-closed");

    try expectContains(helper, "pub const ArgvSplitResult = struct {");
    try expectContains(helper, "pub fn countArgc");
    try expectContains(helper, "pub fn argvSplit");
    try expectContains(helper, "pub fn argvSplitWithArgc");
    try expectContains(helper, "pub fn argvFree");
    try expectContains(helper, "pub fn deinit(self: *ArgvSplitResult, allocator: std.mem.Allocator) void");
    try expectContains(helper, "pub fn cArgv(self: *const ArgvSplitResult)");
    try expectContains(helper, "fn nextSplitArgSpan");

    try expectContains(helper_companion, "const argv_split = @import(\"argv_split\");");
    try expectContains(helper_companion, "phase 7 argv split companion replays copied-storage token ownership");
    try expectContains(helper_companion, "phase 7 argv split companion replays blank-input sentinel reuse and first-NUL truncation");
    try expectContains(helper_companion, "phase 7 argv split companion replays caller-owned teardown and failure boundaries");

    try expectContains(samples_readme, "Current `master` still ships no standalone Phase 5 sample-root files here for:");
    try expectContains(samples_readme, "* `*argv*`");
    try expectNotContains(samples_readme, "* `argv_split*`");
}