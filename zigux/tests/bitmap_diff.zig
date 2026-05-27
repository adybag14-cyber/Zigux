const std = @import("std");

const Word = u64;
const word_bits: usize = @bitSizeOf(Word);
const bitmap_nbits: usize = 192;
const word_count: usize = bitmap_nbits / word_bits;

const manifest_source = @embedFile("phase4_bitmap_diff_manifest.json");
const bitmap_diff_source = @embedFile("bitmap_diff.zig");

const ThresholdReplay = struct {
    iterations: usize,
    checksum: u64,
    final_weight: usize,
    nth_bit_9: usize,
    first_zero_after_prefix: usize,
};

const Bitmap = struct {
    words: [word_count]Word = [_]Word{0} ** word_count,

    fn clearAll(self: *Bitmap) void {
        @memset(self.words[0..], 0);
    }

    fn setBit(self: *Bitmap, index: usize) !void {
        if (index >= bitmap_nbits) return error.OutOfBounds;
        const word_index = index / word_bits;
        const bit_index: std.math.Log2Int(Word) = @intCast(index % word_bits);
        self.words[word_index] |= (@as(Word, 1) << bit_index);
    }

    fn clearBit(self: *Bitmap, index: usize) !void {
        if (index >= bitmap_nbits) return error.OutOfBounds;
        const word_index = index / word_bits;
        const bit_index: std.math.Log2Int(Word) = @intCast(index % word_bits);
        self.words[word_index] &= ~(@as(Word, 1) << bit_index);
    }

    fn testBit(self: *const Bitmap, index: usize) bool {
        if (index >= bitmap_nbits) return false;
        const word_index = index / word_bits;
        const bit_index: std.math.Log2Int(Word) = @intCast(index % word_bits);
        return (self.words[word_index] & (@as(Word, 1) << bit_index)) != 0;
    }

    fn fillPrefix(self: *Bitmap, nbits: usize) !void {
        self.clearAll();
        for (0..@min(nbits, bitmap_nbits)) |index| {
            try self.setBit(index);
        }
    }

    fn zeroPrefix(self: *Bitmap, nbits: usize) !void {
        try self.zeroRange(0, nbits);
    }

    fn zeroRange(self: *Bitmap, start: usize, len: usize) !void {
        if (start > bitmap_nbits or len > bitmap_nbits - start) return error.OutOfBounds;
        for (start..start + len) |index| {
            try self.clearBit(index);
        }
    }

    fn copyClearTail(self: *Bitmap, other: *const Bitmap, nbits: usize) !void {
        if (nbits > bitmap_nbits) return error.OutOfBounds;
        self.words = other.words;
        for (nbits..bitmap_nbits) |index| {
            try self.clearBit(index);
        }
    }

    fn weight(self: *const Bitmap) usize {
        var total: usize = 0;
        for (self.words) |word| {
            total += @popCount(word);
        }
        return total;
    }

    fn firstZeroBit(self: *const Bitmap) usize {
        for (0..bitmap_nbits) |index| {
            if (!self.testBit(index)) return index;
        }
        return bitmap_nbits;
    }

    fn findNthBit(self: *const Bitmap, nth: usize) !usize {
        var seen: usize = 0;
        for (0..bitmap_nbits) |index| {
            if (!self.testBit(index)) continue;
            if (seen == nth) return index;
            seen += 1;
        }
        return error.NthBitOutOfBounds;
    }
};

fn gitBlobShaHex(source: []const u8) [40]u8 {
    var hasher = std.crypto.hash.Sha1.init(.{});
    hasher.update("blob ");

    var len_buf: [32]u8 = undefined;
    const len_text = std.fmt.bufPrint(&len_buf, "{}", .{source.len}) catch unreachable;
    hasher.update(len_text);
    hasher.update(&[_]u8{0});
    hasher.update(source);

    var digest: [20]u8 = undefined;
    hasher.final(&digest);
    return std.fmt.bytesToHex(digest, .lower);
}

fn expectMarker(haystack: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, marker) != null);
}

fn expectManifestContainsGitBlobSha(
    manifest: []const u8,
    field_name: []const u8,
    source: []const u8,
) !void {
    const blob_sha = gitBlobShaHex(source);
    const marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "\"{s}\": \"{s}\"",
        .{ field_name, blob_sha },
    );
    defer std.testing.allocator.free(marker);
    try expectMarker(manifest, marker);
}

fn runThresholdReplay(iterations: usize) !ThresholdReplay {
    if (iterations == 0) return error.EmptyThresholdReplayBatch;

    var hasher = std.hash.Wyhash.init(0);
    var final_bitmap = Bitmap{};
    var final_nth_bit_9: usize = 0;
    var final_first_zero: usize = 0;

    for (0..iterations) |iteration| {
        var source = Bitmap{};
        try source.fillPrefix(140 + iteration);

        var bitmap = Bitmap{};
        try bitmap.copyClearTail(&source, 96 + iteration);
        try bitmap.zeroRange(12, 5);
        try bitmap.zeroRange(0, 0);
        try bitmap.zeroPrefix(0);
        if ((iteration % 2) == 0) {
            try bitmap.zeroPrefix(3);
        }

        final_nth_bit_9 = try bitmap.findNthBit(9);
        final_first_zero = bitmap.firstZeroBit();
        hasher.update(std.mem.asBytes(&bitmap.words));

        var iteration_buf: [8]u8 = undefined;
        std.mem.writeInt(u64, &iteration_buf, iteration, .little);
        hasher.update(&iteration_buf);

        final_bitmap = bitmap;
    }

    return .{
        .iterations = iterations,
        .checksum = hasher.final(),
        .final_weight = final_bitmap.weight(),
        .nth_bit_9 = final_nth_bit_9,
        .first_zero_after_prefix = final_first_zero,
    };
}

