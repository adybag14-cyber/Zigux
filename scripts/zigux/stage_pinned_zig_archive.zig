const std = @import("std");
const Io = std.Io;
const policy = @import("toolchain_policy.zig");
const resolver = @import("toolchain_resolver.zig");

pub const toolchain_policy_rel = "scripts/zigux/zig-toolchain-policy.json";
pub const third_party_rel = "third_party";
pub const self_test_pass_marker = "STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass";
pub const self_test_case_count_prefix = "STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT=";

pub const expected_archive_sizes = std.StaticStringMap(u64).initComptime(.{
    .{ "x86_64-linux", 59_093_540 },
    .{ "x86_64-windows", 103_440_485 },
});

pub const InputMode = enum {
    source,
    parts_dir,

    pub fn name(self: InputMode) []const u8 {
        return switch (self) {
            .source => "source",
            .parts_dir => "parts_dir",
        };
    }
};

pub const StageStatus = enum {
    staged,
    already_present,
    checked,

    pub fn name(self: StageStatus) []const u8 {
        return switch (self) {
            .staged => "staged",
            .already_present => "already_present",
            .checked => "checked",
        };
    }
};

pub const StageMetadata = struct {
    channel: []const u8,
    target: []const u8,
    sha256: []const u8,
    size: u64,
    filename: []const u8,
};

pub const StageArchiveResult = struct {
    metadata: StageMetadata,
    status: StageStatus,
    actual_sha256: []const u8,
    destination: []const u8,
    input_mode: InputMode,
};

pub const ExistingDestination = struct {
    status: StageStatus,
    sha256: []const u8,
};

pub const ValidationFailed = error{
    Invalid,
    OutOfMemory,
};

fn dupePath(allocator: std.mem.Allocator, path: []const u8) ![]const u8 {
    return allocator.dupe(u8, path);
}

fn joinPath(allocator: std.mem.Allocator, root: []const u8, suffix: []const u8) ![]const u8 {
    return std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, suffix });
}

fn failMessage(
    comptime ReturnType: type,
    allocator: std.mem.Allocator,
    err_msg: *?[]const u8,
    comptime fmt: []const u8,
    args: anytype,
) ValidationFailed!ReturnType {
    err_msg.* = try std.fmt.allocPrint(allocator, fmt, args);
    return ValidationFailed.Invalid;
}

pub fn defaultRepoRoot(allocator: std.mem.Allocator) ![]const u8 {
    const script_path = @src().file;
    if (std.fs.path.dirname(script_path)) |script_dir| {
        if (std.fs.path.dirname(script_dir)) |scripts_dir| {
            if (std.fs.path.dirname(scripts_dir)) |root| {
                return try dupePath(allocator, root);
            }
        }
    }
    return try dupePath(allocator, ".");
}

var tmp_counter: std.atomic.Value(u64) = .init(0);

fn tmpSuffix(io: Io) u64 {
    var random_bytes: [8]u8 = undefined;
    io.random(&random_bytes);
    return std.mem.readInt(u64, &random_bytes, .little) ^ tmp_counter.fetchAdd(1, .monotonic);
}

pub fn duplicateArchiveName(
    allocator: std.mem.Allocator,
    expected_filename: []const u8,
) ![]const u8 {
    if (!std.mem.endsWith(u8, expected_filename, ".tar.xz")) return error.InvalidPath;
    const stem = expected_filename[0 .. expected_filename.len - ".tar.xz".len];
    return std.fmt.allocPrint(allocator, "{s} (1).tar.xz", .{stem});
}

fn skipJsonWhitespace(source: []const u8, index: *usize) void {
    while (index.* < source.len and std.ascii.isWhitespace(source[index.*])) : (index.* += 1) {}
}

fn parseJsonString(allocator: std.mem.Allocator, source: []const u8, index: *usize) ![]const u8 {
    if (index.* >= source.len or source[index.*] != '"') return error.InvalidJson;
    index.* += 1;
    const start = index.*;
    while (index.* < source.len) : (index.* += 1) {
        switch (source[index.*]) {
            '\\' => {
                index.* += 1;
                if (index.* >= source.len) return error.InvalidJson;
            },
            '"' => {
                const raw = source[start..index.*];
                index.* += 1;
                return try allocator.dupe(u8, raw);
            },
            else => {},
        }
    }
    return error.InvalidJson;
}

fn skipJsonStringValue(source: []const u8, index: *usize) !void {
    if (index.* >= source.len or source[index.*] != '"') return error.InvalidJson;
    index.* += 1;
    while (index.* < source.len) : (index.* += 1) {
        switch (source[index.*]) {
            '\\' => {
                index.* += 1;
                if (index.* >= source.len) return error.InvalidJson;
            },
            '"' => {
                index.* += 1;
                return;
            },
            else => {},
        }
    }
    return error.InvalidJson;
}

fn skipJsonValue(source: []const u8, index: *usize) !void {
    skipJsonWhitespace(source, index);
    if (index.* >= source.len) return error.InvalidJson;
    switch (source[index.*]) {
        '"' => try skipJsonStringValue(source, index),
        '{', '[' => {
            const open = source[index.*];
            const close: u8 = if (open == '{') '}' else ']';
            index.* += 1;
            while (true) {
                skipJsonWhitespace(source, index);
                if (index.* >= source.len) return error.InvalidJson;
                if (source[index.*] == close) {
                    index.* += 1;
                    return;
                }
                if (open == '{') {
                    try skipJsonStringValue(source, index);
                    skipJsonWhitespace(source, index);
                    if (index.* >= source.len or source[index.*] != ':') return error.InvalidJson;
                    index.* += 1;
                }
                try skipJsonValue(source, index);
                skipJsonWhitespace(source, index);
                if (index.* < source.len and source[index.*] == ',') {
                    index.* += 1;
                    continue;
                }
            }
        },
        else => {
            while (index.* < source.len and !std.ascii.isWhitespace(source[index.*])) {
                if (source[index.*] == ',' or source[index.*] == '}' or source[index.*] == ']') break;
                index.* += 1;
            }
        },
    }
}

fn findDuplicateKeysInObject(
    allocator: std.mem.Allocator,
    source: []const u8,
    object_start: usize,
) !?[]const u8 {
    var index = object_start;
    if (index >= source.len or source[index] != '{') return null;
    index += 1;

    var seen = std.StringArrayHashMapUnmanaged(void){};
    defer {
        var it = seen.iterator();
        while (it.next()) |entry| allocator.free(entry.key_ptr.*);
        seen.deinit(allocator);
    }

    var duplicates: std.ArrayList([]const u8) = .empty;
    defer {
        for (duplicates.items) |item| allocator.free(item);
        duplicates.deinit(allocator);
    }

    while (true) {
        skipJsonWhitespace(source, &index);
        if (index >= source.len) return error.InvalidJson;
        if (source[index] == '}') break;

        const key = try parseJsonString(allocator, source, &index);
        defer allocator.free(key);

        const gop = try seen.getOrPut(allocator, try allocator.dupe(u8, key));
        if (gop.found_existing) {
            var already_listed = false;
            for (duplicates.items) |item| {
                if (std.mem.eql(u8, item, key)) {
                    already_listed = true;
                    break;
                }
            }
            if (!already_listed) try duplicates.append(allocator, try allocator.dupe(u8, key));
        }

        skipJsonWhitespace(source, &index);
        if (index >= source.len or source[index] != ':') return error.InvalidJson;
        index += 1;
        try skipJsonValue(source, &index);
        skipJsonWhitespace(source, &index);
        if (index < source.len and source[index] == ',') {
            index += 1;
            continue;
        }
        if (index < source.len and source[index] == '}') break;
    }

    if (duplicates.items.len == 0) return null;

    var joined: std.ArrayList(u8) = .empty;
    defer joined.deinit(allocator);
    for (duplicates.items, 0..) |item, item_index| {
        if (item_index != 0) try joined.append(allocator, ',');
        try joined.append(allocator, ' ');
        try joined.appendSlice(allocator, item);
    }
    return try joined.toOwnedSlice(allocator);
}

