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

test "phase 8 exec-cmd focused replay keeps deferred path preparation and argv handoff aligned with exec-cmd.c" {
    const config = exec_cmd.Config{
        .exec_name = "perf",
        .prefix = "/usr/libexec/perf-core",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    const cwd_identity = exec_cmd.FileIdentity{ .device = 11, .inode = 7 };
    const matching_pwd_identity = exec_cmd.FileIdentity{ .device = 11, .inode = 7 };

    var logical_env = exec_cmd.EnvMap.init(std.testing.allocator);
    defer logical_env.deinit();

    var logical_state = exec_cmd.ExecCmdState{};
    defer logical_state.deinit(std.testing.allocator);

    try exec_cmd.execCmdInit(&logical_env, config);
    try exec_cmd.setArgvExecPath(std.testing.allocator, &logical_env, &logical_state, config, "tools/bin");
    try exec_cmd.setArgv0Path(std.testing.allocator, &logical_state, "scripts");
    try logical_env.set("PATH", "/usr/bin");

    const logical_path = try exec_cmd.setupPathWithPwd(
        std.testing.allocator,
        &logical_env,
        logical_state,
        config,
        "/repo",
        "/logical/repo",
        cwd_identity,
        matching_pwd_identity,
    );
    defer std.testing.allocator.free(logical_path);

    try std.testing.expectEqualStrings(
        "/logical/repo/tools/bin:/logical/repo/scripts:/usr/bin",
        logical_path,
    );
    try std.testing.expectEqualStrings(logical_path, logical_env.get("PATH").?);

    var deferred_env = exec_cmd.EnvMap.init(std.testing.allocator);
    defer deferred_env.deinit();

    var deferred_state = exec_cmd.ExecCmdState{};
    defer deferred_state.deinit(std.testing.allocator);

    try exec_cmd.execCmdInit(&deferred_env, config);
    try exec_cmd.setArgvExecPath(std.testing.allocator, &deferred_env, &deferred_state, config, "tools/bin");
    try exec_cmd.setArgv0Path(std.testing.allocator, &deferred_state, "scripts");
    try deferred_env.set("PATH", "/usr/bin:/bin");

    var execv_plan = try exec_cmd.planDeferredExecvCall(
        std.testing.allocator,
        &deferred_env,
        deferred_state,
        config,
        "/repo",
        &[_][]const u8{ "record", "-a" },
    );
    defer execv_plan.deinit(std.testing.allocator);

    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/repo/scripts:/usr/bin:/bin",
        execv_plan.path,
    );
    try std.testing.expectEqualStrings(execv_plan.path, deferred_env.get("PATH").?);
    try std.testing.expectEqual(@as(usize, 4), execv_plan.call.argv.len);
    try std.testing.expectEqualStrings("perf", execv_plan.call.argv[0].?);
    try std.testing.expectEqualStrings("record", execv_plan.call.argv[1].?);
    try std.testing.expectEqualStrings("-a", execv_plan.call.argv[2].?);
    try std.testing.expectEqual(@as(?[]const u8, null), execv_plan.call.argv[3]);

    var execl_env = exec_cmd.EnvMap.init(std.testing.allocator);
    defer execl_env.deinit();

    var execl_state = exec_cmd.ExecCmdState{};
    defer execl_state.deinit(std.testing.allocator);

    try exec_cmd.execCmdInit(&execl_env, config);
    try exec_cmd.setArgvExecPath(std.testing.allocator, &execl_env, &execl_state, config, "tools/bin");
    try exec_cmd.setArgv0Path(std.testing.allocator, &execl_state, "scripts");
    try execl_env.set("PATH", "/usr/bin:/bin");

    var execl_plan = try exec_cmd.planDeferredExeclCall(
        std.testing.allocator,
        &execl_env,
        execl_state,
        config,
        "/repo",
        "record",
        &[_]?[]const u8{ "-a", "--stdio", null, "--ignored" },
    );
    defer execl_plan.deinit(std.testing.allocator);

    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/repo/scripts:/usr/bin:/bin",
        execl_plan.path,
    );
    try std.testing.expectEqualStrings(execl_plan.path, execl_env.get("PATH").?);
    try std.testing.expectEqual(@as(usize, 5), execl_plan.call.argv.len);
    try std.testing.expectEqualStrings("perf", execl_plan.call.argv[0].?);
    try std.testing.expectEqualStrings("record", execl_plan.call.argv[1].?);
    try std.testing.expectEqualStrings("-a", execl_plan.call.argv[2].?);
    try std.testing.expectEqualStrings("--stdio", execl_plan.call.argv[3].?);
    try std.testing.expectEqual(@as(?[]const u8, null), execl_plan.call.argv[4]);

    var execl_call = try exec_cmd.buildDeferredExeclCall(
        std.testing.allocator,
        config,
        "record",
        &[_]?[]const u8{ "-a", "--stdio", null, "--ignored" },
    );
    defer execl_call.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 5), execl_call.argv.len);
    try std.testing.expectEqualStrings("perf", execl_call.argv[0].?);
    try std.testing.expectEqualStrings("record", execl_call.argv[1].?);
    try std.testing.expectEqualStrings("-a", execl_call.argv[2].?);
    try std.testing.expectEqualStrings("--stdio", execl_call.argv[3].?);
    try std.testing.expectEqual(@as(?[]const u8, null), execl_call.argv[4]);
}

