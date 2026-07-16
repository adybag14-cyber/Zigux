const std = @import("std");
const builtin = @import("builtin");
const Io = std.Io;
const policy = @import("toolchain_policy.zig");

pub const ResolverError = error{
    InvalidArgument,
    AmbiguousArchive,
    OutOfMemory,
};

pub const ArchiveValidation = struct {
    status: []const u8,
    note: ?[]const u8,
    expected_sha: []const u8,
    actual_sha: []const u8,
};

pub const ResolvedArchive = struct {
    target: ?[]const u8,
    path: ?[]const u8,
};

fn dupePath(allocator: std.mem.Allocator, path: []const u8) ![]const u8 {
    return allocator.dupe(u8, path);
}

fn appendUnique(allocator: std.mem.Allocator, list: *std.ArrayList([]const u8), path: []const u8) !void {
    for (list.items) |existing| {
        if (std.mem.eql(u8, existing, path)) return;
    }
    try list.append(allocator, try dupePath(allocator, path));
}

fn trimTrailingSeparators(path: []const u8) []const u8 {
    var end = path.len;
    while (end > 0 and (path[end - 1] == '/' or path[end - 1] == '\\')) : (end -= 1) {}
    return path[0..end];
}

fn parentPath(allocator: std.mem.Allocator, path: []const u8) ?[]const u8 {
    const trimmed = trimTrailingSeparators(path);
    const sep = std.mem.lastIndexOfAny(u8, trimmed, "/\\") orelse return null;
    if (sep == 0) return allocator.dupe(u8, "/") catch null;
    return allocator.dupe(u8, trimmed[0..sep]) catch null;
}

pub fn iterZigSearchRoots(allocator: std.mem.Allocator, root: []const u8) ![]const []const u8 {
    var list: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (list.items) |item| allocator.free(item);
        list.deinit(allocator);
    }

    const local_roots = [_][]const u8{
        ".zig-toolchain",
        "toolchains",
        ".toolchains",
    };
    for (local_roots) |suffix| {
        const joined = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, suffix });
        defer allocator.free(joined);
        try appendUnique(allocator, &list, joined);
    }

    var current = try dupePath(allocator, root);
    defer allocator.free(current);
    while (current.len > 0) {
        const parent = parentPath(allocator, current) orelse break;
        defer allocator.free(parent);
        for (&[_][]const u8{ ".toolchains", "toolchains" }) |suffix| {
            const joined = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ parent, suffix });
            defer allocator.free(joined);
            try appendUnique(allocator, &list, joined);
        }
        allocator.free(current);
        current = try dupePath(allocator, parent);
    }

    return try list.toOwnedSlice(allocator);
}

pub fn iterArchiveSearchRoots(allocator: std.mem.Allocator, root: []const u8) ![]const []const u8 {
    var list: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (list.items) |item| allocator.free(item);
        list.deinit(allocator);
    }

    const local_roots = [_][]const u8{
        ".zig-toolchain",
        "toolchains",
        ".toolchains",
        "third_party",
        "agent_files",
    };
    for (local_roots) |suffix| {
        const joined = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, suffix });
        defer allocator.free(joined);
        try appendUnique(allocator, &list, joined);
    }

    var current = try dupePath(allocator, root);
    defer allocator.free(current);
    while (current.len > 0) {
        const parent = parentPath(allocator, current) orelse break;
        defer allocator.free(parent);
        for (&[_][]const u8{ ".toolchains", "toolchains", "agent_files" }) |suffix| {
            const joined = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ parent, suffix });
            defer allocator.free(joined);
            try appendUnique(allocator, &list, joined);
        }
        allocator.free(current);
        current = try dupePath(allocator, parent);
    }

    return try list.toOwnedSlice(allocator);
}

