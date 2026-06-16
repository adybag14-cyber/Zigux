const std = @import("std");
const install = @import("install_zig.zig");

test "open url honors retryable status codes" {
    try std.testing.expectEqual(@as(u16, 429), install.retryable_http_status_codes[1]);
    try std.testing.expectEqual(@as(f64, 30.0), install.max_retry_delay_seconds);
}

test "retry delay uses retry-after when present" {
    try std.testing.expectEqual(install.max_retry_delay_seconds, install.retryDelaySeconds(1, 0.5, "60"));
}

test "index reader uses shared open url path" {
    try std.testing.expectEqualStrings(install.index_url, "https://ziglang.org/download/index.json");
}