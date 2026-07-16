const std = @import("std");

pub const ToolchainPolicyError = error{
    UnsupportedVersion,
    InvalidPolicyField,
    DuplicatePolicyKey,
    UnexpectedPolicyKey,
    ArchiveTargetMismatch,
    ChannelLockstepMismatch,
    OutOfMemory,
};

pub const ToolchainStatus = enum {
    present,
    too_old,
    not_pinned,
};

pub const ZigVersion = struct {
    major: u32,
    minor: u32,
    patch: u32,
    release_rank: u8,
    dev_build: u32,

    pub fn order(self: ZigVersion, other: ZigVersion) std.math.Order {
        const fields = .{ self.major, self.minor, self.patch, self.release_rank, self.dev_build };
        const other_fields = .{ other.major, other.minor, other.patch, other.release_rank, other.dev_build };
        inline for (fields, other_fields) |left, right| {
            const cmp = std.math.order(left, right);
            if (cmp != .eq) return cmp;
        }
        return .eq;
    }

    pub fn lessThan(self: ZigVersion, other: ZigVersion) bool {
        return self.order(other) == .lt;
    }
};

pub const ToolchainEvaluation = struct {
    status: ToolchainStatus,
    note: ?[]const u8,
};

pub const UpgradePolicy = struct {
    channel_minimum_lockstep: bool,
    archive_target_scope: []const []const u8,
    required_make_routes: []const []const u8,
};

pub const ToolchainPolicy = struct {
    phase: []const u8,
    channel: []const u8,
    minimum_version: []const u8,
    archive_sha256: std.StringArrayHashMapUnmanaged([]const u8),
    upgrade_policy: UpgradePolicy,
};

pub fn parseZigVersion(raw: []const u8) ToolchainPolicyError!ZigVersion {
    const trimmed = std.mem.trim(u8, raw, " \t\r\n");
    var major: u32 = undefined;
    var minor: u32 = undefined;
    var patch: u32 = undefined;
    var release_rank: u8 = 1;
    var dev_build: u32 = 0;

    var cursor: usize = 0;
    major = try parseDecimalComponent(trimmed, &cursor);
    if (cursor >= trimmed.len or trimmed[cursor] != '.') return ToolchainPolicyError.UnsupportedVersion;
    cursor += 1;
    minor = try parseDecimalComponent(trimmed, &cursor);
    if (cursor >= trimmed.len or trimmed[cursor] != '.') return ToolchainPolicyError.UnsupportedVersion;
    cursor += 1;
    patch = try parseDecimalComponent(trimmed, &cursor);

    if (cursor < trimmed.len and std.mem.startsWith(u8, trimmed[cursor..], "-dev.")) {
        release_rank = 0;
        cursor += "-dev.".len;
        dev_build = try parseDecimalComponent(trimmed, &cursor);
        if (cursor < trimmed.len and trimmed[cursor] == '+') {
            cursor += 1;
            while (cursor < trimmed.len) : (cursor += 1) {
                const ch = trimmed[cursor];
                if (!std.ascii.isAlphanumeric(ch) and ch != '.' and ch != '-') {
                    return ToolchainPolicyError.UnsupportedVersion;
                }
            }
        }
    }

    if (cursor != trimmed.len) return ToolchainPolicyError.UnsupportedVersion;

    return .{
        .major = major,
        .minor = minor,
        .patch = patch,
        .release_rank = release_rank,
        .dev_build = dev_build,
    };
}

fn parseDecimalComponent(text: []const u8, cursor: *usize) ToolchainPolicyError!u32 {
    if (cursor.* >= text.len or !std.ascii.isDigit(text[cursor.*])) {
        return ToolchainPolicyError.UnsupportedVersion;
    }
    var value: u32 = 0;
    while (cursor.* < text.len and std.ascii.isDigit(text[cursor.*])) {
        const digit: u32 = text[cursor.*] - '0';
        const next = value * 10 + digit;
        if (next < value) return ToolchainPolicyError.UnsupportedVersion;
        value = next;
        cursor.* += 1;
    }
    return value;
}

pub fn evaluateToolchainVersion(
    version: []const u8,
    min_version_raw: []const u8,
    expected_channel_raw: ?[]const u8,
) ToolchainPolicyError!ToolchainEvaluation {
    const parsed_version = try parseZigVersion(version);
    const min_version = try parseZigVersion(min_version_raw);
    if (parsed_version.lessThan(min_version)) {
        return .{ .status = .too_old, .note = null };
    }
    if (expected_channel_raw) |expected_raw| {
        const expected_channel = std.mem.trim(u8, expected_raw, " \t\r\n");
        _ = try parseZigVersion(expected_channel);
        const actual = std.mem.trim(u8, version, " \t\r\n");
        if (!std.mem.eql(u8, actual, expected_channel)) {
            return .{ .status = .not_pinned, .note = expected_channel };
        }
    }
    return .{ .status = .present, .note = null };
}

