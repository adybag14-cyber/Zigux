const std = @import("std");
const exec_cmd = @import("exec_cmd");

test "phase 8 exec-cmd deferred plan replay keeps plain execl planning aligned" {
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

    var plan = try exec_cmd.planDeferredExeclCall(
        std.testing.allocator,
        &env,
        state,
        config,
        "/repo",
        "record",
        &[_]?[]const u8{ "-a", "--stdio", null },
    );
    defer plan.deinit(std.testing.allocator);

    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/repo/scripts:/usr/bin:/bin",
        plan.path,
    );
    try std.testing.expectEqualStrings(plan.path, env.get("PATH").?);
    try std.testing.expectEqual(@as(usize, 5), plan.call.argv.len);
    try std.testing.expectEqualStrings("perf", plan.call.argv[0].?);
    try std.testing.expectEqualStrings("record", plan.call.argv[1].?);
    try std.testing.expectEqualStrings("-a", plan.call.argv[2].?);
    try std.testing.expectEqualStrings("--stdio", plan.call.argv[3].?);
    try std.testing.expectEqual(@as(?[]const u8, null), plan.call.argv[4]);

    try std.testing.expectError(
        error.MissingNullTerminator,
        exec_cmd.planDeferredExeclCall(
            std.testing.allocator,
            &env,
            state,
            config,
            "/repo",
            "record",
            &[_]?[]const u8{ "-a", "--stdio" },
        ),
    );
}

test "phase 8 exec-cmd deferred plan replay keeps logical PWD execv planning aligned" {
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
    try env.set("PATH", "/usr/bin");

    var plan = try exec_cmd.planDeferredExecvCallWithPwd(
        std.testing.allocator,
        &env,
        state,
        config,
        "/repo",
        "/logical/repo",
        .{ .device = 3, .inode = 44 },
        .{ .device = 3, .inode = 44 },
        &[_][]const u8{ "record", "-a" },
    );
    defer plan.deinit(std.testing.allocator);

    try std.testing.expectEqualStrings(
        "/logical/repo/tools/bin:/logical/repo/scripts:/usr/bin",
        plan.path,
    );
    try std.testing.expectEqualStrings(plan.path, env.get("PATH").?);
    try std.testing.expectEqual(@as(usize, 4), plan.call.argv.len);
    try std.testing.expectEqualStrings("perf", plan.call.argv[0].?);
    try std.testing.expectEqualStrings("record", plan.call.argv[1].?);
    try std.testing.expectEqualStrings("-a", plan.call.argv[2].?);
    try std.testing.expectEqual(@as(?[]const u8, null), plan.call.argv[3]);
}
