const std = @import("std");
const build_options = @import("build_options");

const default_source_path = "scripts/zigux/install-zig.py";
const max_source_bytes = 256 * 1024;

const RequiredMarker = struct {
    name: []const u8,
    needle: []const u8,
};

const required_markers = [_]RequiredMarker{
    .{
        .name = "current canonical pin",
        .needle = "CANONICAL_RELEASE_CHANNEL = '0.17.0-dev.758+748e7c5e3'",
    },
    .{
        .name = "current canonical release tag",
        .needle = "CANONICAL_RELEASE_TAG = os.environ.get('ZIGUX_ZIG_RELEASE_TAG', 'upstream-748e7c5e39fc')",
    },
    .{
        .name = "sha256 verification",
        .needle = "verify_archive_sha256(path: Path, expected_sha256: str)",
    },
    .{
        .name = "retry-after parser",
        .needle = "def parse_retry_after(headers) -> float | None:",
    },
    .{
        .name = "retry-after delay hook",
        .needle = "def retry_delay_seconds(attempt: int, *, default_delay: float, headers=None) -> float:",
    },
    .{
        .name = "HTTP throttling is retryable",
        .needle = "RETRYABLE_HTTP_STATUS_CODES = {408, 429, 500, 502, 503, 504}",
    },
    .{
        .name = "curl retry all errors",
        .needle = "'--retry-all-errors'",
    },
    .{
        .name = "curl resume flag",
        .needle = "'--continue-at'",
    },
    .{
        .name = "Range resume request",
        .needle = "return urllib.request.Request(url, headers={'Range': f'bytes={start_offset}-'})",
    },
    .{
        .name = "partial response append guard",
        .needle = "append = resume_offset > 0 and status == 206",
    },
    .{
        .name = "curl preferred before urllib fallback",
        .needle = "if shutil.which('curl') is not None:",
    },
    .{
        .name = "curl fallback keeps zero-byte cleanup",
        .needle = "if destination.exists() and destination.stat().st_size == 0:",
    },
};

const OrderedMarker = struct {
    before_name: []const u8,
    before: []const u8,
    after_name: []const u8,
    after: []const u8,
};

const ordered_markers = [_]OrderedMarker{
    .{
        .before_name = "current canonical pin",
        .before = "CANONICAL_RELEASE_CHANNEL = '0.17.0-dev.758+748e7c5e3'",
        .after_name = "canonical direct target resolution",
        .after = "if channel == CANONICAL_RELEASE_CHANNEL:",
    },
    .{
        .before_name = "Retry-After parser",
        .before = "def parse_retry_after(headers) -> float | None:",
        .after_name = "retry delay helper",
        .after = "def retry_delay_seconds(attempt: int, *, default_delay: float, headers=None) -> float:",
    },
    .{
        .before_name = "retry delay helper",
        .before = "def retry_delay_seconds(attempt: int, *, default_delay: float, headers=None) -> float:",
        .after_name = "open_url retry loop",
        .after = "def open_url(url: str | urllib.request.Request, *, retries: int = 3, timeout: float = 30.0):",
    },
    .{
        .before_name = "Range request builder",
        .before = "def build_download_request(url: str, start_offset: int) -> urllib.request.Request | str:",
        .after_name = "urllib fallback copier",
        .after = "def copy_url_to_file(",
    },
    .{
        .before_name = "curl copier",
        .before = "def copy_url_to_file_with_curl(",
        .after_name = "curl preferred dispatch",
        .after = "if shutil.which('curl') is not None:",
    },
};

const ContractError = error{
    MissingMarker,
    MarkerOutOfOrder,
    DuplicateMarker,
};

fn sourcePath() []const u8 {
    return build_options.source_path;
}

fn readSource(allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        sourcePath(),
        allocator,
        .limited(max_source_bytes),
    );
}

fn requireContains(source: []const u8, marker: RequiredMarker) !void {
    if (std.mem.indexOf(u8, source, marker.needle) == null) {
        std.debug.print("missing Lane 05 install-zig retry/resume marker: {s}\n", .{marker.name});
        return ContractError.MissingMarker;
    }
}

fn requireExactlyOnce(source: []const u8, marker: RequiredMarker) !void {
    const first = std.mem.indexOf(u8, source, marker.needle) orelse {
        std.debug.print("missing Lane 05 install-zig retry/resume marker: {s}\n", .{marker.name});
        return ContractError.MissingMarker;
    };
    const rest = source[first + marker.needle.len ..];
    if (std.mem.indexOf(u8, rest, marker.needle) != null) {
        std.debug.print("duplicate Lane 05 install-zig retry/resume marker: {s}\n", .{marker.name});
        return ContractError.DuplicateMarker;
    }
}