pub fn formatSearchRoots(allocator: std.mem.Allocator, roots: []const []const u8) ![]const u8 {
    if (roots.len == 0) return try allocator.dupe(u8, "");
    var buffer: std.ArrayList(u8) = .empty;
    defer buffer.deinit(allocator);
    for (roots, 0..) |root, index| {
        if (index != 0) try buffer.append(allocator, ',');
        try buffer.appendSlice(allocator, root);
    }
    return try buffer.toOwnedSlice(allocator);
}

pub fn freeSearchRoots(allocator: std.mem.Allocator, roots: []const []const u8) void {
    for (roots) |root| allocator.free(root);
    allocator.free(roots);
}

fn pathExists(io: Io, path: []const u8) bool {
    std.Io.Dir.cwd().access(io, path, .{}) catch return false;
    return true;
}

pub fn pathIsFile(io: Io, path: []const u8) bool {
    var file = std.Io.Dir.cwd().openFile(io, path, .{}) catch return false;
    file.close(io);
    return true;
}

fn pathIsDir(io: Io, path: []const u8) bool {
    var dir = std.Io.Dir.cwd().openDir(io, path, .{}) catch return false;
    dir.close(io);
    return true;
}

pub fn computeSha256Hex(io: Io, allocator: std.mem.Allocator, path: []const u8) ![]const u8 {
    var file = try std.Io.Dir.cwd().openFile(io, path, .{});
    defer file.close(io);

    var hasher = std.crypto.hash.sha2.Sha256.init(.{});
    var buffer: [1024 * 1024]u8 = undefined;
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
    return try std.fmt.allocPrint(allocator, "{s}", .{std.fmt.bytesToHex(&digest, .lower)});
}

pub fn expectedArchiveMetadata(
    loaded: *const policy.ToolchainPolicy,
    archive_target: []const u8,
    filename_buffer: []u8,
) !struct { expected_sha: []const u8, expected_filename: []const u8 } {
    const digest = loaded.archive_sha256.get(archive_target) orelse return ResolverError.InvalidArgument;
    const filename = try policy.policyArchiveFilename(archive_target, loaded.channel, filename_buffer);
    return .{ .expected_sha = digest, .expected_filename = filename };
}

pub fn validatePolicyArchive(
    io: Io,
    allocator: std.mem.Allocator,
    loaded: *const policy.ToolchainPolicy,
    path: []const u8,
    archive_target: []const u8,
    file_name: []const u8,
) !ArchiveValidation {
    var filename_buffer: [160]u8 = undefined;
    const meta = try expectedArchiveMetadata(loaded, archive_target, &filename_buffer);
    const actual_sha = try computeSha256Hex(io, allocator, path);

    if (!policy.archiveNameMatchesPolicy(file_name, meta.expected_filename)) {
        return .{
            .status = "mismatch",
            .note = try std.fmt.allocPrint(
                allocator,
                "expected archive filename {s} for {s}, got {s}",
                .{ meta.expected_filename, archive_target, file_name },
            ),
            .expected_sha = try dupePath(allocator, meta.expected_sha),
            .actual_sha = actual_sha,
        };
    }

    if (!std.mem.eql(u8, actual_sha, meta.expected_sha)) {
        return .{
            .status = "mismatch",
            .note = try std.fmt.allocPrint(
                allocator,
                "expected sha256 {s} for {s}, got {s}",
                .{ meta.expected_sha, archive_target, actual_sha },
            ),
            .expected_sha = try dupePath(allocator, meta.expected_sha),
            .actual_sha = actual_sha,
        };
    }

    return .{
        .status = "present",
        .note = null,
        .expected_sha = try dupePath(allocator, meta.expected_sha),
        .actual_sha = actual_sha,
    };
}

pub fn freeArchiveValidation(allocator: std.mem.Allocator, validation: ArchiveValidation) void {
    if (validation.note) |note| allocator.free(note);
    allocator.free(validation.expected_sha);
    allocator.free(validation.actual_sha);
}

const ArchiveCandidate = struct {
    target: []const u8,
    path: []const u8,
};

