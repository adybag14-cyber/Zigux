const std = @import("std");

const pinned_archive_size: u64 = 58_159_088;
const pinned_archive_sha256 = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77";
const pinned_archive_filename = "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz";
const publish_safe_chunk_bytes: u64 = 786_429;
const github_text_ceiling_bytes: u64 = 1_048_576;
const publish_safe_part_count: u64 = 74;
const publish_safe_max_text_bytes: u64 = 1_048_573;

fn divCeilU64(numerator: u64, denominator: u64) u64 {
    return (numerator + denominator - 1) / denominator;
}

fn encodedBase64Bytes(decoded_bytes: u64) u64 {
    return divCeilU64(decoded_bytes, 3) * 4;
}

fn shardTextBytes(decoded_bytes: u64) u64 {
    return encodedBase64Bytes(decoded_bytes) + 1;
}

fn maxShardTextBytes(archive_size: u64, chunk_bytes: u64) u64 {
    const part_count = divCeilU64(archive_size, chunk_bytes);
    var max_text_bytes: u64 = 0;
    var index: u64 = 0;
    while (index < part_count) : (index += 1) {
        const offset = index * chunk_bytes;
        const remaining = archive_size - offset;
        const decoded_bytes = @min(remaining, chunk_bytes);
        max_text_bytes = @max(max_text_bytes, shardTextBytes(decoded_bytes));
    }
    return max_text_bytes;
}

fn requireField(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "Lane 05 publish-safe archive shards stay below text ceiling" {
    try std.testing.expectEqual(publish_safe_part_count, divCeilU64(pinned_archive_size, publish_safe_chunk_bytes));
    try std.testing.expectEqual(publish_safe_max_text_bytes, maxShardTextBytes(pinned_archive_size, publish_safe_chunk_bytes));
    try std.testing.expect(publish_safe_max_text_bytes <= github_text_ceiling_bytes);
}

test "Lane 05 old mebibyte shards exceed text ceiling after base64 encoding" {
    const old_chunk_bytes: u64 = 1_048_576;
    const old_max_text_bytes = maxShardTextBytes(pinned_archive_size, old_chunk_bytes);

    try std.testing.expectEqual(@as(u64, 56), divCeilU64(pinned_archive_size, old_chunk_bytes));
    try std.testing.expect(old_max_text_bytes > github_text_ceiling_bytes);
}

test "Lane 05 archive parts manifest keeps policy-aligned text-ceiling fields" {
    const manifest =
        \\{
        \\  "filename": "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
        \\  "encoding": "base64",
        \\  "sha256": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
        \\  "size": 58159088,
        \\  "chunk_bytes": 786429,
        \\  "part_count": 74,
        \\  "parts_glob": "part-*.b64"
        \\}
    ;

    try requireField(manifest, "\"filename\": \"" ++ pinned_archive_filename ++ "\"");
    try requireField(manifest, "\"encoding\": \"base64\"");
    try requireField(manifest, "\"sha256\": \"" ++ pinned_archive_sha256 ++ "\"");
    try requireField(manifest, "\"size\": 58159088");
    try requireField(manifest, "\"chunk_bytes\": 786429");
    try requireField(manifest, "\"part_count\": 74");
    try requireField(manifest, "\"parts_glob\": \"part-*.b64\"");
}
