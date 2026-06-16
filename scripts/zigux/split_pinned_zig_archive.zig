const std = @import("std");
const Io = std.Io;
const stage = @import("stage_pinned_zig_archive.zig");
const resolver = @import("toolchain_resolver.zig");

pub const toolchain_policy_rel = stage.toolchain_policy_rel;
pub const default_chunk_bytes: usize = 786_432;
pub const self_test_pass_marker = "SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass";
pub const self_test_case_count_prefix = "SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT=";

const ValidationFailed = stage.ValidationFailed;

fn computeSha256HexFromBytes(allocator: std.mem.Allocator, payload: []const u8) ![]const u8 {
    var hasher = std.crypto.hash.sha2.Sha256.init(.{});
    hasher.update(payload);
    var digest: [32]u8 = undefined;
    hasher.final(&digest);
    return try std.fmt.allocPrint(allocator, "{s}", .{std.fmt.bytesToHex(&digest, .lower)});
}

fn printLine(io: Io, comptime fmt: []const u8, args: anytype) !void {
    var buffer: [1024]u8 = undefined;
    var writer = Io.File.stdout().writer(io, &buffer);
    try writer.interface.print(fmt ++ "\n", args);
    try writer.interface.flush();
}

fn ensureCleanOutputDir(io: Io, output_dir: []const u8, err_msg: *?[]const u8, allocator: std.mem.Allocator) anyerror!void {
    if (!guardPathExists(io, output_dir)) {
        try std.Io.Dir.cwd().createDirPath(io, output_dir);
        return;
    }

    var dir = std.Io.Dir.cwd().openDir(io, output_dir, .{ .iterate = true }) catch {
        err_msg.* = try std.fmt.allocPrint(allocator, "output directory must be empty: {s}", .{output_dir});
        return ValidationFailed.Invalid;
    };
    defer dir.close(io);

    var iterator = dir.iterate();
    while (try iterator.next(io)) |entry| {
        _ = entry;
        err_msg.* = try std.fmt.allocPrint(allocator, "output directory must be empty: {s}", .{output_dir});
        return ValidationFailed.Invalid;
    }
}

