const std = @import("std");
const testing = std.testing;

const current_target = "x86_64-linux";
const current_channel = "0.17.0-dev.758+748e7c5e3";
const current_minimum_version = current_channel;
const current_archive_sha256 = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
const current_archive_size: usize = 59_410_844;

const historical_attached_channel = "0.17.0-dev.87+9b177a7d2";
const historical_attached_sha256 = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77";
const historical_attached_size: usize = 58_159_088;

const current_filename = "zig-" ++ current_target ++ "-" ++ current_channel ++ ".tar.xz";
const current_archive_path = "third_party/" ++ current_filename;
const current_parts_path = current_archive_path ++ ".parts";
const current_validation_command =
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive " ++
    current_archive_path ++
    " --archive-target " ++
    current_target;

fn isLowerHexSha256(value: []const u8) bool {
    if (value.len != 64) return false;
    for (value) |byte| {
        if (!((byte >= '0' and byte <= '9') or (byte >= 'a' and byte <= 'f'))) {
            return false;
        }
    }
    return true;
}

fn hasText(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

test "current Lane 05 pinned archive identity is exact" {
    try testing.expectEqualStrings("0.17.0-dev.758+748e7c5e3", current_channel);
    try testing.expectEqualStrings(current_channel, current_minimum_version);
    try testing.expectEqualStrings("zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz", current_filename);
    try testing.expectEqualStrings("third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz", current_archive_path);
    try testing.expectEqualStrings("third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz.parts", current_parts_path);
    try testing.expectEqual(@as(usize, 59_410_844), current_archive_size);
    try testing.expect(isLowerHexSha256(current_archive_sha256));
}

test "current archive validation command matches workflow and README packet" {
    try testing.expect(hasText(current_validation_command, current_archive_path));
    try testing.expect(hasText(current_validation_command, "--archive-target x86_64-linux"));
    try testing.expect(hasText(current_validation_command, "check-zig-toolchain.py --archive-only"));
    try testing.expect(!hasText(current_validation_command, historical_attached_channel));
}

test "older attached archive remains a blocked historical payload, not the current CI pin" {
    try testing.expect(!std.mem.eql(u8, current_channel, historical_attached_channel));
    try testing.expect(!std.mem.eql(u8, current_archive_sha256, historical_attached_sha256));
    try testing.expect(current_archive_size > historical_attached_size);
    try testing.expect(!hasText(current_filename, historical_attached_channel));
    try testing.expect(!hasText(current_parts_path, historical_attached_channel));
}
