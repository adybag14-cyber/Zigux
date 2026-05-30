const std = @import("std");

const expected_filename = "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz";
const expected_sha256 = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77";
const expected_size: u64 = 58_159_088;
const expected_chunk_bytes: u64 = 2_097_152;
const expected_part_count: u64 = 28;
const expected_final_part_bytes: u64 = 1_535_984;
const expected_parts_glob = "part-*.b64";

const Manifest = struct {
    filename: []const u8,
    encoding: []const u8,
    sha256: []const u8,
    size: u64,
    chunk_bytes: u64,
    part_count: u64,
    parts_glob: []const u8,
};

const ContractError = error{
    FilenameMismatch,
    EncodingMismatch,
    Sha256Mismatch,
    SizeMismatch,
    ChunkBytesMismatch,
    PartCountMismatch,
    PartsGlobMismatch,
    FinalPartSizeMismatch,
};

fn expectedPartCount(size: u64, chunk_bytes: u64) u64 {
    return (size + chunk_bytes - 1) / chunk_bytes;
}

fn finalPartBytes(size: u64, chunk_bytes: u64) u64 {
    const remainder = size % chunk_bytes;
    if (remainder == 0) return chunk_bytes;
    return remainder;
}

fn validateManifest(manifest: Manifest) ContractError!void {
    if (!std.mem.eql(u8, manifest.filename, expected_filename)) return error.FilenameMismatch;
    if (!std.mem.eql(u8, manifest.encoding, "base64")) return error.EncodingMismatch;
    if (!std.mem.eql(u8, manifest.sha256, expected_sha256)) return error.Sha256Mismatch;
    if (manifest.size != expected_size) return error.SizeMismatch;
    if (manifest.chunk_bytes != expected_chunk_bytes) return error.ChunkBytesMismatch;
    if (manifest.part_count != expected_part_count) return error.PartCountMismatch;
    if (!std.mem.eql(u8, manifest.parts_glob, expected_parts_glob)) return error.PartsGlobMismatch;
    if (finalPartBytes(manifest.size, manifest.chunk_bytes) != expected_final_part_bytes) {
        return error.FinalPartSizeMismatch;
    }
}

const expected_manifest = Manifest{
    .filename = expected_filename,
    .encoding = "base64",
    .sha256 = expected_sha256,
    .size = expected_size,
    .chunk_bytes = expected_chunk_bytes,
    .part_count = expected_part_count,
    .parts_glob = expected_parts_glob,
};

test "lane05 archive parts manifest pins trusted policy metadata" {
    try std.testing.expectEqualStrings(expected_filename, expected_manifest.filename);
    try std.testing.expectEqualStrings(expected_sha256, expected_manifest.sha256);
    try std.testing.expectEqual(@as(u64, 58_159_088), expected_manifest.size);
    try std.testing.expectEqual(@as(u64, 2_097_152), expected_manifest.chunk_bytes);
    try std.testing.expectEqual(@as(u64, 28), expected_manifest.part_count);
    try std.testing.expectEqualStrings("base64", expected_manifest.encoding);
    try std.testing.expectEqualStrings("part-*.b64", expected_manifest.parts_glob);
    try validateManifest(expected_manifest);
}

test "lane05 archive parts manifest arithmetic preserves the text shard envelope" {
    try std.testing.expectEqual(expected_part_count, expectedPartCount(expected_size, expected_chunk_bytes));
    try std.testing.expectEqual(expected_final_part_bytes, finalPartBytes(expected_size, expected_chunk_bytes));
    try std.testing.expect(expected_final_part_bytes > 0);
    try std.testing.expect(expected_final_part_bytes < expected_chunk_bytes);
}

test "lane05 archive parts manifest rejects stale metadata" {
    var stale = expected_manifest;
    stale.chunk_bytes = 786_432;
    try std.testing.expectError(error.ChunkBytesMismatch, validateManifest(stale));

    stale = expected_manifest;
    stale.part_count = 74;
    try std.testing.expectError(error.PartCountMismatch, validateManifest(stale));

    stale = expected_manifest;
    stale.filename = "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz.part";
    try std.testing.expectError(error.FilenameMismatch, validateManifest(stale));
}

test "lane05 archive parts manifest rejects non-policy shard descriptors" {
    var stale = expected_manifest;
    stale.encoding = "plain";
    try std.testing.expectError(error.EncodingMismatch, validateManifest(stale));

    stale = expected_manifest;
    stale.parts_glob = "*.b64";
    try std.testing.expectError(error.PartsGlobMismatch, validateManifest(stale));

    stale = expected_manifest;
    stale.sha256 = "0000000000000000000000000000000000000000000000000000000000000000";
    try std.testing.expectError(error.Sha256Mismatch, validateManifest(stale));
}
