const std = @import("std");
const install = @import("install_zig.zig");

test "retry-after parsing accepts seconds headers" {
    try std.testing.expect(install.parseRetryAfter(null) == null);
    try std.testing.expect(install.parseRetryAfter("") == null);
    try std.testing.expectEqual(@as(?f64, 7.0), install.parseRetryAfter("7"));
}

test "retry delays are capped" {
    try std.testing.expectEqual(install.max_retry_delay_seconds, install.retryDelaySeconds(1, 0.5, "60"));
    try std.testing.expectEqual(@as(f64, 1.25), install.retryDelaySeconds(2, 1.25, null));
}

test "retryable status codes include throttling responses" {
    try std.testing.expectEqual(@as(usize, 6), install.retryable_http_status_codes.len);
    try std.testing.expect(install.retryable_http_status_codes[1] == 429);
}

test "self-test case count remains pinned" {
    try std.testing.expectEqual(@as(u32, 4), install.download_retries);
    try std.testing.expectEqual(@as(f64, 30.0), install.max_retry_delay_seconds);
}