const std = @import("std");
const exec_cmd = @import("exec_cmd");

test "phase 8 exec-cmd module imports cleanly" {
    _ = exec_cmd;
}

test "phase 8 exec-cmd starter slice covers path resolution, env updates, and argv preparation" {
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

    const search_path = try exec_cmd.buildSearchPath(
        std.testing.allocator,
        "/repo",
        "tools/bin",
        "scripts",
        "/usr/bin",
    );
    defer std.testing.allocator.free(search_path);
    try std.testing.expectEqualStrings("/repo/tools/bin:/repo/scripts:/usr/bin", search_path);

    var prefix_env = try exec_cmd.makePrefixEnv(std.testing.allocator, config);
    defer prefix_env.deinit(std.testing.allocator);
    try std.testing.expectEqualStrings("PREFIX", prefix_env.name);
    try std.testing.expectEqualStrings("/usr/libexec/perf-core", prefix_env.value);

    var exec_path_env = try exec_cmd.makeExecPathEnv(std.testing.allocator, config, "/custom/perf");
    defer exec_path_env.deinit(std.testing.allocator);
    try std.testing.expectEqualStrings("PERF_EXEC_PATH", exec_path_env.name);
    try std.testing.expectEqualStrings("/custom/perf", exec_path_env.value);

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
    try std.testing.expectEqualStrings("perf", prepared[0]);
    try std.testing.expectEqualStrings("record", prepared[1]);
    try std.testing.expectEqualStrings("-a", prepared[2]);
}
