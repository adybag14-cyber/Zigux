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
