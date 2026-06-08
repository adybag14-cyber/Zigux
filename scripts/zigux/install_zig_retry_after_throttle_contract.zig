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

test "retry-after parser accepts numeric and date headers" {
    try requireContains(installer_source, "from datetime import datetime, timedelta, timezone");
    try requireContains(installer_source, "from email.utils import format_datetime, parsedate_to_datetime");
    try requireContains(installer_source, "def parse_retry_after(headers) -> float | None:");
    try requireBefore(
        installer_source,
        "value = headers.get('Retry-After')",
        "if text.isdigit():",
    );
    try requireBefore(
        installer_source,
        "if text.isdigit():",
        "return float(text)",
    );
    try requireBefore(
        installer_source,
        "parsed = parsedate_to_datetime(text)",
        "parsed = parsed.replace(tzinfo=timezone.utc)",
    );
    try requireBefore(
        installer_source,
        "parsed = parsed.replace(tzinfo=timezone.utc)",
        "return max(0.0, parsed.timestamp() - time.time())",
    );
}

test "retry delay prefers retry-after and caps every path" {
    try requireContains(installer_source, "MAX_RETRY_DELAY = 30.0");
    try requireContains(installer_source, "def retry_delay_seconds(attempt: int, *, default_delay: float, headers=None) -> float:");
    try requireBefore(
        installer_source,
        "parsed_retry_after = parse_retry_after(headers)",
        "return min(parsed_retry_after, MAX_RETRY_DELAY)",
    );
    try requireBefore(
        installer_source,
        "return min(parsed_retry_after, MAX_RETRY_DELAY)",
        "return min(default_delay, MAX_RETRY_DELAY)",
    );
}

test "index and download http retries pass response headers into delay policy" {
    try requireContains(installer_source, "RETRYABLE_HTTP_STATUS_CODES = {408, 429, 500, 502, 503, 504}");
    try requireBefore(
        installer_source,
        "if exc.code not in RETRYABLE_HTTP_STATUS_CODES or attempt == retries:",
        "headers=exc.headers",
    );
    try requireBefore(
        installer_source,
        "default_delay=min(0.5 * attempt, 2.0)",
        "headers=exc.headers",
    );
    try requireBefore(
        installer_source,
        "except urllib.error.HTTPError as exc:\n            last_error = exc\n            if attempt == retries:",
        "default_delay=min(1.5 * attempt, 5.0)",
    );
    try requireContains(
        installer_source,
        "retry_delay_seconds(\n                    attempt,\n                    default_delay=min(1.5 * attempt, 5.0),\n                    headers=exc.headers,\n                )",
    );
}

test "explicit-version index fallback remains fail-closed for moving channels" {
    try requireContains(installer_source, "def load_index(channel: str) -> dict:");
    try requireContains(installer_source, "except (TimeoutError, urllib.error.URLError):");
    try requireContains(
        installer_source,
        "except (TimeoutError, urllib.error.URLError):\n        if not is_explicit_version(channel):\n            raise\n        return {}",
    );
}