pub fn policyArchiveExtension(target: []const u8) []const u8 {
    return if (std.mem.endsWith(u8, target, "-windows")) ".zip" else ".tar.xz";
}

pub fn policyArchiveFilename(target: []const u8, channel: []const u8, buffer: []u8) ![]const u8 {
    return std.fmt.bufPrint(buffer, "zig-{s}-{s}{s}", .{ target, channel, policyArchiveExtension(target) });
}

pub fn archiveNameHasDuplicateSuffix(path_name: []const u8, expected_filename: []const u8) bool {
    const extension: []const u8 = if (std.mem.endsWith(u8, expected_filename, ".tar.xz"))
        ".tar.xz"
    else if (std.mem.endsWith(u8, expected_filename, ".zip"))
        ".zip"
    else
        return false;
    if (!std.mem.endsWith(u8, path_name, extension)) return false;

    const stem = expected_filename[0 .. expected_filename.len - extension.len];
    const candidate_stem_end = path_name.len - extension.len;
    if (candidate_stem_end <= stem.len + 3) return false;

    const copy_open = candidate_stem_end - 1;
    if (path_name[copy_open] != ')') return false;

    var digit_end = copy_open;
    while (digit_end > 0 and std.ascii.isDigit(path_name[digit_end - 1])) : (digit_end -= 1) {}
    if (digit_end == 0 or digit_end == copy_open) return false;
    if (digit_end < 2 or path_name[digit_end - 1] != '(') return false;
    if (digit_end < 3 or path_name[digit_end - 2] != ' ') return false;

    const candidate_stem = path_name[0 .. digit_end - 2];
    return std.mem.eql(u8, candidate_stem, stem);
}

pub fn archiveNameMatchesPolicy(path_name: []const u8, expected_filename: []const u8) bool {
    return std.mem.eql(u8, path_name, expected_filename) or
        archiveNameHasDuplicateSuffix(path_name, expected_filename);
}

pub fn isValidSha256Hex(digest: []const u8) bool {
    if (digest.len != 64) return false;
    for (digest) |ch| {
        if (!std.ascii.isHex(ch)) return false;
    }
    return true;
}

fn expectString(value: std.json.Value) ToolchainPolicyError![]const u8 {
    return switch (value) {
        .string => |text| text,
        else => ToolchainPolicyError.InvalidPolicyField,
    };
}

fn expectBool(value: std.json.Value) ToolchainPolicyError!bool {
    return switch (value) {
        .bool => |flag| flag,
        else => ToolchainPolicyError.InvalidPolicyField,
    };
}

fn expectStringArray(allocator: std.mem.Allocator, value: std.json.Value) ToolchainPolicyError![]const []const u8 {
    const items = switch (value) {
        .array => |array| array.items,
        else => return ToolchainPolicyError.InvalidPolicyField,
    };
    if (items.len == 0) return ToolchainPolicyError.InvalidPolicyField;
    const copied = try allocator.alloc([]const u8, items.len);
    errdefer allocator.free(copied);
    for (items, 0..) |item, index| {
        const text = try expectString(item);
        if (text.len == 0) return ToolchainPolicyError.InvalidPolicyField;
        copied[index] = try allocator.dupe(u8, text);
    }
    return copied;
}

