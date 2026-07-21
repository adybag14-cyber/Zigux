const std = @import("std");
const builtin = @import("builtin");
const Io = std.Io;
const policy = @import("toolchain_policy.zig");

pub const index_url = "https://ziglang.org/download/index.json";
pub const fallback_channel = "master";
pub const default_toolchain_policy_rel = "scripts/zigux/zig-toolchain-policy.json";
pub const canonical_release_channel = "0.17.0-dev.1443+6c25d2bd5";
pub const default_canonical_release_repo = "adybag14-cyber/zig";
pub const default_canonical_release_tag = "upstream-6c25d2bd58e4";

pub const retryable_http_status_codes = [_]u16{ 408, 429, 500, 502, 503, 504 };
pub const download_retries: u32 = 4;
pub const download_timeout_seconds: f64 = 120.0;
pub const download_chunk_size: usize = 1024 * 1024;
pub const max_retry_delay_seconds: f64 = 30.0;

pub const InstallIoError = error{
    AccessDenied,
    AntivirusInterference,
    BadPathName,
    BrokenPipe,
    Canceled,
    ConnectionResetByPeer,
    DeviceBusy,
    DiskQuota,
    EndOfStream,
    FileBusy,
    FileLocksUnsupported,
    FileNotFound,
    FileTooBig,
    InputOutput,
    IsDir,
    LinkQuotaExceeded,
    LockViolation,
    NameTooLong,
    NetworkNotFound,
    NoDevice,
    NoSpaceLeft,
    NotDir,
    NotOpenForReading,
    NotOpenForWriting,
    PathAlreadyExists,
    PermissionDenied,
    PipeBusy,
    ProcessFdQuotaExceeded,
    ReadOnlyFileSystem,
    SocketUnconnected,
    StreamTooLong,
    Streaming,
    SymLinkLoop,
    SystemFdQuotaExceeded,
    SystemResources,
    Unexpected,
    Unseekable,
    WouldBlock,
} || std.Io.Cancelable || std.Io.UnexpectedError;

pub const InstallPolicyError = error{
    InvalidPolicyJson,
    InvalidChannel,
    InvalidArchiveSha256,
    InvalidArchiveDigest,
    DuplicatePolicyKey,
    DuplicateArchiveTarget,
    OutOfMemory,
} || InstallIoError;

pub const InstallError = error{
    UnsupportedOs,
    UnsupportedArch,
    UnknownChannel,
    UnknownTarget,
    UnexpectedExtractLayout,
    MissingZigBinary,
    LocalArchiveNotFound,
    LocalArchiveNotFile,
    ArchiveSha256Mismatch,
    MissingPinnedArchiveSha256,
    DownloadFailed,
    ExtractFailed,
    OutOfMemory,
} || InstallPolicyError || InstallIoError || OpenUrlError || std.process.SpawnError || std.process.RunError || std.http.Client.FetchError;

pub const ResolveTargetResult = struct {
    target_key: []const u8,
    version: []const u8,
    tarball_url: []const u8,
};

pub const ArchiveSource = enum {
    local_archive,
    download,

    pub fn name(self: ArchiveSource) []const u8 {
        return switch (self) {
            .local_archive => "local_archive",
            .download => "download",
        };
    }
};

pub const HttpResponse = struct {
    status: u16,
    body: []const u8,
    retry_after: ?[]const u8 = null,
};

pub const OpenUrlError = error{
    HttpStatus,
    Network,
    OutOfMemory,
};

pub const TestHooks = struct {
    read_index_fn: ?*const fn (
        allocator: std.mem.Allocator,
        io: Io,
    ) OpenUrlError!std.json.ObjectMap = null,
    open_url_fn: ?*const fn (
        allocator: std.mem.Allocator,
        io: Io,
        url: []const u8,
        range_start: ?u64,
        retries: u32,
        timeout_seconds: f64,
    ) OpenUrlError!HttpResponse = null,
    curl_available_fn: ?*const fn (io: Io) bool = null,
    copy_url_with_curl_fn: ?*const fn (
        io: Io,
        url: []const u8,
        destination: []const u8,
        retries: u32,
        timeout_seconds: f64,
    ) InstallError!void = null,
    sleep_fn: ?*const fn (seconds: f64) void = null,
};

pub var test_hooks: TestHooks = .{};

const SelfTestState = struct {
    throttled_open_attempts: u32 = 0,
    throttled_download_attempts: u32 = 0,
    curl_copy_calls: u32 = 0,
    download_calls: u32 = 0,
    resume_destination: ?[]const u8 = null,
    throttled_sleep_calls: std.ArrayListUnmanaged(f64) = .empty,
    resume_headers: std.ArrayListUnmanaged(?[]const u8) = .empty,
    curl_commands: std.ArrayListUnmanaged([]const []const u8) = .empty,
};

var self_test_state: SelfTestState = .{
    .throttled_sleep_calls = .empty,
    .resume_headers = .empty,
    .curl_commands = .empty,
};

var install_tmp_counter: std.atomic.Value(u64) = .init(0);

fn installTmpId(io: Io) u64 {
    var random_bytes: [8]u8 = undefined;
    io.random(&random_bytes);
    return std.mem.readInt(u64, &random_bytes, .little) ^ install_tmp_counter.fetchAdd(1, .monotonic);
}

fn dupe(allocator: std.mem.Allocator, text: []const u8) InstallError![]const u8 {
    return allocator.dupe(u8, text) catch return error.OutOfMemory;
}

fn printLine(io: Io, comptime fmt: []const u8, args: anytype) !void {
    var buffer: [512]u8 = undefined;
    var writer = Io.File.stdout().writer(io, &buffer);
    try writer.interface.print(fmt ++ "\n", args);
    try writer.interface.flush();
}

pub fn printErr(io: Io, message: []const u8) void {
    var buffer: [512]u8 = undefined;
    var writer = Io.File.stderr().writer(io, &buffer);
    writer.interface.writeAll(message) catch {};
    writer.interface.writeAll("\n") catch {};
    writer.interface.flush() catch {};
}

pub fn exitWithMessage(io: Io, message: []const u8) noreturn {
    printErr(io, message);
    std.process.exit(1);
}

pub fn defaultRepoRoot(allocator: std.mem.Allocator) InstallError![]const u8 {
    const script_path = @src().file;
    if (std.fs.path.dirname(script_path)) |script_dir| {
        if (std.fs.path.dirname(script_dir)) |scripts_dir| {
            if (std.fs.path.dirname(scripts_dir)) |root| {
                return dupe(allocator, root);
            }
        }
    }
    return dupe(allocator, ".");
}

fn startsWithIgnoreCase(haystack: []const u8, prefix: []const u8) bool {
    if (haystack.len < prefix.len) return false;
    for (haystack[0..prefix.len], prefix) |left, right| {
        if (std.ascii.toLower(left) != std.ascii.toLower(right)) return false;
    }
    return true;
}

fn equalsIgnoreCase(left: []const u8, right: []const u8) bool {
    if (left.len != right.len) return false;
    for (left, right) |l, r| {
        if (std.ascii.toLower(l) != std.ascii.toLower(r)) return false;
    }
    return true;
}

pub fn normalizeOs(name: []const u8) InstallError![]const u8 {
    if (startsWithIgnoreCase(name, "linux")) return "linux";
    if (startsWithIgnoreCase(name, "darwin") or startsWithIgnoreCase(name, "mac")) return "macos";
    if (startsWithIgnoreCase(name, "windows")) return "windows";
    return error.UnsupportedOs;
}

pub fn normalizeArch(name: []const u8) InstallError![]const u8 {
    if (equalsIgnoreCase(name, "amd64") or
        equalsIgnoreCase(name, "x86_64") or
        equalsIgnoreCase(name, "x64"))
        return "x86_64";
    if (equalsIgnoreCase(name, "arm64") or equalsIgnoreCase(name, "aarch64")) return "aarch64";
    if (equalsIgnoreCase(name, "x86") or
        equalsIgnoreCase(name, "i386") or
        equalsIgnoreCase(name, "i686"))
        return "x86";
    return error.UnsupportedArch;
}

pub fn detectSystemKey() InstallError![]const u8 {
    return switch (builtin.os.tag) {
        .linux => "linux",
        .macos => "macos",
        .windows => "windows",
        else => try normalizeOs(@tagName(builtin.os.tag)),
    };
}

pub fn detectArchKey() InstallError![]const u8 {
    return switch (builtin.cpu.arch) {
        .x86_64 => "x86_64",
        .aarch64 => "aarch64",
        .x86 => "x86",
        else => try normalizeArch(@tagName(builtin.cpu.arch)),
    };
}

