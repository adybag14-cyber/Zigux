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
    const owned_path = try allocator.dupe(u8, exec_path);
    errdefer allocator.free(owned_path);

    try env.set(config.exec_path_env, exec_path);

    if (state.argv_exec_path) |previous| {
        allocator.free(previous);
    }
    state.argv_exec_path = owned_path;
}

pub fn setArgv0Path(
    allocator: std.mem.Allocator,
    state: *ExecCmdState,
    argv0_path: ?[]const u8,
) !void {
    if (argv0_path) |path| {
        const owned_path = try allocator.dupe(u8, path);
        if (state.argv0_path) |previous| {
            allocator.free(previous);
        }
        state.argv0_path = owned_path;
        return;
    }

    if (state.argv0_path) |previous| {
        allocator.free(previous);
        state.argv0_path = null;
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

fn prependExecNameToOptionalArgv(
    allocator: std.mem.Allocator,
    config: Config,
    argv: []const ?[]const u8,
) ![]const ?[]const u8 {
    var prefixed = try allocator.alloc(?[]const u8, argv.len + 1);
    prefixed[0] = config.exec_name;
    for (argv, 0..) |arg, index| {
        prefixed[index + 1] = arg;
    }
    return prefixed;
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

pub fn buildDeferredExecvCall(
    allocator: std.mem.Allocator,
    config: Config,
    argv: []const []const u8,
) !DeferredExecCall {
    const prepared = try prepareExecCmd(allocator, config, argv);
    defer allocator.free(prepared);

    return .{
        .argv = try duplicateOptionalArgv(allocator, prepared),
    };
}

pub fn buildDeferredExeclCall(
    allocator: std.mem.Allocator,
    config: Config,
    cmd: []const u8,
    argv_tail: []const ?[]const u8,
) !DeferredExecCall {
    const collected = try collectExeclArgs(allocator, cmd, argv_tail);
    defer allocator.free(collected);

    const prepared = try prependExecNameToOptionalArgv(allocator, config, collected);
    defer allocator.free(prepared);

    return .{
        .argv = try duplicateOptionalArgv(allocator, prepared),
    };
}

test "EnvMap owns inserted keys so later caller mutations cannot corrupt lookups" {
    var env = EnvMap.init(std.testing.allocator);
    defer env.deinit();

    var key = [_]u8{ 'P', 'A', 'T', 'H' };
    var value = [_]u8{ '/', 'b', 'i', 'n' };

    try env.set(key[0..], value[0..]);
    key[0] = 'M';
    value[0] = '.';

    try std.testing.expectEqualStrings("/bin", env.get("PATH").?);
}

test "setArgvExecPath keeps the previous path when allocation fails" {
    var backing: std.heap.DebugAllocator(.{}) = .{};
    defer std.testing.expect(backing.deinit() == .ok) catch @panic("leak");

    var failing_state = std.testing.FailingAllocator.init(backing.allocator(), .{ .fail_index = 1 });
    const failing_allocator = failing_state.allocator();

    var env = EnvMap.init(failing_allocator);
    defer env.deinit();

    var state = ExecCmdState{
        .argv_exec_path = try failing_allocator.dupe(u8, "old"),
    };
    defer state.deinit(failing_allocator);

    const config = Config{
        .exec_name = "perf",
        .prefix = "/usr",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    try std.testing.expectError(
        error.OutOfMemory,
        setArgvExecPath(failing_allocator, &env, &state, config, "new-path"),
    );
    try std.testing.expectEqualStrings("old", state.argv_exec_path.?);
}

test "setArgvExecPath keeps previous state and env when env update fails" {
    var backing: std.heap.DebugAllocator(.{}) = .{};
    defer std.testing.expect(backing.deinit() == .ok) catch @panic("leak");

    var env = EnvMap.init(backing.allocator());
    defer env.deinit();
    try env.set("PERF_EXEC_PATH", "old-env");

    var state = ExecCmdState{
        .argv_exec_path = try backing.allocator().dupe(u8, "old-state"),
    };
    defer state.deinit(backing.allocator());

    var failing_state = std.testing.FailingAllocator.init(backing.allocator(), .{ .fail_index = 1 });
    const failing_allocator = failing_state.allocator();
    env.allocator = failing_allocator;

    const config = Config{
        .exec_name = "perf",
        .prefix = "/usr",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    try std.testing.expectError(
        error.OutOfMemory,
        setArgvExecPath(failing_allocator, &env, &state, config, "new-path"),
    );
    try std.testing.expectEqualStrings("old-state", state.argv_exec_path.?);
    try std.testing.expectEqualStrings("old-env", env.get("PERF_EXEC_PATH").?);
}

test "setArgv0Path keeps the previous path when allocation fails" {
    var backing: std.heap.DebugAllocator(.{}) = .{};
    defer std.testing.expect(backing.deinit() == .ok) catch @panic("leak");

    var state = ExecCmdState{
        .argv0_path = try backing.allocator().dupe(u8, "old-argv0"),
    };
    defer state.deinit(backing.allocator());

    var failing_state = std.testing.FailingAllocator.init(backing.allocator(), .{ .fail_index = 0 });
    const failing_allocator = failing_state.allocator();

    try std.testing.expectError(
        error.OutOfMemory,
        setArgv0Path(failing_allocator, &state, "new-argv0"),
    );
    try std.testing.expectEqualStrings("old-argv0", state.argv0_path.?);
}

test "buildSearchPath rewrites relative entries against the working directory" {
    const rendered = try buildSearchPath(
        std.testing.allocator,
        "/repo",
        "tools/bin",
        "scripts",
        "/usr/bin",
    );
    defer std.testing.allocator.free(rendered);

    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/repo/scripts:/usr/bin",
        rendered,
    );
}

test "extractArgv0Path splits the wrapper directory from the command name" {
    var extracted = (try extractArgv0Path(std.testing.allocator, "/tmp/wrappers/perf-record")).?;
    defer extracted.deinit(std.testing.allocator);

    try std.testing.expectEqualStrings("/tmp/wrappers", extracted.argv0_path.?);
    try std.testing.expectEqualStrings("perf-record", extracted.command_name);
}

test "buildSearchPath normalizes relative exec roots and preserves an empty PATH tail" {
    const rendered = try buildSearchPath(
        std.testing.allocator,
        "/tmp/work",
        "libexec/perf-core",
        "wrappers",
        "",
    );
    defer std.testing.allocator.free(rendered);

    try std.testing.expectEqualStrings(
        "/tmp/work/libexec/perf-core:/tmp/work/wrappers:",
        rendered,
    );
}

test "setupPathWithPwd prefers PWD when identities match for relative argv paths" {
    var env = EnvMap.init(std.testing.allocator);
    defer env.deinit();

    var state = ExecCmdState{};
    defer state.deinit(std.testing.allocator);

    const config = Config{
        .exec_name = "perf",
        .prefix = "/usr",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    try setArgvExecPath(std.testing.allocator, &env, &state, config, "alt/libexec");
    try setArgv0Path(std.testing.allocator, &state, "wrappers");

    const rendered = try setupPathWithPwd(
        std.testing.allocator,
        &env,
        state,
        config,
        "/proc/self/cwd",
        "/tmp/project",
        .{ .device = 1, .inode = 7 },
        .{ .device = 1, .inode = 7 },
    );
    defer std.testing.allocator.free(rendered);

    try std.testing.expectEqualStrings(
        "/tmp/project/alt/libexec:/tmp/project/wrappers:/usr/local/bin:/usr/bin:/bin",
        rendered,
    );
    try std.testing.expectEqualStrings(rendered, env.get("PATH").?);
}

test "setupPathWithPwd falls back to cwd when logical PWD identity is unavailable" {
    var env = EnvMap.init(std.testing.allocator);
    defer env.deinit();

    var state = ExecCmdState{};
    defer state.deinit(std.testing.allocator);

    const config = Config{
        .exec_name = "perf",
        .prefix = "/usr",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    try setArgvExecPath(std.testing.allocator, &env, &state, config, "tools/bin");
    try setArgv0Path(std.testing.allocator, &state, "scripts");
    try env.set("PATH", "/usr/bin");

    const rendered = try setupPathWithPwd(
        std.testing.allocator,
        &env,
        state,
        config,
        "/repo",
        "/logical/repo",
        .{ .device = 1, .inode = 7 },
        null,
    );
    defer std.testing.allocator.free(rendered);

    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/repo/scripts:/usr/bin",
        rendered,
    );
}

test "setupPathWithPwd ignores an explicitly empty logical PWD even when identity matches" {
    var env = EnvMap.init(std.testing.allocator);
    defer env.deinit();

    var state = ExecCmdState{};
    defer state.deinit(std.testing.allocator);

    const config = Config{
        .exec_name = "perf",
        .prefix = "/usr",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    try setArgvExecPath(std.testing.allocator, &env, &state, config, "tools/bin");
    try setArgv0Path(std.testing.allocator, &state, "scripts");
    try env.set("PATH", "/usr/bin");

    const rendered = try setupPathWithPwd(
        std.testing.allocator,
        &env,
        state,
        config,
        "/repo",
        "",
        .{ .device = 1, .inode = 7 },
        .{ .device = 1, .inode = 7 },
    );
    defer std.testing.allocator.free(rendered);

    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/repo/scripts:/usr/bin",
        rendered,
    );
}

test "collectExeclArgs preserves the MAX_ARGS overflow rule from execl_cmd" {
    var argv_tail: [max_execl_slots - 1]?[]const u8 = undefined;
    for (argv_tail[0 .. argv_tail.len - 1], 0..) |*slot, index| {
        slot.* = if ((index & 1) == 0) "arg-even" else "arg-odd";
    }
    argv_tail[argv_tail.len - 1] = null;

    try std.testing.expectError(
        error.TooManyArguments,
        collectExeclArgs(std.testing.allocator, "perf", &argv_tail),
    );
}

test "collectExeclArgs rejects a null terminator that lands in MAX_ARGS" {
    var argv_tail: [max_execl_slots - 1]?[]const u8 = undefined;
    for (argv_tail[0 .. argv_tail.len - 1]) |*slot| {
        slot.* = "--bounded";
    }
    argv_tail[argv_tail.len - 1] = null;

    try std.testing.expectError(
        error.TooManyArguments,
        collectExeclArgs(std.testing.allocator, "record", &argv_tail),
    );
}

test "collectExeclArgs duplicates the deferred argv payload up to the null terminator" {
    const collected = try collectExeclArgs(
        std.testing.allocator,
        "perf",
        &.{ "annotate", "--stdio", null, "ignored" },
    );
    defer std.testing.allocator.free(collected);

    const duplicated = try duplicateOptionalArgv(std.testing.allocator, collected);
    var deferred = DeferredExecCall{ .argv = duplicated };
    defer deferred.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 4), deferred.argv.len);
    try std.testing.expectEqualStrings("perf", deferred.argv[0].?);
    try std.testing.expectEqualStrings("annotate", deferred.argv[1].?);
    try std.testing.expectEqualStrings("--stdio", deferred.argv[2].?);
    try std.testing.expectEqual(@as(?[]u8, null), deferred.argv[3]);
}

test "buildDeferredExeclCall keeps the execl handoff pure and launch-free" {
    const config = Config{
        .exec_name = "perf",
        .prefix = "/usr",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    var deferred = try buildDeferredExeclCall(
        std.testing.allocator,
        config,
        "record",
        &.{ "-a", "--stdio", null },
    );
    defer deferred.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 5), deferred.argv.len);
    try std.testing.expectEqualStrings("perf", deferred.argv[0].?);
    try std.testing.expectEqualStrings("record", deferred.argv[1].?);
    try std.testing.expectEqualStrings("-a", deferred.argv[2].?);
    try std.testing.expectEqualStrings("--stdio", deferred.argv[3].?);
    try std.testing.expectEqual(@as(?[]u8, null), deferred.argv[4]);
}

test "buildDeferredExecvCall keeps the execv handoff prefixed and null terminated" {
    const config = Config{
        .exec_name = "perf",
        .prefix = "/usr",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    var deferred = try buildDeferredExecvCall(
        std.testing.allocator,
        config,
        &.{ "record", "--stdio" },
    );
    defer deferred.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 4), deferred.argv.len);
    try std.testing.expectEqualStrings("perf", deferred.argv[0].?);
    try std.testing.expectEqualStrings("record", deferred.argv[1].?);
    try std.testing.expectEqualStrings("--stdio", deferred.argv[2].?);
    try std.testing.expectEqual(@as(?[]u8, null), deferred.argv[3]);
}