fn scanArchiveCandidates(
    io: Io,
    allocator: std.mem.Allocator,
    loaded: *const policy.ToolchainPolicy,
    root: []const u8,
) ![]ArchiveCandidate {
    var candidates: std.ArrayList(ArchiveCandidate) = .empty;
    errdefer {
        for (candidates.items) |candidate| {
            allocator.free(candidate.target);
            allocator.free(candidate.path);
        }
        candidates.deinit(allocator);
    }

    const search_roots = try iterArchiveSearchRoots(allocator, root);
    defer freeSearchRoots(allocator, search_roots);

    var filename_buffer: [160]u8 = undefined;
    for (loaded.upgrade_policy.archive_target_scope) |target| {
        const expected_filename = try policy.policyArchiveFilename(target, loaded.channel, &filename_buffer);
        for (search_roots) |base| {
            const direct = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ base, expected_filename });
            defer allocator.free(direct);
            if (pathIsFile(io, direct)) {
                try candidates.append(allocator, .{
                    .target = try dupePath(allocator, target),
                    .path = try dupePath(allocator, direct),
                });
            }

            if (!pathIsDir(io, base)) continue;
            var base_dir = try std.Io.Dir.cwd().openDir(io, base, .{ .iterate = true });
            defer base_dir.close(io);
            var iter = base_dir.iterate();
            while (try iter.next(io)) |entry| {
                if (!policy.archiveNameHasDuplicateSuffix(entry.name, expected_filename)) continue;
                const child_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ base, entry.name });
                defer allocator.free(child_path);
                if (!pathIsFile(io, child_path)) continue;
                try candidates.append(allocator, .{
                    .target = try dupePath(allocator, target),
                    .path = try dupePath(allocator, child_path),
                });
            }
        }
    }

    return try candidates.toOwnedSlice(allocator);
}

fn freeArchiveCandidates(allocator: std.mem.Allocator, candidates: []ArchiveCandidate) void {
    for (candidates) |candidate| {
        allocator.free(candidate.target);
        allocator.free(candidate.path);
    }
    allocator.free(candidates);
}

pub fn resolvePolicyArchive(
    io: Io,
    allocator: std.mem.Allocator,
    loaded: *const policy.ToolchainPolicy,
    root: []const u8,
    explicit_archive: ?[]const u8,
    explicit_target: ?[]const u8,
) !ResolvedArchive {
    if (explicit_archive) |archive| {
        var target = explicit_target;
        if (target == null and loaded.upgrade_policy.archive_target_scope.len == 1) {
            target = loaded.upgrade_policy.archive_target_scope[0];
        }
        if (target == null) return ResolverError.InvalidArgument;
        if (explicit_target) |chosen| {
            var found = false;
            for (loaded.upgrade_policy.archive_target_scope) |scope_target| {
                if (std.mem.eql(u8, scope_target, chosen)) found = true;
            }
            if (!found) return ResolverError.InvalidArgument;
        }
        return .{
            .target = try dupePath(allocator, target.?),
            .path = try dupePath(allocator, archive),
        };
    }

    const candidates = try scanArchiveCandidates(io, allocator, loaded, root);
    defer freeArchiveCandidates(allocator, candidates);

    var filtered: std.ArrayList(ArchiveCandidate) = .empty;
    defer {
        for (filtered.items) |candidate| {
            allocator.free(candidate.target);
            allocator.free(candidate.path);
        }
        filtered.deinit(allocator);
    }

    for (candidates) |candidate| {
        if (!pathIsFile(io, candidate.path)) continue;
        if (explicit_target) |chosen| {
            if (!std.mem.eql(u8, candidate.target, chosen)) continue;
        }
        try filtered.append(allocator, .{
            .target = try dupePath(allocator, candidate.target),
            .path = try dupePath(allocator, candidate.path),
        });
    }

    if (filtered.items.len > 1) return ResolverError.AmbiguousArchive;
    if (filtered.items.len == 1) {
        return .{
            .target = try dupePath(allocator, filtered.items[0].target),
            .path = try dupePath(allocator, filtered.items[0].path),
        };
    }

    const fallback_target = if (explicit_target) |chosen|
        chosen
    else if (loaded.upgrade_policy.archive_target_scope.len == 1)
        loaded.upgrade_policy.archive_target_scope[0]
    else
        null;

    return .{
        .target = if (fallback_target) |target| try dupePath(allocator, target) else null,
        .path = null,
    };
}