pub fn isExplicitVersion(channel: []const u8) bool {
    var cursor: usize = 0;
    const parseDigits = struct {
        fn call(text: []const u8, cursor_ptr: *usize) bool {
            if (cursor_ptr.* >= text.len or !std.ascii.isDigit(text[cursor_ptr.*])) return false;
            while (cursor_ptr.* < text.len and std.ascii.isDigit(text[cursor_ptr.*])) : (cursor_ptr.* += 1) {}
            return true;
        }
    }.call;
    if (!parseDigits(channel, &cursor)) return false;
    if (cursor >= channel.len or channel[cursor] != '.') return false;
    cursor += 1;
    if (!parseDigits(channel, &cursor)) return false;
    if (cursor >= channel.len or channel[cursor] != '.') return false;
    cursor += 1;
    if (!parseDigits(channel, &cursor)) return false;
    if (cursor < channel.len and std.mem.startsWith(u8, channel[cursor..], "-dev.")) {
        cursor += "-dev.".len;
        if (!parseDigits(channel, &cursor)) return false;
        if (cursor < channel.len and channel[cursor] == '+') {
            cursor += 1;
            while (cursor < channel.len) : (cursor += 1) {
                const ch = channel[cursor];
                if (!std.ascii.isAlphanumeric(ch) and ch != '.' and ch != '-') return false;
            }
        }
    }
    return cursor == channel.len;
}

fn isRetryableStatus(status: u16) bool {
    for (retryable_http_status_codes) |code| {
        if (status == code) return true;
    }
    return false;
}

pub fn parseRetryAfter(retry_after: ?[]const u8) ?f64 {
    const value = retry_after orelse return null;
    const text = std.mem.trim(u8, value, " \t\r\n");
    if (text.len == 0) return null;
    for (text) |ch| {
        if (!std.ascii.isDigit(ch)) break;
    } else return std.fmt.parseFloat(f64, text) catch null;
    return parseHttpDateDelay(text);
}

fn parseHttpDateDelay(text: []const u8) ?f64 {
    const months = [_][]const u8{ "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" };
    if (text.len < 20) return null;
    var day: u32 = 0;
    var month: u8 = 0;
    var year: u32 = 0;
    var hour: u32 = 0;
    var minute: u32 = 0;
    var second: u32 = 0;
    day = std.fmt.parseInt(u32, text[0..2], 10) catch return null;
    if (text[2] != ' ') return null;
    const month_text = text[3..6];
    for (months, 0..) |name, index| {
        if (std.mem.eql(u8, month_text, name)) {
            month = @intCast(index);
            break;
        }
    } else return null;
    if (text[6] != ' ') return null;
    year = std.fmt.parseInt(u32, text[7..11], 10) catch return null;
    if (text[11] != ' ') return null;
    hour = std.fmt.parseInt(u32, text[12..14], 10) catch return null;
    if (text[14] != ':') return null;
    minute = std.fmt.parseInt(u32, text[15..17], 10) catch return null;
    if (text[17] != ':') return null;
    second = std.fmt.parseInt(u32, text[18..20], 10) catch return null;
    const epoch = httpDateToEpoch(year, month, day, hour, minute, second) orelse return null;
    return epoch;
}

fn httpDateToEpoch(year: u32, month: u8, day: u32, hour: u32, minute: u32, second: u32) ?f64 {
    if (month > 11 or day == 0 or day > 31) return null;
    var y: i32 = @intCast(year);
    var m: i32 = @intCast(month);
    if (m <= 1) {
        y -= 1;
        m += 12;
    }
    const era: i32 = if (y >= 0)
        @divTrunc(y, 400) - @divTrunc(y, 100) + @divTrunc(y, 4)
    else
        @divTrunc(y - 399, 400) - @divTrunc(y - 399, 100) + @divTrunc(y - 399, 4);
    const yoe: u32 = @intCast(y - era * 400);
    const doy = @divTrunc(153 * m + 2, 5) + @as(i32, @intCast(day)) - 307;
    const doe = yoe * 365 + @divTrunc(yoe, 4) - @divTrunc(yoe, 100) + @as(u32, @intCast(doy));
    const days: i64 = @as(i64, era) * 146097 + @as(i64, @intCast(doe)) - 719468;
    return @as(f64, @floatFromInt(days * 86_400 + hour * 3600 + minute * 60 + second));
}

pub fn retryDelaySeconds(attempt: u32, default_delay: f64, retry_after: ?[]const u8) f64 {
    if (parseRetryAfter(retry_after)) |parsed| return @min(parsed, max_retry_delay_seconds);
    _ = attempt;
    return @min(default_delay, max_retry_delay_seconds);
}

fn sleepSeconds(io: Io, seconds: f64) void {
    if (test_hooks.sleep_fn) |hook| {
        hook(seconds);
        return;
    }
    const ns: u64 = @intFromFloat(seconds * 1_000_000_000.0);
    std.Io.sleep(io, .{ .nanoseconds = ns }, .awake) catch {};
}

pub fn canonicalReleaseRepo(allocator: std.mem.Allocator, environ_map: std.process.Environ.Map) InstallError![]const u8 {
    if (environ_map.get("ZIGUX_ZIG_RELEASE_REPO")) |value| return dupe(allocator, value);
    return dupe(allocator, default_canonical_release_repo);
}

pub fn canonicalReleaseTag(allocator: std.mem.Allocator, environ_map: std.process.Environ.Map) InstallError![]const u8 {
    if (environ_map.get("ZIGUX_ZIG_RELEASE_TAG")) |value| return dupe(allocator, value);
    return dupe(allocator, default_canonical_release_tag);
}

pub fn loadPolicyChannel(
    io: Io,
    allocator: std.mem.Allocator,
    policy_path: []const u8,
    fallback: []const u8,
) InstallPolicyError![]const u8 {
    const json_bytes = std.Io.Dir.cwd().readFileAlloc(io, policy_path, allocator, .unlimited) catch |err| switch (err) {
        error.FileNotFound => return allocator.dupe(u8, fallback) catch error.OutOfMemory,
        else => return err,
    };
    defer allocator.free(json_bytes);

    const parsed_value = std.json.parseFromSlice(std.json.Value, allocator, json_bytes, .{
        .duplicate_field_behavior = .@"error",
    }) catch |err| switch (err) {
        error.DuplicateField => return error.DuplicatePolicyKey,
        error.SyntaxError, error.UnexpectedToken, error.InvalidNumber, error.InvalidCharacter => return error.InvalidPolicyJson,
        else => return error.InvalidChannel,
    };
    defer parsed_value.deinit();

    const root = switch (parsed_value.value) {
        .object => |object| object,
        else => return error.InvalidPolicyJson,
    };
    const channel_value = root.get("channel") orelse return error.InvalidChannel;
    const channel = switch (channel_value) {
        .string => |text| std.mem.trim(u8, text, " \t\r\n"),
        else => return error.InvalidChannel,
    };
    if (channel.len == 0) return error.InvalidChannel;
    return allocator.dupe(u8, channel) catch error.OutOfMemory;
}

pub fn loadPolicyArchiveSha256(
    io: Io,
    allocator: std.mem.Allocator,
    policy_path: []const u8,
    target_key: []const u8,
) InstallPolicyError!?[]const u8 {
    const json_bytes = std.Io.Dir.cwd().readFileAlloc(io, policy_path, allocator, .unlimited) catch |err| switch (err) {
        error.FileNotFound => return null,
        else => return err,
    };
    defer allocator.free(json_bytes);

    const parsed_value = std.json.parseFromSlice(std.json.Value, allocator, json_bytes, .{
        .duplicate_field_behavior = .@"error",
    }) catch |err| switch (err) {
        error.DuplicateField => return error.DuplicatePolicyKey,
        error.SyntaxError, error.UnexpectedToken, error.InvalidNumber, error.InvalidCharacter => return error.InvalidPolicyJson,
        else => return error.InvalidArchiveSha256,
    };
    defer parsed_value.deinit();

    const root = switch (parsed_value.value) {
        .object => |object| object,
        else => return error.InvalidArchiveSha256,
    };

    const archive_value = root.get("archive_sha256") orelse return null;
    const archive_object = switch (archive_value) {
        .object => |object| object,
        else => return error.InvalidArchiveSha256,
    };

    const digest_value = archive_object.get(target_key) orelse return null;
    const digest = switch (digest_value) {
        .string => |text| text,
        else => return error.InvalidArchiveDigest,
    };
    if (!policy.isValidSha256Hex(digest)) return error.InvalidArchiveDigest;
    return allocator.dupe(u8, digest) catch error.OutOfMemory;
}

pub fn calculateSha256(io: Io, allocator: std.mem.Allocator, path: []const u8) InstallError![]const u8 {
    var file = std.Io.Dir.cwd().openFile(io, path, .{}) catch |err| return err;
    defer file.close(io);

    var hasher = std.crypto.hash.sha2.Sha256.init(.{});
    var buffer: [download_chunk_size]u8 = undefined;
    while (true) {
        const read = std.Io.File.readStreaming(file, io, &.{&buffer}) catch |err| switch (err) {
            error.EndOfStream => break,
            else => return err,
        };
        if (read == 0) break;
        hasher.update(buffer[0..read]);
    }

    var digest: [32]u8 = undefined;
    hasher.final(&digest);
    return std.fmt.allocPrint(allocator, "{s}", .{std.fmt.bytesToHex(&digest, .lower)}) catch error.OutOfMemory;
}

pub fn verifyArchiveSha256(io: Io, allocator: std.mem.Allocator, path: []const u8, expected_sha256: []const u8) InstallError![]const u8 {
    const actual = try calculateSha256(io, allocator, path);
    if (!std.ascii.eqlIgnoreCase(actual, expected_sha256)) {
        allocator.free(actual);
        return error.ArchiveSha256Mismatch;
    }
    return actual;
}

