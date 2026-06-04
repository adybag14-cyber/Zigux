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

fn expectCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    try std.testing.expectEqual(expected, std.mem.count(u8, haystack, needle));
}

test "retry-after parsing accepts seconds and http-date headers" {
    try expectContains(installer_source, "from email.utils import format_datetime, parsedate_to_datetime");
    try expectContains(installer_source, "def parse_retry_after(headers) -> float | None:");
    try expectContains(installer_source, "value = headers.get('Retry-After')");
    try expectContains(installer_source, "if text.isdigit():\n        return float(text)");
    try expectContains(installer_source, "parsed = parsedate_to_datetime(text)");
    try expectContains(installer_source, "parsed = parsed.replace(tzinfo=timezone.utc)");
    try expectContains(installer_source, "return max(0.0, parsed.timestamp() - time.time())");
}

test "retry delays are capped and reused by index and download http retries" {
    try expectContains(installer_source, "MAX_RETRY_DELAY = 30.0");
    try expectContains(installer_source, "def retry_delay_seconds(attempt: int, *, default_delay: float, headers=None) -> float:");
    try expectContains(installer_source, "parsed_retry_after = parse_retry_after(headers)");
    try expectContains(installer_source, "return min(parsed_retry_after, MAX_RETRY_DELAY)");
    try expectContains(installer_source, "return min(default_delay, MAX_RETRY_DELAY)");

    try expectContains(installer_source, "except urllib.error.HTTPError as exc:");
    try expectContains(installer_source, "if exc.code not in RETRYABLE_HTTP_STATUS_CODES or attempt == retries:");
    try expectContains(installer_source, "headers=exc.headers");
    try expectOrder(
        installer_source,
        "def open_url(url: str | urllib.request.Request, *, retries: int = 3, timeout: float = 30.0):",
        "def copy_url_to_file(",
    );
    try expectOrder(
        installer_source,
        "def copy_url_to_file(",
        "def read_index() -> dict:",
    );
}

test "python download fallback keeps resumable retry behavior distinct from curl" {
    try expectContains(installer_source, "if shutil.which('curl') is not None:");
    try expectContains(installer_source, "shutil.which = lambda name: None if name == 'curl' else original_which(name)");
    try expectContains(installer_source, "resume_offset = destination.stat().st_size if destination.exists() else 0");
    try expectContains(installer_source, "request = build_download_request(url, resume_offset)");
    try expectContains(installer_source, "append = resume_offset > 0 and status == 206");
    try expectContains(installer_source, "if not append and destination.exists():\n                    destination.unlink()");
    try expectContains(installer_source, "copy_response_chunks(response, destination, append=append)");
    try expectContains(installer_source, "assert resume_headers == [None, 'bytes=4-']");
    try expectContains(installer_source,
        \\        except TimeoutError as exc:
        \\            last_error = exc
        \\        except urllib.error.HTTPError as exc:
        \\            last_error = exc
    );
    try expectContains(installer_source,
        \\        except urllib.error.HTTPError as exc:
        \\            last_error = exc
        \\            if attempt == retries:
        \\                break
        \\            time.sleep(
    );
    try expectContains(installer_source,
        \\            continue
        \\        except urllib.error.URLError as exc:
        \\            last_error = exc
    );
}

test "self-test covers throttled index and archive retry-after paths" {
    try expectCount(installer_source, "code=429", 2);
    try expectCount(installer_source, "hdrs={'Retry-After': '0'}", 2);
    try expectContains(installer_source, "throttled_sleep_calls: list[float] = []");
    try expectContains(installer_source, "assert throttled_sleep_calls == [0.0]");
    try expectContains(installer_source, "throttled_download_attempts = 0");
    try expectContains(installer_source, "def throttled_download_open_url(target: str | urllib.request.Request, *, retries: int = 3, timeout: float = 30.0):");
    try expectContains(installer_source, "assert throttled_download_path.read_bytes() == b'zig-download'");
    try expectContains(installer_source, "assert throttled_download_attempts == 2");
    try expectContains(installer_source, "print('ZIG_INSTALL_SELF_TEST=pass')");
    try expectContains(installer_source, "print('ZIG_INSTALL_SELF_TEST_CASE_COUNT=46')");
}