test "phase4 bitmap diff gate keeps exact range and prefix rollback checks explicit" {
    var bitmap = Bitmap{};

    try bitmap.fillPrefix(35);
    try std.testing.expectEqual(@as(usize, 35), bitmap.weight());
    try std.testing.expectEqual(@as(usize, 35), bitmap.firstZeroBit());

    try bitmap.fillPrefix(115);
    try std.testing.expectEqual(@as(usize, 115), bitmap.weight());
    try std.testing.expectEqual(@as(usize, 115), bitmap.firstZeroBit());

    try bitmap.zeroPrefix(35);
    try std.testing.expectEqual(@as(usize, 80), bitmap.weight());
    try std.testing.expectEqual(@as(usize, 35), try bitmap.findNthBit(0));
}

test "phase4 bitmap diff gate keeps zero-length range and prefix no-op checks explicit" {
    var bitmap = Bitmap{};
    try bitmap.fillPrefix(64);
    const before = bitmap.words;

    try bitmap.zeroRange(12, 0);
    try bitmap.zeroPrefix(0);

    try std.testing.expectEqualDeep(before, bitmap.words);
    try std.testing.expectEqual(@as(usize, 64), bitmap.weight());
}

test "phase4 bitmap diff gate keeps copy-tail and zero-length copy invariants explicit" {
    var source = Bitmap{};
    try source.fillPrefix(109);

    var bitmap = Bitmap{};
    try bitmap.fillPrefix(bitmap_nbits);
    try bitmap.copyClearTail(&source, 97);

    try std.testing.expectEqual(@as(usize, 97), bitmap.weight());
    try std.testing.expectEqual(@as(usize, 97), bitmap.firstZeroBit());

    var zero_length_copy = Bitmap{};
    try zero_length_copy.fillPrefix(bitmap_nbits);
    try zero_length_copy.copyClearTail(&source, 0);

    try std.testing.expectEqual(@as(usize, 0), zero_length_copy.weight());
    try std.testing.expectEqual(@as(usize, 0), zero_length_copy.firstZeroBit());
}

test "phase4 bitmap diff gate keeps exact find_nth_bit and out-of-bounds rejection explicit" {
    var bitmap = Bitmap{};
    try bitmap.fillPrefix(32);
    try bitmap.zeroRange(4, 3);

    try std.testing.expectEqual(@as(usize, 0), try bitmap.findNthBit(0));
    try std.testing.expectEqual(@as(usize, 3), try bitmap.findNthBit(3));
    try std.testing.expectEqual(@as(usize, 7), try bitmap.findNthBit(4));
    try std.testing.expectError(error.NthBitOutOfBounds, bitmap.findNthBit(29));
    try std.testing.expectError(error.OutOfBounds, bitmap.zeroRange(191, 2));
}

test "phase4 bitmap diff gate keeps exact 81-bit find_nth_bit window boundary explicit" {
    var bitmap = Bitmap{};
    try bitmap.fillPrefix(81);

    try std.testing.expectEqual(@as(usize, 80), try bitmap.findNthBit(80));
    try std.testing.expectError(error.NthBitOutOfBounds, bitmap.findNthBit(81));
    try std.testing.expectEqual(@as(usize, 81), bitmap.firstZeroBit());
}

test "phase4 bitmap diff gate keeps manifest-backed source inventory explicit" {
    try expectMarker(manifest_source, "\"lane_key\": \"P4-L10\"");
    try expectMarker(manifest_source, "\"roadmap_target_path\": \"zigux/tests/bitmap_diff.zig\"");
    try expectMarker(manifest_source, "\"owner\": \"Shared Subsystems Pod\"");
    try expectMarker(manifest_source, "\"rollback_owner\": \"Shared Subsystems Pod\"");
    try expectMarker(manifest_source, "\"threshold_posture\": \"threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks\"");
    try expectMarker(bitmap_diff_source, "phase4 bitmap diff gate keeps exact 81-bit find_nth_bit window boundary explicit");
    try expectManifestContainsGitBlobSha(manifest_source, "live_gate_blob_sha", bitmap_diff_source);
}

test "phase4 bitmap diff gate keeps checksum-pinned threshold replay checkpoints explicit" {
    try std.testing.expectError(error.EmptyThresholdReplayBatch, runThresholdReplay(0));

    const single = try runThresholdReplay(1);
    const repeated = try runThresholdReplay(4);

    try std.testing.expectEqual(@as(usize, 1), single.iterations);
    try std.testing.expectEqual(@as(usize, 4), repeated.iterations);
    try std.testing.expectEqual(@as(usize, 88), single.final_weight);
    try std.testing.expectEqual(@as(usize, 94), repeated.final_weight);
    try std.testing.expectEqual(@as(usize, 17), single.nth_bit_9);
    try std.testing.expectEqual(@as(usize, 9), repeated.nth_bit_9);
    try std.testing.expectEqual(@as(usize, 0), single.first_zero_after_prefix);
    try std.testing.expectEqual(@as(usize, 12), repeated.first_zero_after_prefix);
    try std.testing.expectEqual(single, try runThresholdReplay(1));
    try std.testing.expectEqual(repeated, try runThresholdReplay(4));
    try std.testing.expect(single.checksum != repeated.checksum);
}