pub fn inferTarballUrl(
    allocator: std.mem.Allocator,
    channel: []const u8,
    target_key: []const u8,
    system_key: []const u8,
    release_repo: []const u8,
    release_tag: []const u8,
) InstallError![]const u8 {
    const suffix = if (std.mem.eql(u8, system_key, "windows")) ".zip" else ".tar.xz";
    if (std.mem.eql(u8, channel, canonical_release_channel)) {
        return std.fmt.allocPrint(
            allocator,
            "https://github.com/{s}/releases/download/{s}/zig-{s}-{s}{s}",
            .{ release_repo, release_tag, target_key, channel, suffix },
        ) catch error.OutOfMemory;
    }
    if (std.mem.indexOf(u8, channel, "-dev.")) |_| {
        return std.fmt.allocPrint(
            allocator,
            "https://ziglang.org/builds/zig-{s}-{s}{s}",
            .{ target_key, channel, suffix },
        ) catch error.OutOfMemory;
    }
    return std.fmt.allocPrint(
        allocator,
        "https://ziglang.org/download/{s}/zig-{s}-{s}{s}",
        .{ channel, target_key, channel, suffix },
    ) catch error.OutOfMemory;
}

pub fn resolveTarget(
    allocator: std.mem.Allocator,
    index: std.json.ObjectMap,
    channel: []const u8,
    arch_key: []const u8,
    system_key: []const u8,
    release_repo: []const u8,
    release_tag: []const u8,
) InstallError!ResolveTargetResult {
    const target_key = try std.fmt.allocPrint(allocator, "{s}-{s}", .{ arch_key, system_key });
    errdefer allocator.free(target_key);

    if (std.mem.eql(u8, channel, canonical_release_channel)) {
        const tarball_url = try inferTarballUrl(allocator, channel, target_key, system_key, release_repo, release_tag);
        return .{
            .target_key = target_key,
            .version = try dupe(allocator, channel),
            .tarball_url = tarball_url,
        };
    }

    var entry = index.get(channel);
    if (entry == null and isExplicitVersion(channel)) {
        var it = index.iterator();
        while (it.next()) |item| {
            const candidate = item.value_ptr.*;
            if (candidate != .object) continue;
            const version_value = candidate.object.get("version") orelse continue;
            const version_text = switch (version_value) {
                .string => |text| text,
                else => continue,
            };
            if (std.mem.eql(u8, version_text, channel)) {
                entry = candidate;
                break;
            }
        }
        if (entry == null) {
            const tarball_url = try inferTarballUrl(allocator, channel, target_key, system_key, release_repo, release_tag);
            return .{
                .target_key = target_key,
                .version = try dupe(allocator, channel),
                .tarball_url = tarball_url,
            };
        }
    }

    const entry_object = entry orelse return error.UnknownChannel;
    const object = switch (entry_object) {
        .object => |value| value,
        else => return error.UnknownChannel,
    };

    const target_value = object.get(target_key) orelse return error.UnknownTarget;
    const target_object = switch (target_value) {
        .object => |value| value,
        else => return error.UnknownTarget,
    };
    const tarball_value = target_object.get("tarball") orelse return error.UnknownTarget;
    const tarball = switch (tarball_value) {
        .string => |text| text,
        else => return error.UnknownTarget,
    };
    const version_value = object.get("version") orelse return error.UnknownChannel;
    const version = switch (version_value) {
        .string => |text| text,
        else => return error.UnknownChannel,
    };

    return .{
        .target_key = target_key,
        .version = try dupe(allocator, version),
        .tarball_url = try dupe(allocator, tarball),
    };
}

pub fn readIndex(allocator: std.mem.Allocator, io: Io) OpenUrlError!std.json.ObjectMap {
    if (test_hooks.read_index_fn) |hook| return hook(allocator, io);
    const response = try openUrl(allocator, io, index_url, null, 3, 30.0);
    defer allocator.free(response.body);
    var parsed = std.json.parseFromSlice(std.json.Value, allocator, response.body, .{}) catch return error.OutOfMemory;
    const value = parsed.value;
    parsed.value = .null;
    parsed.deinit();
    return switch (value) {
        .object => |object| object,
        else => error.Network,
    };
}

pub fn loadIndex(allocator: std.mem.Allocator, io: Io, channel: []const u8) OpenUrlError!std.json.ObjectMap {
    return readIndex(allocator, io) catch |err| {
        if (!isExplicitVersion(channel)) return err;
        return std.json.ObjectMap{};
    };
}

pub fn openUrl(
    allocator: std.mem.Allocator,
    io: Io,
    url: []const u8,
    range_start: ?u64,
    retries: u32,
    timeout_seconds: f64,
) OpenUrlError!HttpResponse {
    if (test_hooks.open_url_fn) |hook| {
        var last_error: ?OpenUrlError = null;
        var attempt: u32 = 0;
        while (attempt < retries) : (attempt += 1) {
            const response = hook(allocator, io, url, range_start, retries, timeout_seconds) catch |err| {
                last_error = err;
                if (attempt + 1 == retries) return err;
                sleepSeconds(io, @min(0.5 * @as(f64, @floatFromInt(attempt + 1)), 2.0));
                continue;
            };
            if (response.status >= 400 and isRetryableStatus(response.status)) {
                if (attempt + 1 == retries) return error.HttpStatus;
                sleepSeconds(io, retryDelaySeconds(attempt + 1, @min(0.5 * @as(f64, @floatFromInt(attempt + 1)), 2.0), response.retry_after));
                continue;
            }
            return response;
        }
        return last_error orelse error.Network;
    }

    var last_error: ?OpenUrlError = null;
    var attempt: u32 = 0;
    while (attempt < retries) : (attempt += 1) {
        var client = std.http.Client{ .allocator = allocator, .io = io };
        defer client.deinit();

        var extra_headers_buffer: [1]std.http.Header = undefined;
        var extra_headers: []const std.http.Header = &.{};
        var range_buffer: [64]u8 = undefined;
        if (range_start) |offset| {
            const range_value = std.fmt.bufPrint(&range_buffer, "bytes={d}-", .{offset}) catch return error.OutOfMemory;
            extra_headers_buffer[0] = .{ .name = "Range", .value = range_value };
            extra_headers = extra_headers_buffer[0..];
        }

        var body: std.ArrayList(u8) = .empty;
        var writer = std.Io.Writer.fromArrayList(&body);

        const fetch_result = client.fetch(.{
            .location = .{ .url = url },
            .method = .GET,
            .extra_headers = extra_headers,
            .response_writer = &writer,
        }) catch |err| {
            last_error = switch (err) {
                error.OutOfMemory => error.OutOfMemory,
                else => error.Network,
            };
            if (attempt + 1 == retries) return last_error.?;
            sleepSeconds(io, @min(0.5 * @as(f64, @floatFromInt(attempt + 1)), 2.0));
            continue;
        };

        const status: u16 = @backingInt(fetch_result.status);
        if (status >= 400) {
            if (!isRetryableStatus(status) or attempt + 1 == retries) return error.HttpStatus;
            sleepSeconds(io, retryDelaySeconds(attempt + 1, @min(0.5 * @as(f64, @floatFromInt(attempt + 1)), 2.0), null));
            continue;
        }

        if (timeout_seconds < 0) return error.Network;
        body = std.Io.Writer.toArrayList(&writer);
        return .{
            .status = status,
            .body = try body.toOwnedSlice(allocator),
        };
    }
    return last_error orelse error.Network;
}

pub fn curlAvailable(io: Io) bool {
    if (test_hooks.curl_available_fn) |hook| return hook(io);
    const result = std.process.run(std.heap.page_allocator, io, .{
        .argv = &.{ "curl", "--version" },
        .stdout_limit = .limited(1024),
        .stderr_limit = .limited(1024),
    }) catch return false;
    defer std.heap.page_allocator.free(result.stdout);
    defer std.heap.page_allocator.free(result.stderr);
    return switch (result.term) {
        .exited => |code| code == 0,
        else => false,
    };
}

pub fn copyUrlToFileWithCurl(
    io: Io,
    url: []const u8,
    destination: []const u8,
    retries: u32,
    timeout_seconds: f64,
) InstallError!void {
    if (test_hooks.copy_url_with_curl_fn) |hook| return hook(io, url, destination, retries, timeout_seconds);

    const parent = std.fs.path.dirname(destination) orelse return error.DownloadFailed;
    try std.Io.Dir.cwd().createDirPath(io, parent);

    const connect_timeout = @max(5, @as(u32, @intFromFloat(timeout_seconds / 4)));
    const speed_time = @max(30, @as(u32, @intFromFloat(timeout_seconds)));
    const retries_text = try std.fmt.allocPrint(std.heap.page_allocator, "{d}", .{retries});
    defer std.heap.page_allocator.free(retries_text);
    const connect_timeout_text = try std.fmt.allocPrint(std.heap.page_allocator, "{d}", .{connect_timeout});
    defer std.heap.page_allocator.free(connect_timeout_text);
    const speed_time_text = try std.fmt.allocPrint(std.heap.page_allocator, "{d}", .{speed_time});
    defer std.heap.page_allocator.free(speed_time_text);

    const result = std.process.run(std.heap.page_allocator, io, .{
        .argv = &.{
            "curl",
            "--fail",
            "--location",
            "--silent",
            "--show-error",
            "--retry",
            retries_text,
            "--retry-all-errors",
            "--retry-delay",
            "2",
            "--connect-timeout",
            connect_timeout_text,
            "--speed-limit",
            "1",
            "--speed-time",
            speed_time_text,
            "--continue-at",
            "-",
            "--output",
            destination,
            url,
        },
        .stdout_limit = .limited(1024),
        .stderr_limit = .limited(16 * 1024),
    }) catch return error.DownloadFailed;
    defer std.heap.page_allocator.free(result.stdout);
    defer std.heap.page_allocator.free(result.stderr);
    switch (result.term) {
        .exited => |code| if (code != 0) return error.DownloadFailed,
        else => return error.DownloadFailed,
    }
}

