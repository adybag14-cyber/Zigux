const std = @import("std");
const exec_cmd = @import("exec_cmd");

test "phase 8 exec-cmd module imports cleanly" {
    _ = exec_cmd;
}

test "phase 8 exec-cmd starter slice covers path resolution and null-terminated argv preparation" {
    const config = exec_cmd.Config{
        .exec_name = "perf",
        .prefix = "/usr/libexec/perf-core",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    const resolved = try exec_cmd.getArgvExecPath(
        std.testing.allocator,
        config,
        null,
        "/custom/perf",
    );
    defer std.testing.allocator.free(resolved);
    try std.testing.expectEqualStrings("/custom/perf", resolved);

    const explicit_empty = try exec_cmd.getArgvExecPath(
        std.testing.allocator,
        config,
        "",
        "/ignored",
    );
    defer std.testing.allocator.free(explicit_empty);
    try std.testing.expectEqualStrings("", explicit_empty);

    const search_path = try exec_cmd.buildSearchPath(
        std.testing.allocator,
        "/repo",
        "tools/bin",
        "scripts",
        "/usr/bin",
    );
    defer std.testing.allocator.free(search_path);
    try std.testing.expectEqualStrings("/repo/tools/bin:/repo/scripts:/usr/bin", search_path);

    var argv0 = (try exec_cmd.extractArgv0Path(std.testing.allocator, "/repo/bin/perf")) orelse unreachable;
    defer argv0.deinit(std.testing.allocator);
    try std.testing.expectEqualStrings("/repo/bin", argv0.argv0_path.?);
    try std.testing.expectEqualStrings("perf", argv0.command_name);

    const prepared = try exec_cmd.prepareExecCmd(
        std.testing.allocator,
        config,
        &[_][]const u8{ "record", "-a" },
    );
    defer std.testing.allocator.free(prepared);
    try std.testing.expectEqualStrings("perf", prepared[0].?);
    try std.testing.expectEqualStrings("record", prepared[1].?);
    try std.testing.expectEqualStrings("-a", prepared[2].?);
    try std.testing.expectEqual(@as(?[]const u8, null), prepared[3]);
}

test "phase 8 exec-cmd environment wrapper propagates PREFIX, exec path, and PATH updates" {
    const config = exec_cmd.Config{
        .exec_name = "perf",
        .prefix = "/usr/libexec/perf-core",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    var env = exec_cmd.EnvMap.init(std.testing.allocator);
    defer env.deinit();

    var state = exec_cmd.ExecCmdState{};
    defer state.deinit(std.testing.allocator);

    try exec_cmd.execCmdInit(&env, config);
    try exec_cmd.setArgvExecPath(std.testing.allocator, &env, &state, config, "tools/bin");
    try exec_cmd.setArgv0Path(std.testing.allocator, &state, "scripts");
    try env.set("PATH", "/usr/bin:/bin");

    const updated = try exec_cmd.setupPath(
        std.testing.allocator,
        &env,
        state,
        config,
        "/repo",
    );
    defer std.testing.allocator.free(updated);

    try std.testing.expectEqualStrings("/usr/libexec/perf-core", env.get("PREFIX").?);
    try std.testing.expectEqualStrings("tools/bin", env.get("PERF_EXEC_PATH").?);
    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/repo/scripts:/usr/bin:/bin",
        updated,
    );
    try std.testing.expectEqualStrings(updated, env.get("PATH").?);

    var explicit_empty_env = exec_cmd.EnvMap.init(std.testing.allocator);
    defer explicit_empty_env.deinit();

    var explicit_empty_state = exec_cmd.ExecCmdState{};
    defer explicit_empty_state.deinit(std.testing.allocator);

    try exec_cmd.execCmdInit(&explicit_empty_env, config);
    try exec_cmd.setArgvExecPath(
        std.testing.allocator,
        &explicit_empty_env,
        &explicit_empty_state,
        config,
        "",
    );
    try exec_cmd.setArgv0Path(std.testing.allocator, &explicit_empty_state, "scripts");
    try explicit_empty_env.set("PATH", "/usr/bin");

    const explicit_empty_path = try exec_cmd.setupPath(
        std.testing.allocator,
        &explicit_empty_env,
        explicit_empty_state,
        config,
        "/repo",
    );
    defer std.testing.allocator.free(explicit_empty_path);

    try std.testing.expectEqualStrings("", explicit_empty_env.get("PERF_EXEC_PATH").?);
    try std.testing.expectEqualStrings("/repo/scripts:/usr/bin", explicit_empty_path);
    try std.testing.expectEqualStrings(explicit_empty_path, explicit_empty_env.get("PATH").?);

    var inherited_empty_env = exec_cmd.EnvMap.init(std.testing.allocator);
    defer inherited_empty_env.deinit();

    var inherited_empty_state = exec_cmd.ExecCmdState{};
    defer inherited_empty_state.deinit(std.testing.allocator);

    try exec_cmd.execCmdInit(&inherited_empty_env, config);
    try exec_cmd.setArgvExecPath(
        std.testing.allocator,
        &inherited_empty_env,
        &inherited_empty_state,
        config,
        "tools/bin",
    );
    try inherited_empty_env.set("PATH", "");

    const inherited_empty = try exec_cmd.setupPath(
        std.testing.allocator,
        &inherited_empty_env,
        inherited_empty_state,
        config,
        "/repo",
    );
    defer std.testing.allocator.free(inherited_empty);

    try std.testing.expectEqualStrings("/repo/tools/bin:", inherited_empty);
    try std.testing.expectEqualStrings(inherited_empty, inherited_empty_env.get("PATH").?);
}

test "phase 8 exec-cmd setupPathWithPwd reuses logical PWD only when the injected stat proof matches" {
    const config = exec_cmd.Config{
        .exec_name = "perf",
        .prefix = "/usr/libexec/perf-core",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    const cwd_identity = exec_cmd.FileIdentity{ .device = 11, .inode = 7 };
    const matching_pwd_identity = exec_cmd.FileIdentity{ .device = 11, .inode = 7 };
    const different_pwd_identity = exec_cmd.FileIdentity{ .device = 99, .inode = 7 };

    var matching_env = exec_cmd.EnvMap.init(std.testing.allocator);
    defer matching_env.deinit();

    var matching_state = exec_cmd.ExecCmdState{};
    defer matching_state.deinit(std.testing.allocator);

    try exec_cmd.execCmdInit(&matching_env, config);
    try exec_cmd.setArgvExecPath(std.testing.allocator, &matching_env, &matching_state, config, "tools/bin");
    try exec_cmd.setArgv0Path(std.testing.allocator, &matching_state, "scripts");
    try matching_env.set("PATH", "/usr/bin");

    const matching = try exec_cmd.setupPathWithPwd(
        std.testing.allocator,
        &matching_env,
        matching_state,
        config,
        "/repo",
        "/logical/repo",
        cwd_identity,
        matching_pwd_identity,
    );
    defer std.testing.allocator.free(matching);

    try std.testing.expectEqualStrings(
        "/logical/repo/tools/bin:/logical/repo/scripts:/usr/bin",
        matching,
    );
    try std.testing.expectEqualStrings(matching, matching_env.get("PATH").?);

    var different_env = exec_cmd.EnvMap.init(std.testing.allocator);
    defer different_env.deinit();

    var different_state = exec_cmd.ExecCmdState{};
    defer different_state.deinit(std.testing.allocator);

    try exec_cmd.execCmdInit(&different_env, config);
    try exec_cmd.setArgvExecPath(std.testing.allocator, &different_env, &different_state, config, "tools/bin");
    try exec_cmd.setArgv0Path(std.testing.allocator, &different_state, "scripts");
    try different_env.set("PATH", "/usr/bin");

    const different = try exec_cmd.setupPathWithPwd(
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
}

test "phase 8 exec-cmd chooses the logical PWD only when the caller proves it matches cwd" {
    try std.testing.expectEqualStrings(
        "/repo",
        exec_cmd.choosePwdCwd("/repo", null, false),
    );
    try std.testing.expectEqualStrings(
        "/logical/repo",
        exec_cmd.choosePwdCwd("/repo", "/logical/repo", true),
    );
    try std.testing.expectEqualStrings(
        "/repo",
        exec_cmd.choosePwdCwd("/repo", "/other", false),
    );

    const cwd_identity = exec_cmd.FileIdentity{ .device = 11, .inode = 7 };
    const matching_pwd_identity = exec_cmd.FileIdentity{ .device = 11, .inode = 7 };
    const different_pwd_identity = exec_cmd.FileIdentity{ .device = 99, .inode = 7 };

    try std.testing.expect(exec_cmd.sameFileLocation(cwd_identity, matching_pwd_identity));
    try std.testing.expect(!exec_cmd.sameFileLocation(cwd_identity, different_pwd_identity));
    try std.testing.expectEqualStrings(
        "/logical/repo",
        exec_cmd.choosePwdCwdFromFileIdentity(
            "/repo",
            "/logical/repo",
            cwd_identity,
            matching_pwd_identity,
        ),
    );
    try std.testing.expectEqualStrings(
        "/repo",
        exec_cmd.choosePwdCwdFromFileIdentity(
            "/repo",
            "/logical/repo",
            cwd_identity,
            different_pwd_identity,
        ),
    );
    try std.testing.expect(!exec_cmd.samePathIdentity(cwd_identity, null));
    try std.testing.expectEqualStrings(
        "/repo",
        exec_cmd.choosePwdCwdFromIdentities(
            "/repo",
            "/logical/repo",
            cwd_identity,
            null,
        ),
    );
}

test "phase 8 exec-cmd keeps the trailing null slot for empty subcommand tails" {
    const config = exec_cmd.Config{
        .exec_name = "perf",
        .prefix = "/usr/libexec/perf-core",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    const prepared = try exec_cmd.prepareExecCmd(std.testing.allocator, config, &.{});
    defer std.testing.allocator.free(prepared);

    try std.testing.expectEqual(@as(usize, 2), prepared.len);
    try std.testing.expectEqualStrings("perf", prepared[0].?);
    try std.testing.expectEqual(@as(?[]const u8, null), prepared[1]);
}

test "phase 8 exec-cmd models the pure execl-style argv collector and guard" {
    const collected = try exec_cmd.collectExeclArgs(
        std.testing.allocator,
        "record",
        &[_]?[]const u8{ "-a", "--stdio", null, "--ignored" },
    );
    defer std.testing.allocator.free(collected);

    try std.testing.expectEqual(@as(usize, 4), collected.len);
    try std.testing.expectEqualStrings("record", collected[0].?);
    try std.testing.expectEqualStrings("-a", collected[1].?);
    try std.testing.expectEqualStrings("--stdio", collected[2].?);
    try std.testing.expectEqual(@as(?[]const u8, null), collected[3]);

    var overflowing_tail: [31]?[]const u8 = undefined;
    for (overflowing_tail[0..30]) |*slot| {
        slot.* = "x";
    }
    overflowing_tail[30] = null;

    try std.testing.expectError(
        error.TooManyArguments,
        exec_cmd.collectExeclArgs(std.testing.allocator, "record", &overflowing_tail),
    );

    try std.testing.expectError(
        error.MissingNullTerminator,
        exec_cmd.collectExeclArgs(
            std.testing.allocator,
            "record",
            &[_]?[]const u8{ "-a", "--stdio" },
        ),
    );
}