pub fn freeResolvedArchive(allocator: std.mem.Allocator, resolved: ResolvedArchive) void {
    if (resolved.target) |target| allocator.free(target);
    if (resolved.path) |path| allocator.free(path);
}

fn appendZigCandidate(
    allocator: std.mem.Allocator,
    list: *std.ArrayList([]const u8),
    base: []const u8,
) !void {
    inline for (.{ "zig", "zig.exe", "bin/zig", "bin/zig.exe" }) |relative| {
        const candidate = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ base, relative });
        defer allocator.free(candidate);
        try appendUnique(allocator, list, candidate);
    }
}

pub fn hostArchiveTarget() ?[]const u8 {
    return switch (builtin.cpu.arch) {
        .x86_64 => switch (builtin.os.tag) {
            .linux => "x86_64-linux",
            .windows => "x86_64-windows",
            .macos => "x86_64-macos",
            else => null,
        },
        .aarch64 => switch (builtin.os.tag) {
            .linux => "aarch64-linux",
            .windows => "aarch64-windows",
            .macos => "aarch64-macos",
            else => null,
        },
        else => null,
    };
}

pub fn iterRepoLocalZigCandidates(
    io: Io,
    allocator: std.mem.Allocator,
    root: []const u8,
    pinned_channel: ?[]const u8,
) ![]const []const u8 {
    _ = io;
    var list: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (list.items) |item| allocator.free(item);
        list.deinit(allocator);
    }

    const search_roots = try iterZigSearchRoots(allocator, root);
    defer freeSearchRoots(allocator, search_roots);

    if (pinned_channel) |channel| {
        if (hostArchiveTarget()) |target| {
            for (search_roots) |base| {
                const pinned_dir = try std.fmt.allocPrint(allocator, "{s}/zig-{s}-{s}", .{ base, target, channel });
                defer allocator.free(pinned_dir);
                try appendZigCandidate(allocator, &list, pinned_dir);
            }
        }
    }

    for (search_roots) |base| {
        try appendZigCandidate(allocator, &list, base);
    }

    return try list.toOwnedSlice(allocator);
}

pub fn resolveZigExecutable(
    io: Io,
    allocator: std.mem.Allocator,
    root: []const u8,
    explicit_zig: ?[]const u8,
    pinned_channel: ?[]const u8,
) !?[]const u8 {
    if (explicit_zig) |zig| {
        if (!pathExists(io, zig)) return ResolverError.InvalidArgument;
        if (pathIsDir(io, zig)) return ResolverError.InvalidArgument;
        return try dupePath(allocator, zig);
    }

    const candidates = try iterRepoLocalZigCandidates(io, allocator, root, pinned_channel);
    defer {
        for (candidates) |candidate| allocator.free(candidate);
        allocator.free(candidates);
    }
    for (candidates) |candidate| {
        if (pathIsFile(io, candidate)) return try dupePath(allocator, candidate);
    }

    const path_zig = try allocator.dupe(u8, "zig");
    const probe = std.process.run(allocator, io, .{
        .argv = &.{ path_zig, "version" },
        .stdout_limit = .limited(256),
        .stderr_limit = .limited(256),
    }) catch {
        allocator.free(path_zig);
        return null;
    };
    defer allocator.free(probe.stdout);
    defer allocator.free(probe.stderr);
    switch (probe.term) {
        .exited => |code| if (code == 0 and probe.stdout.len > 0) return path_zig,
        else => {},
    }
    allocator.free(path_zig);
    return null;
}