test "phase 8 exec-cmd docs keep the parked deferred execution boundary explicit" {
    const slice_note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-exec-cmd-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(slice_note);

    try expectContains(slice_note, "PHASE8_STATUS=parked");
    try expectContains(slice_note, "PHASE8_SLICE=exec-cmd-tooling-parked");
    try expectContains(slice_note, "tools/lib/subcmd/exec-cmd.zig");
    try expectContains(slice_note, "zigux/tests/phase8_exec_cmd.zig");
    try expectContains(slice_note, "zigux/tests/phase8_exec_cmd_only_build.zig");
    try expectContains(slice_note, "deferred execution");
    try expectContains(slice_note, "make -C zigux phase8-exec-cmd-test");
    try expectContains(slice_note, "Phase 14");
    try expectContains(slice_note, "kernel/workqueue.c");
    try expectContains(slice_note, "`execv_cmd()`");
    try expectContains(slice_note, "`execvp()`");
    try expectContains(slice_note, "scheduler-facing transport ownership");
    try expectContains(slice_note, "empty-tail `execl_cmd(cmd, NULL)` shape");
    try expectContains(slice_note, "`planDeferredExeclCall()`");
}

test "phase 8 exec-cmd review checklist keeps deferred handoff review wording aligned" {
    const review_checklist = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/review-checklist.md",
        64 * 1024,
    );
    defer std.testing.allocator.free(review_checklist);

    try expectContains(review_checklist, "parked Phase 8 `exec-cmd` helper packet");
    try expectContains(review_checklist, "Documentation/zigux/phase8-exec-cmd-slice.md");
    try expectContains(review_checklist, "zigux/tests/phase8_exec_cmd.zig");
    try expectContains(review_checklist, "deferred execution helper-only");
    try expectContains(review_checklist, "kernel/workqueue.c");
    try expectContains(review_checklist, "`execv_cmd()`");
    try expectContains(review_checklist, "`execl_cmd()`");
    try expectContains(review_checklist, "direct `execvp()` side effects");
    try expectContains(review_checklist, "queue ownership");
    try expectContains(review_checklist, "scheduler-facing transport claims");
}

test "phase 8 exec-cmd build wiring keeps focused and shared gates explicit" {
    const focused_build = try readWorkspaceFile(
        std.testing.allocator,
        "zigux/tests/phase8_exec_cmd_only_build.zig",
        16 * 1024,
    );
    defer std.testing.allocator.free(focused_build);

    try expectContains(focused_build, "../../tools/lib/subcmd/exec-cmd.zig");
    try expectContains(focused_build, "phase8_exec_cmd.zig");
    try expectContains(focused_build, "phase8-exec-cmd-tests");
    try expectContains(focused_build, "Run focused Phase 8 exec-cmd tests");

    const shared_build = try readWorkspaceFile(
        std.testing.allocator,
        "zigux/tests/phase8_build.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(shared_build);

    try expectContains(shared_build, "../../tools/lib/subcmd/exec-cmd.zig");
    try expectContains(shared_build, "phase8_exec_cmd.zig");
    try expectContains(shared_build, "phase8-exec-cmd-tests");

    const makefile = try readWorkspaceFile(
        std.testing.allocator,
        "zigux/Makefile",
        32 * 1024,
    );
    defer std.testing.allocator.free(makefile);

    try expectContains(makefile, "phase8-exec-cmd-test:");
    try expectContains(makefile, "$(ZIG) test tools/lib/subcmd/exec-cmd.zig");
    try expectContains(makefile, "zigux/tests/phase8_exec_cmd_only_build.zig");
    try expectContains(makefile, "phase8: phase8-validate phase8-exec-cmd-test");
}

test "phase 8 exec-cmd evidence still matches the live C helper anchors" {
    const exec_cmd_c = try readWorkspaceFile(
        std.testing.allocator,
        "tools/lib/subcmd/exec-cmd.c",
        32 * 1024,
    );
    defer std.testing.allocator.free(exec_cmd_c);

    try expectContains(exec_cmd_c, "static const char *get_pwd_cwd(char *buf, size_t sz)");
    try expectContains(exec_cmd_c, "pwd_stat.st_dev == cwd_stat.st_dev");
    try expectContains(exec_cmd_c, "pwd_stat.st_ino == cwd_stat.st_ino");
    try expectContains(exec_cmd_c, "char *get_argv_exec_path(void)");
    try expectContains(exec_cmd_c, "if (argv_exec_path)");
    try expectContains(exec_cmd_c, "env = getenv(subcmd_config.exec_path_env);");
    try expectContains(exec_cmd_c, "if (env && *env)");
    try expectContains(exec_cmd_c, "void setup_path(void)");
    try expectContains(exec_cmd_c, "add_path(&new_path, tmp);");
    try expectContains(exec_cmd_c, "add_path(&new_path, argv0_path);");
    try expectContains(exec_cmd_c, "static const char **prepare_exec_cmd(const char **argv)");
    try expectContains(exec_cmd_c, "int execv_cmd(const char **argv)");
    try expectContains(exec_cmd_c, "execvp(subcmd_config.exec_name, (char **)nargv);");
    try expectContains(exec_cmd_c, "int execl_cmd(const char *cmd,...)");
    try expectContains(exec_cmd_c, "while (argc < MAX_ARGS)");
    try expectContains(exec_cmd_c, "if (MAX_ARGS <= argc)");
}
