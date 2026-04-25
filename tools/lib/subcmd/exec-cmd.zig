const std = @import("std");

pub const Config = struct {
    exec_name: []const u8,
    prefix: []const u8,
    exec_path: []const u8,
    exec_path_env: []const u8,
};

pub const ExtractArgv0Result = struct {
    argv0_path: ?[]u8,
    command_name: []const u8,

    pub fn deinit(self: *ExtractArgv0Result, allocator: std.mem.Allocator) void {
        if (self.argv0_path) |path| {
            allocator.free(path);
        }
        self.* = undefined;
    }
};

pub fn isAbsolutePath(path: []const u8) bool {
    return path.len != 0 and path[0] == '/';
}

pub fn systemPath(allocator: std.mem.Allocator, config: Config, path: []const u8) ![]u8 {
    if (isAbsolutePath(path)) {
        return allocator.dupe(u8, path);
    }

    return std.fmt.allocPrint(allocator, "{s}/{s}", .{ config.prefix, path });
}

pub fn extractArgv0Path(allocator: std.mem.Allocator, argv0: ?[]const u8) !?ExtractArgv0Result {
    const text = argv0 orelse return null;
    if (text.len == 0) {
        return null;
    }

    if (std.mem.lastIndexOfScalar(u8, text, '/')) |slash| {
        return .{
            .argv0_path = try allocator.dupe(u8, text[0..slash]),
            .command_name = text[slash + 1 ..],
        };
    }

    return .{
        .argv0_path = null,
        .command_name = text,
    };
}

pub fn makeNonrelativePath(allocator: std.mem.Allocator, cwd: []const u8, path: []const u8) ![]u8 {
    if (isAbsolutePath(path)) {
        return allocator.dupe(u8, path);
    }

    if (cwd.len == 0) {
        return error.MissingCurrentWorkingDirectory;
    }

    return std.fmt.allocPrint(allocator, "{s}/{s}", .{ cwd, path });
}

pub fn getArgvExecPath(
    allocator: std.mem.Allocator,
    config: Config,
    explicit_exec_path: ?[]const u8,
    env_exec_path: ?[]const u8,
) ![]u8 {
    if (explicit_exec_path) |path| {
        return allocator.dupe(u8, path);
    }

    if (env_exec_path) |path| {
        if (path.len != 0) {
            return allocator.dupe(u8, path);
        }
    }

    return systemPath(allocator, config, config.exec_path);
}

fn appendPathEntry(
    builder: *std.ArrayList(u8),
    allocator: std.mem.Allocator,
    cwd: []const u8,
    path: []const u8,
) !void {
    if (path.len == 0) {
        return;
    }

    const normalized = try makeNonrelativePath(allocator, cwd, path);
    defer allocator.free(normalized);

    if (builder.items.len != 0) {
        try builder.append(allocator, ':');
    }
    try builder.appendSlice(allocator, normalized);
}

pub fn buildSearchPath(
    allocator: std.mem.Allocator,
    cwd: []const u8,
    argv_exec_path: []const u8,
    argv0_path: ?[]const u8,
    old_path: ?[]const u8,
) ![]u8 {
    var builder = std.ArrayList(u8).empty;
    errdefer builder.deinit(allocator);

    try appendPathEntry(&builder, allocator, cwd, argv_exec_path);
    if (argv0_path) |path| {
        try appendPathEntry(&builder, allocator, cwd, path);
    }

    const tail = old_path orelse "/usr/local/bin:/usr/bin:/bin";
    if (tail.len != 0) {
        if (builder.items.len != 0) {
            try builder.append(allocator, ':');
        }
        try builder.appendSlice(allocator, tail);
    }

    return builder.toOwnedSlice(allocator);
}

pub fn prepareExecCmd(
    allocator: std.mem.Allocator,
    config: Config,
    argv: []const []const u8,
) ![]const ?[]const u8 {
    var nargv = try allocator.alloc(?[]const u8, argv.len + 2);
    nargv[0] = config.exec_name;
    for (argv, 0..) |arg, index| {
        nargv[index + 1] = arg;
    }
    nargv[argv.len + 1] = null;
    return nargv;
}

