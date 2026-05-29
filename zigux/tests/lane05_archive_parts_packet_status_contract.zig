const std = @import("std");

const PacketStatus = enum {
    verified,
    missing_allowed,

    fn label(self: PacketStatus) []const u8 {
        return switch (self) {
            .verified => "verified",
            .missing_allowed => "missing_allowed",
        };
    }

    fn isCiPass(self: PacketStatus) bool {
        return switch (self) {
            .verified, .missing_allowed => true,
        };
    }

    fn emitsDecodedMetadata(self: PacketStatus) bool {
        return switch (self) {
            .verified => true,
            .missing_allowed => false,
        };
    }
};

const OutputLine = struct {
    key: []const u8,
    value: []const u8,
};

const pinned_filename = "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz";
const pinned_sha256 = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77";
const pinned_size_bytes: usize = 58_159_088;
const publish_safe_chunk_bytes: usize = 786_432;
const publish_safe_part_count: usize = 74;

const missing_allowed_output = [_]OutputLine{
    .{ .key = "LANE05_ARCHIVE_PARTS_PACKET", .value = "pass" },
    .{ .key = "LANE05_ARCHIVE_PARTS_PACKET_STATUS", .value = "missing_allowed" },
    .{ .key = "LANE05_ARCHIVE_PARTS_PACKET_FILENAME", .value = pinned_filename },
    .{ .key = "LANE05_ARCHIVE_PARTS_PACKET_EXPECTED_SHA256", .value = pinned_sha256 },
    .{ .key = "LANE05_ARCHIVE_PARTS_PACKET_EXPECTED_SIZE", .value = "58159088" },
};

const verified_output = [_]OutputLine{
    .{ .key = "LANE05_ARCHIVE_PARTS_PACKET", .value = "pass" },
    .{ .key = "LANE05_ARCHIVE_PARTS_PACKET_STATUS", .value = "verified" },
    .{ .key = "LANE05_ARCHIVE_PARTS_PACKET_FILENAME", .value = pinned_filename },
    .{ .key = "LANE05_ARCHIVE_PARTS_PACKET_EXPECTED_SHA256", .value = pinned_sha256 },
    .{ .key = "LANE05_ARCHIVE_PARTS_PACKET_EXPECTED_SIZE", .value = "58159088" },
    .{ .key = "LANE05_ARCHIVE_PARTS_PACKET_CHUNK_BYTES", .value = "786432" },
    .{ .key = "LANE05_ARCHIVE_PARTS_PACKET_PART_COUNT", .value = "74" },
};

fn expectedPartCount(size: usize, chunk_bytes: usize) usize {
    return (size + chunk_bytes - 1) / chunk_bytes;
}

fn statusOutput(status: PacketStatus) []const OutputLine {
    return switch (status) {
        .missing_allowed => &missing_allowed_output,
        .verified => &verified_output,
    };
}

fn expectLine(lines: []const OutputLine, key: []const u8, value: []const u8) !void {
    for (lines) |line| {
        if (std.mem.eql(u8, line.key, key)) {
            try std.testing.expectEqualStrings(value, line.value);
            return;
        }
    }
    return error.MissingExpectedOutputLine;
}

fn expectNoLine(lines: []const OutputLine, key: []const u8) !void {
    for (lines) |line| {
        try std.testing.expect(!std.mem.eql(u8, line.key, key));
    }
}

test "lane 05 archive parts packet pass statuses stay intentionally narrow" {
    try std.testing.expect(PacketStatus.verified.isCiPass());
    try std.testing.expect(PacketStatus.missing_allowed.isCiPass());
    try std.testing.expectEqualStrings("verified", PacketStatus.verified.label());
    try std.testing.expectEqualStrings("missing_allowed", PacketStatus.missing_allowed.label());
    try std.testing.expect(PacketStatus.verified.emitsDecodedMetadata());
    try std.testing.expect(!PacketStatus.missing_allowed.emitsDecodedMetadata());
}

test "lane 05 missing packet output still reports policy identity without decoded metadata" {
    const lines = statusOutput(.missing_allowed);
    try expectLine(lines, "LANE05_ARCHIVE_PARTS_PACKET", "pass");
    try expectLine(lines, "LANE05_ARCHIVE_PARTS_PACKET_STATUS", "missing_allowed");
    try expectLine(lines, "LANE05_ARCHIVE_PARTS_PACKET_FILENAME", pinned_filename);
    try expectLine(lines, "LANE05_ARCHIVE_PARTS_PACKET_EXPECTED_SHA256", pinned_sha256);
    try expectLine(lines, "LANE05_ARCHIVE_PARTS_PACKET_EXPECTED_SIZE", "58159088");
    try expectNoLine(lines, "LANE05_ARCHIVE_PARTS_PACKET_CHUNK_BYTES");
    try expectNoLine(lines, "LANE05_ARCHIVE_PARTS_PACKET_PART_COUNT");
}

test "lane 05 verified packet output records publish safe shard metadata" {
    try std.testing.expectEqual(
        @as(usize, publish_safe_part_count),
        expectedPartCount(pinned_size_bytes, publish_safe_chunk_bytes),
    );

    const lines = statusOutput(.verified);
    try expectLine(lines, "LANE05_ARCHIVE_PARTS_PACKET", "pass");
    try expectLine(lines, "LANE05_ARCHIVE_PARTS_PACKET_STATUS", "verified");
    try expectLine(lines, "LANE05_ARCHIVE_PARTS_PACKET_FILENAME", pinned_filename);
    try expectLine(lines, "LANE05_ARCHIVE_PARTS_PACKET_EXPECTED_SHA256", pinned_sha256);
    try expectLine(lines, "LANE05_ARCHIVE_PARTS_PACKET_EXPECTED_SIZE", "58159088");
    try expectLine(lines, "LANE05_ARCHIVE_PARTS_PACKET_CHUNK_BYTES", "786432");
    try expectLine(lines, "LANE05_ARCHIVE_PARTS_PACKET_PART_COUNT", "74");
}