fn guardPathExists(io: Io, path: []const u8) bool {
    std.Io.Dir.cwd().access(io, path, .{}) catch return false;
    return true;
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

fn loadManifest(
    io: Io,
    allocator: std.mem.Allocator,
    parts_dir: []const u8,
    err_msg: *?[]const u8,
) anyerror!struct {
    filename: []const u8,
    sha256: []const u8,
    size: u64,
    chunk_bytes: usize,
    part_count: usize,
} {
    const manifest_path = try std.fmt.allocPrint(allocator, "{s}/manifest.json", .{parts_dir});
    defer allocator.free(manifest_path);

    const manifest_bytes = std.Io.Dir.cwd().readFileAlloc(io, manifest_path, allocator, .unlimited) catch {
        err_msg.* = try std.fmt.allocPrint(allocator, "missing manifest: {s}", .{manifest_path});
        return ValidationFailed.Invalid;
    };
    defer allocator.free(manifest_bytes);

    const parsed = std.json.parseFromSlice(std.json.Value, allocator, manifest_bytes, .{}) catch {
        err_msg.* = try std.fmt.allocPrint(allocator, "invalid manifest JSON in {s}", .{manifest_path});
        return ValidationFailed.Invalid;
    };
    defer parsed.deinit();

    const manifest = switch (parsed.value) {
        .object => |object| object,
        else => {
            err_msg.* = try std.fmt.allocPrint(allocator, "invalid manifest payload in {s}: expected object", .{manifest_path});
            return ValidationFailed.Invalid;
        },
    };

    const filename_value = manifest.get("filename") orelse {
        try setInvalidManifestField(allocator, err_msg, "filename");
        return ValidationFailed.Invalid;
    };
    const encoding_value = manifest.get("encoding") orelse {
        try setInvalidManifestField(allocator, err_msg, "encoding");
        return ValidationFailed.Invalid;
    };
    const sha256_value = manifest.get("sha256") orelse {
        try setInvalidManifestField(allocator, err_msg, "sha256");
        return ValidationFailed.Invalid;
    };
    const size_value = manifest.get("size") orelse {
        try setInvalidManifestField(allocator, err_msg, "size");
        return ValidationFailed.Invalid;
    };
    const chunk_bytes_value = manifest.get("chunk_bytes") orelse {
        try setInvalidManifestField(allocator, err_msg, "chunk_bytes");
        return ValidationFailed.Invalid;
    };
    const part_count_value = manifest.get("part_count") orelse {
        try setInvalidManifestField(allocator, err_msg, "part_count");
        return ValidationFailed.Invalid;
    };
    const parts_glob_value = manifest.get("parts_glob") orelse {
        try setInvalidManifestField(allocator, err_msg, "parts_glob");
        return ValidationFailed.Invalid;
    };

    const filename = try dupeJsonString(allocator, filename_value, err_msg, "filename");
    const encoding = try dupeJsonString(allocator, encoding_value, err_msg, "encoding");
    defer allocator.free(encoding);
    const sha256 = try dupeJsonString(allocator, sha256_value, err_msg, "sha256");
    const size = try parseJsonPositiveInt(size_value, err_msg, allocator, "size");
    const chunk_bytes = @as(usize, @intCast(try parseJsonPositiveInt(chunk_bytes_value, err_msg, allocator, "chunk_bytes")));
    const part_count = @as(usize, @intCast(try parseJsonPositiveInt(part_count_value, err_msg, allocator, "part_count")));
    const parts_glob = try dupeJsonString(allocator, parts_glob_value, err_msg, "parts_glob");
    defer allocator.free(parts_glob);

    if (!std.mem.eql(u8, encoding, "base64")) {
        allocator.free(filename);
        allocator.free(sha256);
        err_msg.* = try std.fmt.allocPrint(allocator, "unsupported manifest encoding: {s}", .{encoding});
        return ValidationFailed.Invalid;
    }
    if (!std.mem.eql(u8, parts_glob, "part-*.b64")) {
        allocator.free(filename);
        allocator.free(sha256);
        err_msg.* = try std.fmt.allocPrint(allocator, "unsupported manifest parts_glob: {s}", .{parts_glob});
        return ValidationFailed.Invalid;
    }

    return .{
        .filename = filename,
        .sha256 = sha256,
        .size = @as(u64, @intCast(size)),
        .chunk_bytes = chunk_bytes,
        .part_count = part_count,
    };
}

fn setInvalidManifestField(allocator: std.mem.Allocator, err_msg: *?[]const u8, key: []const u8) !void {
    err_msg.* = try std.fmt.allocPrint(allocator, "invalid manifest field: {s}", .{key});
}

fn dupeJsonString(allocator: std.mem.Allocator, value: std.json.Value, err_msg: *?[]const u8, key: []const u8) ValidationFailed![]const u8 {
    const text = switch (value) {
        .string => |raw| raw,
        else => {
            try setInvalidManifestField(allocator, err_msg, key);
            return ValidationFailed.Invalid;
        },
    };
    const trimmed = std.mem.trim(u8, text, " \t\r\n");
    if (trimmed.len == 0) {
        try setInvalidManifestField(allocator, err_msg, key);
        return ValidationFailed.Invalid;
    }
    return try allocator.dupe(u8, trimmed);
}

fn parseJsonPositiveInt(value: std.json.Value, err_msg: *?[]const u8, allocator: std.mem.Allocator, key: []const u8) ValidationFailed!i64 {
    const raw = switch (value) {
        .integer => |n| n,
        else => {
            try setInvalidManifestField(allocator, err_msg, key);
            return ValidationFailed.Invalid;
        },
    };
    if (raw <= 0) {
        try setInvalidManifestField(allocator, err_msg, key);
        return ValidationFailed.Invalid;
    }
    return raw;
}

pub fn splitArchive(
    io: Io,
    allocator: std.mem.Allocator,
    source: []const u8,
    output_dir: []const u8,
    metadata: stage.StageMetadata,
    chunk_bytes: usize,
    err_msg: *?[]const u8,
) anyerror!usize {
    if (chunk_bytes == 0) {
        err_msg.* = try allocator.dupe(u8, "chunk_bytes must be positive");
        return ValidationFailed.Invalid;
    }

    const validated_sha = try stage.validateSourceArchive(allocator, io, source, metadata.size, metadata.sha256, err_msg);
    defer allocator.free(validated_sha);
    try ensureCleanOutputDir(io, output_dir, err_msg, allocator);

    const part_count = (metadata.size + chunk_bytes - 1) / chunk_bytes;
    var file = std.Io.Dir.cwd().openFile(io, source, .{}) catch {
        err_msg.* = try std.fmt.allocPrint(allocator, "missing source archive: {s}", .{source});
        return ValidationFailed.Invalid;
    };
    defer file.close(io);

    var read_buffer: [1024 * 1024]u8 = undefined;
    var index: usize = 0;
    while (index < part_count) : (index += 1) {
        const read_len = try std.Io.File.readStreaming(file, io, &.{read_buffer[0..chunk_bytes]});
        if (read_len == 0) {
            err_msg.* = try std.fmt.allocPrint(allocator, "expected archive data for part {d}, got EOF", .{index});
            return ValidationFailed.Invalid;
        }
        const chunk = read_buffer[0..read_len];

        const encoded_len = std.base64.standard.Encoder.calcSize(chunk.len);
        const encoded = try allocator.alloc(u8, encoded_len);
        defer allocator.free(encoded);
        _ = std.base64.standard.Encoder.encode(encoded, chunk);

        const shard_path = try std.fmt.allocPrint(allocator, "{s}/part-{d:0>3}.b64", .{ output_dir, index });
        defer allocator.free(shard_path);
        const shard_text = try std.fmt.allocPrint(allocator, "{s}\n", .{encoded});
        defer allocator.free(shard_text);
        try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = shard_path, .data = shard_text });
    }

    const leftover_len = std.Io.File.readStreaming(file, io, &.{read_buffer[0..1]}) catch |err| switch (err) {
        error.EndOfStream => 0,
        else => return err,
    };
    if (leftover_len != 0) {
        err_msg.* = try allocator.dupe(u8, "source archive had unexpected trailing bytes after part split");
        return ValidationFailed.Invalid;
    }

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
        .{ metadata.filename, metadata.sha256, metadata.size, chunk_bytes, part_count },
    );
    defer allocator.free(manifest);
    const manifest_path = try std.fmt.allocPrint(allocator, "{s}/manifest.json", .{output_dir});
    defer allocator.free(manifest_path);
    try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = manifest_path, .data = manifest });

    return part_count;
}

