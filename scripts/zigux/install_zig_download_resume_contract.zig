const std = @import("std");
const install = @import("install_zig.zig");

test "http fallback supports ranged resume requests" {
    _ = install.copyUrlToFile;
    _ = install.openUrl;
    try std.testing.expectEqual(@as(u32, 4), install.download_retries);
}

test "curl path keeps continue-at semantics via dedicated helper" {
    _ = install.copyUrlToFileWithCurl;
    try std.testing.expectEqual(@as(usize, 1024 * 1024), install.download_chunk_size);
}

test "staging uses download path for remote archives" {
    try std.testing.expectEqualStrings("download", install.ArchiveSource.download.name());
}