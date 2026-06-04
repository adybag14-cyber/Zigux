const std = @import("std");

const CurrentPinnedArchive = struct {
    target: []const u8 = "x86_64-linux",
    channel: []const u8 = "0.17.0-dev.758+748e7c5e3",
    filename: []const u8 = "zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz",
    archive_path: []const u8 = "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz",
    parts_dir: []const u8 = "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz.parts",
    sha256: []const u8 = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6",
    size_bytes: usize = 59_410_844,
};

const HistoricalAttachedArchive = struct {
    channel: []const u8 = "0.17.0-dev.87+9b177a7d2",
    sha256: []const u8 = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
    size_bytes: usize = 58_159_088,
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "lane 05 publish boundary names the current archive and parts directory" {
    const current: CurrentPinnedArchive = .{};

    try std.testing.expectEqualStrings("x86_64-linux", current.target);
    try std.testing.expectEqualStrings("0.17.0-dev.758+748e7c5e3", current.channel);
    try std.testing.expectEqualStrings(
        "zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz",
        current.filename,
    );
    try std.testing.expectEqualStrings(
        "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz",
        current.archive_path,
    );
    try std.testing.expectEqualStrings(
        "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz.parts",
        current.parts_dir,
    );
    try std.testing.expectEqualStrings(
        "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6",
        current.sha256,
    );
    try std.testing.expectEqual(@as(usize, 59_410_844), current.size_bytes);
}

test "lane 05 parts publish path remains binary safe and local first" {
    const current: CurrentPinnedArchive = .{};
    const parts_suffix = ".tar.xz.parts";

    try std.testing.expect(std.mem.endsWith(u8, current.parts_dir, parts_suffix));
    try expectContains(current.parts_dir, current.filename);
    try expectContains(current.parts_dir, "third_party/");
    try expectNotContains(current.parts_dir, "ziglang.org");
    try expectNotContains(current.parts_dir, "github.com");
}

test "lane 05 current payload stays separate from the historical attached archive" {
    const current: CurrentPinnedArchive = .{};
    const historical: HistoricalAttachedArchive = .{};

    try std.testing.expect(!std.mem.eql(u8, current.channel, historical.channel));
    try std.testing.expect(!std.mem.eql(u8, current.sha256, historical.sha256));
    try std.testing.expect(current.size_bytes != historical.size_bytes);
    try std.testing.expectEqualStrings("0.17.0-dev.87+9b177a7d2", historical.channel);
    try std.testing.expectEqual(@as(usize, 58_159_088), historical.size_bytes);
}