fn fileSize(io: Io, path: []const u8) InstallError!u64 {
    var file = try std.Io.Dir.cwd().openFile(io, path, .{});
    defer file.close(io);
    return (try file.stat(io)).size;
}

fn removeFileIfExists(io: Io, path: []const u8) void {
    std.Io.Dir.cwd().deleteFile(io, path) catch {};
}

pub fn copyUrlToFile(
    allocator: std.mem.Allocator,
    io: Io,
    url: []const u8,
    destination: []const u8,
    retries: u32,
    timeout_seconds: f64,
) InstallError!void {
    var last_error: ?InstallError = null;

    if (curlAvailable(io)) {
        if (copyUrlToFileWithCurl(io, url, destination, retries, timeout_seconds)) {
            return;
        } else |err| {
            last_error = err;
            if (fileSize(io, destination) catch 0 == 0) removeFileIfExists(io, destination);
        }
    }

    var attempt: u32 = 0;
    while (attempt < retries) : (attempt += 1) {
        const resume_offset = if (std.Io.Dir.cwd().access(io, destination, .{})) blk: {
            break :blk fileSize(io, destination) catch 0;
        } else |_| 0;

        const response = openUrl(allocator, io, url, if (resume_offset > 0) resume_offset else null, 1, timeout_seconds) catch |err| {
            last_error = switch (err) {
                error.OutOfMemory => error.OutOfMemory,
                else => error.DownloadFailed,
            };
            if (attempt + 1 == retries) break;
            sleepSeconds(io, @min(1.5 * @as(f64, @floatFromInt(attempt + 1)), 5.0));
            continue;
        };
        defer allocator.free(response.body);

        const append = resume_offset > 0 and response.status == 206;
        if (!append) removeFileIfExists(io, destination);

        const parent = std.fs.path.dirname(destination) orelse return error.DownloadFailed;
        try std.Io.Dir.cwd().createDirPath(io, parent);

        var out = if (append)
            try std.Io.Dir.cwd().openFile(io, destination, .{ .mode = .read_write })
        else
            try std.Io.Dir.cwd().createFile(io, destination, .{ .truncate = true });
        defer out.close(io);
        if (append) try io.vtable.fileSeekTo(io.userdata, out, resume_offset);

        try std.Io.File.writeStreamingAll(out, io, response.body);
        return;
    }

    return last_error orelse error.DownloadFailed;
}

fn copyFile(io: Io, source: []const u8, destination: []const u8) InstallError!void {
    const parent = std.fs.path.dirname(destination) orelse return error.OutOfMemory;
    try std.Io.Dir.cwd().createDirPath(io, parent);

    var src = try std.Io.Dir.cwd().openFile(io, source, .{});
    defer src.close(io);

    var dst = try std.Io.Dir.cwd().createFile(io, destination, .{ .truncate = true });
    defer dst.close(io);

    var buffer: [download_chunk_size]u8 = undefined;
    while (true) {
        const read = std.Io.File.readStreaming(src, io, &.{&buffer}) catch |err| switch (err) {
            error.EndOfStream => break,
            else => return err,
        };
        if (read == 0) break;
        try std.Io.File.writeStreamingAll(dst, io, buffer[0..read]);
    }
}

fn copyDirRecursive(io: Io, source: []const u8, destination: []const u8) InstallError!void {
    try std.Io.Dir.cwd().createDirPath(io, destination);
    var dir = try std.Io.Dir.cwd().openDir(io, source, .{ .iterate = true });
    defer dir.close(io);

    var it = dir.iterate();
    while (try it.next(io)) |entry| {
        const child_source = try std.fmt.allocPrint(std.heap.page_allocator, "{s}/{s}", .{ source, entry.name });
        defer std.heap.page_allocator.free(child_source);
        const child_destination = try std.fmt.allocPrint(std.heap.page_allocator, "{s}/{s}", .{ destination, entry.name });
        defer std.heap.page_allocator.free(child_destination);
        switch (entry.kind) {
            .directory => try copyDirRecursive(io, child_source, child_destination),
            .file => try copyFile(io, child_source, child_destination),
            else => {},
        }
    }
}

pub fn extractArchive(io: Io, allocator: std.mem.Allocator, archive_path: []const u8, dest_path: []const u8) InstallError![]const u8 {
    try std.Io.Dir.cwd().createDirPath(io, dest_path);

    if (std.mem.endsWith(u8, archive_path, ".zip")) {
        var archive_file = try std.Io.Dir.cwd().openFile(io, archive_path, .{});
        defer archive_file.close(io);
        var file_reader_buffer: [download_chunk_size]u8 = undefined;
        var file_reader = archive_file.reader(io, &file_reader_buffer);
        var dest_dir = try std.Io.Dir.cwd().openDir(io, dest_path, .{});
        defer dest_dir.close(io);
        std.zip.extract(dest_dir, &file_reader, .{}) catch return error.ExtractFailed;
    } else {
        var archive_file = try std.Io.Dir.cwd().openFile(io, archive_path, .{});
        defer archive_file.close(io);
        var file_reader_buffer: [download_chunk_size]u8 = undefined;
        var file_reader = archive_file.reader(io, &file_reader_buffer);
        const xz_buffer = try allocator.alloc(u8, 256 * 1024);
        defer allocator.free(xz_buffer);
        var xz = std.compress.xz.Decompress.init(&file_reader.interface, allocator, xz_buffer) catch return error.ExtractFailed;
        defer xz.deinit();
        var dest_dir = try std.Io.Dir.cwd().openDir(io, dest_path, .{});
        defer dest_dir.close(io);
        std.tar.extract(io, dest_dir, &xz.reader, .{}) catch return error.ExtractFailed;
    }

    var dest_dir = try std.Io.Dir.cwd().openDir(io, dest_path, .{ .iterate = true });
    defer dest_dir.close(io);
    var children = std.ArrayListUnmanaged([]const u8).empty;
    defer {
        for (children.items) |item| allocator.free(item);
        children.deinit(allocator);
    }
    var it = dest_dir.iterate();
    while (try it.next(io)) |entry| {
        if (entry.kind != .directory) continue;
        try children.append(allocator, try dupe(allocator, entry.name));
    }
    if (children.items.len != 1) return error.UnexpectedExtractLayout;
    return dupe(allocator, children.items[0]);
}

fn pathAccessible(io: Io, path: []const u8) bool {
    std.Io.Dir.cwd().access(io, path, .{}) catch return false;
    return true;
}

pub fn resolveBinDir(io: Io, allocator: std.mem.Allocator, final_root: []const u8) InstallError![]const u8 {
    const zig_path = try std.fmt.allocPrint(std.heap.page_allocator, "{s}/zig", .{final_root});
    defer std.heap.page_allocator.free(zig_path);
    const zig_exe_path = try std.fmt.allocPrint(std.heap.page_allocator, "{s}/zig.exe", .{final_root});
    defer std.heap.page_allocator.free(zig_exe_path);
    if (pathAccessible(io, zig_path) or pathAccessible(io, zig_exe_path)) {
        return dupe(allocator, final_root);
    }

    const bin_zig_path = try std.fmt.allocPrint(std.heap.page_allocator, "{s}/bin/zig", .{final_root});
    defer std.heap.page_allocator.free(bin_zig_path);
    const bin_zig_exe_path = try std.fmt.allocPrint(std.heap.page_allocator, "{s}/bin/zig.exe", .{final_root});
    defer std.heap.page_allocator.free(bin_zig_exe_path);
    const bin_dir = try std.fmt.allocPrint(allocator, "{s}/bin", .{final_root});
    if (pathAccessible(io, bin_zig_path) or pathAccessible(io, bin_zig_exe_path)) {
        return bin_dir;
    }
    allocator.free(bin_dir);
    return error.MissingZigBinary;
}

pub fn appendGithubPath(io: Io, environ_map: std.process.Environ.Map, path: []const u8) InstallError!void {
    const github_path = environ_map.get("GITHUB_PATH") orelse return;
    const resolved = std.Io.Dir.cwd().realPathFileAlloc(io, path, std.heap.page_allocator) catch return error.OutOfMemory;
    defer std.heap.page_allocator.free(resolved);

    var file = try std.Io.Dir.cwd().openFile(io, github_path, .{ .mode = .read_write });
    defer file.close(io);
    const end_offset = (try file.stat(io)).size;
    const line = try std.fmt.allocPrint(std.heap.page_allocator, "{s}\n", .{resolved});
    defer std.heap.page_allocator.free(line);
    try std.Io.File.writePositionalAll(file, io, line, end_offset);
}