fn findDuplicateRootKeys(allocator: std.mem.Allocator, json_bytes: []const u8) !?[]const u8 {
    const trimmed = std.mem.trim(u8, json_bytes, " \t\r\n");
    if (trimmed.len == 0 or trimmed[0] != '{') return null;
    return findDuplicateKeysInObject(allocator, trimmed, 0);
}

fn findNestedObject(allocator: std.mem.Allocator, json_bytes: []const u8, field_name: []const u8) !?usize {
    const needle = try std.fmt.allocPrint(allocator, "\"{s}\":", .{field_name});
    defer allocator.free(needle);
    const found = std.mem.indexOf(u8, json_bytes, needle) orelse return null;
    var index = found + needle.len;
    skipJsonWhitespace(json_bytes, &index);
    if (index >= json_bytes.len or json_bytes[index] != '{') return null;
    return index;
}

pub fn loadStagePolicy(
    allocator: std.mem.Allocator,
    io: Io,
    root: []const u8,
    err_msg: *?[]const u8,
) anyerror!StageMetadata {
    const policy_path = try joinPath(allocator, root, toolchain_policy_rel);
    defer allocator.free(policy_path);

    const json_bytes = std.Io.Dir.cwd().readFileAlloc(io, policy_path, allocator, .unlimited) catch |read_err| switch (read_err) {
        error.FileNotFound => return failMessage(StageMetadata, allocator, err_msg, "missing toolchain policy: {s}", .{policy_path}),
        else => |err| return err,
    };
    defer allocator.free(json_bytes);

    if (try findDuplicateRootKeys(allocator, json_bytes)) |duplicate_keys| {
        defer allocator.free(duplicate_keys);
        return failMessage(StageMetadata, allocator, err_msg, "duplicate toolchain policy keys in {s}: {s}", .{ policy_path, duplicate_keys });
    }

    if (try findNestedObject(allocator, json_bytes, "archive_sha256")) |archive_start| {
        if (try findDuplicateKeysInObject(allocator, json_bytes, archive_start)) |duplicate_keys| {
            defer allocator.free(duplicate_keys);
            return failMessage(StageMetadata, allocator, err_msg, "duplicate archive_sha256 targets in {s}: {s}", .{ policy_path, duplicate_keys });
        }
    }

    if (try findNestedObject(allocator, json_bytes, "upgrade_policy")) |upgrade_start| {
        if (try findDuplicateKeysInObject(allocator, json_bytes, upgrade_start)) |duplicate_keys| {
            defer allocator.free(duplicate_keys);
            return failMessage(StageMetadata, allocator, err_msg, "duplicate upgrade_policy keys in {s}: {s}", .{ policy_path, duplicate_keys });
        }
    }

    var loaded = policy.loadPolicyFromJson(allocator, json_bytes) catch |err| switch (err) {
        policy.ToolchainPolicyError.InvalidPolicyField => return failMessage(StageMetadata, allocator, err_msg, "invalid toolchain policy payload in {s}: expected object", .{policy_path}),
        policy.ToolchainPolicyError.DuplicatePolicyKey => return failMessage(StageMetadata, allocator, err_msg, "duplicate archive_sha256 targets in {s}", .{policy_path}),
        policy.ToolchainPolicyError.ArchiveTargetMismatch => return failMessage(StageMetadata, allocator, err_msg, "archive_target_scope references missing archive_sha256 entry in {s}", .{policy_path}),
        policy.ToolchainPolicyError.ChannelLockstepMismatch => return failMessage(StageMetadata, allocator, err_msg, "minimum_version must match channel when channel_minimum_lockstep is true in {s}", .{policy_path}),
        else => return err,
    };
    defer policy.freePolicy(allocator, &loaded);

    const scope = loaded.upgrade_policy.archive_target_scope;
    const target = blk: {
        for (scope) |candidate| {
            if (std.mem.eql(u8, candidate, "x86_64-linux")) break :blk candidate;
        }
        return failMessage(StageMetadata, allocator, err_msg, "missing x86_64-linux archive target in {s}", .{policy_path});
    };
    const digest = loaded.archive_sha256.get(target) orelse {
        return failMessage(StageMetadata, allocator, err_msg, "archive_target_scope references missing archive_sha256 entry in {s}: {s}", .{ policy_path, target });
    };

    const size = expected_archive_sizes.get(target) orelse {
        return failMessage(StageMetadata, allocator, err_msg, "missing expected archive size for {s}", .{target});
    };

    var filename_buffer: [160]u8 = undefined;
    const filename = try policy.policyArchiveFilename(target, loaded.channel, &filename_buffer);

    return .{
        .channel = try dupePath(allocator, loaded.channel),
        .target = try dupePath(allocator, target),
        .sha256 = try dupePath(allocator, digest),
        .size = size,
        .filename = try dupePath(allocator, filename),
    };
}

pub fn freeStageMetadata(allocator: std.mem.Allocator, metadata: *StageMetadata) void {
    allocator.free(metadata.channel);
    allocator.free(metadata.target);
    allocator.free(metadata.sha256);
    allocator.free(metadata.filename);
}

fn pathIsFile(io: Io, path: []const u8) bool {
    var file = std.Io.Dir.cwd().openFile(io, path, .{}) catch return false;
    defer file.close(io);
    const stat = file.stat(io) catch return false;
    return stat.kind == .file;
}

fn pathIsDir(io: Io, path: []const u8) bool {
    var dir = std.Io.Dir.cwd().openDir(io, path, .{}) catch return false;
    dir.close(io);
    return true;
}

pub fn validateSourceArchive(
    allocator: std.mem.Allocator,
    io: Io,
    source: []const u8,
    expected_size: u64,
    expected_sha: []const u8,
    err_msg: *?[]const u8,
) anyerror![]const u8 {
    std.Io.Dir.cwd().access(io, source, .{}) catch {
        return failMessage([]const u8, allocator, err_msg, "missing source archive: {s}", .{source});
    };

    if (!pathIsFile(io, source)) {
        return failMessage([]const u8, allocator, err_msg, "source archive is not a regular file: {s}", .{source});
    }

    var file = std.Io.Dir.cwd().openFile(io, source, .{}) catch {
        return failMessage([]const u8, allocator, err_msg, "source archive is not a regular file: {s}", .{source});
    };
    defer file.close(io);

    const stat = try file.stat(io);
    if (stat.size != expected_size) {
        return failMessage([]const u8, allocator, err_msg, "expected {s} to be {d} bytes, got {d}", .{ source, expected_size, stat.size });
    }

    const actual_sha = try resolver.computeSha256Hex(io, allocator, source);
    errdefer allocator.free(actual_sha);
    if (!std.mem.eql(u8, actual_sha, expected_sha)) {
        return failMessage([]const u8, allocator, err_msg, "expected {s} to have sha256 {s}, got {s}", .{ source, expected_sha, actual_sha });
    }

    return actual_sha;
}