pub fn loadPolicyFromJson(
    allocator: std.mem.Allocator,
    json_bytes: []const u8,
) ToolchainPolicyError!ToolchainPolicy {
    const parsed = std.json.parseFromSlice(std.json.Value, allocator, json_bytes, .{}) catch return ToolchainPolicyError.InvalidPolicyField;
    defer parsed.deinit();

    const root = switch (parsed.value) {
        .object => |object| object,
        else => return ToolchainPolicyError.InvalidPolicyField,
    };

    const phase = try expectString(root.get("phase") orelse return ToolchainPolicyError.InvalidPolicyField);
    const channel = try expectString(root.get("channel") orelse return ToolchainPolicyError.InvalidPolicyField);
    const minimum_version = try expectString(root.get("minimum_version") orelse return ToolchainPolicyError.InvalidPolicyField);
    if (phase.len == 0 or channel.len == 0 or minimum_version.len == 0) {
        return ToolchainPolicyError.InvalidPolicyField;
    }

    _ = try parseZigVersion(channel);
    _ = try parseZigVersion(minimum_version);

    const archive_object = switch (root.get("archive_sha256") orelse return ToolchainPolicyError.InvalidPolicyField) {
        .object => |object| object,
        else => return ToolchainPolicyError.InvalidPolicyField,
    };
    if (archive_object.count() == 0) return ToolchainPolicyError.InvalidPolicyField;

    var archive_sha256 = std.StringArrayHashMapUnmanaged([]const u8){};
    errdefer {
        var cleanup_it = archive_sha256.iterator();
        while (cleanup_it.next()) |entry| {
            allocator.free(entry.key_ptr.*);
            allocator.free(entry.value_ptr.*);
        }
        archive_sha256.deinit(allocator);
    }

    var archive_it = archive_object.iterator();
    while (archive_it.next()) |entry| {
        const target = entry.key_ptr.*;
        if (target.len == 0) return ToolchainPolicyError.InvalidPolicyField;
        const digest = try expectString(entry.value_ptr.*);
        if (!isValidSha256Hex(digest)) return ToolchainPolicyError.InvalidPolicyField;
        const gop = try archive_sha256.getOrPut(allocator, try allocator.dupe(u8, target));
        if (gop.found_existing) return ToolchainPolicyError.DuplicatePolicyKey;
        gop.value_ptr.* = try allocator.dupe(u8, digest);
    }

    const upgrade_policy_value = root.get("upgrade_policy") orelse return ToolchainPolicyError.InvalidPolicyField;
    const upgrade_policy_object = switch (upgrade_policy_value) {
        .object => |object| object,
        else => return ToolchainPolicyError.InvalidPolicyField,
    };

    const lockstep = try expectBool(upgrade_policy_object.get("channel_minimum_lockstep") orelse return ToolchainPolicyError.InvalidPolicyField);
    const archive_target_scope = try expectStringArray(allocator, upgrade_policy_object.get("archive_target_scope") orelse return ToolchainPolicyError.InvalidPolicyField);
    errdefer freeStringArray(allocator, archive_target_scope);
    const required_make_routes = try expectStringArray(allocator, upgrade_policy_object.get("required_make_routes") orelse return ToolchainPolicyError.InvalidPolicyField);
    errdefer freeStringArray(allocator, required_make_routes);

    var scope_seen = std.StringArrayHashMapUnmanaged(void){};
    defer scope_seen.deinit(allocator);
    for (archive_target_scope) |target| {
        const gop = try scope_seen.getOrPut(allocator, target);
        if (gop.found_existing) return ToolchainPolicyError.DuplicatePolicyKey;
        if (archive_sha256.get(target) == null) return ToolchainPolicyError.ArchiveTargetMismatch;
    }

    var extra_it = archive_sha256.iterator();
    while (extra_it.next()) |entry| {
        if (scope_seen.get(entry.key_ptr.*) == null) return ToolchainPolicyError.ArchiveTargetMismatch;
    }

    var route_seen = std.StringArrayHashMapUnmanaged(void){};
    defer route_seen.deinit(allocator);
    for (required_make_routes) |route| {
        const gop = try route_seen.getOrPut(allocator, route);
        if (gop.found_existing) return ToolchainPolicyError.DuplicatePolicyKey;
    }

    if (lockstep and !std.mem.eql(u8, minimum_version, channel)) {
        return ToolchainPolicyError.ChannelLockstepMismatch;
    }

    return .{
        .phase = try allocator.dupe(u8, phase),
        .channel = try allocator.dupe(u8, channel),
        .minimum_version = try allocator.dupe(u8, minimum_version),
        .archive_sha256 = archive_sha256,
        .upgrade_policy = .{
            .channel_minimum_lockstep = lockstep,
            .archive_target_scope = archive_target_scope,
            .required_make_routes = required_make_routes,
        },
    };
}

fn freeStringArray(allocator: std.mem.Allocator, items: []const []const u8) void {
    for (items) |item| allocator.free(item);
    allocator.free(items);
}

pub fn freePolicy(allocator: std.mem.Allocator, policy: *ToolchainPolicy) void {
    allocator.free(policy.phase);
    allocator.free(policy.channel);
    allocator.free(policy.minimum_version);
    var it = policy.archive_sha256.iterator();
    while (it.next()) |entry| {
        allocator.free(entry.key_ptr.*);
        allocator.free(entry.value_ptr.*);
    }
    policy.archive_sha256.deinit(allocator);
    freeStringArray(allocator, policy.upgrade_policy.archive_target_scope);
    freeStringArray(allocator, policy.upgrade_policy.required_make_routes);
}