pub fn stageArchive(
    io: Io,
    local_archive: ?[]const u8,
    tarball_url: []const u8,
    archive_path: []const u8,
    allocator: std.mem.Allocator,
) InstallError!ArchiveSource {
    if (local_archive) |source| {
        var src_file = std.Io.Dir.cwd().openFile(io, source, .{}) catch return error.LocalArchiveNotFound;
        defer src_file.close(io);
        const kind = (try src_file.stat(io)).kind;
        if (kind != .file) return error.LocalArchiveNotFile;
        try copyFile(io, source, archive_path);
        return .local_archive;
    }
    try copyUrlToFile(allocator, io, tarball_url, archive_path, download_retries, download_timeout_seconds);
    return .download;
}

pub fn expandUserPath(allocator: std.mem.Allocator, environ_map: std.process.Environ.Map, path: []const u8) InstallError![]const u8 {
    if (!std.mem.startsWith(u8, path, "~")) return dupe(allocator, path);
    const home = environ_map.get("USERPROFILE") orelse environ_map.get("HOME") orelse return dupe(allocator, path);
    if (path.len == 1) return dupe(allocator, home);
    if (path[1] == '/' or path[1] == '\\') {
        return std.fmt.allocPrint(allocator, "{s}{s}", .{ home, path[1..] }) catch error.OutOfMemory;
    }
    return dupe(allocator, path);
}

pub fn freeResolveTarget(allocator: std.mem.Allocator, resolved: *ResolveTargetResult) void {
    allocator.free(resolved.target_key);
    allocator.free(resolved.version);
    allocator.free(resolved.tarball_url);
}

fn throttledOpenHook(alloc: std.mem.Allocator, _: Io, _: []const u8, _: ?u64, _: u32, _: f64) OpenUrlError!HttpResponse {
    self_test_state.throttled_open_attempts += 1;
    if (self_test_state.throttled_open_attempts == 1) return .{ .status = 429, .body = try alloc.dupe(u8, ""), .retry_after = "0" };
    return .{ .status = 200, .body = try alloc.dupe(u8, "{}") };
}

fn throttledSleepHook(seconds: f64) void {
    self_test_state.throttled_sleep_calls.append(std.heap.page_allocator, seconds) catch {};
}

fn resumableOpenHook(alloc: std.mem.Allocator, io: Io, _: []const u8, range_start: ?u64, _: u32, _: f64) OpenUrlError!HttpResponse {
    if (range_start) |offset| {
        const header = try std.fmt.allocPrint(alloc, "bytes={d}-", .{offset});
        try self_test_state.resume_headers.append(alloc, header);
        return .{ .status = 206, .body = try alloc.dupe(u8, "data") };
    }
    try self_test_state.resume_headers.append(alloc, null);
    if (self_test_state.resume_destination) |destination| {
        std.Io.Dir.cwd().writeFile(io, .{ .sub_path = destination, .data = "zig-" }) catch {};
    }
    return error.Network;
}

fn throttledDownloadOpenHook(alloc: std.mem.Allocator, _: Io, _: []const u8, range_start: ?u64, _: u32, _: f64) OpenUrlError!HttpResponse {
    _ = range_start;
    self_test_state.throttled_download_attempts += 1;
    if (self_test_state.throttled_download_attempts == 1) return .{ .status = 429, .body = try alloc.dupe(u8, ""), .retry_after = "0" };
    return .{ .status = 200, .body = try alloc.dupe(u8, "zig-download") };
}

fn recordCurlCommandHook(_: Io, url: []const u8, destination: []const u8, retries: u32, timeout_seconds: f64) InstallError!void {
    const cmd = try std.heap.page_allocator.alloc([]const u8, 3);
    cmd[0] = try dupe(std.heap.page_allocator, "curl");
    cmd[1] = try dupe(std.heap.page_allocator, destination);
    cmd[2] = try dupe(std.heap.page_allocator, url);
    try self_test_state.curl_commands.append(std.heap.page_allocator, cmd);
    _ = retries;
    _ = timeout_seconds;
}

fn curlAlwaysAvailableHook(_: Io) bool {
    return true;
}

fn curlUnavailableHook(_: Io) bool {
    return false;
}

fn countCurlCopyHook(_: Io, _: []const u8, _: []const u8, _: u32, _: f64) InstallError!void {
    self_test_state.curl_copy_calls += 1;
}

fn downloadOpenHook(alloc: std.mem.Allocator, _: Io, _: []const u8, _: ?u64, _: u32, _: f64) OpenUrlError!HttpResponse {
    self_test_state.download_calls += 1;
    return .{ .status = 200, .body = try alloc.dupe(u8, "downloaded") };
}

fn resetSelfTestState(allocator: std.mem.Allocator) void {
    for (self_test_state.resume_headers.items) |item| {
        if (item) |value| allocator.free(value);
    }
    self_test_state.resume_headers.deinit(allocator);
    self_test_state.throttled_sleep_calls.deinit(std.heap.page_allocator);
    for (self_test_state.curl_commands.items) |cmd| {
        for (cmd) |arg| std.heap.page_allocator.free(arg);
        std.heap.page_allocator.free(cmd);
    }
    self_test_state.curl_commands.deinit(std.heap.page_allocator);
    self_test_state = .{
        .throttled_sleep_calls = .empty,
        .resume_headers = .empty,
        .curl_commands = .empty,
    };
}

var self_test_check_index: u32 = 0;

fn expectSelfTestCheck(io: Io, ok: bool) InstallError!void {
    _ = io;
    self_test_check_index += 1;
    if (!ok) return error.DownloadFailed;
}

