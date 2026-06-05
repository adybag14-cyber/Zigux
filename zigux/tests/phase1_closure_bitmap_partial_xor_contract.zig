const std = @import("std");
const testing = std.testing;

const helper_manifest = @embedFile("fixtures/phase1_helper_manifest.json");
const helper_fixture = @embedFile("fixtures/phase1_helpers.json");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAnyContains(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        if (std.mem.indexOf(u8, haystack, needle) != null) return;
    }

    try testing.expect(false);
}

fn readRepoFile(path: []const u8, max_bytes: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        path,
        testing.allocator,
        .limited(max_bytes),
    );
}

fn readClosureNote() ![]u8 {
    return readRepoFile("Documentation/zigux/phase1-closure.md", 128 * 1024);
}

fn readBitmapHelper() ![]u8 {
    return readRepoFile("tools/lib/bitmap.zig", 256 * 1024);
}

test "phase1 closure note keeps bitmap partial xor review explicit" {
    const closure_note = try readClosureNote();
    defer testing.allocator.free(closure_note);

    try expectContains(closure_note, "PHASE1_BITMAP_PARTIAL_XOR_REVIEW");
    try expectContains(closure_note, "partial_xor_nbits and partial_xor_masked_values");
    try expectContains(closure_note, "shared Phase 1 parity fixture and replay");
    try expectContains(closure_note, "caller-selected bit windows cannot silently leak tail bits beyond nbits");
}

test "phase1 closure note keeps the shared xor packet narrow" {
    const closure_note = try readClosureNote();
    defer testing.allocator.free(closure_note);

    try expectContains(closure_note, "partial_xor_nbits = 4");
    try expectContains(closure_note, "partial_xor_masked_values = [14]");
    try expectContains(closure_note, "single-word packet");
    try expectContains(closure_note, "broader multiword-tail clamp guarantee");
}

test "phase1 helper manifest names the bitmap partial xor fixture fields" {
    try expectContains(helper_manifest, "partial_xor_review_fields");
    try expectContains(helper_manifest, "partial_xor_nbits");
    try expectContains(helper_manifest, "partial_xor_masked_values");
    try expectContains(helper_manifest, "bitmap xor keeps caller-selected bit window");
}

test "bitmap helper keeps partial xor direct anchors review-visible" {
    const bitmap_helper = try readBitmapHelper();
    defer testing.allocator.free(bitmap_helper);

    try expectContains(bitmap_helper, "test \"bitmap xor keeps caller-selected bit window\"");
    try expectContains(bitmap_helper, "xorBits(&dst, &lhs, &rhs, 4)");
    try expectContains(bitmap_helper, "dst[0] & lastWordMask(4)");

    if (std.mem.indexOf(u8, bitmap_helper, "test \"bitmap xor across a multiword tail still lets callers clamp the last word\"") != null) {
        try expectContains(bitmap_helper, "const nbits = bits_per_long + 5");
        try expectContains(bitmap_helper, "dst[1] & lastWordMask(nbits)");
    }
}

test "phase1 helper fixture pins the bounded partial xor witness" {
    try expectAnyContains(helper_fixture, &.{
        "\"partial_xor_nbits\":4",
        "\"partial_xor_nbits\": 4",
    });
    try expectAnyContains(helper_fixture, &.{
        "\"partial_xor_masked_values\":[14]",
        "\"partial_xor_masked_values\": [14]",
    });
}
