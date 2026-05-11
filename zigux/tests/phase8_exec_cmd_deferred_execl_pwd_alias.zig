const std = @import("std");
const exec_cmd = @import("../../tools/lib/subcmd/exec-cmd.zig");

test "phase 8 exec-cmd deferred execl planning reuses a caller-proved logical PWD alias" {
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

    var planned = try exec_cmd.planDeferredExeclCallWithPwd(
        std.testing.allocator,
        &env,
        state,
        config,
        "/repo",
        "/logical/repo",
        true,
        "record",
        &[_]?[]const u8{ "-a", "--stdio", null, "--ignored" },
    );
    defer planned.deinit(std.testing.allocator);

    try std.testing.expectEqualStrings(
        "/logical/repo/tools/bin:/logical/repo/scripts:/usr/bin:/bin",
        planned.path,
    );
    try std.testing.expectEqualStrings(planned.path, env.get("PATH").?);
    try std.testing.expectEqualStrings("perf", planned.call.argv[0].?);
    try std.testing.expectEqualStrings("record", planned.call.argv[1].?);
    try std.testing.expectEqualStrings("-a", planned.call.argv[2].?);
    try std.testing.expectEqualStrings("--stdio", planned.call.argv[3].?);
    try std.testing.expectEqual(@as(?[]const u8, null), planned.call.argv[4]);
}

test "phase 8 exec-cmd deferred execl planning falls back to cwd when the alias is not proven" {
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

    var planned = try exec_cmd.planDeferredExeclCallWithPwd(
        std.testing.allocator,
        &env,
        state,
        config,
        "/repo",
        "/logical/repo",
        false,
        "record",
        &[_]?[]const u8{ "-a", "--stdio", null, "--ignored" },
    );
    defer planned.deinit(std.testing.allocator);

    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/repo/scripts:/usr/bin:/bin",
        planned.path,
    );
    try std.testing.expectEqualStrings(planned.path, env.get("PATH").?);
    try std.testing.expectEqualStrings("perf", planned.call.argv[0].?);
    try std.testing.expectEqualStrings("record", planned.call.argv[1].?);
    try std.testing.expectEqualStrings("-a", planned.call.argv[2].?);
    try std.testing.expectEqualStrings("--stdio", planned.call.argv[3].?);
    try std.testing.expectEqual(@as(?[]const u8, null), planned.call.argv[4]);
}