pub fn reconstructArchive(
    io: Io,
    allocator: std.mem.Allocator,
    parts_dir: []const u8,
    destination: []const u8,
    err_msg: *?[]const u8,
) anyerror!struct {
    filename: []const u8,
    sha256: []const u8,
    size: u64,
    part_count: usize,
} {
    const metadata = try loadManifest(io, allocator, parts_dir, err_msg);
    defer allocator.free(metadata.filename);
    defer allocator.free(metadata.sha256);

    var combined: std.ArrayList(u8) = .empty;
    defer combined.deinit(allocator);

    var index: usize = 0;
    while (index < metadata.part_count) : (index += 1) {
        const shard_name = try std.fmt.allocPrint(allocator, "part-{d:0>3}.b64", .{index});
        defer allocator.free(shard_name);
        const shard_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ parts_dir, shard_name });
        defer allocator.free(shard_path);

        const encoded = std.Io.Dir.cwd().readFileAlloc(io, shard_path, allocator, .unlimited) catch {
            err_msg.* = try std.fmt.allocPrint(allocator, "missing expected shard: {s}", .{shard_name});
            return ValidationFailed.Invalid;
        };
        defer allocator.free(encoded);

        const chunk = decodeBase64Shard(allocator, encoded) catch {
            err_msg.* = try std.fmt.allocPrint(allocator, "invalid base64 shard: {s}", .{shard_name});
            return ValidationFailed.Invalid;
        };
        defer allocator.free(chunk);
        try combined.appendSlice(allocator, chunk);
    }

    if (combined.items.len != metadata.size) {
        err_msg.* = try std.fmt.allocPrint(allocator, "expected reconstructed archive to be {d} bytes, got {d}", .{ metadata.size, combined.items.len });
        return ValidationFailed.Invalid;
    }

    const actual_sha = try computeSha256HexFromBytes(allocator, combined.items);
    defer allocator.free(actual_sha);
    if (!std.mem.eql(u8, actual_sha, metadata.sha256)) {
        err_msg.* = try std.fmt.allocPrint(allocator, "expected reconstructed archive to have sha256 {s}, got {s}", .{ metadata.sha256, actual_sha });
        return ValidationFailed.Invalid;
    }

    if (std.fs.path.dirname(destination)) |parent| {
        try std.Io.Dir.cwd().createDirPath(io, parent);
    }
    try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = destination, .data = combined.items });

    return .{
        .filename = try allocator.dupe(u8, metadata.filename),
        .sha256 = try allocator.dupe(u8, metadata.sha256),
        .size = metadata.size,
        .part_count = metadata.part_count,
    };
}