pub fn readZigVersion(io: Io, allocator: std.mem.Allocator, zig: []const u8) ![]const u8 {
    const result = std.process.run(allocator, io, .{
        .argv = &.{ zig, "version" },
        .stdout_limit = .limited(256),
        .stderr_limit = .limited(256),
    }) catch |err| switch (err) {
        error.FileNotFound,
        error.AccessDenied,
        error.PermissionDenied,
        error.InvalidExe,
        error.IsDir,
        error.NotDir,
        => return ResolverError.InvalidArgument,
        else => return err,
    };
    defer allocator.free(result.stderr);

    switch (result.term) {
        .exited => |code| if (code != 0) return ResolverError.InvalidArgument,
        else => return ResolverError.InvalidArgument,
    }
    if (result.stdout.len == 0) return ResolverError.InvalidArgument;
    const trimmed = std.mem.trim(u8, result.stdout, " \t\r\n");
    return try dupePath(allocator, trimmed);
}

pub fn toolchainStatusName(status: policy.ToolchainStatus) []const u8 {
    return switch (status) {
        .present => "present",
        .too_old => "too_old",
        .not_pinned => "not_pinned",
    };
}

pub fn describeInvalidExplicitArchivePath(io: Io, allocator: std.mem.Allocator, path: []const u8) !?[]const u8 {
    if (!pathExists(io, path)) return null;
    if (pathIsDir(io, path)) {
        return try std.fmt.allocPrint(
            allocator,
            "explicit archive path is a directory, expected a regular file: {s}",
            .{path},
        );
    }
    if (!pathIsFile(io, path)) {
        return try std.fmt.allocPrint(
            allocator,
            "explicit archive path is not a regular file: {s}",
            .{path},
        );
    }
    return null;
}

pub const MissingArchiveDiagnostic = struct {
    message: []const u8,
    search_roots_summary: ?[]const u8,
};

pub fn describeMissingArchive(
    allocator: std.mem.Allocator,
    archive_path: ?[]const u8,
    explicit_archive: ?[]const u8,
    search_roots: []const []const u8,
) !MissingArchiveDiagnostic {
    if (explicit_archive != null) {
        const resolved = archive_path orelse explicit_archive.?;
        return .{
            .message = try std.fmt.allocPrint(
                allocator,
                "explicit archive path does not exist: {s}",
                .{resolved},
            ),
            .search_roots_summary = null,
        };
    }
    const formatted = try formatSearchRoots(allocator, search_roots);
    return .{
        .message = try allocator.dupe(u8, "pinned Zig archive not found in archive search roots"),
        .search_roots_summary = formatted,
    };
}

pub fn freeMissingArchiveDiagnostic(allocator: std.mem.Allocator, diagnostic: MissingArchiveDiagnostic) void {
    allocator.free(diagnostic.message);
    if (diagnostic.search_roots_summary) |summary| allocator.free(summary);
}

pub const MissingZigDiagnostic = struct {
    message: []const u8,
    search_roots_summary: []const u8,
};

pub fn describeMissingZig(
    allocator: std.mem.Allocator,
    pinned_channel: ?[]const u8,
    search_roots: []const []const u8,
) !MissingZigDiagnostic {
    const formatted = try formatSearchRoots(allocator, search_roots);
    if (pinned_channel) |channel| {
        return .{
            .message = try std.fmt.allocPrint(
                allocator,
                "zig not found on PATH or in repo-local toolchain search roots for pinned channel {s}",
                .{channel},
            ),
            .search_roots_summary = formatted,
        };
    }
    return .{
        .message = try allocator.dupe(u8, "zig not found on PATH or in repo-local toolchain search roots"),
        .search_roots_summary = formatted,
    };
}

pub fn freeMissingZigDiagnostic(allocator: std.mem.Allocator, diagnostic: MissingZigDiagnostic) void {
    allocator.free(diagnostic.message);
    allocator.free(diagnostic.search_roots_summary);
}

