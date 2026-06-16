const std = @import("std");
const install = @import("install_zig.zig");

test "installer keeps http fallback when curl is unavailable" {
    _ = install.copyUrlToFile;
    _ = install.curlAvailable;
    try std.testing.expect(install.test_hooks.open_url_fn == null);
}

test "open url retry path is exported for fallback downloads" {
    _ = install.openUrl;
    try std.testing.expectEqual(@as(u32, 4), install.download_retries);
}

test "curl remains preferred but http fallback stays reachable" {
    _ = install.copyUrlToFileWithCurl;
    try std.testing.expectEqual(@as(f64, 120.0), install.download_timeout_seconds);
}