const std = @import("std");
const build_options = @import("build_options");
const exec_cmd = @import("exec_cmd");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
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

test "phase 8 exec-cmd note keeps deferred execution boundaries explicit" {
    const allocator = std.testing.allocator;

    const slice_note = try readWorkspaceFile(
        allocator,
        "Documentation/zigux/phase8-exec-cmd-slice.md",
        64 * 1024,
    );
    defer allocator.free(slice_note);

    const helper = try readWorkspaceFile(
        allocator,
        "tools/lib/subcmd/exec-cmd.zig",
        64 * 1024,
    );
    defer allocator.free(helper);

    try expectContains(slice_note, "tools/lib/subcmd/exec-cmd.zig");
    try expectContains(slice_note, "deferred execution");
    try expectContains(slice_note, "queue ownership");
    try expectContains(slice_note, "kernel/workqueue.c remains a Phase 14 boundary-study target");
    try expectContains(slice_note, "buildDeferredExeclCall()");
    try expectContains(slice_note, "buildDeferredExecvCall()");
    try expectContains(slice_note, "no retry scheduling, timer-backed backoff, timeout handling, or poll-loop ownership around deferred execution");
    try expectContains(slice_note, "no queue ownership, wakeup routing, worker-pool control, or scheduler-visible execution substrate");
    try expectContains(slice_note, "deferred-execution runtime, a broader task queue, or any workqueue-style execution substrate");

    try expectContains(helper, "pub fn setupPathWithPwd(");
    try expectContains(helper, "pub fn collectExeclArgs(");
    try expectContains(helper, "pub fn buildDeferredExeclCall(");
    try expectContains(helper, "pub fn buildDeferredExecvCall(");
}