pub fn requireCleanThirdParty(
    allocator: std.mem.Allocator,
    io: Io,
    root: []const u8,
    expected_filename: []const u8,
    err_msg: *?[]const u8,
) anyerror!void {
    const third_party_path = try joinPath(allocator, root, third_party_rel);
    defer allocator.free(third_party_path);

    if (!pathIsDir(io, third_party_path)) return;

    var third_party = std.Io.Dir.cwd().openDir(io, third_party_path, .{ .iterate = true }) catch return;
    defer third_party.close(io);

    var duplicate_names: std.ArrayList([]const u8) = .empty;
    defer {
        for (duplicate_names.items) |name| allocator.free(name);
        duplicate_names.deinit(allocator);
    }

    var iter = third_party.iterate();
    while (try iter.next(io)) |entry| {
        if (!std.mem.endsWith(u8, entry.name, ".tar.xz")) continue;
        if (!policy.archiveNameHasDuplicateSuffix(entry.name, expected_filename)) continue;
        try duplicate_names.append(allocator, try dupePath(allocator, entry.name));
    }

    if (duplicate_names.items.len == 0) return;

    std.sort.pdq([]const u8, duplicate_names.items, {}, struct {
        fn lessThan(_: void, left: []const u8, right: []const u8) bool {
            return std.mem.order(u8, left, right) == .lt;
        }
    }.lessThan);

    var joined: std.ArrayList(u8) = .empty;
    defer joined.deinit(allocator);
    for (duplicate_names.items, 0..) |name, index| {
        if (index != 0) try joined.appendSlice(allocator, ", ");
        try joined.appendSlice(allocator, name);
    }
    const rendered = try joined.toOwnedSlice(allocator);
    defer allocator.free(rendered);
    return failMessage(void, allocator, err_msg, "third_party contains duplicate-suffix archive copies: {s}", .{rendered});
}

pub fn inspectDestination(
    allocator: std.mem.Allocator,
    io: Io,
    source: []const u8,
    destination: []const u8,
    expected_size: u64,
    expected_sha: []const u8,
    actual_sha: []const u8,
    err_msg: *?[]const u8,
) anyerror!?ExistingDestination {
    std.Io.Dir.cwd().access(io, destination, .{}) catch return null;

    if (!pathIsFile(io, destination)) {
        return failMessage(?ExistingDestination, allocator, err_msg, "destination archive is not a regular file: {s}", .{destination});
    }

    const destination_sha = try validateSourceArchive(allocator, io, destination, expected_size, expected_sha, err_msg);
    errdefer allocator.free(destination_sha);

    const source_real = std.Io.Dir.cwd().realPathFileAlloc(io, source, allocator) catch return error.OutOfMemory;
    defer allocator.free(source_real);
    const destination_real = std.Io.Dir.cwd().realPathFileAlloc(io, destination, allocator) catch return error.OutOfMemory;
    defer allocator.free(destination_real);

    if (std.mem.eql(u8, source_real, destination_real)) {
        return .{ .status = .already_present, .sha256 = destination_sha };
    }

    if (!std.mem.eql(u8, destination_sha, actual_sha)) {
        return failMessage(?ExistingDestination, allocator, err_msg, "destination archive {s} already exists with different bytes than {s}", .{ destination, source });
    }

    return .{ .status = .already_present, .sha256 = destination_sha };
}

fn copyFile(io: Io, source: []const u8, destination: []const u8) !void {
    const parent = std.fs.path.dirname(destination) orelse return error.InvalidPath;
    try std.Io.Dir.cwd().createDirPath(io, parent);

    var src = try std.Io.Dir.cwd().openFile(io, source, .{});
    defer src.close(io);

    var dst = try std.Io.Dir.cwd().createFile(io, destination, .{ .truncate = true });
    defer dst.close(io);

    var buffer: [1024 * 1024]u8 = undefined;
    while (true) {
        const read = std.Io.File.readStreaming(src, io, &.{&buffer}) catch |err| switch (err) {
            error.EndOfStream => break,
            else => return err,
        };
        if (read == 0) break;
        try std.Io.File.writeStreamingAll(dst, io, buffer[0..read]);
    }
}

fn writeConstantByteFile(io: Io, destination: []const u8, byte: u8, size: u64) !void {
    const parent = std.fs.path.dirname(destination) orelse return error.InvalidPath;
    try std.Io.Dir.cwd().createDirPath(io, parent);

    var dst = try std.Io.Dir.cwd().createFile(io, destination, .{ .truncate = true });
    defer dst.close(io);

    var buffer: [1024 * 1024]u8 = undefined;
    @memset(&buffer, byte);

    var remaining = size;
    while (remaining > 0) {
        const chunk = @min(remaining, buffer.len);
        try std.Io.File.writeStreamingAll(dst, io, buffer[0..chunk]);
        remaining -= chunk;
    }
}

fn requireManifestString(
    allocator: std.mem.Allocator,
    manifest: std.json.ObjectMap,
    key: []const u8,
    manifest_path: []const u8,
    err_msg: *?[]const u8,
) anyerror![]const u8 {
    const value = manifest.get(key) orelse {
        return failMessage([]const u8, allocator, err_msg, "invalid shard manifest {s} in {s}", .{ key, manifest_path });
    };
    const text = switch (value) {
        .string => |raw| raw,
        else => return failMessage([]const u8, allocator, err_msg, "invalid shard manifest {s} in {s}", .{ key, manifest_path }),
    };
    const trimmed = std.mem.trim(u8, text, " \t\r\n");
    if (trimmed.len == 0) {
        return failMessage([]const u8, allocator, err_msg, "invalid shard manifest {s} in {s}", .{ key, manifest_path });
    }
    return try dupePath(allocator, trimmed);
}

fn requireManifestInt(
    allocator: std.mem.Allocator,
    manifest: std.json.ObjectMap,
    key: []const u8,
    manifest_path: []const u8,
    err_msg: *?[]const u8,
) anyerror!i64 {
    const value = manifest.get(key) orelse {
        return failMessage(i64, allocator, err_msg, "invalid shard manifest {s} in {s}", .{ key, manifest_path });
    };
    return switch (value) {
        .integer => |raw| {
            if (raw <= 0) return failMessage(i64, allocator, err_msg, "invalid shard manifest {s} in {s}", .{ key, manifest_path });
            return raw;
        },
        else => failMessage(i64, allocator, err_msg, "invalid shard manifest {s} in {s}", .{ key, manifest_path }),
    };
}

pub fn loadShardManifest(
    allocator: std.mem.Allocator,
    io: Io,
    parts_dir: []const u8,
    err_msg: *?[]const u8,
) anyerror!std.json.ObjectMap {
    const manifest_path = try std.fmt.allocPrint(allocator, "{s}/manifest.json", .{parts_dir});
    defer allocator.free(manifest_path);

    const manifest_bytes = std.Io.Dir.cwd().readFileAlloc(io, manifest_path, allocator, .unlimited) catch |read_err| switch (read_err) {
        error.FileNotFound => return failMessage(std.json.ObjectMap, allocator, err_msg, "missing shard manifest: {s}", .{manifest_path}),
        else => |err| return err,
    };
    defer allocator.free(manifest_bytes);

    const parsed = std.json.parseFromSlice(std.json.Value, allocator, manifest_bytes, .{}) catch {
        return failMessage(std.json.ObjectMap, allocator, err_msg, "invalid shard manifest JSON in {s}", .{manifest_path});
    };

    defer parsed.deinit();

    return switch (parsed.value) {
        .object => |object| object,
        else => failMessage(std.json.ObjectMap, allocator, err_msg, "invalid shard manifest payload in {s}: expected object", .{manifest_path}),
    };
}