test "systemPath and getArgvExecPath preserve C-style precedence" {
    const config = Config{
        .exec_name = "perf",
        .prefix = "/usr/libexec/perf-core",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    const absolute = try systemPath(std.testing.allocator, config, "/opt/perf/bin");
    defer std.testing.allocator.free(absolute);
    try std.testing.expectEqualStrings("/opt/perf/bin", absolute);

    const relative = try systemPath(std.testing.allocator, config, "libexec/perf-core");
    defer std.testing.allocator.free(relative);
    try std.testing.expectEqualStrings("/usr/libexec/perf-core/libexec/perf-core", relative);

    const explicit = try getArgvExecPath(std.testing.allocator, config, "/tmp/perf", "/ignored");
    defer std.testing.allocator.free(explicit);
    try std.testing.expectEqualStrings("/tmp/perf", explicit);

    const from_env = try getArgvExecPath(std.testing.allocator, config, null, "/env/perf");
    defer std.testing.allocator.free(from_env);
    try std.testing.expectEqualStrings("/env/perf", from_env);

    const fallback = try getArgvExecPath(std.testing.allocator, config, null, "");
    defer std.testing.allocator.free(fallback);
    try std.testing.expectEqualStrings("/usr/libexec/perf-core/libexec/perf-core", fallback);
}

test "extractArgv0Path splits command names from directory prefixes" {
    var extracted = (try extractArgv0Path(std.testing.allocator, "/tmp/perf")) orelse unreachable;
    defer extracted.deinit(std.testing.allocator);
    try std.testing.expectEqualStrings("/tmp", extracted.argv0_path.?);
    try std.testing.expectEqualStrings("perf", extracted.command_name);

    var bare = (try extractArgv0Path(std.testing.allocator, "perf")) orelse unreachable;
    defer bare.deinit(std.testing.allocator);
    try std.testing.expectEqual(@as(?[]u8, null), bare.argv0_path);
    try std.testing.expectEqualStrings("perf", bare.command_name);

    try std.testing.expectEqual(@as(?ExtractArgv0Result, null), try extractArgv0Path(std.testing.allocator, ""));
}

test "buildSearchPath rewrites relative entries against the working directory" {
    const built = try buildSearchPath(
        std.testing.allocator,
        "/work/tree",
        "tools/bin",
        "scripts",
        "/usr/bin:/bin",
    );
    defer std.testing.allocator.free(built);

    try std.testing.expectEqualStrings(
        "/work/tree/tools/bin:/work/tree/scripts:/usr/bin:/bin",
        built,
    );

    const fallback = try buildSearchPath(
        std.testing.allocator,
        "/work/tree",
        "/opt/perf/bin",
        null,
        null,
    );
    defer std.testing.allocator.free(fallback);
    try std.testing.expectEqualStrings(
        "/opt/perf/bin:/usr/local/bin:/usr/bin:/bin",
        fallback,
    );
}

test "prepareExecCmd prepends the configured executable name and preserves a trailing null slot" {
    const config = Config{
        .exec_name = "perf",
        .prefix = "/unused",
        .exec_path = "unused",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    const prepared = try prepareExecCmd(
        std.testing.allocator,
        config,
        &[_][]const u8{ "status", "--help" },
    );
    defer std.testing.allocator.free(prepared);

    try std.testing.expectEqual(@as(usize, 4), prepared.len);
    try std.testing.expectEqualStrings("perf", prepared[0].?);
    try std.testing.expectEqualStrings("status", prepared[1].?);
    try std.testing.expectEqualStrings("--help", prepared[2].?);
    try std.testing.expectEqual(@as(?[]const u8, null), prepared[3]);
}

test "prepareExecCmd keeps the null terminator even when no subcommand args are present" {
    const config = Config{
        .exec_name = "perf",
        .prefix = "/unused",
        .exec_path = "unused",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    const prepared = try prepareExecCmd(std.testing.allocator, config, &.{});
    defer std.testing.allocator.free(prepared);

    try std.testing.expectEqual(@as(usize, 2), prepared.len);
    try std.testing.expectEqualStrings("perf", prepared[0].?);
    try std.testing.expectEqual(@as(?[]const u8, null), prepared[1]);
}
