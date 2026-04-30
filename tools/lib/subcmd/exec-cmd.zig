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
    argv: []const ?[]const u8,

    pub fn deinit(self: *DeferredExecCall, allocator: std.mem.Allocator) void {
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

    var argv = try allocator.alloc(?[]const u8, collected.len + 1);
    argv[0] = config.exec_name;
    for (collected, 0..) |arg, index| {
        argv[index + 1] = arg;
    }

    return .{ .argv = argv };
}

pub fn buildDeferredExecvCall(
    allocator: std.mem.Allocator,
    config: Config,
    argv: []const []const u8,
) !DeferredExecCall {
    return .{ .argv = try prepareExecCmd(allocator, config, argv) };
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

test "extractArgv0Path splits command names from directory prefixes" {
    var extracted = (try extractArgv0Path(std.testing.allocator, "/tmp/perf")) orelse unreachable;
    defer extracted.deinit(std.testing.allocator);
    try std.testing.expectEqualStrings("/tmp", extracted.argv0_path.?);
    try std.testing.expectEqualStrings("perf", extracted.command_name);

    var directory_only = (try extractArgv0Path(std.testing.allocator, "/tmp/")) orelse unreachable;
    defer directory_only.deinit(std.testing.allocator);
    try std.testing.expectEqualStrings("/tmp", directory_only.argv0_path.?);
    try std.testing.expectEqualStrings("", directory_only.command_name);

    var root = (try extractArgv0Path(std.testing.allocator, "/perf")) orelse unreachable;
    defer root.deinit(std.testing.allocator);
    try std.testing.expect(root.argv0_path != null);
    try std.testing.expectEqual(@as(usize, 0), root.argv0_path.?.len);
    try std.testing.expectEqualStrings("perf", root.command_name);

    var root_directory_only = (try extractArgv0Path(std.testing.allocator, "/")) orelse unreachable;
    defer root_directory_only.deinit(std.testing.allocator);
    try std.testing.expect(root_directory_only.argv0_path != null);
    try std.testing.expectEqual(@as(usize, 0), root_directory_only.argv0_path.?.len);
    try std.testing.expectEqualStrings("", root_directory_only.command_name);

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

    const explicit_empty_exec_path = try buildSearchPath(
        std.testing.allocator,
        "/work/tree",
        "",
        "scripts",
        "/usr/bin",
    );
    defer std.testing.allocator.free(explicit_empty_exec_path);
    try std.testing.expectEqualStrings(
        "/work/tree/scripts:/usr/bin",
        explicit_empty_exec_path,
    );

    const inherited_empty = try buildSearchPath(
        std.testing.allocator,
        "/work/tree",
        "tools/bin",
        null,
        "",
    );
    defer std.testing.allocator.free(inherited_empty);
    try std.testing.expectEqualStrings(
        "/work/tree/tools/bin:",
        inherited_empty,
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

    const root_cwd = try buildSearchPath(
        std.testing.allocator,
        "/",
        "tools/bin",
        "scripts",
        "/usr/bin",
    );
    defer std.testing.allocator.free(root_cwd);
    try std.testing.expectEqualStrings(
        "//tools/bin://scripts:/usr/bin",
        root_cwd,
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

test "collectExeclArgs accepts the last null-terminated shape that stays below MAX_ARGS" {
    var argv_tail: [30]?[]const u8 = undefined;
    for (argv_tail[0..29]) |*slot| {
        slot.* = "x";
    }
    argv_tail[29] = null;

    const collected = try collectExeclArgs(std.testing.allocator, "record", &argv_tail);
    defer std.testing.allocator.free(collected);

    try std.testing.expectEqual(@as(usize, max_execl_slots - 1), collected.len);
    try std.testing.expectEqualStrings("record", collected[0].?);
    try std.testing.expectEqualStrings("x", collected[max_execl_slots - 3].?);
    try std.testing.expectEqual(@as(?[]const u8, null), collected[max_execl_slots - 2]);
}

test "collectExeclArgs rejects the C helper's MAX_ARGS null-slot overflow shape" {
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

test "collectExeclArgs requires the C helper's trailing null terminator" {
    try std.testing.expectError(
        error.MissingNullTerminator,
        collectExeclArgs(
            std.testing.allocator,
            "record",
            &[_]?[]const u8{ "-a", "--stdio" },
        ),
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

test "buildDeferredExecvCall keeps the execv handoff pure and launch-free" {
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

    var empty = try buildDeferredExecvCall(std.testing.allocator, config, &.{});
    defer empty.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 2), empty.argv.len);
    try std.testing.expectEqualStrings("perf", empty.argv[0].?);
    try std.testing.expectEqual(@as(?[]const u8, null), empty.argv[1]);
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

    var explicit_empty_env = EnvMap.init(std.testing.allocator);
    defer explicit_empty_env.deinit();
    try execCmdInit(&explicit_empty_env, config);

    var explicit_empty_state = ExecCmdState{};
    defer explicit_empty_state.deinit(std.testing.allocator);
    try setArgvExecPath(
        std.testing.allocator,
        &explicit_empty_env,
        &explicit_empty_state,
        config,
        "",
    );
    try setArgv0Path(std.testing.allocator, &explicit_empty_state, "scripts");
    try explicit_empty_env.set("PATH", "/usr/bin");

    const explicit_empty = try setupPath(
        std.testing.allocator,
        &explicit_empty_env,
        explicit_empty_state,
        config,
        "/repo",
    );
    defer std.testing.allocator.free(explicit_empty);

    try std.testing.expectEqualStrings("", explicit_empty_env.get("PERF_EXEC_PATH").?);
    try std.testing.expectEqualStrings(
        "/repo/scripts:/usr/bin",
        explicit_empty,
    );
    try std.testing.expectEqualStrings(explicit_empty, explicit_empty_env.get("PATH").?);

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

    var inherited_empty_env = EnvMap.init(std.testing.allocator);
    defer inherited_empty_env.deinit();
    try execCmdInit(&inherited_empty_env, config);

    var inherited_empty_state = ExecCmdState{};
    defer inherited_empty_state.deinit(std.testing.allocator);
    try setArgvExecPath(
        std.testing.allocator,
        &inherited_empty_env,
        &inherited_empty_state,
        config,
        "tools/bin",
    );
    try inherited_empty_env.set("PATH", "");

    const inherited_empty = try setupPath(
        std.testing.allocator,
        &inherited_empty_env,
        inherited_empty_state,
        config,
        "/repo",
    );
    defer std.testing.allocator.free(inherited_empty);

    try std.testing.expectEqualStrings(
        "/repo/tools/bin:",
        inherited_empty,
    );
    try std.testing.expectEqualStrings(inherited_empty, inherited_empty_env.get("PATH").?);
}

test "setupPathWithPwd reuses the logical PWD only when the injected identities match" {
    const config = Config{
        .exec_name = "perf",
        .prefix = "/usr/libexec/perf-core",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    const cwd_identity = FileIdentity{ .device = 3, .inode = 44 };
    const matching_pwd_identity = FileIdentity{ .device = 3, .inode = 44 };
    const different_pwd_identity = FileIdentity{ .device = 7, .inode = 44 };

    var matched_env = EnvMap.init(std.testing.allocator);
    defer matched_env.deinit();
    try execCmdInit(&matched_env, config);

    var matched_state = ExecCmdState{};
    defer matched_state.deinit(std.testing.allocator);
    try setArgvExecPath(std.testing.allocator, &matched_env, &matched_state, config, "tools/bin");
    try setArgv0Path(std.testing.allocator, &matched_state, "scripts");
    try matched_env.set("PATH", "/usr/bin");

    const matched = try setupPathWithPwd(
        std.testing.allocator,
        &matched_env,
        matched_state,
        config,
        "/repo",
        "/logical/repo",
        cwd_identity,
        matching_pwd_identity,
    );
    defer std.testing.allocator.free(matched);

    try std.testing.expectEqualStrings(
        "/logical/repo/tools/bin:/logical/repo/scripts:/usr/bin",
        matched,
    );
    try std.testing.expectEqualStrings(matched, matched_env.get("PATH").?);

    var different_env = EnvMap.init(std.testing.allocator);
    defer different_env.deinit();
    try execCmdInit(&different_env, config);

    var different_state = ExecCmdState{};
    defer different_state.deinit(std.testing.allocator);
    try setArgvExecPath(std.testing.allocator, &different_env, &different_state, config, "tools/bin");
    try setArgv0Path(std.testing.allocator, &different_state, "scripts");
    try different_env.set("PATH", "/usr/bin");

    const different = try setupPathWithPwd(
        std.testing.allocator,
        &different_env,
        different_state,
        config,
        "/repo",
        "/logical/repo",
        cwd_identity,
        different_pwd_identity,
    );
    defer std.testing.allocator.free(different);

    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/repo/scripts:/usr/bin",
        different,
    );
    try std.testing.expectEqualStrings(different, different_env.get("PATH").?);

    var missing_env = EnvMap.init(std.testing.allocator);
    defer missing_env.deinit();
    try execCmdInit(&missing_env, config);

    var missing_state = ExecCmdState{};
    defer missing_state.deinit(std.testing.allocator);
    try setArgvExecPath(std.testing.allocator, &missing_env, &missing_state, config, "tools/bin");
    try setArgv0Path(std.testing.allocator, &missing_state, "scripts");
    try missing_env.set("PATH", "/usr/bin");

    const missing = try setupPathWithPwd(
        std.testing.allocator,
        &missing_env,
        missing_state,
        config,
        "/repo",
        "/logical/repo",
        cwd_identity,
        null,
    );
    defer std.testing.allocator.free(missing);

    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/repo/scripts:/usr/bin",
        missing,
    );
    try std.testing.expectEqualStrings(missing, missing_env.get("PATH").?);

    var empty_env = EnvMap.init(std.testing.allocator);
    defer empty_env.deinit();
    try execCmdInit(&empty_env, config);

    var empty_state = ExecCmdState{};
    defer empty_state.deinit(std.testing.allocator);
    try setArgvExecPath(std.testing.allocator, &empty_env, &empty_state, config, "tools/bin");
    try setArgv0Path(std.testing.allocator, &empty_state, "scripts");
    try empty_env.set("PATH", "/usr/bin");

    const empty = try setupPathWithPwd(
        std.testing.allocator,
        &empty_env,
        empty_state,
        config,
        "/repo",
        "",
        cwd_identity,
        matching_pwd_identity,
    );
    defer std.testing.allocator.free(empty);

    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/repo/scripts:/usr/bin",
        empty,
    );
    try std.testing.expectEqualStrings(empty, empty_env.get("PATH").?);
}

test "choosePwdCwd prefers PWD only when it points at the same location" {
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
    try std.testing.expectEqualStrings(
        "/repo",
        choosePwdCwd("/repo", "", true),
    );
}

test "sameFileLocation and choosePwdCwdFromFileIdentity model the stat-backed pwd proof" {
    try std.testing.expect(sameFileLocation(
        .{ .device = 3, .inode = 44 },
        .{ .device = 3, .inode = 44 },
    ));
    try std.testing.expect(!sameFileLocation(
        .{ .device = 3, .inode = 44 },
        .{ .device = 7, .inode = 44 },
    ));
    try std.testing.expectEqualStrings(
        "/logical/repo",
        choosePwdCwdFromFileIdentity(
            "/repo",
            "/logical/repo",
            .{ .device = 3, .inode = 44 },
            .{ .device = 3, .inode = 44 },
        ),
    );
    try std.testing.expectEqualStrings(
        "/repo",
        choosePwdCwdFromFileIdentity(
            "/repo",
            "/logical/repo",
            .{ .device = 3, .inode = 44 },
            .{ .device = 7, .inode = 44 },
        ),
    );
    try std.testing.expect(samePathIdentity(
        .{ .device = 3, .inode = 44 },
        .{ .device = 3, .inode = 44 },
    ));
    try std.testing.expect(!samePathIdentity(
        .{ .device = 3, .inode = 44 },
        .{ .device = 7, .inode = 44 },
    ));
    try std.testing.expect(!samePathIdentity(
        .{ .device = 3, .inode = 44 },
        null,
    ));
    try std.testing.expectEqualStrings(
        "/logical/repo",
        choosePwdCwdFromIdentities(
            "/repo",
            "/logical/repo",
            .{ .device = 3, .inode = 44 },
            .{ .device = 3, .inode = 44 },
        ),
    );
    try std.testing.expectEqualStrings(
        "/repo",
        choosePwdCwdFromIdentities(
            "/repo",
            "/logical/repo",
            .{ .device = 3, .inode = 44 },
            .{ .device = 7, .inode = 44 },
        ),
    );
    try std.testing.expectEqualStrings(
        "/repo",
        choosePwdCwdFromIdentities(
            "/repo",
            "/logical/repo",
            .{ .device = 3, .inode = 44 },
            null,
        ),
    );
}
