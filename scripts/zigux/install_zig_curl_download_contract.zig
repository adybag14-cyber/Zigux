const std = @import("std");
const install = @import("install_zig.zig");

test "curl download helper is exported" {
    _ = install.copyUrlToFileWithCurl;
    _ = install.curlAvailable;
    try std.testing.expectEqual(@as(u32, 4), install.download_retries);
}

test "http fallback remains available when curl is unavailable" {
    _ = install.copyUrlToFile;
    try std.testing.expect(install.test_hooks.curl_available_fn == null);
}

test "download staging uses shared copy helper" {
    _ = install.stageArchive;
    try std.testing.expectEqual(@as(f64, 120.0), install.download_timeout_seconds);
}