fn decodeBase64Shard(allocator: std.mem.Allocator, encoded: []const u8) ![]u8 {
    const trimmed = std.mem.trim(u8, encoded, " \t\r\n");
    const decoder = std.base64.standard.Decoder;
    const max_len = decoder.calcSizeForSlice(trimmed) catch return error.InvalidBase64;
    const buffer = try allocator.alloc(u8, max_len);
    errdefer allocator.free(buffer);
    decoder.decode(buffer, trimmed) catch {
        allocator.free(buffer);
        return error.InvalidBase64;
    };
    return buffer[0..max_len];
}

pub fn reconstructArchiveFromParts(
    allocator: std.mem.Allocator,
    io: Io,
    parts_dir: []const u8,
    destination: []const u8,
    expected_filename: []const u8,
    expected_sha: []const u8,
    expected_size: u64,
    err_msg: *?[]const u8,
) anyerror![]const u8 {
    const manifest_path = try std.fmt.allocPrint(allocator, "{s}/manifest.json", .{parts_dir});
    defer allocator.free(manifest_path);

    const manifest_bytes = std.Io.Dir.cwd().readFileAlloc(io, manifest_path, allocator, .unlimited) catch |read_err| switch (read_err) {
        error.FileNotFound => return failMessage([]const u8, allocator, err_msg, "missing shard manifest: {s}", .{manifest_path}),
        else => |err| return err,
    };
    defer allocator.free(manifest_bytes);

    const parsed = std.json.parseFromSlice(std.json.Value, allocator, manifest_bytes, .{}) catch {
        return failMessage([]const u8, allocator, err_msg, "invalid shard manifest JSON in {s}", .{manifest_path});
    };
    defer parsed.deinit();

    const manifest = switch (parsed.value) {
        .object => |object| object,
        else => return failMessage([]const u8, allocator, err_msg, "invalid shard manifest payload in {s}: expected object", .{manifest_path}),
    };

    const filename = try requireManifestString(allocator, manifest, "filename", manifest_path, err_msg);
    defer allocator.free(filename);
    const encoding = try requireManifestString(allocator, manifest, "encoding", manifest_path, err_msg);
    defer allocator.free(encoding);
    const sha256_value = try requireManifestString(allocator, manifest, "sha256", manifest_path, err_msg);
    defer allocator.free(sha256_value);
    const size = try requireManifestInt(allocator, manifest, "size", manifest_path, err_msg);
    const part_count = @as(usize, @intCast(try requireManifestInt(allocator, manifest, "part_count", manifest_path, err_msg)));
    _ = try requireManifestInt(allocator, manifest, "chunk_bytes", manifest_path, err_msg);
    const parts_glob = try requireManifestString(allocator, manifest, "parts_glob", manifest_path, err_msg);
    defer allocator.free(parts_glob);

    if (!std.mem.eql(u8, filename, expected_filename)) {
        return failMessage([]const u8, allocator, err_msg, "expected shard manifest filename {s}, got {s}", .{ expected_filename, filename });
    }
    if (!std.mem.eql(u8, encoding, "base64")) {
        return failMessage([]const u8, allocator, err_msg, "expected shard manifest encoding base64, got {s}", .{encoding});
    }
    if (!std.mem.eql(u8, sha256_value, expected_sha)) {
        return failMessage([]const u8, allocator, err_msg, "expected shard manifest sha256 {s}, got {s}", .{ expected_sha, sha256_value });
    }
    if (@as(u64, @intCast(size)) != expected_size) {
        return failMessage([]const u8, allocator, err_msg, "expected shard manifest size {d}, got {d}", .{ expected_size, size });
    }
    if (!std.mem.eql(u8, parts_glob, "part-*.b64")) {
        return failMessage([]const u8, allocator, err_msg, "expected shard manifest parts_glob part-*.b64, got {s}", .{parts_glob});
    }

    const parent = std.fs.path.dirname(destination) orelse return error.InvalidPath;
    try std.Io.Dir.cwd().createDirPath(io, parent);

    var dst = try std.Io.Dir.cwd().createFile(io, destination, .{ .truncate = true });

    var index: usize = 0;
    while (index < part_count) : (index += 1) {
        const shard_name = try std.fmt.allocPrint(allocator, "part-{d:0>3}.b64", .{index});
        defer allocator.free(shard_name);
        const shard_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ parts_dir, shard_name });
        defer allocator.free(shard_path);

        const encoded = std.Io.Dir.cwd().readFileAlloc(io, shard_path, allocator, .unlimited) catch {
            return failMessage([]const u8, allocator, err_msg, "missing expected shard: {s}", .{shard_name});
        };
        defer allocator.free(encoded);

        const chunk = decodeBase64Shard(allocator, encoded) catch {
            return failMessage([]const u8, allocator, err_msg, "invalid base64 shard: {s}", .{shard_name});
        };
        defer allocator.free(chunk);
        try std.Io.File.writeStreamingAll(dst, io, chunk);
    }

    dst.close(io);
    return validateSourceArchive(allocator, io, destination, expected_size, expected_sha, err_msg);
}

pub const ResolvedSource = struct {
    path: []const u8,
    input_mode: InputMode,
    temp_root: ?[]const u8,
};

pub fn freeResolvedSource(allocator: std.mem.Allocator, resolved: *ResolvedSource) void {
    allocator.free(resolved.path);
    if (resolved.temp_root) |temp_root| allocator.free(temp_root);
}

pub fn resolveSourceArchive(
    allocator: std.mem.Allocator,
    io: Io,
    source: ?[]const u8,
    parts_dir: ?[]const u8,
    metadata: *const StageMetadata,
    err_msg: *?[]const u8,
) anyerror!ResolvedSource {
    if ((source == null) == (parts_dir == null)) {
        return failMessage(ResolvedSource, allocator, err_msg, "exactly one of source or parts_dir must be provided", .{});
    }

    if (source) |source_path| {
        const validated_sha = try validateSourceArchive(allocator, io, source_path, metadata.size, metadata.sha256, err_msg);
        allocator.free(validated_sha);
        return .{
            .path = try dupePath(allocator, source_path),
            .input_mode = .source,
            .temp_root = null,
        };
    }

    const parts = parts_dir.?;
    const temp_root = try std.fmt.allocPrint(allocator, ".zig-cache/tmp/stage_archive_parts_{d}", .{tmpSuffix(io)});
    try std.Io.Dir.cwd().createDirPath(io, temp_root);
    const reconstructed_source = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ temp_root, metadata.filename });
    const reconstructed_sha = try reconstructArchiveFromParts(
        allocator,
        io,
        parts,
        reconstructed_source,
        metadata.filename,
        metadata.sha256,
        metadata.size,
        err_msg,
    );
    allocator.free(reconstructed_sha);

    return .{
        .path = reconstructed_source,
        .input_mode = .parts_dir,
        .temp_root = temp_root,
    };
}