test "phase 8 exec-cmd review witness keeps the surviving shared reminder surfaces explicit" {
    const allocator = std.testing.allocator;

    const checker = try readWorkspaceFile(
        allocator,
        "scripts/zigux/check-phase8-exec-cmd-packet.py",
        96 * 1024,
    );
    defer allocator.free(checker);

    const validate_phase8 = try readWorkspaceFile(
        allocator,
        "scripts/zigux/validate-phase8.py",
        192 * 1024,
    );
    defer allocator.free(validate_phase8);

    const focused_build = try readWorkspaceFile(
        allocator,
        "zigux/tests/phase8_exec_cmd_only_build.zig",
        32 * 1024,
    );
    defer allocator.free(focused_build);

    const shared_build = try readWorkspaceFile(
        allocator,
        "zigux/tests/phase8_build.zig",
        64 * 1024,
    );
    defer allocator.free(shared_build);

    try expectContains(checker, "PHASE8_EXEC_CMD_PACKET_SELF_TEST=pass");
    try expectContains(checker, "\"tools/lib/subcmd/exec-cmd.zig\"");
    try expectContains(focused_build, "Run focused Phase 8 exec-cmd tests");
    try expectContains(shared_build, "phase8-exec-cmd-shared-tests");
    try expectContains(shared_build, "../../tools/lib/subcmd/exec-cmd.zig");
    try expectNotContains(validate_phase8, "expectMissingPath(\"tools/lib/subcmd/exec-cmd.zig\")");
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

    try env.set("PATH", "/usr/bin");
    const mismatched = try exec_cmd.setupPathWithPwd(
        std.testing.allocator,
        &env,
        state,
        config,
        "/repo",
        "/logical/repo",
        .{ .device = 11, .inode = 7 },
        .{ .device = 12, .inode = 9 },
    );
    defer std.testing.allocator.free(mismatched);
    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/repo/scripts:/usr/bin",
        mismatched,
    );

    try exec_cmd.setArgvExecPath(std.testing.allocator, &env, &state, config, "");
    try exec_cmd.setArgv0Path(std.testing.allocator, &state, "tools");
    try env.set("PATH", "");

    const root_empty_path = try exec_cmd.setupPath(
        std.testing.allocator,
        &env,
        state,
        config,
        "/",
    );
    defer std.testing.allocator.free(root_empty_path);
    try std.testing.expectEqualStrings("//tools:", root_empty_path);

    try std.testing.expectError(
        error.MissingNullTerminator,
        exec_cmd.collectExeclArgs(
            std.testing.allocator,
            "record",
            &[_]?[]const u8{ "-a", "--stdio" },
        ),
    );

    var overflowing_tail: [exec_cmd.max_execl_slots - 1]?[]const u8 = undefined;
    for (overflowing_tail[0 .. overflowing_tail.len - 1]) |*slot| {
        slot.* = "--bounded";
    }
    overflowing_tail[overflowing_tail.len - 1] = null;

    try std.testing.expectError(
        error.TooManyArguments,
        exec_cmd.collectExeclArgs(
            std.testing.allocator,
            "record",
            overflowing_tail[0..],
        ),
    );
    try std.testing.expectError(
        error.TooManyArguments,
        exec_cmd.buildDeferredExeclCall(
            std.testing.allocator,
            config,
            "record",
            overflowing_tail[0..],
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

    var deferred_execl_command_only = try exec_cmd.buildDeferredExeclCall(
        std.testing.allocator,
        config,
        "record",
        &[_]?[]const u8{null},
    );
    defer deferred_execl_command_only.deinit(std.testing.allocator);
    try std.testing.expectEqual(@as(usize, 3), deferred_execl_command_only.argv.len);
    try std.testing.expectEqualStrings("perf", deferred_execl_command_only.argv[0].?);
    try std.testing.expectEqualStrings("record", deferred_execl_command_only.argv[1].?);
    try std.testing.expectEqual(@as(?[]const u8, null), deferred_execl_command_only.argv[2]);

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

    var deferred_execv_command_only = try exec_cmd.buildDeferredExecvCall(
        std.testing.allocator,
        config,
        &[_][]const u8{},
    );
    defer deferred_execv_command_only.deinit(std.testing.allocator);
    try std.testing.expectEqual(@as(usize, 2), deferred_execv_command_only.argv.len);
    try std.testing.expectEqualStrings("perf", deferred_execv_command_only.argv[0].?);
    try std.testing.expectEqual(@as(?[]const u8, null), deferred_execv_command_only.argv[1]);
}

test "phase 8 exec-cmd shared witness keeps argv0 sentinel path shapes explicit" {
    const config = exec_cmd.Config{
        .exec_name = "perf",
        .prefix = "/usr",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    var rooted = (try exec_cmd.extractArgv0Path(
        std.testing.allocator,
        "/usr/libexec/perf-core/perf",
    )).?;
    defer rooted.deinit(std.testing.allocator);
    try std.testing.expectEqualStrings("perf", rooted.command_name);
    try std.testing.expectEqualStrings("/usr/libexec/perf-core", rooted.argv0_path.?);

    const rooted_search_path = try exec_cmd.buildSearchPath(
        std.testing.allocator,
        "/repo",
        "tools/bin",
        rooted.argv0_path,
        "/usr/bin",
    );
    defer std.testing.allocator.free(rooted_search_path);
    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/usr/libexec/perf-core:/usr/bin",
        rooted_search_path,
    );

    var directory_only = (try exec_cmd.extractArgv0Path(std.testing.allocator, "/tmp/")).?;
    defer directory_only.deinit(std.testing.allocator);
    try std.testing.expectEqualStrings("", directory_only.command_name);
    try std.testing.expectEqualStrings("/tmp", directory_only.argv0_path.?);

    const directory_only_search_path = try exec_cmd.buildSearchPath(
        std.testing.allocator,
        "/repo",
        "tools/bin",
        directory_only.argv0_path,
        "/usr/bin",
    );
    defer std.testing.allocator.free(directory_only_search_path);
    try std.testing.expectEqualStrings("/repo/tools/bin:/tmp:/usr/bin", directory_only_search_path);

    var root_only = (try exec_cmd.extractArgv0Path(std.testing.allocator, "/")).?;
    defer root_only.deinit(std.testing.allocator);
    try std.testing.expectEqualStrings("", root_only.command_name);
    try std.testing.expectEqualStrings("", root_only.argv0_path.?);

    const root_only_search_path = try exec_cmd.buildSearchPath(
        std.testing.allocator,
        "/repo",
        "tools/bin",
        root_only.argv0_path,
        "/usr/bin",
    );
    defer std.testing.allocator.free(root_only_search_path);
    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/usr/bin",
        root_only_search_path,
    );

    const system_prefixed = try exec_cmd.systemPath(
        std.testing.allocator,
        config,
        "bin/perf",
    );
    defer std.testing.allocator.free(system_prefixed);
    try std.testing.expectEqualStrings("/usr/bin/perf", system_prefixed);
}
