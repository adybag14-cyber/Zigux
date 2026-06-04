const std = @import("std");

const default_closure_path = "Documentation/zigux/phase1-closure.md";
const default_manifest_path = "zigux/tests/fixtures/phase1_helper_manifest.json";

const string_review_guard_marker =
    "`PHASE1_STRING_REVIEW_GUARD=python3 scripts/zigux/check-phase1-string-review-packet.py exact-checks helper-local string anchors plus the committed replaceChar and current string fixture packet across the helper, closure note, lane note, manifest, and fixture`";

const memparse_review_anchors =
    "\"memparse_review_anchors\": [\n" ++
    "        \"test \\\"memparse handles decimal hexadecimal octal and suffixes\\\"\",\n" ++
    "        \"test \\\"memparse keeps original rest when sign is not followed by digits\\\"\",\n" ++
    "        \"test \\\"memparse saturates signed overflow instead of trapping\\\"\",\n" ++
    "        \"test \\\"memparse clamps explicit positive signed overflow\\\"\",\n" ++
    "        \"test \\\"memparse keeps signed values and their trailing rest aligned\\\"\",\n" ++
    "        \"test \\\"memparse consumes suffix after saturation\\\"\",\n" ++
    "        \"test \\\"memparse applies suffixes before signed clamping\\\"\"\n" ++
    "      ]";

const memparse_review_summary =
    "\"memparse_review_summary\": \"helper-local memparse safety anchors stay explicit through the direct string tests so sign-prefixed invalid input preserves rest, signed inputs keep their trailing-rest split aligned with unsigned parsing, implicit and explicit signed overflow clamp instead of trapping, and suffixes are still consumed after saturation\"";

const next_safe_step_note =
    "\"next_safe_step_note\": \"If this helper lane reopens, keep the helper-local strlcat, sysfs, case-insensitive compare, and match-or-terminator review anchors aligned across the string review packet and this lane note unless dedicated shared fixture keys land; do not reopen missing closure-side validator names by default.\"";

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "closure note keeps string review routed through the current guard" {
    const closure = try readRepoFile(default_closure_path, 96 * 1024);
    defer std.testing.allocator.free(closure);

    try expectContains(closure, string_review_guard_marker);
    try expectContains(closure, "Current `master` now also spells the helper-local `memtostr()`, `memtostrPad()`, and `memtostr_pad()` anchors directly in the shipped manifest-backed string review packet");
    try expectNotContains(closure, "`PHASE1_STRING_MEMPARSE_REVIEW=");
    try expectNotContains(closure, "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`");
}

test "manifest keeps the memparse safety anchor packet explicit" {
    const manifest = try readRepoFile(default_manifest_path, 256 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, "\"tools/lib/string.zig\": {");
    try expectContains(manifest, memparse_review_anchors);
    try expectContains(manifest, memparse_review_summary);
}

test "memparse review stays helper-local and outside shared fixture ownership" {
    const manifest = try readRepoFile(default_manifest_path, 256 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, next_safe_step_note);
    try expectContains(manifest, "\"parity_fixture_keys\": [\n        \"strtobool_y\",");
    try expectNotContains(manifest, "\"memparse_decimal\"");
    try expectNotContains(manifest, "\"memparse_signed_overflow\"");
    try expectNotContains(manifest, "\"memparse_suffix_after_saturation\"");
}