fn requireOrdered(source: []const u8, pair: OrderedMarker) !void {
    const before_index = std.mem.indexOf(u8, source, pair.before) orelse {
        std.debug.print("missing ordered Lane 05 install-zig marker: {s}\n", .{pair.before_name});
        return ContractError.MissingMarker;
    };
    const after_index = std.mem.indexOf(u8, source, pair.after) orelse {
        std.debug.print("missing ordered Lane 05 install-zig marker: {s}\n", .{pair.after_name});
        return ContractError.MissingMarker;
    };
    if (before_index >= after_index) {
        std.debug.print(
            "Lane 05 install-zig marker order drifted: {s} must stay before {s}\n",
            .{ pair.before_name, pair.after_name },
        );
        return ContractError.MarkerOutOfOrder;
    }
}

fn validateInstallZigSource(source: []const u8) !void {
    for (required_markers) |marker| {
        try requireContains(source, marker);
    }

    try requireExactlyOnce(source, .{
        .name = "current canonical pin",
        .needle = "CANONICAL_RELEASE_CHANNEL = '0.17.0-dev.758+748e7c5e3'",
    });
    try requireExactlyOnce(source, .{
        .name = "current canonical release tag",
        .needle = "CANONICAL_RELEASE_TAG = os.environ.get('ZIGUX_ZIG_RELEASE_TAG', 'upstream-748e7c5e39fc')",
    });

    for (ordered_markers) |pair| {
        try requireOrdered(source, pair);
    }
}

fn replaceAll(
    allocator: std.mem.Allocator,
    source: []const u8,
    needle: []const u8,
    replacement: []const u8,
) ![]u8 {
    return std.mem.replaceOwned(u8, allocator, source, needle, replacement);
}

test "current install-zig retry/resume contract source stays fail-closed" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);
    try validateInstallZigSource(source);
}

test "contract rejects loss of curl retry-all-errors protection" {
    const broken = try replaceAll(std.testing.allocator, sample_source, "'--retry-all-errors'", "'--retry'");
    defer std.testing.allocator.free(broken);
    try std.testing.expectError(ContractError.MissingMarker, validateInstallZigSource(broken));
}

test "contract rejects loss of urllib Range resume fallback" {
    const broken = try replaceAll(
        std.testing.allocator,
        sample_source,
        "return urllib.request.Request(url, headers={'Range': f'bytes={start_offset}-'})",
        "return urllib.request.Request(url)",
    );
    defer std.testing.allocator.free(broken);
    try std.testing.expectError(ContractError.MissingMarker, validateInstallZigSource(broken));
}

test "contract rejects stale canonical release pin drift" {
    const broken = try replaceAll(
        std.testing.allocator,
        sample_source,
        "CANONICAL_RELEASE_CHANNEL = '0.17.0-dev.758+748e7c5e3'",
        "CANONICAL_RELEASE_CHANNEL = '0.17.0-dev.87+9b177a7d2'",
    );
    defer std.testing.allocator.free(broken);
    try std.testing.expectError(ContractError.MissingMarker, validateInstallZigSource(broken));
}

test "contract rejects retry helper ordering drift" {
    const before = "def parse_retry_after(headers) -> float | None:";
    const after = "def retry_delay_seconds(attempt: int, *, default_delay: float, headers=None) -> float:";
    const without_before = try replaceAll(std.testing.allocator, sample_source, before, "def parse_retry_after_TMP(headers) -> float | None:");
    defer std.testing.allocator.free(without_before);
    const swapped = try replaceAll(std.testing.allocator, without_before, after, before);
    defer std.testing.allocator.free(swapped);
    const restored = try replaceAll(std.testing.allocator, swapped, "def parse_retry_after_TMP(headers) -> float | None:", after);
    defer std.testing.allocator.free(restored);
    try std.testing.expectError(ContractError.MarkerOutOfOrder, validateInstallZigSource(restored));
}

const sample_source =
    \\CANONICAL_RELEASE_CHANNEL = '0.17.0-dev.758+748e7c5e3'
    \\CANONICAL_RELEASE_TAG = os.environ.get('ZIGUX_ZIG_RELEASE_TAG', 'upstream-748e7c5e39fc')
    \\RETRYABLE_HTTP_STATUS_CODES = {408, 429, 500, 502, 503, 504}
    \\def verify_archive_sha256(path: Path, expected_sha256: str)
    \\def parse_retry_after(headers) -> float | None:
    \\def retry_delay_seconds(attempt: int, *, default_delay: float, headers=None) -> float:
    \\def open_url(url: str | urllib.request.Request, *, retries: int = 3, timeout: float = 30.0):
    \\if channel == CANONICAL_RELEASE_CHANNEL:
    \\def build_download_request(url: str, start_offset: int) -> urllib.request.Request | str:
    \\    return urllib.request.Request(url, headers={'Range': f'bytes={start_offset}-'})
    \\def copy_url_to_file_with_curl(
    \\        '--retry-all-errors'
    \\        '--continue-at'
    \\def copy_url_to_file(
    \\    if shutil.which('curl') is not None:
    \\        if destination.exists() and destination.stat().st_size == 0:
    \\        append = resume_offset > 0 and status == 206
;
