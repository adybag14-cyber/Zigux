const std = @import("std");

const installer_source = @embedFile("install-zig.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrder(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn expectOrderAfter(haystack: []const u8, anchor: []const u8, earlier: []const u8, later: []const u8) !void {
    const anchor_index = std.mem.indexOf(u8, haystack, anchor) orelse return error.MissingAnchorMarker;
    try expectOrder(haystack[anchor_index..], earlier, later);
}

fn expectCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    try std.testing.expectEqual(expected, std.mem.count(u8, haystack, needle));
}

test "retryable status set covers throttling and transient gateway failures" {
    try expectContains(installer_source, "RETRYABLE_HTTP_STATUS_CODES = {408, 429, 500, 502, 503, 504}");
    try expectContains(installer_source, "MAX_RETRY_DELAY = 30.0");
    try expectContains(installer_source, "DOWNLOAD_RETRIES = 4");
    try expectContains(installer_source, "DOWNLOAD_TIMEOUT = 120.0");
}

test "retry-after parsing accepts delay seconds and http-date headers" {
    try expectContains(installer_source, "from email.utils import format_datetime, parsedate_to_datetime");
    try expectContains(installer_source, "def parse_retry_after(headers) -> float | None:");
    try expectContains(installer_source, "value = headers.get('Retry-After')");
    try expectContains(installer_source, "if text.isdigit():\n        return float(text)");
    try expectContains(installer_source, "parsed = parsedate_to_datetime(text)");
    try expectContains(installer_source, "parsed = parsed.replace(tzinfo=timezone.utc)");
    try expectContains(installer_source, "return max(0.0, parsed.timestamp() - time.time())");
}

test "open_url honors retry-after only for retryable http failures" {
    try expectContains(installer_source, "def open_url(url: str | urllib.request.Request, *, retries: int = 3, timeout: float = 30.0):");
    try expectContains(installer_source, "except urllib.error.HTTPError as exc:");
    try expectContains(installer_source, "if exc.code not in RETRYABLE_HTTP_STATUS_CODES or attempt == retries:");
    try expectContains(installer_source, "headers=exc.headers");
    try expectOrderAfter(
        installer_source,
        "def open_url(url: str | urllib.request.Request, *, retries: int = 3, timeout: float = 30.0):",
        "if exc.code not in RETRYABLE_HTTP_STATUS_CODES or attempt == retries:",
        "retry_delay_seconds(",
    );
    try expectOrderAfter(
        installer_source,
        "def open_url(url: str | urllib.request.Request, *, retries: int = 3, timeout: float = 30.0):",
        "except urllib.error.HTTPError as exc:",
        "except urllib.error.URLError as exc:",
    );
}

test "download fallback uses retry-after while keeping generic retry delay separate" {
    try expectContains(installer_source, "def copy_url_to_file(");
    try expectOrderAfter(
        installer_source,
        "def copy_url_to_file(",
        "except urllib.error.HTTPError as exc:",
        "headers=exc.headers",
    );
    try expectOrderAfter(
        installer_source,
        "def copy_url_to_file(",
        "headers=exc.headers",
        "continue",
    );
    try expectOrderAfter(
        installer_source,
        "def copy_url_to_file(",
        "except urllib.error.URLError as exc:",
        "time.sleep(min(1.5 * attempt, 5.0))",
    );
}

test "self-test covers throttled index and archive retry paths" {
    try expectCount(installer_source, "code=429", 2);
    try expectCount(installer_source, "hdrs={'Retry-After': '0'}", 2);
    try expectContains(installer_source, "throttled_sleep_calls: list[float] = []");
    try expectContains(installer_source, "assert throttled_sleep_calls == [0.0]");
    try expectContains(installer_source, "throttled_download_attempts = 0");
    try expectContains(installer_source, "def throttled_download_open_url(target: str | urllib.request.Request, *, retries: int = 3, timeout: float = 30.0):");
    try expectContains(installer_source, "assert throttled_download_attempts == 2");
    try expectContains(installer_source, "print('ZIG_INSTALL_SELF_TEST=pass')");
    try expectContains(installer_source, "print('ZIG_INSTALL_SELF_TEST_CASE_COUNT=46')");
}