pub fn stageArchive(
    allocator: std.mem.Allocator,
    io: Io,
    root: []const u8,
    source: ?[]const u8,
    parts_dir: ?[]const u8,
    check_only: bool,
    err_msg: *?[]const u8,
) anyerror!StageArchiveResult {
    var metadata = try loadStagePolicy(allocator, io, root, err_msg);
    errdefer freeStageMetadata(allocator, &metadata);

    const destination_rel = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ third_party_rel, metadata.filename });
    defer allocator.free(destination_rel);
    const destination = try joinPath(allocator, root, destination_rel);
    defer allocator.free(destination);

    try requireCleanThirdParty(allocator, io, root, metadata.filename, err_msg);

    var resolved = try resolveSourceArchive(allocator, io, source, parts_dir, &metadata, err_msg);
    defer {
        if (resolved.temp_root) |temp_root| std.Io.Dir.cwd().deleteTree(io, temp_root) catch {};
        freeResolvedSource(allocator, &resolved);
    }

    const actual_sha = try validateSourceArchive(allocator, io, resolved.path, metadata.size, metadata.sha256, err_msg);
    errdefer allocator.free(actual_sha);

    const existing = try inspectDestination(allocator, io, resolved.path, destination, metadata.size, metadata.sha256, actual_sha, err_msg);
    if (check_only) {
        const reported_sha = if (existing) |entry| blk: {
            allocator.free(actual_sha);
            break :blk entry.sha256;
        } else actual_sha;
        return .{
            .metadata = metadata,
            .status = .checked,
            .actual_sha256 = reported_sha,
            .destination = try dupePath(allocator, destination),
            .input_mode = resolved.input_mode,
        };
    }

    if (existing) |entry| {
        allocator.free(actual_sha);
        return .{
            .metadata = metadata,
            .status = entry.status,
            .actual_sha256 = entry.sha256,
            .destination = try dupePath(allocator, destination),
            .input_mode = resolved.input_mode,
        };
    }

    try copyFile(io, resolved.path, destination);
    const staged_sha = try validateSourceArchive(allocator, io, destination, metadata.size, metadata.sha256, err_msg);
    allocator.free(actual_sha);

    return .{
        .metadata = metadata,
        .status = .staged,
        .actual_sha256 = staged_sha,
        .destination = try dupePath(allocator, destination),
        .input_mode = resolved.input_mode,
    };
}

pub fn freeStageArchiveResult(allocator: std.mem.Allocator, result: *StageArchiveResult) void {
    freeStageMetadata(allocator, &result.metadata);
    allocator.free(result.actual_sha256);
    allocator.free(result.destination);
}

fn printLine(io: Io, comptime fmt: []const u8, args: anytype) !void {
    var buffer: [512]u8 = undefined;
    var writer = Io.File.stdout().writer(io, &buffer);
    try writer.interface.print(fmt ++ "\n", args);
    try writer.interface.flush();
}

const SelfTestError = error{SelfTestFailed};

fn expectSelfTest(condition: bool) SelfTestError!void {
    if (!condition) return SelfTestError.SelfTestFailed;
}

const RuntimeTmp = struct {
    io: Io,
    allocator: std.mem.Allocator,
    sub_path: []const u8,

    fn init(io: Io, allocator: std.mem.Allocator, prefix: []const u8) !RuntimeTmp {
        const sub_path = try std.fmt.allocPrint(allocator, "stage_archive_{s}_{d}", .{ prefix, tmpSuffix(io) });
        const root = try std.fmt.allocPrint(allocator, ".zig-cache/tmp/{s}", .{sub_path});
        defer allocator.free(root);
        std.Io.Dir.cwd().deleteTree(io, root) catch {};
        try std.Io.Dir.cwd().createDirPath(io, root);
        return .{ .io = io, .allocator = allocator, .sub_path = sub_path };
    }

    fn deinit(self: *RuntimeTmp) void {
        const root = std.fmt.allocPrint(self.allocator, ".zig-cache/tmp/{s}", .{self.sub_path}) catch return;
        defer self.allocator.free(root);
        std.Io.Dir.cwd().deleteTree(self.io, root) catch {};
        self.allocator.free(self.sub_path);
    }

    fn rootPath(self: *const RuntimeTmp, allocator: std.mem.Allocator) ![]const u8 {
        return std.fmt.allocPrint(allocator, ".zig-cache/tmp/{s}", .{self.sub_path});
    }

    fn write(self: *RuntimeTmp, relative: []const u8, data: []const u8) !void {
        const path = try std.fmt.allocPrint(self.allocator, ".zig-cache/tmp/{s}/{s}", .{ self.sub_path, relative });
        defer self.allocator.free(path);
        if (std.fs.path.dirname(relative)) |parent| {
            const parent_path = try std.fmt.allocPrint(self.allocator, ".zig-cache/tmp/{s}/{s}", .{ self.sub_path, parent });
            defer self.allocator.free(parent_path);
            try std.Io.Dir.cwd().createDirPath(self.io, parent_path);
        }
        try std.Io.Dir.cwd().writeFile(self.io, .{ .sub_path = path, .data = data });
    }
};

fn writeFixture(
    tmp: *RuntimeTmp,
    source_bytes: []const u8,
    source_size: ?u64,
) ![]const u8 {
    const size = source_size orelse expected_archive_sizes.get("x86_64-linux").?;
    try tmp.write("scripts/zigux/.keep", "\n");
    try tmp.write("third_party/.keep", "\n");
    try tmp.write("sources/.keep", "\n");

    var payload = try tmp.allocator.alloc(u8, @intCast(size));
    defer tmp.allocator.free(payload);
    var offset: usize = 0;
    while (offset < payload.len) {
        const chunk = @min(source_bytes.len, payload.len - offset);
        @memcpy(payload[offset..][0..chunk], source_bytes[0..chunk]);
        offset += chunk;
    }

    const source_path = try std.fmt.allocPrint(tmp.allocator, ".zig-cache/tmp/{s}/sources/zig-source.tar.xz", .{tmp.sub_path});
    try std.Io.Dir.cwd().writeFile(tmp.io, .{ .sub_path = source_path, .data = payload });
    return source_path;
}

fn writePolicy(tmp: *RuntimeTmp, sha256_hex: []const u8) !void {
    const policy_json = try std.fmt.allocPrint(
        tmp.allocator,
        \\{{
        \\  "phase": "Phase 2",
        \\  "channel": "0.17.0-dev.1443+6c25d2bd5",
        \\  "minimum_version": "0.17.0-dev.1443+6c25d2bd5",
        \\  "archive_sha256": {{
        \\    "x86_64-linux": "{s}"
        \\  }},
        \\  "upgrade_policy": {{
        \\    "channel_minimum_lockstep": true,
        \\    "archive_target_scope": ["x86_64-linux"],
        \\    "required_make_routes": ["phase2-toolchain", "phase2-validate"]
        \\  }}
        \\}}
        \\
    ,
        .{sha256_hex},
    );
    defer tmp.allocator.free(policy_json);
    try tmp.write("scripts/zigux/zig-toolchain-policy.json", policy_json);
}

