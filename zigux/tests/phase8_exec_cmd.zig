const std = @import("std");
const build_options = @import("build_options");
const exec_cmd = @import("exec_cmd");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readWorkspaceFile(allocator: std.mem.Allocator, path: []const u8, limit: usize) ![]u8 {
    const full_path = try std.fs.path.join(allocator, &.{ build_options.repo_root, path });
    defer allocator.free(full_path);

    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        full_path,
        allocator,
        .limited(limit),
    );
}

test "phase 8 exec-cmd module imports cleanly" {
    _ = exec_cmd;
}

test "phase 8 exec-cmd focused helper packet covers deferred handoff boundaries" {
    const config = exec_cmd.Config{
        .exec_name = "perf",
        .prefix = "/usr/libexec/perf-core",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    const explicit_empty = try exec_cmd.getArgvExecPath(
        std.testing.allocator,
        config,
        "",
        "/ignored",
    );
    defer std.testing.allocator.free(explicit_empty);
    try std.testing.expectEqualStrings("", explicit_empty);

    var env = exec_cmd.EnvMap.init(std.testing.allocator);
    defer env.deinit();
    var state = exec_cmd.ExecCmdState{};
    defer state.deinit(std.testing.allocator);

    try exec_cmd.execCmdInit(&env, config);
    try exec_cmd.setArgvExecPath(std.testing.allocator, &env, &state, config, "tools/bin");
    try exec_cmd.setArgv0Path(std.testing.allocator, &state, "scripts");
    try env.set("PATH", "/usr/bin");

    const matched = try exec_cmd.setupPathWithPwd(
        std.testing.allocator,
        &env,
        state,
        config,
        "/repo",
        "/logical/repo",
        .{ .device = 11, .inode = 7 },
        .{ .device = 11, .inode = 7 },
    );
    defer std.testing.allocator.free(matched);
    try std.testing.expectEqualStrings(
        "/logical/repo/tools/bin:/logical/repo/scripts:/usr/bin",
        matched,
    );

    try std.testing.expectError(
        error.MissingNullTerminator,
        exec_cmd.collectExeclArgs(
            std.testing.allocator,
            "record",
            &[_]?[]const u8{ "-a", "--stdio" },
        ),
    );

    var deferred_execl = try exec_cmd.buildDeferredExeclCall(
        std.testing.allocator,
        config,
        "record",
        &[_]?[]const u8{ "-a", "--stdio", null },
    );
    defer deferred_execl.deinit(std.testing.allocator);
    try std.testing.expectEqual(@as(usize, 5), deferred_execl.argv.len);
    try std.testing.expectEqualStrings("perf", deferred_execl.argv[0].?);
    try std.testing.expectEqualStrings("record", deferred_execl.argv[1].?);
    try std.testing.expectEqualStrings("-a", deferred_execl.argv[2].?);
    try std.testing.expectEqualStrings("--stdio", deferred_execl.argv[3].?);
    try std.testing.expectEqual(@as(?[]const u8, null), deferred_execl.argv[4]);

    var deferred_execv = try exec_cmd.buildDeferredExecvCall(
        std.testing.allocator,
        config,
        &[_][]const u8{ "record", "-a" },
    );
    defer deferred_execv.deinit(std.testing.allocator);
    try std.testing.expectEqual(@as(usize, 4), deferred_execv.argv.len);
    try std.testing.expectEqualStrings("perf", deferred_execv.argv[0].?);
    try std.testing.expectEqualStrings("record", deferred_execv.argv[1].?);
    try std.testing.expectEqualStrings("-a", deferred_execv.argv[2].?);
    try std.testing.expectEqual(@as(?[]const u8, null), deferred_execv.argv[3]);
}

test "phase 8 exec-cmd note keeps deferred execution boundaries explicit" {
    const slice_note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-exec-cmd-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(slice_note);

    try expectContains(slice_note, "deferred execution");
    try expectContains(slice_note, "buildDeferredExeclCall()");
    try expectContains(slice_note, "buildDeferredExecvCall()");
    try expectContains(slice_note, "queue ownership");
    try expectContains(slice_note, "kernel/workqueue.c");
    try expectContains(slice_note, "Phase 14");
}
