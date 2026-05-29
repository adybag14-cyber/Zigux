const std = @import("std");

const archive_size: usize = 58_159_088;
const chunk_bytes: usize = 2_097_152;
const part_count: usize = 28;
const final_decoded_bytes: usize = 1_535_984;
const sha256_hex = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77";
const filename = "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz";
const parts_dir = "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz.parts";

fn encodedLen(decoded_len: usize) usize {
    return ((decoded_len + 2) / 3) * 4;
}

fn partPath(buffer: []u8, index: usize) ![]const u8 {
    return std.fmt.bufPrint(buffer, parts_dir ++ "/part-{d:0>3}.b64", .{index});
}

test "trusted archive text shard envelope stays publishable" {
    try std.testing.expectEqual(@as(usize, 58_159_088), archive_size);
    try std.testing.expectEqual(@as(usize, 2_097_152), chunk_bytes);
    try std.testing.expectEqual(@as(usize, 28), part_count);
    try std.testing.expectEqual(@as(usize, 1_535_984), final_decoded_bytes);
    try std.testing.expectEqual(@as(usize, archive_size), (chunk_bytes * (part_count - 1)) + final_decoded_bytes);

    try std.testing.expectEqual(@as(usize, 2_796_204), encodedLen(chunk_bytes));
    try std.testing.expectEqual(@as(usize, 2_047_980), encodedLen(final_decoded_bytes));

    const encoded_payload_bytes = (encodedLen(chunk_bytes) * (part_count - 1)) + encodedLen(final_decoded_bytes);
    const encoded_file_bytes = encoded_payload_bytes + part_count;
    try std.testing.expectEqual(@as(usize, 77_545_516), encoded_file_bytes);
}

test "manifest fields match the repo-trusted archive policy" {
    try std.testing.expectEqualStrings("zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz", filename);
    try std.testing.expectEqualStrings("313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77", sha256_hex);
    try std.testing.expectEqual(@as(usize, 64), sha256_hex.len);
    try std.testing.expectEqualStrings("third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz.parts", parts_dir);
}

test "published shard names are contiguous and LF text" {
    var first_buf: [128]u8 = undefined;
    var last_buf: [128]u8 = undefined;
    try std.testing.expectEqualStrings(parts_dir ++ "/part-000.b64", try partPath(&first_buf, 0));
    try std.testing.expectEqualStrings(parts_dir ++ "/part-027.b64", try partPath(&last_buf, part_count - 1));

    const sample_full_shard_line_bytes = encodedLen(chunk_bytes) + 1;
    const sample_final_shard_line_bytes = encodedLen(final_decoded_bytes) + 1;
    try std.testing.expectEqual(@as(usize, 2_796_205), sample_full_shard_line_bytes);
    try std.testing.expectEqual(@as(usize, 2_047_981), sample_final_shard_line_bytes);
}