pub fn writePartsFixture(
    io: Io,
    allocator: std.mem.Allocator,
    parts_dir: []const u8,
    payload: []const u8,
    filename: []const u8,
    sha256_hex: []const u8,
    chunk_bytes: usize,
) !void {
    try std.Io.Dir.cwd().createDirPath(io, parts_dir);

    const chunk_count = (payload.len + chunk_bytes - 1) / chunk_bytes;
    const manifest = try std.fmt.allocPrint(
        allocator,
        \\{{
        \\  "filename": "{s}",
        \\  "encoding": "base64",
        \\  "sha256": "{s}",
        \\  "size": {d},
        \\  "chunk_bytes": {d},
        \\  "part_count": {d},
        \\  "parts_glob": "part-*.b64"
        \\}}
        \\
    ,
        .{ filename, sha256_hex, payload.len, chunk_bytes, chunk_count },
    );
    defer allocator.free(manifest);

    const manifest_path = try std.fmt.allocPrint(allocator, "{s}/manifest.json", .{parts_dir});
    defer allocator.free(manifest_path);
    try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = manifest_path, .data = manifest });

    var index: usize = 0;
    while (index < chunk_count) : (index += 1) {
        const start = index * chunk_bytes;
        const end = @min(start + chunk_bytes, payload.len);
        const chunk = payload[start..end];
        const encoded_len = std.base64.standard.Encoder.calcSize(chunk.len);
        const encoded = try allocator.alloc(u8, encoded_len);
        defer allocator.free(encoded);
        _ = std.base64.standard.Encoder.encode(encoded, chunk);
        const shard_path = try std.fmt.allocPrint(allocator, "{s}/part-{d:0>3}.b64", .{ parts_dir, index });
        defer allocator.free(shard_path);
        const shard_text = try std.fmt.allocPrint(allocator, "{s}\n", .{encoded});
        defer allocator.free(shard_text);
        try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = shard_path, .data = shard_text });
    }
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var case_count: usize = 0;

    {
        var tmp = try RuntimeTmp.init(io, allocator, "pass");
        defer tmp.deinit();
        const root = try tmp.rootPath(allocator);
        defer allocator.free(root);
        const source = try writeFixture(&tmp, "x", null);
        defer allocator.free(source);
        const expected_sha = try resolver.computeSha256Hex(io, allocator, source);
        defer allocator.free(expected_sha);
        try writePolicy(&tmp, expected_sha);

        var err_msg: ?[]const u8 = null;
        defer if (err_msg) |msg| allocator.free(msg);

        var result = try stageArchive(allocator, io, root, source, null, false, &err_msg);
        defer freeStageArchiveResult(allocator, &result);
        try expectSelfTest(result.status == .staged);
        try expectSelfTest(std.mem.eql(u8, result.actual_sha256, expected_sha));
        try expectSelfTest(std.mem.eql(u8, result.metadata.filename, "zig-x86_64-linux-0.17.0-dev.1443+6c25d2bd5.tar.xz"));
        try expectSelfTest(result.input_mode == .source);
        case_count += 1;

        var again = try stageArchive(allocator, io, root, source, null, false, &err_msg);
        defer freeStageArchiveResult(allocator, &again);
        try expectSelfTest(again.status == .already_present);
        try expectSelfTest(std.mem.eql(u8, again.actual_sha256, expected_sha));
        try expectSelfTest(again.input_mode == .source);
        case_count += 1;

        var checked = try stageArchive(allocator, io, root, source, null, true, &err_msg);
        defer freeStageArchiveResult(allocator, &checked);
        try expectSelfTest(checked.status == .checked);
        try expectSelfTest(std.mem.eql(u8, checked.actual_sha256, expected_sha));
        try expectSelfTest(checked.input_mode == .source);
        case_count += 1;
    }

    {
        var tmp = try RuntimeTmp.init(io, allocator, "external_duplicate_source_pass");
        defer tmp.deinit();
        const root = try tmp.rootPath(allocator);
        defer allocator.free(root);
        const source = try writeFixture(&tmp, "x", null);
        defer allocator.free(source);
        const expected_sha = try resolver.computeSha256Hex(io, allocator, source);
        defer allocator.free(expected_sha);
        try writePolicy(&tmp, expected_sha);

        var err_msg: ?[]const u8 = null;
        defer if (err_msg) |msg| allocator.free(msg);

        var metadata = try loadStagePolicy(allocator, io, root, &err_msg);
        defer freeStageMetadata(allocator, &metadata);

        const duplicate_name = try duplicateArchiveName(allocator, metadata.filename);
        defer allocator.free(duplicate_name);
        const duplicate_rel = try std.fmt.allocPrint(allocator, "sources/{s}", .{duplicate_name});
        defer allocator.free(duplicate_rel);
        const duplicate_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, duplicate_rel });
        defer allocator.free(duplicate_path);

        const bytes = std.Io.Dir.cwd().readFileAlloc(io, source, allocator, .unlimited) catch return error.ReadFailed;
        defer allocator.free(bytes);
        try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = duplicate_path, .data = bytes });
        try std.Io.Dir.cwd().deleteFile(io, source);

        var result = try stageArchive(allocator, io, root, duplicate_path, null, false, &err_msg);
        defer freeStageArchiveResult(allocator, &result);
        try expectSelfTest(result.status == .staged);
        try expectSelfTest(std.mem.eql(u8, result.actual_sha256, expected_sha));
        try expectSelfTest(std.mem.endsWith(u8, result.destination, metadata.filename));
        try expectSelfTest(result.input_mode == .source);
        case_count += 1;
    }

    {
        var tmp = try RuntimeTmp.init(io, allocator, "parts_pass");
        defer tmp.deinit();
        const root = try tmp.rootPath(allocator);
        defer allocator.free(root);
        const source = try writeFixture(&tmp, "x", null);
        defer allocator.free(source);
        const expected_sha = try resolver.computeSha256Hex(io, allocator, source);
        defer allocator.free(expected_sha);
        try writePolicy(&tmp, expected_sha);

        var err_msg: ?[]const u8 = null;
        defer if (err_msg) |msg| allocator.free(msg);

        var metadata = try loadStagePolicy(allocator, io, root, &err_msg);
        defer freeStageMetadata(allocator, &metadata);

        const parts_dir = try std.fmt.allocPrint(allocator, "{s}/parts", .{root});
        defer allocator.free(parts_dir);
        const payload = std.Io.Dir.cwd().readFileAlloc(io, source, allocator, .unlimited) catch return error.ReadFailed;
        defer allocator.free(payload);
        try writePartsFixture(io, allocator, parts_dir, payload, metadata.filename, metadata.sha256, 786432);

        var result = try stageArchive(allocator, io, root, null, parts_dir, false, &err_msg);
        defer freeStageArchiveResult(allocator, &result);
        try expectSelfTest(result.status == .staged);
        try expectSelfTest(std.mem.eql(u8, result.actual_sha256, expected_sha));
        try expectSelfTest(result.input_mode == .parts_dir);
        case_count += 1;
    }

    const ExpectFailure = struct {
        source_bytes: []const u8 = "x",
        source_size: ?u64 = null,
        check_only: bool = true,
        use_parts_dir: bool = false,
        expected_substring: []const u8,
        mutator: ?*const fn (io_ctx: Io, alloc: std.mem.Allocator, root: []const u8, source: []const u8, expected_sha: []const u8, parts_dir: ?[]const u8) anyerror!void = null,
    };

    const failure_cases = [_]ExpectFailure{
        .{ .source_size = 1, .expected_substring = "to be 59093540 bytes, got 1" },
        .{
            .expected_substring = "to have sha256",
            .mutator = struct {
                fn mutate(io_ctx: Io, alloc: std.mem.Allocator, root: []const u8, _: []const u8, expected_sha: []const u8, _: ?[]const u8) !void {
                    const policy_path = try joinPath(alloc, root, toolchain_policy_rel);
                    defer alloc.free(policy_path);
                    const policy_text = try std.Io.Dir.cwd().readFileAlloc(io_ctx, policy_path, alloc, .unlimited);
                    defer alloc.free(policy_text);
                    const bad_sha = "3333333333333333333333333333333333333333333333333333333333333333";
                    const replaced = try std.mem.replaceOwned(u8, alloc, policy_text, expected_sha, bad_sha);
                    defer alloc.free(replaced);
                    try std.Io.Dir.cwd().writeFile(io_ctx, .{ .sub_path = policy_path, .data = replaced });
                }
            }.mutate,
        },
        .{
            .expected_substring = "duplicate-suffix archive copies",
            .mutator = struct {
                fn mutate(io_ctx: Io, alloc: std.mem.Allocator, root: []const u8, _: []const u8, _: []const u8, _: ?[]const u8) !void {
                    const duplicate = try joinPath(alloc, root, "third_party/zig-x86_64-linux-0.17.0-dev.1443+6c25d2bd5 (1).tar.xz");
                    defer alloc.free(duplicate);
                    try std.Io.Dir.cwd().writeFile(io_ctx, .{ .sub_path = duplicate, .data = "x" });
                }
            }.mutate,
        },
        .{
            .expected_substring = "destination archive is not a regular file",
            .mutator = struct {
                fn mutate(io_ctx: Io, alloc: std.mem.Allocator, root: []const u8, _: []const u8, _: []const u8, _: ?[]const u8) !void {
                    const destination = try joinPath(alloc, root, "third_party/zig-x86_64-linux-0.17.0-dev.1443+6c25d2bd5.tar.xz");
                    defer alloc.free(destination);
                    try std.Io.Dir.cwd().createDirPath(io_ctx, destination);
                }
            }.mutate,
        },
        .{
            .check_only = false,
            .expected_substring = "to have sha256",
            .mutator = struct {
                fn mutate(io_ctx: Io, alloc: std.mem.Allocator, root: []const u8, _: []const u8, _: []const u8, _: ?[]const u8) !void {
                    const destination = try joinPath(alloc, root, "third_party/zig-x86_64-linux-0.17.0-dev.1443+6c25d2bd5.tar.xz");
                    defer alloc.free(destination);
                    try writeConstantByteFile(
                        io_ctx,
                        destination,
                        'y',
                        expected_archive_sizes.get("x86_64-linux").?,
                    );
                }
            }.mutate,
        },
        .{
            .expected_substring = "duplicate toolchain policy keys",
            .mutator = struct {
                fn mutate(io_ctx: Io, alloc: std.mem.Allocator, root: []const u8, _: []const u8, expected_sha: []const u8, _: ?[]const u8) !void {
                    const policy_path = try joinPath(alloc, root, toolchain_policy_rel);
                    defer alloc.free(policy_path);
                    const policy_text = try std.fmt.allocPrint(
                        alloc,
                        "{{\"phase\":\"Phase 2\",\"phase\":\"Phase 3\",\"channel\":\"0.17.0-dev.1443+6c25d2bd5\",\"minimum_version\":\"0.17.0-dev.1443+6c25d2bd5\",\"archive_sha256\":{{\"x86_64-linux\":\"{s}\"}},\"upgrade_policy\":{{\"channel_minimum_lockstep\":true,\"archive_target_scope\":[\"x86_64-linux\"],\"required_make_routes\":[\"phase2-toolchain\",\"phase2-validate\"]}}}}\n",
                        .{expected_sha},
                    );
                    defer alloc.free(policy_text);
                    try std.Io.Dir.cwd().writeFile(io_ctx, .{ .sub_path = policy_path, .data = policy_text });
                }
            }.mutate,
        },
        .{
            .use_parts_dir = true,
            .check_only = false,
            .expected_substring = "missing shard manifest",
            .mutator = struct {
                fn mutate(io_ctx: Io, alloc: std.mem.Allocator, _: []const u8, _: []const u8, _: []const u8, parts_dir: ?[]const u8) !void {
                    const manifest_path = try std.fmt.allocPrint(alloc, "{s}/manifest.json", .{parts_dir.?});
                    defer alloc.free(manifest_path);
                    try std.Io.Dir.cwd().deleteFile(io_ctx, manifest_path);
                }
            }.mutate,
        },
        .{
            .use_parts_dir = true,
            .check_only = false,
            .expected_substring = "expected shard manifest filename",
            .mutator = struct {
                fn mutate(io_ctx: Io, alloc: std.mem.Allocator, _: []const u8, _: []const u8, _: []const u8, parts_dir: ?[]const u8) !void {
                    const manifest_path = try std.fmt.allocPrint(alloc, "{s}/manifest.json", .{parts_dir.?});
                    defer alloc.free(manifest_path);
                    const manifest_text = try std.Io.Dir.cwd().readFileAlloc(io_ctx, manifest_path, alloc, .unlimited);
                    defer alloc.free(manifest_text);
                    const replaced = try std.mem.replaceOwned(
                        u8,
                        alloc,
                        manifest_text,
                        "zig-x86_64-linux-0.17.0-dev.1443+6c25d2bd5.tar.xz",
                        "zig-aarch64-linux-0.17.0-dev.1443+6c25d2bd5.tar.xz",
                    );
                    defer alloc.free(replaced);
                    try std.Io.Dir.cwd().writeFile(io_ctx, .{ .sub_path = manifest_path, .data = replaced });
                }
            }.mutate,
        },
        .{
            .use_parts_dir = true,
            .check_only = false,
            .expected_substring = "missing expected shard",
            .mutator = struct {
                fn mutate(io_ctx: Io, alloc: std.mem.Allocator, _: []const u8, _: []const u8, _: []const u8, parts_dir: ?[]const u8) !void {
                    const shard_path = try std.fmt.allocPrint(alloc, "{s}/part-001.b64", .{parts_dir.?});
                    defer alloc.free(shard_path);
                    try std.Io.Dir.cwd().deleteFile(io_ctx, shard_path);
                }
            }.mutate,
        },
        .{
            .use_parts_dir = true,
            .check_only = false,
            .expected_substring = "invalid base64 shard",
            .mutator = struct {
                fn mutate(io_ctx: Io, alloc: std.mem.Allocator, _: []const u8, _: []const u8, _: []const u8, parts_dir: ?[]const u8) !void {
                    const shard_path = try std.fmt.allocPrint(alloc, "{s}/part-000.b64", .{parts_dir.?});
                    defer alloc.free(shard_path);
                    try std.Io.Dir.cwd().writeFile(io_ctx, .{ .sub_path = shard_path, .data = "not base64!\n" });
                }
            }.mutate,
        },
    };

    for (failure_cases) |failure_case| {
        var tmp = try RuntimeTmp.init(io, allocator, "fail");
        defer tmp.deinit();
        const root = try tmp.rootPath(allocator);
        defer allocator.free(root);
        const source = try writeFixture(&tmp, failure_case.source_bytes, failure_case.source_size);
        defer allocator.free(source);
        const expected_sha = try resolver.computeSha256Hex(io, allocator, source);
        defer allocator.free(expected_sha);
        try writePolicy(&tmp, expected_sha);

        var parts_dir: ?[]const u8 = null;
        defer if (parts_dir) |path| allocator.free(path);
        if (failure_case.use_parts_dir) {
            var setup_err_msg: ?[]const u8 = null;
            defer if (setup_err_msg) |msg| allocator.free(msg);
            var metadata = try loadStagePolicy(allocator, io, root, &setup_err_msg);
            defer freeStageMetadata(allocator, &metadata);
            parts_dir = try std.fmt.allocPrint(allocator, "{s}/parts", .{root});
            const payload = try std.Io.Dir.cwd().readFileAlloc(io, source, allocator, .unlimited);
            defer allocator.free(payload);
            try writePartsFixture(io, allocator, parts_dir.?, payload, metadata.filename, metadata.sha256, 8 * 1024 * 1024);
        }

        if (failure_case.mutator) |mutator| {
            try mutator(io, allocator, root, source, expected_sha, parts_dir);
        }

        var err_msg: ?[]const u8 = null;
        defer if (err_msg) |msg| allocator.free(msg);

        const stage_result = stageArchive(
            allocator,
            io,
            root,
            if (failure_case.use_parts_dir) null else source,
            parts_dir,
            failure_case.check_only,
            &err_msg,
        );

        if (stage_result) |_| {
            return SelfTestError.SelfTestFailed;
        } else |err| switch (err) {
            ValidationFailed.Invalid => {
                const message = err_msg orelse return SelfTestError.SelfTestFailed;
                if (std.mem.indexOf(u8, message, failure_case.expected_substring) == null) {
                    std.debug.print(
                        "unexpected failure message for {s}: {s}\n",
                        .{ failure_case.expected_substring, message },
                    );
                    return SelfTestError.SelfTestFailed;
                }
                case_count += 1;
            },
            else => return err,
        }
    }

    try printLine(io, "{s}", .{self_test_pass_marker});
    try printLine(io, "{s}{d}", .{ self_test_case_count_prefix, case_count });
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

    var self_test = false;
    var check_only = false;
    var root: ?[]const u8 = null;
    var source: ?[]const u8 = null;
    var parts_dir: ?[]const u8 = null;

    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--check-only")) {
            check_only = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            root = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--source")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            source = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--parts-dir")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            parts_dir = args[index];
            continue;
        }
        std.process.exit(2);
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    if ((source == null) == (parts_dir == null)) {
        var stderr_buffer: [256]u8 = undefined;
        var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
        try stderr_writer.interface.writeAll("exactly one of --source or --parts-dir is required unless --self-test is used\n");
        try stderr_writer.interface.flush();
        std.process.exit(2);
    }

    const resolved_root = if (root) |explicit_root|
        try std.Io.Dir.cwd().realPathFileAlloc(io, explicit_root, allocator)
    else
        try defaultRepoRoot(allocator);
    defer allocator.free(resolved_root);

    const resolved_source = if (source) |value| try std.Io.Dir.cwd().realPathFileAlloc(io, value, allocator) else null;
    defer if (resolved_source) |value| allocator.free(value);
    const resolved_parts_dir = if (parts_dir) |value| try std.Io.Dir.cwd().realPathFileAlloc(io, value, allocator) else null;
    defer if (resolved_parts_dir) |value| allocator.free(value);

    var err_msg: ?[]const u8 = null;
    defer if (err_msg) |msg| allocator.free(msg);

    var outcome = stageArchive(allocator, io, resolved_root, resolved_source, resolved_parts_dir, check_only, &err_msg) catch |err| switch (err) {
        ValidationFailed.Invalid => {
            try printLine(io, "STAGE_PINNED_ZIG_ARCHIVE=fail", .{});
            try printLine(io, "STAGE_PINNED_ZIG_ARCHIVE_ROOT={s}", .{resolved_root});
            if (resolved_source) |value| try printLine(io, "STAGE_PINNED_ZIG_ARCHIVE_SOURCE={s}", .{value});
            if (resolved_parts_dir) |value| try printLine(io, "STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR={s}", .{value});
            try printLine(io, "STAGE_PINNED_ZIG_ARCHIVE_NOTE={s}", .{err_msg.?});
            std.process.exit(1);
        },
        else => return err,
    };
    defer freeStageArchiveResult(allocator, &outcome);

    try printLine(io, "STAGE_PINNED_ZIG_ARCHIVE=pass", .{});
    try printLine(io, "STAGE_PINNED_ZIG_ARCHIVE_ROOT={s}", .{resolved_root});
    if (resolved_source) |value| try printLine(io, "STAGE_PINNED_ZIG_ARCHIVE_SOURCE={s}", .{value});
    if (resolved_parts_dir) |value| try printLine(io, "STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR={s}", .{value});
    try printLine(io, "STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={s}", .{outcome.input_mode.name()});
    try printLine(io, "STAGE_PINNED_ZIG_ARCHIVE_TARGET={s}", .{outcome.metadata.target});
    try printLine(io, "STAGE_PINNED_ZIG_ARCHIVE_FILENAME={s}", .{outcome.metadata.filename});
    try printLine(io, "STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SIZE={d}", .{outcome.metadata.size});
    try printLine(io, "STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256={s}", .{outcome.metadata.sha256});
    try printLine(io, "STAGE_PINNED_ZIG_ARCHIVE_ACTUAL_SHA256={s}", .{outcome.actual_sha256});
    try printLine(io, "STAGE_PINNED_ZIG_ARCHIVE_DESTINATION={s}", .{outcome.destination});
    try printLine(io, "STAGE_PINNED_ZIG_ARCHIVE_STATUS={s}", .{outcome.status.name()});
    std.process.exit(0);
}

