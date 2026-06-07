const std = @import("std");

const installer_source = @embedFile("install-zig.py");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "retryable http status roster keeps throttle and transient server failures" {
    try requireContains(installer_source, "RETRYABLE_HTTP_STATUS_CODES = {408, 429, 500, 502, 503, 504}");
    try requireContains(installer_source, "DOWNLOAD_RETRIES = 4");
    try requireContains(installer_source, "MAX_RETRY_DELAY = 30.0");
}

test "retry-after parsing is capped before exponential fallback delay" {
    try requireBefore(
        installer_source,
        "def parse_retry_after(headers) -> float | None:",
        "def retry_delay_seconds(attempt: int, *, default_delay: float, headers=None) -> float:",
    );
    try requireContains(installer_source, "value = headers.get('Retry-After')");
    try requireContains(installer_source, "return min(parsed_retry_after, MAX_RETRY_DELAY)");
    try requireContains(installer_source, "return min(default_delay, MAX_RETRY_DELAY)");
}

test "index open path retries only explicitly retryable http failures" {
    try requireContains(installer_source, "def open_url(url: str | urllib.request.Request, *, retries: int = 3, timeout: float = 30.0):");
    try requireContains(installer_source, "if exc.code not in RETRYABLE_HTTP_STATUS_CODES or attempt == retries:");
    try requireContains(installer_source, "default_delay=min(0.5 * attempt, 2.0)");
    try requireContains(installer_source, "headers=exc.headers");
}

test "archive download fallback reuses retry-after delay and preserves resume state" {
    try requireContains(installer_source, "def copy_url_to_file(");
    try requireBefore(
        installer_source,
        "resume_offset = destination.stat().st_size if destination.exists() else 0",
        "request = build_download_request(url, resume_offset)",
    );
    try requireBefore(
        installer_source,
        "except urllib.error.HTTPError as exc:",
        "headers=exc.headers",
    );
    try requireContains(installer_source, "time.sleep(min(1.5 * attempt, 5.0))");
}