fn expectSelfTest(condition: bool) error{ SelfTestFailed }!void {
    if (!condition) return error.SelfTestFailed;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var case_count: usize = 0;
    var payload_buf: [4097]u8 = undefined;
    const unit = "lane05-archive-payload-";
    var offset: usize = 0;
    while (offset < payload_buf.len) {
        const chunk = @min(unit.len, payload_buf.len - offset);
        @memcpy(payload_buf[offset..][0..chunk], unit[0..chunk]);
        offset += chunk;
    }
    const trimmed_payload = payload_buf[0..];

    {
        var tmp = try RuntimeTmp.init(io, allocator, "pass");
        defer tmp.deinit();
        const root = try tmp.rootPath(allocator);
        defer allocator.free(root);
        const source_path = try writeFixture(&tmp, trimmed_payload);
        defer allocator.free(source_path);
        const expected_sha = try resolver.computeSha256Hex(io, allocator, source_path);
        defer allocator.free(expected_sha);
        try writePolicy(&tmp, expected_sha);

        var err_msg: ?[]const u8 = null;
        defer if (err_msg) |msg| allocator.free(msg);
        var metadata = stage.StageMetadata{
            .channel = try allocator.dupe(u8, "0.17.0-dev.877+a3ae499dc"),
            .target = try allocator.dupe(u8, "x86_64-linux"),
            .sha256 = try allocator.dupe(u8, expected_sha),
            .size = trimmed_payload.len,
            .filename = try allocator.dupe(u8, "zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz"),
        };
        defer stage.freeStageMetadata(allocator, &metadata);

        const output_dir = try std.fmt.allocPrint(allocator, "{s}/out", .{root});
        defer allocator.free(output_dir);
        try stage.writePartsFixture(io, allocator, output_dir, trimmed_payload, metadata.filename, metadata.sha256, 1024);
        const part_count = (trimmed_payload.len + 1023) / 1024;
        try expectSelfTest(part_count > 0);

        const rebuilt_path = try std.fmt.allocPrint(allocator, "{s}/rebuilt.tar.xz", .{root});
        defer allocator.free(rebuilt_path);
        const rebuilt = try reconstructArchive(io, allocator, output_dir, rebuilt_path, &err_msg);
        defer allocator.free(rebuilt.filename);
        defer allocator.free(rebuilt.sha256);

        const rebuilt_bytes = try std.Io.Dir.cwd().readFileAlloc(io, rebuilt_path, allocator, .unlimited);
        defer allocator.free(rebuilt_bytes);
        try expectSelfTest(std.mem.eql(u8, rebuilt_bytes, trimmed_payload));
        try expectSelfTest(std.mem.eql(u8, rebuilt.sha256, expected_sha));
        case_count += 1;
    }

    try printLine(io, "{s}", .{self_test_pass_marker});
    try printLine(io, "{s}{d}", .{ self_test_case_count_prefix, case_count });
    return 0;
}

