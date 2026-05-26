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
            self.allocator.free(entry.key_ptr.*);
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

        if (self.values.getPtr(key)) |value_ptr| {
            self.allocator.free(value_ptr.*);
            value_ptr.* = owned_value;
            return;
        }

        const owned_key = try self.allocator.dupe(u8, key);
        errdefer self.allocator.free(owned_key);

        try self.values.putNoClobber(owned_key, owned_value);
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

pub const FileIdentity = struct {
    device: u64,
    inode: u64,
};

pub const PathIdentity = FileIdentity;

pub const max_execl_slots: usize = 32;
pub const CollectExeclArgsError = error{
    MissingNullTerminator,
    TooManyArguments,
};

pub const DeferredExecCall = struct {
    argv: []const ?[]u8,

    pub fn deinit(self: *DeferredExecCall, allocator: std.mem.Allocator) void {
        for (self.argv) |arg| {
            if (arg) |value| {
                allocator.free(value);
            }
        }
        allocator.free(self.argv);
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

pub fn sameFileLocation(cwd_identity: FileIdentity, pwd_identity: FileIdentity) bool {
    return cwd_identity.device == pwd_identity.device and
        cwd_identity.inode == pwd_identity.inode;
}

pub fn samePathIdentity(cwd_identity: FileIdentity, pwd_identity: ?FileIdentity) bool {
    const pwd_value = pwd_identity orelse return false;
    return sameFileLocation(cwd_identity, pwd_value);
}

pub fn choosePwdCwdFromFileIdentity(
    cwd: []const u8,
    pwd: ?[]const u8,
    cwd_identity: FileIdentity,
    pwd_identity: FileIdentity,
) []const u8 {
    return choosePwdCwd(cwd, pwd, sameFileLocation(cwd_identity, pwd_identity));
}

pub fn choosePwdCwdFromIdentities(
    cwd: []const u8,
    pwd: ?[]const u8,
    cwd_identity: FileIdentity,
    pwd_identity: ?FileIdentity,
) []const u8 {
    return choosePwdCwd(cwd, pwd, samePathIdentity(cwd_identity, pwd_identity));
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
    const had_old_path = old_path != null;

    try appendPathEntry(&builder, allocator, cwd, argv_exec_path);
    if (argv0_path) |path| {
        try appendPathEntry(&builder, allocator, cwd, path);
    }

    const tail = old_path orelse "/usr/local/bin:/usr/bin:/bin";
    if (tail.len != 0 or had_old_path) {
        if (builder.items.len != 0) {
            try builder.append(allocator, ':');
        }
    }
    if (tail.len != 0) {
        try builder.appendSlice(allocator, tail);
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

    const new_path = try buildSearchPath(
        allocator,
        cwd,
        argv_exec_path,
        state.argv0_path,
        env.get("PATH"),
    );
    errdefer allocator.free(new_path);

    try env.set("PATH", new_path);
    return new_path;
}

pub fn setupPathWithPwd(
    allocator: std.mem.Allocator,
    env: *EnvMap,
    state: ExecCmdState,
    config: Config,
    cwd: []const u8,
    pwd: ?[]const u8,
    cwd_identity: FileIdentity,
    pwd_identity: ?FileIdentity,
) ![]u8 {
    return setupPath(
        allocator,
        env,
        state,
        config,
        choosePwdCwdFromIdentities(cwd, pwd, cwd_identity, pwd_identity),
    );
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

fn duplicateOptionalArgv(
    allocator: std.mem.Allocator,
    argv: []const ?[]const u8,
) ![]const ?[]u8 {
    var owned = try allocator.alloc(?[]u8, argv.len);
    var initialized: usize = 0;
    errdefer {
        for (owned[0..initialized]) |arg| {
            if (arg) |value| {
                allocator.free(value);
            }
        }
        allocator.free(owned);
    }

    for (argv, 0..) |arg, index| {
        owned[index] = if (arg) |value| try allocator.dupe(u8, value) else null;
        initialized = index + 1;
    }

    return owned;
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
        try collected.append(allocator, arg);
        argc += 1;

        // `execl_cmd()` increments `argc` immediately after each `va_arg()`
        // fetch, so a terminating null in slot `MAX_ARGS` still overflows.
        if (argc >= max_execl_slots) {
            return error.TooManyArguments;
        }
        if (arg == null) {
            return collected.toOwnedSlice(allocator);
        }
    }

    return error.MissingNullTerminator;
}

pub fn buildDeferredExeclCall(
    allocator: std.mem.Allocator,
    config: Config,
    cmd: []const u8,
    argv_tail: []const ?[]const u8,
) (CollectExeclArgsError || std.mem.Allocator.Error)!DeferredExecCall {
    const collected = try collectExeclArgs(allocator, cmd, argv_tail);
    defer allocator.free(collected);

    var borrowed = try allocator.alloc(?[]const u8, collected.len + 1);
    defer allocator.free(borrowed);

    borrowed[0] = config.exec_name;
    for (collected, 0..) |arg, index| {
        borrowed[index + 1] = arg;
    }

    return .{ .argv = try duplicateOptionalArgv(allocator, borrowed) };
}

pub fn buildDeferredExecvCall(
    allocator: std.mem.Allocator,
    config: Config,
    argv: []const []const u8,
) !DeferredExecCall {
    const prepared = try prepareExecCmd(allocator, config, argv);
    defer allocator.free(prepared);

    return .{ .argv = try duplicateOptionalArgv(allocator, prepared) };
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

    const explicit_empty = try getArgvExecPath(std.testing.allocator, config, "", "/ignored");
    defer std.testing.allocator.free(explicit_empty);
    try std.testing.expectEqualStrings("", explicit_empty);

    const from_env = try getArgvExecPath(std.testing.allocator, config, null, "/env/perf");
    defer std.testing.allocator.free(from_env);
    try std.testing.expectEqualStrings("/env/perf", from_env);

    const fallback = try getArgvExecPath(std.testing.allocator, config, null, "");
    defer std.testing.allocator.free(fallback);
    try std.testing.expectEqualStrings("/usr/libexec/perf-core/libexec/perf-core", fallback);
}

test "EnvMap owns inserted keys so later caller mutations cannot corrupt lookups" {
    var env = EnvMap.init(std.testing.allocator);
    defer env.deinit();

    const mutable_key = try std.testing.allocator.dupe(u8, "PERF_EXEC_PATH");
    defer std.testing.allocator.free(mutable_key);

    try env.set(mutable_key, "/tmp/perf");
    @memset(mutable_key, 'X');

    try std.testing.expectEqualStrings("/tmp/perf", env.get("PERF_EXEC_PATH").?);
    try std.testing.expectEqual(@as(?[]const u8, null), env.get("XXXXXXXXXXXXXX"));
}

test "extractArgv0Path splits command names from directory prefixes" {
    var extracted = (try extractArgv0Path(std.testing.allocator, "/tmp/perf")) orelse unreachable;
    defer extracted.deinit(std.testing.allocator);
    try std.testing.expectEqualStrings("/tmp", extracted.argv0_path.?);
    try std.testing.expectEqualStrings("perf", extracted.command_name);
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
}

test "buildSearchPath preserves root-cwd doubled slashes used by the C helper" {
    const built = try buildSearchPath(
        std.testing.allocator,
        "/",
        "tools/bin",
        "scripts",
        "/usr/bin:/bin",
    );
    defer std.testing.allocator.free(built);

    try std.testing.expectEqualStrings(
        "//tools/bin://scripts:/usr/bin:/bin",
        built,
    );
}

test "buildSearchPath skips rooted argv0 empty directories when assembling PATH" {
    var rooted = (try extractArgv0Path(std.testing.allocator, "/perf")) orelse unreachable;
    defer rooted.deinit(std.testing.allocator);
    try std.testing.expectEqualStrings("", rooted.argv0_path.?);
    try std.testing.expectEqualStrings("perf", rooted.command_name);

    const built = try buildSearchPath(
        std.testing.allocator,
        "/repo",
        "tools/bin",
        rooted.argv0_path,
        "/usr/bin",
    );
    defer std.testing.allocator.free(built);

    try std.testing.expectEqualStrings("/repo/tools/bin:/usr/bin", built);
}

test "setupPath preserves the inherited exec-path string while normalizing PATH entries" {
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
    try env.set(config.exec_path_env, "tools/bin");
    try setArgv0Path(std.testing.allocator, &state, "scripts");
    try env.set("PATH", "/usr/bin");

    const new_path = try setupPath(
        std.testing.allocator,
        &env,
        state,
        config,
        "/repo",
    );
    defer std.testing.allocator.free(new_path);

    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/repo/scripts:/usr/bin",
        new_path,
    );
    try std.testing.expectEqualStrings(new_path, env.get("PATH").?);
    try std.testing.expectEqualStrings("tools/bin", env.get(config.exec_path_env).?);
}

test "setupPathWithPwd keeps logical PWD when identity matches" {
    try std.testing.expectEqualStrings(
        "/logical/repo",
        choosePwdCwdFromIdentities(
            "/repo",
            "/logical/repo",
            .{ .device = 3, .inode = 44 },
            .{ .device = 3, .inode = 44 },
        ),
    );
}

test "setupPathWithPwd falls back to cwd when logical PWD identity does not match" {
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
    try env.set("PATH", "/usr/bin");

    const new_path = try setupPathWithPwd(
        std.testing.allocator,
        &env,
        state,
        config,
        "/repo",
        "/logical/repo",
        .{ .device = 3, .inode = 44 },
        .{ .device = 9, .inode = 99 },
    );
    defer std.testing.allocator.free(new_path);

    try std.testing.expectEqualStrings("/repo/tools/bin:/repo/scripts:/usr/bin", new_path);
    try std.testing.expectEqualStrings(new_path, env.get("PATH").?);
}

test "setupPathWithPwd falls back to cwd when logical PWD identity is unavailable" {
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
    try env.set("PATH", "/usr/bin");

    const new_path = try setupPathWithPwd(
        std.testing.allocator,
        &env,
        state,
        config,
        "/repo",
        "/logical/repo",
        .{ .device = 3, .inode = 44 },
        null,
    );
    defer std.testing.allocator.free(new_path);

    try std.testing.expectEqualStrings("/repo/tools/bin:/repo/scripts:/usr/bin", new_path);
    try std.testing.expectEqualStrings(new_path, env.get("PATH").?);
}

test "setupPathWithPwd ignores an explicitly empty logical PWD even when identity matches" {
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
    try env.set("PATH", "/usr/bin");

    const new_path = try setupPathWithPwd(
        std.testing.allocator,
        &env,
        state,
        config,
        "/repo",
        "",
        .{ .device = 3, .inode = 44 },
        .{ .device = 3, .inode = 44 },
    );
    defer std.testing.allocator.free(new_path);

    try std.testing.expectEqualStrings("/repo/tools/bin:/repo/scripts:/usr/bin", new_path);
    try std.testing.expectEqualStrings(new_path, env.get("PATH").?);
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

test "collectExeclArgs rejects a tail that never terminates with null" {
    try std.testing.expectError(
        error.MissingNullTerminator,
        collectExeclArgs(
            std.testing.allocator,
            "record",
            &[_]?[]const u8{ "-a", "--call-graph" },
        ),
    );
}

test "collectExeclArgs rejects a null terminator that lands in MAX_ARGS" {
    var argv_tail = [_]?[]const u8{null} ** (max_execl_slots - 1);
    for (argv_tail[0 .. argv_tail.len - 1]) |*slot| {
        slot.* = "--stdio";
    }

    try std.testing.expectError(
        error.TooManyArguments,
        collectExeclArgs(std.testing.allocator, "record", argv_tail[0..]),
    );
}

test "buildDeferredExeclCall keeps the execl handoff pure and launch-free" {
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

test "buildDeferredExecvCall owns deferred argv entries for later handoff" {
    const owned_exec_name = try std.testing.allocator.dupe(u8, "perf");
    defer std.testing.allocator.free(owned_exec_name);
    const command = try std.testing.allocator.dupe(u8, "record");
    defer std.testing.allocator.free(command);
    const flag = try std.testing.allocator.dupe(u8, "-a");
    defer std.testing.allocator.free(flag);

    const config = Config{
        .exec_name = owned_exec_name,
        .prefix = "/unused",
        .exec_path = "unused",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    var deferred = try buildDeferredExecvCall(
        std.testing.allocator,
        config,
        &[_][]const u8{ command, flag },
    );
    defer deferred.deinit(std.testing.allocator);

    @memset(owned_exec_name, 'X');
    @memset(command, 'Y');
    @memset(flag, 'Z');

    try std.testing.expectEqualStrings("perf", deferred.argv[0].?);
    try std.testing.expectEqualStrings("record", deferred.argv[1].?);
    try std.testing.expectEqualStrings("-a", deferred.argv[2].?);
    try std.testing.expectEqual(@as(?[]const u8, null), deferred.argv[3]);
}

test "buildDeferredExeclCall owns deferred argv entries for later handoff" {
    const owned_exec_name = try std.testing.allocator.dupe(u8, "perf");
    defer std.testing.allocator.free(owned_exec_name);
    const command = try std.testing.allocator.dupe(u8, "record");
    defer std.testing.allocator.free(command);
    const flag = try std.testing.allocator.dupe(u8, "--stdio");
    defer std.testing.allocator.free(flag);

    const config = Config{
        .exec_name = owned_exec_name,
        .prefix = "/unused",
        .exec_path = "unused",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    var deferred = try buildDeferredExeclCall(
        std.testing.allocator,
        config,
        command,
        &[_]?[]const u8{ flag, null },
    );
    defer deferred.deinit(std.testing.allocator);

    @memset(owned_exec_name, 'X');
    @memset(command, 'Y');
    @memset(flag, 'Z');

    try std.testing.expectEqualStrings("perf", deferred.argv[0].?);
    try std.testing.expectEqualStrings("record", deferred.argv[1].?);
    try std.testing.expectEqualStrings("--stdio", deferred.argv[2].?);
    try std.testing.expectEqual(@as(?[]const u8, null), deferred.argv[3]);
}