test "parseZigVersion accepts release and dev builds" {
    const release = try parseZigVersion("0.16.0");
    try std.testing.expectEqual(@as(u32, 0), release.major);
    try std.testing.expectEqual(@as(u32, 16), release.minor);
    try std.testing.expectEqual(@as(u8, 1), release.release_rank);
    try std.testing.expectEqual(@as(u32, 0), release.dev_build);

    const dev = try parseZigVersion("0.17.0-dev.877+a3ae499dc");
    try std.testing.expectEqual(@as(u32, 877), dev.dev_build);
    try std.testing.expectEqual(@as(u8, 0), dev.release_rank);
}

test "parseZigVersion rejects malformed strings" {
    try std.testing.expectError(ToolchainPolicyError.UnsupportedVersion, parseZigVersion("not-a-version"));
    try std.testing.expectError(ToolchainPolicyError.UnsupportedVersion, parseZigVersion("0.17"));
}

test "evaluateToolchainVersion classifies present too_old and not_pinned" {
    const present = try evaluateToolchainVersion(
        "0.17.0-dev.877+a3ae499dc",
        "0.17.0-dev.877+a3ae499dc",
        "0.17.0-dev.877+a3ae499dc",
    );
    try std.testing.expectEqual(ToolchainStatus.present, present.status);
    try std.testing.expect(present.note == null);

    const too_old = try evaluateToolchainVersion(
        "0.16.0",
        "0.17.0-dev.877+a3ae499dc",
        null,
    );
    try std.testing.expectEqual(ToolchainStatus.too_old, too_old.status);

    const not_pinned = try evaluateToolchainVersion(
        "0.17.0-dev.877+stalehash",
        "0.17.0-dev.877+a3ae499dc",
        "0.17.0-dev.877+a3ae499dc",
    );
    try std.testing.expectEqual(ToolchainStatus.not_pinned, not_pinned.status);
    try std.testing.expect(not_pinned.note != null);
}

test "archive duplicate suffix detection stays exact" {
    const expected = "zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz";
    try std.testing.expect(archiveNameMatchesPolicy(expected, expected));
    try std.testing.expect(archiveNameMatchesPolicy(
        "zig-x86_64-linux-0.17.0-dev.877+a3ae499dc (1).tar.xz",
        expected,
    ));
    try std.testing.expect(!archiveNameMatchesPolicy("zig-x86_64-linux-other.tar.xz", expected));

    const windows_expected = "zig-x86_64-windows-0.17.0-dev.1415+64dfaa568.zip";
    try std.testing.expect(archiveNameMatchesPolicy(windows_expected, windows_expected));
    try std.testing.expect(archiveNameMatchesPolicy(
        "zig-x86_64-windows-0.17.0-dev.1415+64dfaa568 (1).zip",
        windows_expected,
    ));
}

test "loadPolicyFromJson validates live policy shape" {
    const json = @embedFile("zig-toolchain-policy.json");
    var policy = try loadPolicyFromJson(std.testing.allocator, json);
    defer freePolicy(std.testing.allocator, &policy);

    try std.testing.expectEqualStrings("Phase 2", policy.phase);
    try std.testing.expect(policy.upgrade_policy.channel_minimum_lockstep);
    try std.testing.expectEqual(@as(usize, 2), policy.upgrade_policy.archive_target_scope.len);
    try std.testing.expectEqualStrings("x86_64-linux", policy.upgrade_policy.archive_target_scope[0]);
    try std.testing.expectEqualStrings("x86_64-windows", policy.upgrade_policy.archive_target_scope[1]);

    var filename_buffer: [128]u8 = undefined;
    const linux_filename = try policyArchiveFilename("x86_64-linux", policy.channel, &filename_buffer);
    try std.testing.expect(std.mem.startsWith(u8, linux_filename, "zig-x86_64-linux-"));
    try std.testing.expect(std.mem.endsWith(u8, linux_filename, ".tar.xz"));

    var windows_filename_buffer: [128]u8 = undefined;
    const windows_filename = try policyArchiveFilename("x86_64-windows", policy.channel, &windows_filename_buffer);
    try std.testing.expect(std.mem.startsWith(u8, windows_filename, "zig-x86_64-windows-"));
    try std.testing.expect(std.mem.endsWith(u8, windows_filename, ".zip"));
    try std.testing.expectEqual(@as(usize, 64), policy.archive_sha256.get("x86_64-windows").?.len);
}
