const std = @import("std");
const testing = std.testing;

const installer_retry_slice =
    \\RETRYABLE_HTTP_STATUS_CODES = {408, 429, 500, 502, 503, 504}
    \\DOWNLOAD_RETRIES = 4
    \\MAX_RETRY_DELAY = 30.0
    \\def parse_retry_after(headers) -> float | None:
    \\    if headers is None:
    \\        return None
    \\    value = headers.get('Retry-After')
    \\    if value is None:
    \\        return None
    \\    text = value.strip()
    \\    if not text:
    \\        return None
    \\    if text.isdigit():
    \\        return float(text)
    \\    try:
    \\        parsed = parsedate_to_datetime(text)
    \\    except (TypeError, ValueError, IndexError, OverflowError):
    \\        return None
    \\    if parsed.tzinfo is None:
    \\        parsed = parsed.replace(tzinfo=timezone.utc)
    \\    return max(0.0, parsed.timestamp() - time.time())
    \\
    \\
    \\def retry_delay_seconds(attempt: int, *, default_delay: float, headers=None) -> float:
    \\    parsed_retry_after = parse_retry_after(headers)
    \\    if parsed_retry_after is not None:
    \\        return min(parsed_retry_after, MAX_RETRY_DELAY)
    \\    return min(default_delay, MAX_RETRY_DELAY)
    \\
    \\
    \\def open_url(url: str | urllib.request.Request, *, retries: int = 3, timeout: float = 30.0):
    \\        except urllib.error.HTTPError as exc:
    \\            if exc.code not in RETRYABLE_HTTP_STATUS_CODES or attempt == retries:
    \\                raise
    \\            last_error = exc
    \\            time.sleep(
    \\                retry_delay_seconds(
    \\                    attempt,
    \\                    default_delay=min(0.5 * attempt, 2.0),
    \\                    headers=exc.headers,
    \\                )
    \\            )
    \\
    \\
    \\def copy_url_to_file(
    \\        except urllib.error.HTTPError as exc:
    \\            last_error = exc
    \\            if attempt == retries:
    \\                break
    \\            time.sleep(
    \\                retry_delay_seconds(
    \\                    attempt,
    \\                    default_delay=min(1.5 * attempt, 5.0),
    \\                    headers=exc.headers,
    \\                )
    \\            )
;

const retry_after_markers = [_][]const u8{
    "value = headers.get('Retry-After')",
    "if text.isdigit():",
    "return float(text)",
    "parsed = parsedate_to_datetime(text)",
    "except (TypeError, ValueError, IndexError, OverflowError):",
    "parsed = parsed.replace(tzinfo=timezone.utc)",
    "return max(0.0, parsed.timestamp() - time.time())",
};

const delay_markers = [_][]const u8{
    "MAX_RETRY_DELAY = 30.0",
    "parsed_retry_after = parse_retry_after(headers)",
    "return min(parsed_retry_after, MAX_RETRY_DELAY)",
    "return min(default_delay, MAX_RETRY_DELAY)",
};

const retry_call_markers = [_][]const u8{
    "RETRYABLE_HTTP_STATUS_CODES = {408, 429, 500, 502, 503, 504}",
    "DOWNLOAD_RETRIES = 4",
    "default_delay=min(0.5 * attempt, 2.0)",
    "default_delay=min(1.5 * attempt, 5.0)",
    "headers=exc.headers",
};

fn requireMarkers(source: []const u8, markers: []const []const u8) !void {
    for (markers) |marker| {
        try testing.expect(std.mem.indexOf(u8, source, marker) != null);
    }
}

fn firstIndex(source: []const u8, marker: []const u8) !usize {
    return std.mem.indexOf(u8, source, marker) orelse error.MissingMarker;
}

test "Retry-After parser accepts numeric and HTTP-date forms defensively" {
    try requireMarkers(installer_retry_slice, retry_after_markers[0..]);
    try testing.expect(try firstIndex(installer_retry_slice, "if text.isdigit():") < try firstIndex(installer_retry_slice, "parsed = parsedate_to_datetime(text)"));
    try testing.expect(try firstIndex(installer_retry_slice, "except (TypeError, ValueError, IndexError, OverflowError):") < try firstIndex(installer_retry_slice, "parsed = parsed.replace(tzinfo=timezone.utc)"));
}

test "retry delay helper clamps both header and fallback delays" {
    try requireMarkers(installer_retry_slice, delay_markers[0..]);
    try testing.expect(try firstIndex(installer_retry_slice, "parsed_retry_after = parse_retry_after(headers)") < try firstIndex(installer_retry_slice, "return min(parsed_retry_after, MAX_RETRY_DELAY)"));
    try testing.expect(try firstIndex(installer_retry_slice, "return min(parsed_retry_after, MAX_RETRY_DELAY)") < try firstIndex(installer_retry_slice, "return min(default_delay, MAX_RETRY_DELAY)"));
}

test "HTTP retry action paths pass response headers into delay calculation" {
    try requireMarkers(installer_retry_slice, retry_call_markers[0..]);
    const open_url_backoff = try firstIndex(installer_retry_slice, "default_delay=min(0.5 * attempt, 2.0)");
    const urllib_backoff = try firstIndex(installer_retry_slice, "default_delay=min(1.5 * attempt, 5.0)");
    try testing.expect(open_url_backoff < urllib_backoff);
    try testing.expect(std.mem.count(u8, installer_retry_slice, "headers=exc.headers") == 2);
}