fn expectSelfTestError(io: Io, comptime expected: anyerror, result: anytype) InstallError!void {
    if (result) |_| {
        try expectSelfTestCheck(io, false);
    } else |err| {
        try expectSelfTestCheck(io, err == expected);
    }
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator, environ_map: std.process.Environ.Map) InstallError!u32 {
    const saved_open_url_fn = test_hooks.open_url_fn;
    const saved_read_index_fn = test_hooks.read_index_fn;
    const saved_sleep_fn = test_hooks.sleep_fn;
    const saved_curl_available_fn = test_hooks.curl_available_fn;
    const saved_copy_url_with_curl_fn = test_hooks.copy_url_with_curl_fn;
    defer {
        test_hooks.open_url_fn = saved_open_url_fn;
        test_hooks.read_index_fn = saved_read_index_fn;
        test_hooks.sleep_fn = saved_sleep_fn;
        test_hooks.curl_available_fn = saved_curl_available_fn;
        test_hooks.copy_url_with_curl_fn = saved_copy_url_with_curl_fn;
        resetSelfTestState(allocator);
    }
    test_hooks.curl_available_fn = curlUnavailableHook;
    var scratch = std.heap.ArenaAllocator.init(allocator);
    defer scratch.deinit();
    const scratch_allocator = scratch.allocator();
    var case_count: u32 = 0;
    self_test_check_index = 0;

    try expectSelfTestCheck(io, std.mem.eql(u8, try normalizeOs("Linux"), "linux"));
    case_count += 1;
    try expectSelfTestCheck(io, std.mem.eql(u8, try normalizeOs("Darwin"), "macos"));
    case_count += 1;
    try expectSelfTestCheck(io, std.mem.eql(u8, try normalizeOs("Windows"), "windows"));
    case_count += 1;

    try expectSelfTestCheck(io, std.mem.eql(u8, try normalizeArch("amd64"), "x86_64"));
    case_count += 1;
    try expectSelfTestCheck(io, std.mem.eql(u8, try normalizeArch("aarch64"), "aarch64"));
    case_count += 1;
    try expectSelfTestCheck(io, std.mem.eql(u8, try normalizeArch("i686"), "x86"));
    case_count += 1;

    var sample_index = std.json.ObjectMap{};
    defer sample_index.deinit(scratch_allocator);
    try sample_index.put(
        scratch_allocator,
        "master",
        .{ .object = blk: {
            var master = std.json.ObjectMap{};
            try master.put(scratch_allocator, "version", .{ .string = canonical_release_channel });
            var linux_target = std.json.ObjectMap{};
            try linux_target.put(scratch_allocator, "tarball", .{ .string = "https://example.invalid/zig-linux.tar.xz" });
            try master.put(scratch_allocator, "x86_64-linux", .{ .object = linux_target });
            var macos_target = std.json.ObjectMap{};
            try macos_target.put(scratch_allocator, "tarball", .{ .string = "https://example.invalid/zig-macos.tar.xz" });
            try master.put(scratch_allocator, "aarch64-macos", .{ .object = macos_target });
            break :blk master;
        } },
    );
    try sample_index.put(
        scratch_allocator,
        "0.16.0",
        .{ .object = blk: {
            var release = std.json.ObjectMap{};
            try release.put(scratch_allocator, "version", .{ .string = "0.16.0" });
            var linux_target = std.json.ObjectMap{};
            try linux_target.put(scratch_allocator, "tarball", .{ .string = "https://example.invalid/zig-0.16.0.tar.xz" });
            try release.put(scratch_allocator, "x86_64-linux", .{ .object = linux_target });
            break :blk release;
        } },
    );

    const release_repo = try canonicalReleaseRepo(allocator, environ_map);
    defer allocator.free(release_repo);
    const release_tag = try canonicalReleaseTag(allocator, environ_map);
    defer allocator.free(release_tag);

    var resolved_master = try resolveTarget(allocator, sample_index, "master", "x86_64", "linux", release_repo, release_tag);
    defer freeResolveTarget(allocator, &resolved_master);
    try expectSelfTestCheck(io, std.mem.eql(u8, resolved_master.target_key, "x86_64-linux") and
        std.mem.eql(u8, resolved_master.version, canonical_release_channel) and
        std.mem.eql(u8, resolved_master.tarball_url, "https://example.invalid/zig-linux.tar.xz"));
    case_count += 1;

    var resolved_macos = try resolveTarget(allocator, sample_index, "master", "aarch64", "macos", release_repo, release_tag);
    defer freeResolveTarget(allocator, &resolved_macos);
    try expectSelfTestCheck(io, std.mem.eql(u8, resolved_macos.target_key, "aarch64-macos"));
    case_count += 1;

    var resolved_canonical = try resolveTarget(allocator, sample_index, canonical_release_channel, "x86_64", "linux", release_repo, release_tag);
    defer freeResolveTarget(allocator, &resolved_canonical);
    const canonical_url = try std.fmt.allocPrint(
        allocator,
        "https://github.com/{s}/releases/download/{s}/zig-x86_64-linux-{s}.tar.xz",
        .{ release_repo, release_tag, canonical_release_channel },
    );
    defer allocator.free(canonical_url);
    try expectSelfTestCheck(io, std.mem.eql(u8, resolved_canonical.tarball_url, canonical_url));
    case_count += 1;

    var partial_index = std.json.ObjectMap{};
    defer partial_index.deinit(scratch_allocator);
    try partial_index.put(scratch_allocator, "0.16.0", sample_index.get("0.16.0").?);
    var resolved_fallback = try resolveTarget(allocator, partial_index, canonical_release_channel, "x86_64", "linux", release_repo, release_tag);
    defer freeResolveTarget(allocator, &resolved_fallback);
    try expectSelfTestCheck(io, std.mem.eql(u8, resolved_fallback.tarball_url, canonical_url));
    case_count += 1;

    const original_read_index = test_hooks.read_index_fn;
    test_hooks.read_index_fn = struct {
        fn hook(alloc: std.mem.Allocator, _: Io) OpenUrlError!std.json.ObjectMap {
            _ = alloc;
            return error.Network;
        }
    }.hook;
    var empty_index = try loadIndex(allocator, io, canonical_release_channel);
    defer empty_index.deinit(allocator);
    try expectSelfTestCheck(io, empty_index.count() == 0);
    case_count += 1;
    if (loadIndex(allocator, io, "master")) |_| {
        return error.DownloadFailed;
    } else |err| {
        try expectSelfTestCheck(io, err == error.Network);
    }
    case_count += 1;
    test_hooks.read_index_fn = original_read_index;

    const policy_root = try std.fmt.allocPrint(allocator, ".zig-cache/tmp/zigux_install_zig_policy_{d}", .{installTmpId(io)});
    defer allocator.free(policy_root);
    std.Io.Dir.cwd().deleteTree(io, policy_root) catch {};
    try std.Io.Dir.cwd().createDirPath(io, policy_root);
    defer std.Io.Dir.cwd().deleteTree(io, policy_root) catch {};

    const policy_path = try std.fmt.allocPrint(allocator, "{s}/zig-toolchain-policy.json", .{policy_root});
    defer allocator.free(policy_path);

    const missing_channel = try loadPolicyChannel(io, allocator, policy_path, "0.15.0");
    defer allocator.free(missing_channel);
    try expectSelfTestCheck(io, std.mem.eql(u8, missing_channel, "0.15.0"));
    case_count += 1;
    try expectSelfTestCheck(io, (try loadPolicyArchiveSha256(io, allocator, policy_path, "x86_64-linux")) == null);
    case_count += 1;

    try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = policy_path, .data = "{\"channel\":\"0.17.0-dev.1443+6c25d2bd5\",\"archive_sha256\":{\"x86_64-linux\":\"4620f31b3889dcdcb257e6a0da6a4bc9a0b2b8e3db04219c1c160798e2cdc5a9\"}}\n" });
    const policy_channel = try loadPolicyChannel(io, allocator, policy_path, "0.15.0");
    defer allocator.free(policy_channel);
    try expectSelfTestCheck(io, std.mem.eql(u8, policy_channel, canonical_release_channel));
    case_count += 1;
    const policy_digest = (try loadPolicyArchiveSha256(io, allocator, policy_path, "x86_64-linux")).?;
    defer allocator.free(policy_digest);
    try expectSelfTestCheck(io, std.mem.eql(u8, policy_digest, "4620f31b3889dcdcb257e6a0da6a4bc9a0b2b8e3db04219c1c160798e2cdc5a9"));
    case_count += 1;
    try expectSelfTestCheck(io, (try loadPolicyArchiveSha256(io, allocator, policy_path, "aarch64-linux")) == null);
    case_count += 1;

    try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = policy_path, .data = "{\"channel\":7}\n" });
    try expectSelfTestError(io, error.InvalidChannel, loadPolicyChannel(io, allocator, policy_path, "0.15.0"));
    case_count += 1;
    try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = policy_path, .data = "{\"channel\":\"0.17.0-dev.1443+6c25d2bd5\",\"archive_sha256\":7}\n" });
    try expectSelfTestError(io, error.InvalidArchiveSha256, loadPolicyArchiveSha256(io, allocator, policy_path, "x86_64-linux"));
    case_count += 1;
    try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = policy_path, .data = "{\"channel\":\"0.17.0-dev.1443+6c25d2bd5\",\"archive_sha256\":{\"x86_64-linux\":\"short\"}}\n" });
    try expectSelfTestError(io, error.InvalidArchiveDigest, loadPolicyArchiveSha256(io, allocator, policy_path, "x86_64-linux"));
    case_count += 1;
    try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = policy_path, .data = "{not-json}\n" });
    try expectSelfTestError(io, error.InvalidPolicyJson, loadPolicyChannel(io, allocator, policy_path, "0.15.0"));
    case_count += 1;
    try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = policy_path, .data = "{\"channel\":\"0.17.0-dev.1443+6c25d2bd5\",\"channel\":\"0.17.0-dev.90+abcdef\"}\n" });
    try expectSelfTestError(io, error.DuplicatePolicyKey, loadPolicyChannel(io, allocator, policy_path, "0.15.0"));
    case_count += 1;
    try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = policy_path, .data = "{\"channel\":\"0.17.0-dev.1443+6c25d2bd5\",\"archive_sha256\":{\"x86_64-linux\":\"4620f31b3889dcdcb257e6a0da6a4bc9a0b2b8e3db04219c1c160798e2cdc5a9\",\"x86_64-linux\":\"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\"}}\n" });
    try expectSelfTestError(io, error.DuplicatePolicyKey, loadPolicyArchiveSha256(io, allocator, policy_path, "x86_64-linux"));
    case_count += 1;

    const sha_root = try std.fmt.allocPrint(allocator, ".zig-cache/tmp/zigux_install_zig_sha_{d}", .{installTmpId(io)});
    defer allocator.free(sha_root);
    std.Io.Dir.cwd().deleteTree(io, sha_root) catch {};
    try std.Io.Dir.cwd().createDirPath(io, sha_root);
    defer std.Io.Dir.cwd().deleteTree(io, sha_root) catch {};
    const archive_path = try std.fmt.allocPrint(allocator, "{s}/archive.tar.xz", .{sha_root});
    defer allocator.free(archive_path);
    try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = archive_path, .data = "zigux-archive" });
    const expected_sha = try calculateSha256(io, allocator, archive_path);
    defer allocator.free(expected_sha);
    try expectSelfTestCheck(io, std.mem.eql(u8, expected_sha, "af1d92212224e2ce162e6e44f002997d81d5e7bb293a5e55c526f91a51b31a8a"));
    case_count += 1;
    const verified = try verifyArchiveSha256(io, allocator, archive_path, expected_sha);
    defer allocator.free(verified);
    try expectSelfTestCheck(io, std.mem.eql(u8, verified, expected_sha));
    case_count += 1;
    try expectSelfTestError(io, error.ArchiveSha256Mismatch, verifyArchiveSha256(io, allocator, archive_path, "0000000000000000000000000000000000000000000000000000000000000000"));
    case_count += 1;

    try expectSelfTestCheck(io, parseRetryAfter(null) == null and parseRetryAfter("") == null);
    case_count += 1;
    try expectSelfTestCheck(io, parseRetryAfter("7").? == 7.0);
    case_count += 1;
    try expectSelfTestCheck(io, retryDelaySeconds(1, 0.5, "60") == max_retry_delay_seconds);
    case_count += 1;
    try expectSelfTestCheck(io, retryDelaySeconds(2, 1.25, null) == 1.25);
    case_count += 1;

    resetSelfTestState(allocator);
    test_hooks.curl_available_fn = curlUnavailableHook;
    const original_open_url = test_hooks.open_url_fn;
    const original_sleep = test_hooks.sleep_fn;
    test_hooks.open_url_fn = throttledOpenHook;
    test_hooks.sleep_fn = throttledSleepHook;
    const throttled_response = try openUrl(allocator, io, "https://example.invalid/index.json", null, 2, 1.0);
    defer allocator.free(throttled_response.body);
    try expectSelfTestCheck(io, std.mem.eql(u8, throttled_response.body, "{}"));
    try expectSelfTestCheck(io, self_test_state.throttled_open_attempts == 2);
    try expectSelfTestCheck(io, self_test_state.throttled_sleep_calls.items.len == 1 and self_test_state.throttled_sleep_calls.items[0] == 0.0);
    case_count += 1;
    test_hooks.open_url_fn = original_open_url;
    test_hooks.sleep_fn = original_sleep;

    resetSelfTestState(allocator);
    test_hooks.curl_available_fn = curlUnavailableHook;
    test_hooks.open_url_fn = resumableOpenHook;
    const resume_root = try std.fmt.allocPrint(allocator, ".zig-cache/tmp/zigux_install_zig_selftest_{d}", .{installTmpId(io)});
    defer allocator.free(resume_root);
    std.Io.Dir.cwd().deleteTree(io, resume_root) catch {};
    try std.Io.Dir.cwd().createDirPath(io, resume_root);
    defer std.Io.Dir.cwd().deleteTree(io, resume_root) catch {};
    const resume_path = try std.fmt.allocPrint(allocator, "{s}/archive.tar.xz", .{resume_root});
    defer allocator.free(resume_path);
    self_test_state.resume_destination = resume_path;
    try copyUrlToFile(allocator, io, "https://example.invalid/archive.tar.xz", resume_path, 2, 1.0);
    self_test_state.resume_destination = null;
    const resume_bytes = try std.Io.Dir.cwd().readFileAlloc(io, resume_path, allocator, .unlimited);
    defer allocator.free(resume_bytes);
    try expectSelfTestCheck(io, std.mem.eql(u8, resume_bytes, "zig-data"));
    try expectSelfTestCheck(io, self_test_state.resume_headers.items.len == 2);
    try expectSelfTestCheck(io, self_test_state.resume_headers.items[1] != null and std.mem.eql(u8, self_test_state.resume_headers.items[1].?, "bytes=4-"));
    case_count += 1;

    resetSelfTestState(allocator);
    test_hooks.open_url_fn = throttledDownloadOpenHook;
    const throttled_root = try std.fmt.allocPrint(allocator, ".zig-cache/tmp/zigux_install_zig_throttle_{d}", .{installTmpId(io)});
    defer allocator.free(throttled_root);
    std.Io.Dir.cwd().deleteTree(io, throttled_root) catch {};
    try std.Io.Dir.cwd().createDirPath(io, throttled_root);
    defer std.Io.Dir.cwd().deleteTree(io, throttled_root) catch {};
    const throttled_path = try std.fmt.allocPrint(allocator, "{s}/archive.tar.xz", .{throttled_root});
    defer allocator.free(throttled_path);
    try copyUrlToFile(allocator, io, "https://example.invalid/archive.tar.xz", throttled_path, 2, 1.0);
    const throttled_bytes = try std.Io.Dir.cwd().readFileAlloc(io, throttled_path, allocator, .unlimited);
    defer allocator.free(throttled_bytes);
    try expectSelfTestCheck(io, std.mem.eql(u8, throttled_bytes, "zig-download"));
    try expectSelfTestCheck(io, self_test_state.throttled_download_attempts == 2);
    case_count += 1;

    resetSelfTestState(allocator);
    test_hooks.curl_available_fn = curlUnavailableHook;
    test_hooks.copy_url_with_curl_fn = recordCurlCommandHook;
    try copyUrlToFileWithCurl(io, "https://example.invalid/archive.tar.xz", ".zig-cache/tmp/zigux-install-zig-curl-test/archive.tar.xz", 5, 90.0);
    try expectSelfTestCheck(io, self_test_state.curl_commands.items.len == 1);
    try expectSelfTestCheck(io, std.mem.eql(u8, self_test_state.curl_commands.items[0][0], "curl"));
    try expectSelfTestCheck(io, std.mem.eql(u8, self_test_state.curl_commands.items[0][2], "https://example.invalid/archive.tar.xz"));
    case_count += 1;

    resetSelfTestState(allocator);
    test_hooks.curl_available_fn = curlAlwaysAvailableHook;
    test_hooks.copy_url_with_curl_fn = countCurlCopyHook;
    try copyUrlToFile(allocator, io, "https://example.invalid/archive.tar.xz", ".zig-cache/tmp/zigux-install-zig-curl-preferred/archive.tar.xz", 7, 9.0);
    try expectSelfTestCheck(io, self_test_state.curl_copy_calls == 1);
    case_count += 1;
    test_hooks.copy_url_with_curl_fn = null;
    test_hooks.curl_available_fn = null;
    test_hooks.open_url_fn = original_open_url;

    const layout_root = try std.fmt.allocPrint(allocator, ".zig-cache/tmp/zigux_install_zig_layout_{d}", .{installTmpId(io)});
    defer allocator.free(layout_root);
    std.Io.Dir.cwd().deleteTree(io, layout_root) catch {};
    try std.Io.Dir.cwd().createDirPath(io, layout_root);
    defer std.Io.Dir.cwd().deleteTree(io, layout_root) catch {};
    const root_layout = try std.fmt.allocPrint(allocator, "{s}/root-layout", .{layout_root});
    defer allocator.free(root_layout);
    try std.Io.Dir.cwd().createDirPath(io, root_layout);
    const root_zig_path = try std.fmt.allocPrint(allocator, "{s}/zig", .{root_layout});
    defer allocator.free(root_zig_path);
    try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = root_zig_path, .data = "" });
    const root_bin = try resolveBinDir(io, allocator, root_layout);
    defer allocator.free(root_bin);
    try expectSelfTestCheck(io, std.mem.eql(u8, root_bin, root_layout));
    case_count += 1;

    const bin_layout = try std.fmt.allocPrint(allocator, "{s}/bin-layout", .{layout_root});
    defer allocator.free(bin_layout);
    const bin_layout_bin = try std.fmt.allocPrint(allocator, "{s}/bin", .{bin_layout});
    defer allocator.free(bin_layout_bin);
    try std.Io.Dir.cwd().createDirPath(io, bin_layout_bin);
    const bin_zig_path = try std.fmt.allocPrint(allocator, "{s}/bin/zig", .{bin_layout});
    defer allocator.free(bin_zig_path);
    try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = bin_zig_path, .data = "" });
    const nested_bin = try resolveBinDir(io, allocator, bin_layout);
    defer allocator.free(nested_bin);
    try expectSelfTestCheck(io, std.mem.eql(u8, nested_bin, bin_layout_bin));
    case_count += 1;
    const missing_layout = try std.fmt.allocPrint(allocator, "{s}/missing-layout", .{layout_root});
    defer allocator.free(missing_layout);
    try expectSelfTestError(io, error.MissingZigBinary, resolveBinDir(io, allocator, missing_layout));
    case_count += 1;

    const stage_root = try std.fmt.allocPrint(allocator, ".zig-cache/tmp/zigux_install_zig_archive_stage_{d}", .{installTmpId(io)});
    defer allocator.free(stage_root);
    std.Io.Dir.cwd().deleteTree(io, stage_root) catch {};
    try std.Io.Dir.cwd().createDirPath(io, stage_root);
    defer std.Io.Dir.cwd().deleteTree(io, stage_root) catch {};
    const local_archive_path = try std.fmt.allocPrint(allocator, "{s}/local.tar.xz", .{stage_root});
    defer allocator.free(local_archive_path);
    try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = local_archive_path, .data = "local-zig-archive" });
    const staged_archive_path = try std.fmt.allocPrint(allocator, "{s}/staged.tar.xz", .{stage_root});
    defer allocator.free(staged_archive_path);
    const staged_source = try stageArchive(io, local_archive_path, "https://example.invalid/archive.tar.xz", staged_archive_path, allocator);
    try expectSelfTestCheck(io, staged_source == .local_archive);
    const staged_bytes = try std.Io.Dir.cwd().readFileAlloc(io, staged_archive_path, allocator, .unlimited);
    defer allocator.free(staged_bytes);
    try expectSelfTestCheck(io, std.mem.eql(u8, staged_bytes, "local-zig-archive"));
    case_count += 1;
    const missing_archive_path = try std.fmt.allocPrint(allocator, "{s}/missing.tar.xz", .{stage_root});
    defer allocator.free(missing_archive_path);
    try expectSelfTestError(io, error.LocalArchiveNotFound, stageArchive(io, missing_archive_path, "https://example.invalid/archive.tar.xz", staged_archive_path, allocator));
    case_count += 1;

    resetSelfTestState(allocator);
    test_hooks.curl_available_fn = curlUnavailableHook;
    test_hooks.open_url_fn = downloadOpenHook;
    const download_stage_root = try std.fmt.allocPrint(allocator, ".zig-cache/tmp/zigux_install_zig_download_stage_{d}", .{installTmpId(io)});
    defer allocator.free(download_stage_root);
    std.Io.Dir.cwd().deleteTree(io, download_stage_root) catch {};
    try std.Io.Dir.cwd().createDirPath(io, download_stage_root);
    defer std.Io.Dir.cwd().deleteTree(io, download_stage_root) catch {};
    const downloaded_archive_path = try std.fmt.allocPrint(allocator, "{s}/downloaded.tar.xz", .{download_stage_root});
    defer allocator.free(downloaded_archive_path);
    const download_source = try stageArchive(io, null, "https://example.invalid/archive.tar.xz", downloaded_archive_path, allocator);
    try expectSelfTestCheck(io, download_source == .download);
    try expectSelfTestCheck(io, self_test_state.download_calls == 1);
    const downloaded_bytes = try std.Io.Dir.cwd().readFileAlloc(io, downloaded_archive_path, allocator, .unlimited);
    defer allocator.free(downloaded_bytes);
    try expectSelfTestCheck(io, std.mem.eql(u8, downloaded_bytes, "downloaded"));
    case_count += 1;
    test_hooks.open_url_fn = null;
    test_hooks.curl_available_fn = null;

    try expectSelfTestError(io, error.UnsupportedOs, normalizeOs("plan9"));
    case_count += 1;
    try expectSelfTestError(io, error.UnsupportedArch, normalizeArch("sparc"));
    case_count += 1;
    try expectSelfTestError(io, error.UnknownChannel, resolveTarget(allocator, sample_index, "stable", "x86_64", "linux", release_repo, release_tag));
    case_count += 1;
    try expectSelfTestError(io, error.UnknownTarget, resolveTarget(allocator, sample_index, "master", "loongarch64", "linux", release_repo, release_tag));
    case_count += 1;

    try printLine(io, "ZIG_INSTALL_SELF_TEST=pass", .{});
    try printLine(io, "ZIG_INSTALL_SELF_TEST_CASE_COUNT=46", .{});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const environ_map = init.environ_map.*;
    const args = try init.minimal.args.toSlice(allocator);

    var channel: ?[]const u8 = null;
    var dest: []const u8 = ".zig-toolchain";
    var system_override: ?[]const u8 = null;
    var arch_override: ?[]const u8 = null;
    var local_archive: ?[]const u8 = null;
    var archive_target: ?[]const u8 = null;
    var resolve_only = false;
    var self_test = false;

    var index: usize = if (args.len > 0 and std.mem.startsWith(u8, args[0], "-")) 0 else 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--resolve-only")) {
            resolve_only = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--channel")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            channel = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--dest")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            dest = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--system")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            system_override = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--arch")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            arch_override = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--archive")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            local_archive = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--archive-target")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            archive_target = args[index];
            continue;
        }
    }

    if (self_test) {
        std.process.exit(@intCast(try runSelfTest(io, allocator, environ_map)));
    }

    const repo_root = try defaultRepoRoot(allocator);
    defer allocator.free(repo_root);
    const policy_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ repo_root, default_toolchain_policy_rel });
    defer allocator.free(policy_path);

    const policy_channel = try loadPolicyChannel(io, allocator, policy_path, fallback_channel);
    defer allocator.free(policy_channel);

    const selected_channel = channel orelse policy_channel;
    const system_key = if (system_override) |value| normalizeOs(value) catch |err| switch (err) {
        error.UnsupportedOs => exitWithMessage(io, "unsupported OS for Zig installer"),
        else => return err,
    } else try detectSystemKey();
    const arch_key = if (arch_override) |value| normalizeArch(value) catch |err| switch (err) {
        error.UnsupportedArch => exitWithMessage(io, "unsupported architecture for Zig installer"),
        else => return err,
    } else try detectArchKey();

    const release_repo = try canonicalReleaseRepo(allocator, environ_map);
    defer allocator.free(release_repo);
    const release_tag = try canonicalReleaseTag(allocator, environ_map);
    defer allocator.free(release_tag);

    var index_map = try loadIndex(allocator, io, selected_channel);
    defer index_map.deinit(allocator);

    var resolved = try resolveTarget(allocator, index_map, selected_channel, arch_key, system_key, release_repo, release_tag);
    defer freeResolveTarget(allocator, &resolved);

    var expected_archive_sha256: ?[]const u8 = null;
    defer if (expected_archive_sha256) |digest| allocator.free(digest);

    if (std.mem.eql(u8, selected_channel, policy_channel)) {
        expected_archive_sha256 = try loadPolicyArchiveSha256(io, allocator, policy_path, resolved.target_key);
    }

    const archive_target_key = archive_target orelse resolved.target_key;
    if (local_archive != null and std.mem.eql(u8, selected_channel, policy_channel) and !std.mem.eql(u8, archive_target_key, resolved.target_key)) {
        expected_archive_sha256 = try loadPolicyArchiveSha256(io, allocator, policy_path, archive_target_key);
    }
    if (local_archive != null and std.mem.eql(u8, selected_channel, policy_channel) and expected_archive_sha256 == null) {
        const message = try std.fmt.allocPrint(allocator, "no pinned archive sha256 for target {s} in {s}", .{ archive_target_key, policy_path });
        defer allocator.free(message);
        printErr(io, message);
        std.process.exit(1);
    }

    try printLine(io, "ZIG_INSTALL_CHANNEL={s}", .{selected_channel});
    try printLine(io, "ZIG_INSTALL_VERSION={s}", .{resolved.version});
    try printLine(io, "ZIG_INSTALL_TARGET={s}", .{resolved.target_key});
    if (archive_target != null) try printLine(io, "ZIG_INSTALL_ARCHIVE_TARGET={s}", .{archive_target_key});
    try printLine(io, "ZIG_INSTALL_URL={s}", .{resolved.tarball_url});
    if (expected_archive_sha256) |digest| try printLine(io, "ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={s}", .{digest});
    if (resolve_only) {
        try printLine(io, "ZIG_INSTALL_STATUS=resolved", .{});
        std.process.exit(0);
    }

    try std.Io.Dir.cwd().createDirPath(io, dest);

    const expanded_archive = if (local_archive) |value| try expandUserPath(allocator, environ_map, value) else null;
    defer if (expanded_archive) |value| allocator.free(value);

    const tmp_root = try std.fmt.allocPrint(allocator, ".zig-cache/tmp/zigux_install_zig_{d}", .{installTmpId(io)});
    defer allocator.free(tmp_root);
    std.Io.Dir.cwd().deleteTree(io, tmp_root) catch {};
    try std.Io.Dir.cwd().createDirPath(io, tmp_root);
    defer std.Io.Dir.cwd().deleteTree(io, tmp_root) catch {};

    const archive_name = if (expanded_archive) |value| std.fs.path.basename(value) else blk: {
        const slash = std.mem.lastIndexOf(u8, resolved.tarball_url, "/") orelse resolved.tarball_url.len;
        break :blk resolved.tarball_url[slash + 1 ..];
    };
    const staged_archive_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ tmp_root, archive_name });
    defer allocator.free(staged_archive_path);

    const archive_source = try stageArchive(io, expanded_archive, resolved.tarball_url, staged_archive_path, allocator);
    if (expected_archive_sha256) |digest| {
        const actual = try verifyArchiveSha256(io, allocator, staged_archive_path, digest);
        defer allocator.free(actual);
        try printLine(io, "ZIG_INSTALL_ARCHIVE_SHA256={s}", .{actual});
        try printLine(io, "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified", .{});
    } else {
        try printLine(io, "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified", .{});
    }
    try printLine(io, "ZIG_INSTALL_SOURCE={s}", .{archive_source.name()});

    const extract_root = try std.fmt.allocPrint(allocator, "{s}/extract", .{tmp_root});
    defer allocator.free(extract_root);
    const extracted_name = try extractArchive(io, allocator, staged_archive_path, extract_root);
    defer allocator.free(extracted_name);

    const extracted_root = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ extract_root, extracted_name });
    defer allocator.free(extracted_root);
    const final_root = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ dest, extracted_name });
    defer allocator.free(final_root);

    std.Io.Dir.cwd().deleteTree(io, final_root) catch {};
    try copyDirRecursive(io, extracted_root, final_root);

    const bin_dir = try resolveBinDir(io, allocator, final_root);
    defer allocator.free(bin_dir);
    try appendGithubPath(io, environ_map, bin_dir);
    const resolved_bin = std.Io.Dir.cwd().realPathFileAlloc(io, bin_dir, allocator) catch bin_dir;
    defer if (!std.mem.eql(u8, resolved_bin, bin_dir)) allocator.free(resolved_bin);
    try printLine(io, "ZIG_INSTALL_PATH={s}", .{resolved_bin});
    try printLine(io, "ZIG_INSTALL_STATUS=pass", .{});
    std.process.exit(0);
}

test "installer self-test completes" {
    var environ = std.process.Environ.Map.init(std.testing.allocator);
    defer environ.deinit();
    try std.testing.expectEqual(@as(u32, 0), try runSelfTest(std.testing.io, std.testing.allocator, environ));
}