pub fn formatResolvePolicyArchiveError(
    allocator: std.mem.Allocator,
    err: ResolverError,
    loaded: ?*const policy.ToolchainPolicy,
    explicit_target: ?[]const u8,
    explicit_archive: ?[]const u8,
) ![]const u8 {
    _ = explicit_archive;
    return switch (err) {
        ResolverError.AmbiguousArchive => try allocator.dupe(u8, "multiple repo-local pinned archive candidates matched"),
        ResolverError.InvalidArgument => blk: {
            if (explicit_target) |target| {
                if (loaded) |policy_loaded| {
                    for (policy_loaded.upgrade_policy.archive_target_scope) |scope_target| {
                        if (std.mem.eql(u8, scope_target, target)) {
                            break :blk try std.fmt.allocPrint(
                                allocator,
                                "archive target {s} is not pinned in policy",
                                .{target},
                            );
                        }
                    }
                    var scope_buffer: [256]u8 = undefined;
                    var scope_len: usize = 0;
                    for (policy_loaded.upgrade_policy.archive_target_scope, 0..) |scope_target, index| {
                        if (index != 0) {
                            scope_buffer[scope_len] = ',';
                            scope_len += 1;
                        }
                        const copied = try std.fmt.bufPrint(scope_buffer[scope_len..], "{s}", .{scope_target});
                        scope_len += copied.len;
                    }
                    return try std.fmt.allocPrint(
                        allocator,
                        "archive target {s} is outside archive_target_scope: {s}",
                        .{ target, scope_buffer[0..scope_len] },
                    );
                }
            }
            if (loaded) |policy_loaded| {
                if (policy_loaded.upgrade_policy.archive_target_scope.len != 1) {
                    break :blk try allocator.dupe(u8, "archive target must be explicit when policy covers multiple archive targets");
                }
            }
            break :blk try allocator.dupe(u8, "invalid archive resolution arguments");
        },
        ResolverError.OutOfMemory => try allocator.dupe(u8, "out of memory"),
    };
}

test "archive search roots include third_party and agent_files" {
    const roots = try iterArchiveSearchRoots(std.testing.allocator, ".");
    defer freeSearchRoots(std.testing.allocator, roots);
    var has_third_party = false;
    var has_agent_files = false;
    for (roots) |root| {
        if (std.mem.endsWith(u8, root, "/third_party")) has_third_party = true;
        if (std.mem.endsWith(u8, root, "/agent_files")) has_agent_files = true;
    }
    try std.testing.expect(has_third_party);
    try std.testing.expect(has_agent_files);
}

test "validate policy archive accepts live metadata shape" {
    const json = @embedFile("zig-toolchain-policy.json");
    var loaded = try policy.loadPolicyFromJson(std.testing.allocator, json);
    defer policy.freePolicy(std.testing.allocator, &loaded);
    var filename_buffer: [160]u8 = undefined;
    const meta = try expectedArchiveMetadata(&loaded, "x86_64-linux", &filename_buffer);
    try std.testing.expect(std.mem.endsWith(u8, meta.expected_filename, ".tar.xz"));
    try std.testing.expectEqual(@as(usize, 64), meta.expected_sha.len);

    var windows_filename_buffer: [160]u8 = undefined;
    const windows_meta = try expectedArchiveMetadata(&loaded, "x86_64-windows", &windows_filename_buffer);
    try std.testing.expect(std.mem.endsWith(u8, windows_meta.expected_filename, ".zip"));
    try std.testing.expectEqual(@as(usize, 64), windows_meta.expected_sha.len);
}

test "host archive target matches supported native platform" {
    const target = hostArchiveTarget() orelse return error.SkipZigTest;
    try std.testing.expect(std.mem.indexOf(u8, target, @tagName(builtin.cpu.arch)) != null);
    try std.testing.expect(std.mem.endsWith(u8, target, @tagName(builtin.os.tag)));
}
