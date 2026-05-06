const std = @import("std");

pub const Config = struct {
    exec_name: []const u8,
    prefix: []const u8,
    exec_path: []const u8,
    exec_path_env: []const u8,
};

pub const EnvMap = struct {
    allocator: std.mem.Allocator,
    values: std.StringHashMap([]u8),

    pub fn init(allocator: std.mem.Allocator) EnvMap {
        return .{
            .allocator = allocator,
            .values = std.StringHashMap([]u8).init(allocator),
        };
    }

    pub fn deinit(self: *EnvMap) void {
        var iterator = self.values.iterator();
        while (iterator.next()) |entry| {
            self.allocator.free(entry.value_ptr.*);
        }
        self.values.deinit();
        self.* = undefined;
    }

    pub fn get(self: *const EnvMap, key: []const u8) ?[]const u8 {
        return self.values.get(key);
    }

    pub fn set(self: *EnvMap, key: []const u8, value: []const u8) !void {
        const owned_value = try self.allocator.dupe(u8, value);
        errdefer self.allocator.free(owned_value);

        const entry = try self.values.getOrPut(key);
        if (entry.found_existing) {
            self.allocator.free(entry.value_ptr.*);
        }
        entry.value_ptr.* = owned_value;
    }
};

pub const ExecCmdState = struct {
    argv_exec_path: ?[]u8 = null,
    argv0_path: ?[]u8 = null,

    pub fn deinit(self: *ExecCmdState, allocator: std.mem.Allocator) void {
        if (self.argv_exec_path) |path| {
            allocator.free(path);
        }
        if (self.argv0_path) |path| {
            allocator.free(path);
        }
        self.* = undefined;
    }
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

pub const DeferredExecCall = struct {
    argv: []const ?[]const u8,

    pub fn deinit(self: *DeferredExecCall, allocator: std.mem.Allocator) void {
        allocator.free(self.argv);
        self.* = undefined;
    }
};

pub const max_execl_slots: usize = 32;
pub const CollectExeclArgsError = error{
    MissingNullTerminator,
    TooManyArguments,
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
        const argv0_path = if (slash == 0) "/" else text[0..slash];
        return .{
            .argv0_path = try allocator.dupe(u8, argv0_path),
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

pub fn sameLocation(cwd: []const u8, pwd: []const u8) bool {
    if (cwd.len == 0 or pwd.len == 0) {
        return false;
    }

    const linux = std.os.linux;
    var cwd_path_buf: [std.posix.PATH_MAX]u8 = undefined;
    var pwd_path_buf: [std.posix.PATH_MAX]u8 = undefined;

    const cwd_z = std.fmt.bufPrintZ(&cwd_path_buf, "{s}", .{cwd}) catch return false;
    const pwd_z = std.fmt.bufPrintZ(&pwd_path_buf, "{s}", .{pwd}) catch return false;

    var cwd_statx = std.mem.zeroes(linux.Statx);
    if (linux.errno(linux.statx(linux.AT.FDCWD, cwd_z, linux.AT.NO_AUTOMOUNT, .{
        .INO = true,
        .MNT_ID = true,
    }, &cwd_statx)) != .SUCCESS) {
        return false;
    }

    var pwd_statx = std.mem.zeroes(linux.Statx);
    if (linux.errno(linux.statx(linux.AT.FDCWD, pwd_z, linux.AT.NO_AUTOMOUNT, .{
        .INO = true,
        .MNT_ID = true,
    }, &pwd_statx)) != .SUCCESS) {
        return false;
    }

    return cwd_statx.mnt_id == pwd_statx.mnt_id and
        cwd_statx.ino == pwd_statx.ino and
        cwd_statx.dev_major == pwd_statx.dev_major and
        cwd_statx.dev_minor == pwd_statx.dev_minor;
}

pub fn choosePwdCwd(cwd: []const u8, pwd: ?[]const u8, same_location: bool) []const u8 {
    const pwd_value = pwd orelse return cwd;
    if (pwd_value.len == 0) {
        return cwd;
    }
    if (std.mem.eql(u8, pwd_value, cwd)) {
        return cwd;
    }
    if (same_location) {
        return pwd_value;
    }
    return cwd;
}

pub fn choosePwdCwdFromFilesystem(cwd: []const u8, pwd: ?[]const u8) []const u8 {
    const pwd_value = pwd orelse return cwd;
    if (pwd_value.len == 0) {
        return cwd;
    }
    if (std.mem.eql(u8, pwd_value, cwd)) {
        return cwd;
    }
    if (sameLocation(cwd, pwd_value)) {
        return pwd_value;
    }
    return cwd;
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

pub fn execCmdInit(env: *EnvMap, config: Config) !void {
    try env.set("PREFIX", config.prefix);
}

pub fn setArgvExecPath(
    allocator: std.mem.Allocator,
    env: *EnvMap,
    state: *ExecCmdState,
    config: Config,
    exec_path: []const u8,
) !void {
    if (state.argv_exec_path) |previous| {
        allocator.free(previous);
    }
    state.argv_exec_path = try allocator.dupe(u8, exec_path);
    try env.set(config.exec_path_env, exec_path);
}

pub fn setArgv0Path(
    allocator: std.mem.Allocator,
    state: *ExecCmdState,
    argv0_path: ?[]const u8,
) !void {
    if (state.argv0_path) |previous| {
        allocator.free(previous);
        state.argv0_path = null;
    }

    if (argv0_path) |path| {
        state.argv0_path = try allocator.dupe(u8, path);
    }
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

    try builder.appendSlice(allocator, normalized);
    try builder.append(allocator, ':');
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

    if (old_path) |tail| {
        try builder.appendSlice(allocator, tail);
    } else {
        try builder.appendSlice(allocator, "/usr/local/bin:/usr/bin:/bin");
    }
    return builder.toOwnedSlice(allocator);
}

pub fn setupPath(
    allocator: std.mem.Allocator,
    env: *EnvMap,
    state: ExecCmdState,
    config: Config,
    cwd: []const u8,
) ![]u8 {
    const argv_exec_path = try getArgvExecPath(
        allocator,
        config,
        state.argv_exec_path,
        env.get(config.exec_path_env),
    );
    defer allocator.free(argv_exec_path);

    const effective_cwd = choosePwdCwdFromFilesystem(cwd, env.get("PWD"));
    const new_path = try buildSearchPath(
        allocator,
        effective_cwd,
        argv_exec_path,
        state.argv0_path,
        env.get("PATH"),
    );
    errdefer allocator.free(new_path);

    try env.set("PATH", new_path);
    return new_path;
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

pub fn collectExeclArgs(
    allocator: std.mem.Allocator,
    cmd: []const u8,
    argv_tail: []const ?[]const u8,
) (CollectExeclArgsError || std.mem.Allocator.Error)![]const ?[]const u8 {
    var argc: usize = 1;
    var collected = std.ArrayList(?[]const u8).empty;
    errdefer collected.deinit(allocator);

    try collected.append(allocator, cmd);

    for (argv_tail) |arg| {
        argc += 1;
        if (argc >= max_execl_slots) {
            return error.TooManyArguments;
        }
        if (arg == null) {
            try collected.append(allocator, null);
            return collected.toOwnedSlice(allocator);
        }
        try collected.append(allocator, arg);
    }

    return error.MissingNullTerminator;
}

fn buildDeferredCallFromNullTerminatedArgs(
    allocator: std.mem.Allocator,
    config: Config,
    args: []const ?[]const u8,
) !DeferredExecCall {
    var deferred = try allocator.alloc(?[]const u8, args.len + 1);
    deferred[0] = config.exec_name;
    for (args, 0..) |arg, index| {
        deferred[index + 1] = arg;
    }
    return .{ .argv = deferred };
}

pub fn buildDeferredExecvCall(
    allocator: std.mem.Allocator,
    config: Config,
    argv: []const []const u8,
) !DeferredExecCall {
    return .{ .argv = try prepareExecCmd(allocator, config, argv) };
}

pub fn buildDeferredExeclCall(
    allocator: std.mem.Allocator,
    config: Config,
    cmd: []const u8,
    argv_tail: []const ?[]const u8,
) (CollectExeclArgsError || std.mem.Allocator.Error)!DeferredExecCall {
    const args = try collectExeclArgs(allocator, cmd, argv_tail);
    defer allocator.free(args);
    return buildDeferredCallFromNullTerminatedArgs(allocator, config, args);
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

    var root = (try extractArgv0Path(std.testing.allocator, "/perf")) orelse unreachable;
    defer root.deinit(std.testing.allocator);
    try std.testing.expectEqualStrings("/", root.argv0_path.?);
    try std.testing.expectEqualStrings("perf", root.command_name);

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

test "buildSearchPath preserves the C helper's trailing colon when PATH exists but is empty" {
    const built = try buildSearchPath(
        std.testing.allocator,
        "/work/tree",
        "tools/bin",
        "scripts",
        "",
    );
    defer std.testing.allocator.free(built);

    try std.testing.expectEqualStrings(
        "/work/tree/tools/bin:/work/tree/scripts:",
        built,
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

test "buildDeferredExecvCall models a pure deferred execv-style handoff" {
    const config = Config{
        .exec_name = "perf",
        .prefix = "/unused",
        .exec_path = "unused",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    var deferred = try buildDeferredExecvCall(
        std.testing.allocator,
        config,
        &[_][]const u8{ "record", "-a" },
    );
    defer deferred.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 4), deferred.argv.len);
    try std.testing.expectEqualStrings("perf", deferred.argv[0].?);
    try std.testing.expectEqualStrings("record", deferred.argv[1].?);
    try std.testing.expectEqualStrings("-a", deferred.argv[2].?);
    try std.testing.expectEqual(@as(?[]const u8, null), deferred.argv[3]);
}

test "buildDeferredExeclCall models a pure deferred execl-style handoff" {
    const config = Config{
        .exec_name = "perf",
        .prefix = "/unused",
        .exec_path = "unused",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    var deferred = try buildDeferredExeclCall(
        std.testing.allocator,
        config,
        "record",
        &[_]?[]const u8{ "-a", "--stdio", null, "--ignored" },
    );
    defer deferred.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 5), deferred.argv.len);
    try std.testing.expectEqualStrings("perf", deferred.argv[0].?);
    try std.testing.expectEqualStrings("record", deferred.argv[1].?);
    try std.testing.expectEqualStrings("-a", deferred.argv[2].?);
    try std.testing.expectEqualStrings("--stdio", deferred.argv[3].?);
    try std.testing.expectEqual(@as(?[]const u8, null), deferred.argv[4]);
}

test "buildDeferredExeclCall keeps the legacy collector guards before launch exists" {
    const config = Config{
        .exec_name = "perf",
        .prefix = "/unused",
        .exec_path = "unused",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    try std.testing.expectError(
        error.MissingNullTerminator,
        buildDeferredExeclCall(
            std.testing.allocator,
            config,
            "record",
            &[_]?[]const u8{ "-a", "--stdio" },
        ),
    );
}

test "collectExeclArgs keeps the command head and first null terminator" {
    const collected = try collectExeclArgs(
        std.testing.allocator,
        "record",
        &[_]?[]const u8{ "-a", "--call-graph", null, "--ignored" },
    );
    defer std.testing.allocator.free(collected);

    try std.testing.expectEqual(@as(usize, 4), collected.len);
    try std.testing.expectEqualStrings("record", collected[0].?);
    try std.testing.expectEqualStrings("-a", collected[1].?);
    try std.testing.expectEqualStrings("--call-graph", collected[2].?);
    try std.testing.expectEqual(@as(?[]const u8, null), collected[3]);
}

test "collectExeclArgs rejects the C helper's too-many-args shape" {
    var argv_tail: [31]?[]const u8 = undefined;
    for (argv_tail[0..30]) |*slot| {
        slot.* = "x";
    }
    argv_tail[30] = null;

    try std.testing.expectError(
        error.TooManyArguments,
        collectExeclArgs(std.testing.allocator, "record", &argv_tail),
    );
}

test "execCmdInit and setArgvExecPath propagate the expected environment keys" {
    const config = Config{
        .exec_name = "perf",
        .prefix = "/usr/libexec/perf-core",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    var env = EnvMap.init(std.testing.allocator);
    defer env.deinit();

    var state = ExecCmdState{};
    defer state.deinit(std.testing.allocator);

    try execCmdInit(&env, config);
    try std.testing.expectEqualStrings("/usr/libexec/perf-core", env.get("PREFIX").?);

    try setArgvExecPath(
        std.testing.allocator,
        &env,
        &state,
        config,
        "/tmp/perf-core",
    );
    try std.testing.expectEqualStrings("/tmp/perf-core", state.argv_exec_path.?);
    try std.testing.expectEqualStrings("/tmp/perf-core", env.get("PERF_EXEC_PATH").?);
}

test "setupPath updates PATH using stored exec path, argv0 path, and fallback defaults" {
    const config = Config{
        .exec_name = "perf",
        .prefix = "/usr/libexec/perf-core",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    var env = EnvMap.init(std.testing.allocator);
    defer env.deinit();

    var state = ExecCmdState{};
    defer state.deinit(std.testing.allocator);

    try execCmdInit(&env, config);
    try setArgvExecPath(std.testing.allocator, &env, &state, config, "tools/bin");
    try setArgv0Path(std.testing.allocator, &state, "scripts");
    try env.set("PATH", "/usr/bin:/bin");

    const updated = try setupPath(std.testing.allocator, &env, state, config, "/repo");
    defer std.testing.allocator.free(updated);

    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/repo/scripts:/usr/bin:/bin",
        updated,
    );
    try std.testing.expectEqualStrings(updated, env.get("PATH").?);

    var fallback_env = EnvMap.init(std.testing.allocator);
    defer fallback_env.deinit();
    try execCmdInit(&fallback_env, config);

    var fallback_state = ExecCmdState{};
    defer fallback_state.deinit(std.testing.allocator);
    try setArgvExecPath(std.testing.allocator, &fallback_env, &fallback_state, config, "tools/bin");

    const fallback = try setupPath(
        std.testing.allocator,
        &fallback_env,
        fallback_state,
        config,
        "/repo",
    );
    defer std.testing.allocator.free(fallback);

    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/usr/local/bin:/usr/bin:/bin",
        fallback,
    );
    try std.testing.expectEqualStrings(fallback, fallback_env.get("PATH").?);
}

test "setupPath preserves the C helper's logical PWD alias when PATH entries are relative" {
    const linux = std.os.linux;
    var root_buf: [std.posix.PATH_MAX]u8 = undefined;
    const root = try std.fmt.bufPrintZ(&root_buf, "/tmp/zigux-p8-l02-{d}", .{linux.getpid()});
    try std.testing.expectEqual(.SUCCESS, linux.errno(linux.mkdirat(linux.AT.FDCWD, root, 0o755)));
    defer _ = linux.rmdir(root);

    var repo_buf: [std.posix.PATH_MAX]u8 = undefined;
    const repo = try std.fmt.bufPrintZ(&repo_buf, "{s}/repo", .{root});
    try std.testing.expectEqual(.SUCCESS, linux.errno(linux.mkdirat(linux.AT.FDCWD, repo, 0o755)));
    defer _ = linux.rmdir(repo);

    var link_buf: [std.posix.PATH_MAX]u8 = undefined;
    const link = try std.fmt.bufPrintZ(&link_buf, "{s}/repo-link", .{root});
    try std.testing.expectEqual(.SUCCESS, linux.errno(linux.symlinkat(repo, linux.AT.FDCWD, link)));
    defer _ = linux.unlinkat(linux.AT.FDCWD, link, 0);

    const cwd = repo[0..repo.len];
    const logical_pwd = link[0..link.len];

    const config = Config{
        .exec_name = "perf",
        .prefix = "/usr/libexec/perf-core",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    var env = EnvMap.init(std.testing.allocator);
    defer env.deinit();

    var state = ExecCmdState{};
    defer state.deinit(std.testing.allocator);

    try execCmdInit(&env, config);
    try setArgvExecPath(std.testing.allocator, &env, &state, config, "tools/bin");
    try setArgv0Path(std.testing.allocator, &state, "scripts");
    try env.set("PWD", logical_pwd);
    try env.set("PATH", "/usr/bin:/bin");

    const updated = try setupPath(std.testing.allocator, &env, state, config, cwd);
    defer std.testing.allocator.free(updated);

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/tools/bin:{s}/scripts:/usr/bin:/bin",
        .{ logical_pwd, logical_pwd },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, updated);
}

test "setupPath preserves the C helper's trailing colon when PATH is set to an empty string" {
    const config = Config{
        .exec_name = "perf",
        .prefix = "/usr/libexec/perf-core",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    var env = EnvMap.init(std.testing.allocator);
    defer env.deinit();

    var state = ExecCmdState{};
    defer state.deinit(std.testing.allocator);

    try execCmdInit(&env, config);
    try setArgvExecPath(std.testing.allocator, &env, &state, config, "tools/bin");
    try setArgv0Path(std.testing.allocator, &state, "scripts");
    try env.set("PATH", "");

    const updated = try setupPath(std.testing.allocator, &env, state, config, "/repo");
    defer std.testing.allocator.free(updated);

    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/repo/scripts:",
        updated,
    );
    try std.testing.expectEqualStrings(updated, env.get("PATH").?);
}

test "choosePwdCwd prefers PWD only when the caller proves it matches cwd" {
    try std.testing.expectEqualStrings(
        "/repo",
        choosePwdCwd("/repo", null, false),
    );
    try std.testing.expectEqualStrings(
        "/repo",
        choosePwdCwd("/repo", "/repo", true),
    );
    try std.testing.expectEqualStrings(
        "/logical/repo",
        choosePwdCwd("/repo", "/logical/repo", true),
    );
    try std.testing.expectEqualStrings(
        "/repo",
        choosePwdCwd("/repo", "/other", false),
    );
}

test "sameLocation and choosePwdCwdFromFilesystem honor logical PWD aliases" {
    const linux = std.os.linux;
    var root_buf: [std.posix.PATH_MAX]u8 = undefined;
    const root = try std.fmt.bufPrintZ(&root_buf, "/tmp/zigux-p8-l06-{d}", .{linux.getpid()});
    try std.testing.expectEqual(.SUCCESS, linux.errno(linux.mkdirat(linux.AT.FDCWD, root, 0o755)));
    defer _ = linux.rmdir(root);

    var repo_buf: [std.posix.PATH_MAX]u8 = undefined;
    const repo = try std.fmt.bufPrintZ(&repo_buf, "{s}/repo", .{root});
    try std.testing.expectEqual(.SUCCESS, linux.errno(linux.mkdirat(linux.AT.FDCWD, repo, 0o755)));
    defer _ = linux.rmdir(repo);

    var link_buf: [std.posix.PATH_MAX]u8 = undefined;
    const link = try std.fmt.bufPrintZ(&link_buf, "{s}/repo-link", .{root});
    try std.testing.expectEqual(.SUCCESS, linux.errno(linux.symlinkat(repo, linux.AT.FDCWD, link)));
    defer _ = linux.unlinkat(linux.AT.FDCWD, link, 0);

    const cwd = repo[0..repo.len];
    const logical_pwd = link[0..link.len];

    try std.testing.expect(sameLocation(cwd, logical_pwd));
    try std.testing.expectEqualStrings(logical_pwd, choosePwdCwdFromFilesystem(cwd, logical_pwd));
    try std.testing.expectEqualStrings(cwd, choosePwdCwdFromFilesystem(cwd, "/definitely/missing"));
}
