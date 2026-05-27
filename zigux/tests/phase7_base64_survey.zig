const std = @import("std");

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    verified_on_utc: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    current_master_state: []const u8,
    review_surfaces: []const []const u8,
    covered_helpers: []const []const u8,
    ownership_focus: []const []const u8,
    next_bounded_step: []const u8,
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.fs.cwd().readFileAlloc(allocator, path, 256 * 1024);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectStringSliceContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |item| {
        if (std.mem.eql(u8, item, needle)) return;
    }
    try std.testing.expect(false);
}

test "phase 7 base64 survey keeps the returned helper-local packet truthful" {
    const allocator = std.testing.allocator;

    const manifest_json = try readRepoFile(allocator, "zigux/tests/phase7_base64_manifest.json");
    defer allocator.free(manifest_json);
    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-base64-slice.md");
    defer allocator.free(slice_note);
    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase7-base64-packet.py");
    defer allocator.free(checker);
    const helper = try readRepoFile(allocator, "lib/base64.zig");
    defer allocator.free(helper);
    const helper_companion = try readRepoFile(allocator, "zigux/tests/phase7_base64.zig");
    defer allocator.free(helper_companion);
    const build_file = try readRepoFile(allocator, "zigux/tests/phase7_base64_build.zig");
    defer allocator.free(build_file);

    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P7-L14", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("lib/base64.c", manifest.anchor);
    try std.testing.expectEqualStrings("helper_slice_test_build_survey_manifest_checker_anchor", manifest.current_master_state);
    try std.testing.expectEqualStrings("lib/base64.zig", manifest.roadmap_destinations[0]);
    try std.testing.expect(manifest.verified_on_utc.len != 0);

    try expectStringSliceContains(manifest.review_surfaces, "Documentation/zigux/phase7-base64-slice.md");
    try expectStringSliceContains(manifest.review_surfaces, "scripts/zigux/check-phase7-base64-packet.py");
    try expectStringSliceContains(manifest.review_surfaces, "lib/base64.zig");
    try expectStringSliceContains(manifest.review_surfaces, "zigux/tests/phase7_base64.zig");
    try expectStringSliceContains(manifest.review_surfaces, "zigux/tests/phase7_base64_build.zig");
    try expectStringSliceContains(manifest.review_surfaces, "zigux/tests/phase7_base64_survey.zig");
    try expectStringSliceContains(manifest.review_surfaces, "zigux/tests/phase7_base64_manifest.json");

    try expectStringSliceContains(manifest.covered_helpers, "bytesStd");
    try expectStringSliceContains(manifest.covered_helpers, "encodeStd");
    try expectStringSliceContains(manifest.covered_helpers, "decodeStd");
    try expectStringSliceContains(manifest.covered_helpers, "encodeUrlsafe");
    try expectStringSliceContains(manifest.covered_helpers, "decodeUrlsafe");
    try expectStringSliceContains(manifest.covered_helpers, "encodeImap");
    try expectStringSliceContains(manifest.covered_helpers, "decodeImap");

    try expectStringSliceContains(manifest.ownership_focus, "variant-pinned convenience wrappers keep the standard, urlsafe, and IMAP alphabets explicit without widening into shared streaming ownership");
    try expectContains(manifest.next_bounded_step, "helper-local base64 packet");

    try expectContains(slice_note, "`PHASE7_STATUS=helper_local_slice_note_test_build_survey_manifest_checker_anchor`");
    try expectContains(slice_note, "`PHASE7_SLICE=base64-runtime-leaf`");
    try expectContains(slice_note, "`PHASE7_LANE_KEY=P7-L14`");
    try expectContains(slice_note, "`lib/base64.zig`");
    try expectContains(slice_note, "`zigux/tests/phase7_base64_build.zig`");
    try expectContains(slice_note, "urlsafe short tails stay inside the urlsafe alphabet and reject standard `+`-prefixed foreign tails");

    try expectContains(checker, "PHASE7_BASE64_PACKET=pass");
    try expectContains(checker, "PHASE7_BASE64_PACKET_SELF_TEST=pass");
    try expectContains(checker, "zigux/tests/phase7_base64_build.zig");
    try expectContains(checker, "lib/base64.zig");

    try expectContains(helper, "pub const Variant = enum {");
    try expectContains(helper, "pub fn bytesStd(src: []const u8, padding: bool) DecodeError!usize {");
    try expectContains(helper, "pub fn encodeStd(dst: []u8, src: []const u8, padding: bool) EncodeError!usize {");
    try expectContains(helper, "pub fn decodeStd(dst: []u8, src: []const u8, padding: bool) DecodeError!usize {");
    try expectContains(helper, "pub fn encodeUrlsafe(dst: []u8, src: []const u8, padding: bool) EncodeError!usize {");
    try expectContains(helper, "pub fn decodeUrlsafe(dst: []u8, src: []const u8, padding: bool) DecodeError!usize {");
    try expectContains(helper, "pub fn encodeImap(dst: []u8, src: []const u8, padding: bool) EncodeError!usize {");
    try expectContains(helper, "pub fn decodeImap(dst: []u8, src: []const u8, padding: bool) DecodeError!usize {");
    try expectContains(helper, "test \"variant-pinned convenience helpers mirror the generic api\" {");

    try expectContains(helper_companion, "phase 7 base64 companion replays standard padded convenience wrappers");
    try expectContains(helper_companion, "phase 7 base64 companion replays urlsafe short-tail wrappers without crossing into standard tails");
    try expectContains(helper_companion, "phase 7 base64 companion replays IMAP short-tail wrappers without slash-backed standard tails");
    try expectContains(helper_companion, "phase 7 base64 companion replays exact-span slice and allocator companions");

    try expectContains(build_file, "../../lib/base64.zig");
    try expectContains(build_file, "phase7_base64.zig");
    try expectContains(build_file, "root_module.addImport(\"base64\", base64_module);");
    try expectContains(build_file, "\"phase7-base64-test\"");
}