test "duplicate archive suffix helper matches policy stem" {
    const expected = "zig-x86_64-linux-0.17.0-dev.1443+6c25d2bd5.tar.xz";
    try std.testing.expect(policy.archiveNameHasDuplicateSuffix("zig-x86_64-linux-0.17.0-dev.1443+6c25d2bd5 (1).tar.xz", expected));
}

test "writeConstantByteFile writes expected archive size" {
    const io = std.testing.io;
    const root = try std.fmt.allocPrint(std.testing.allocator, ".zig-cache/tmp/stage_archive_test_constant_{d}", .{tmpSuffix(io)});
    defer std.testing.allocator.free(root);
    std.Io.Dir.cwd().deleteTree(io, root) catch {};
    try std.Io.Dir.cwd().createDirPath(io, root);
    defer std.Io.Dir.cwd().deleteTree(io, root) catch {};

    const destination = try std.fmt.allocPrint(std.testing.allocator, "{s}/third_party/zig-x86_64-linux-0.17.0-dev.1443+6c25d2bd5.tar.xz", .{root});
    defer std.testing.allocator.free(destination);
    const expected_size = expected_archive_sizes.get("x86_64-linux").?;
    try writeConstantByteFile(io, destination, 'y', expected_size);

    var file = try std.Io.Dir.cwd().openFile(io, destination, .{});
    defer file.close(io);
    try std.testing.expectEqual(expected_size, (try file.stat(io)).size);
}

test "load stage policy accepts live policy shape" {
    const root = try defaultRepoRoot(std.testing.allocator);
    defer std.testing.allocator.free(root);
    var err_msg: ?[]const u8 = null;
    defer if (err_msg) |msg| std.testing.allocator.free(msg);
    var metadata = try loadStagePolicy(std.testing.allocator, std.testing.io, root, &err_msg);
    defer freeStageMetadata(std.testing.allocator, &metadata);
    try std.testing.expectEqualStrings("x86_64-linux", metadata.target);
}