const RuntimeTmp = struct {
    io: Io,
    allocator: std.mem.Allocator,
    sub_path: []const u8,

    fn init(io: Io, allocator: std.mem.Allocator, prefix: []const u8) !RuntimeTmp {
        const id = tmp_counter.fetchAdd(1, .monotonic);
        const sub_path = try std.fmt.allocPrint(allocator, "split_archive_{s}_{d}", .{ prefix, id });
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

    fn write(self: *const RuntimeTmp, relative: []const u8, data: []const u8) !void {
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

var tmp_counter: std.atomic.Value(u32) = .init(0);

fn writeFixture(tmp: *RuntimeTmp, payload: []const u8) ![]const u8 {
    try tmp.write("scripts/zigux/.keep", "\n");
    try tmp.write("sources/.keep", "\n");
    const source_path = try std.fmt.allocPrint(tmp.allocator, ".zig-cache/tmp/{s}/sources/zig-source.tar.xz", .{tmp.sub_path});
    try std.Io.Dir.cwd().writeFile(tmp.io, .{ .sub_path = source_path, .data = payload });
    return source_path;
}

fn writePolicy(tmp: *RuntimeTmp, sha256_hex: []const u8) !void {
    const policy_json = try std.fmt.allocPrint(
        tmp.allocator,
        \\{{
        \\  "phase": "Phase 2",
        \\  "channel": "0.17.0-dev.877+a3ae499dc",
        \\  "minimum_version": "0.17.0-dev.877+a3ae499dc",
        \\  "archive_sha256": {{
        \\    "x86_64-linux": "{s}"
        \\  }},
        \\  "upgrade_policy": {{
        \\    "channel_minimum_lockstep": true,
        \\    "archive_target_scope": ["x86_64-linux"],
        \\    "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"]
        \\  }}
        \\}}
        \\
    ,
        .{sha256_hex},
    );
    defer tmp.allocator.free(policy_json);
    try tmp.write("scripts/zigux/zig-toolchain-policy.json", policy_json);
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

    var self_test = false;
    var root: ?[]const u8 = null;
    var source: ?[]const u8 = null;
    var output_dir: ?[]const u8 = null;
    var parts_dir: ?[]const u8 = null;
    var destination: ?[]const u8 = null;
    var chunk_bytes: usize = default_chunk_bytes;

    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
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
        if (std.mem.eql(u8, arg, "--output-dir")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            output_dir = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--chunk-bytes")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            chunk_bytes = std.fmt.parseInt(usize, args[index], 10) catch std.process.exit(2);
            continue;
        }
        if (std.mem.eql(u8, arg, "--parts-dir")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            parts_dir = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--destination")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            destination = args[index];
            continue;
        }
        std.process.exit(2);
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const split_mode = source != null or output_dir != null;
    const reconstruct_mode = parts_dir != null or destination != null;
    if (split_mode and reconstruct_mode) {
        std.process.exit(2);
    }

    const resolved_root = if (root) |value|
        try std.Io.Dir.cwd().realPathFileAlloc(io, value, allocator)
    else
        try stage.defaultRepoRoot(allocator);
    defer allocator.free(resolved_root);

    if (split_mode) {
        if (source == null or output_dir == null) std.process.exit(2);
        const resolved_source = try std.Io.Dir.cwd().realPathFileAlloc(io, source.?, allocator);
        defer allocator.free(resolved_source);
        const resolved_output = try std.Io.Dir.cwd().realPathFileAlloc(io, output_dir.?, allocator);
        defer allocator.free(resolved_output);

        var err_msg: ?[]const u8 = null;
        defer if (err_msg) |msg| allocator.free(msg);

        var metadata = stage.loadStagePolicy(allocator, io, resolved_root, &err_msg) catch |err| switch (err) {
            stage.ValidationFailed.Invalid => {
                try printLine(io, "SPLIT_PINNED_ZIG_ARCHIVE=fail", .{});
                try printLine(io, "SPLIT_PINNED_ZIG_ARCHIVE_ROOT={s}", .{resolved_root});
                try printLine(io, "SPLIT_PINNED_ZIG_ARCHIVE_SOURCE={s}", .{resolved_source});
                try printLine(io, "SPLIT_PINNED_ZIG_ARCHIVE_NOTE={s}", .{err_msg.?});
                std.process.exit(1);
            },
            else => return err,
        };
        defer stage.freeStageMetadata(allocator, &metadata);

        const part_count = splitArchive(io, allocator, resolved_source, resolved_output, metadata, chunk_bytes, &err_msg) catch |err| switch (err) {
            ValidationFailed.Invalid => {
                try printLine(io, "SPLIT_PINNED_ZIG_ARCHIVE=fail", .{});
                try printLine(io, "SPLIT_PINNED_ZIG_ARCHIVE_ROOT={s}", .{resolved_root});
                try printLine(io, "SPLIT_PINNED_ZIG_ARCHIVE_SOURCE={s}", .{resolved_source});
                try printLine(io, "SPLIT_PINNED_ZIG_ARCHIVE_NOTE={s}", .{err_msg.?});
                std.process.exit(1);
            },
            else => return err,
        };

        try printLine(io, "SPLIT_PINNED_ZIG_ARCHIVE=pass", .{});
        try printLine(io, "SPLIT_PINNED_ZIG_ARCHIVE_ROOT={s}", .{resolved_root});
        try printLine(io, "SPLIT_PINNED_ZIG_ARCHIVE_SOURCE={s}", .{resolved_source});
        try printLine(io, "SPLIT_PINNED_ZIG_ARCHIVE_OUTPUT_DIR={s}", .{resolved_output});
        try printLine(io, "SPLIT_PINNED_ZIG_ARCHIVE_FILENAME={s}", .{metadata.filename});
        try printLine(io, "SPLIT_PINNED_ZIG_ARCHIVE_SHA256={s}", .{metadata.sha256});
        try printLine(io, "SPLIT_PINNED_ZIG_ARCHIVE_SIZE={d}", .{metadata.size});
        try printLine(io, "SPLIT_PINNED_ZIG_ARCHIVE_PART_COUNT={d}", .{part_count});
        try printLine(io, "SPLIT_PINNED_ZIG_ARCHIVE_CHUNK_BYTES={d}", .{chunk_bytes});
        try printLine(io, "SPLIT_PINNED_ZIG_ARCHIVE_MANIFEST={s}/manifest.json", .{resolved_output});
        return;
    }

    if (reconstruct_mode) {
        if (parts_dir == null or destination == null) std.process.exit(2);
        const resolved_parts = try std.Io.Dir.cwd().realPathFileAlloc(io, parts_dir.?, allocator);
        defer allocator.free(resolved_parts);
        const resolved_destination = try std.Io.Dir.cwd().realPathFileAlloc(io, destination.?, allocator);
        defer allocator.free(resolved_destination);

        var err_msg: ?[]const u8 = null;
        defer if (err_msg) |msg| allocator.free(msg);

        const rebuilt = reconstructArchive(io, allocator, resolved_parts, resolved_destination, &err_msg) catch |err| switch (err) {
            ValidationFailed.Invalid => {
                try printLine(io, "RECONSTRUCT_PINNED_ZIG_ARCHIVE=fail", .{});
                try printLine(io, "RECONSTRUCT_PINNED_ZIG_ARCHIVE_PARTS_DIR={s}", .{resolved_parts});
                try printLine(io, "RECONSTRUCT_PINNED_ZIG_ARCHIVE_DESTINATION={s}", .{resolved_destination});
                try printLine(io, "RECONSTRUCT_PINNED_ZIG_ARCHIVE_NOTE={s}", .{err_msg.?});
                std.process.exit(1);
            },
            else => return err,
        };
        defer allocator.free(rebuilt.filename);
        defer allocator.free(rebuilt.sha256);

        try printLine(io, "RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass", .{});
        try printLine(io, "RECONSTRUCT_PINNED_ZIG_ARCHIVE_PARTS_DIR={s}", .{resolved_parts});
        try printLine(io, "RECONSTRUCT_PINNED_ZIG_ARCHIVE_DESTINATION={s}", .{resolved_destination});
        try printLine(io, "RECONSTRUCT_PINNED_ZIG_ARCHIVE_FILENAME={s}", .{rebuilt.filename});
        try printLine(io, "RECONSTRUCT_PINNED_ZIG_ARCHIVE_SHA256={s}", .{rebuilt.sha256});
        try printLine(io, "RECONSTRUCT_PINNED_ZIG_ARCHIVE_SIZE={d}", .{rebuilt.size});
        try printLine(io, "RECONSTRUCT_PINNED_ZIG_ARCHIVE_PART_COUNT={d}", .{rebuilt.part_count});
        return;
    }

    std.process.exit(2);
}