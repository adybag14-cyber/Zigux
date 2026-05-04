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
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), full_path, allocator, .limited(limit));
}

test "phase 8 exec-cmd module imports cleanly" {
    _ = exec_cmd;
}

test "phase 8 exec-cmd focused replay keeps inherited relative PERF_EXEC_PATH raw in env while the deferred handoff normalizes PATH" {
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
    try exec_cmd.setArgv0Path(std.testing.allocator, &state, "scripts");
    try env.set("PERF_EXEC_PATH", "tools/bin");
    try env.set("PATH", "/usr/bin:/bin");

    var execv_plan = try exec_cmd.planDeferredExecvCall(
        std.testing.allocator,
        &env,
        state,
        config,
        "/repo",
        &[_][]const u8{ "record", "-a" },
    );
    defer execv_plan.deinit(std.testing.allocator);

    try std.testing.expectEqualStrings("tools/bin", env.get("PERF_EXEC_PATH").?);
    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/repo/scripts:/usr/bin:/bin",
        execv_plan.path,
    );
    try std.testing.expectEqualStrings(execv_plan.path, env.get("PATH").?);
    try std.testing.expectEqual(@as(usize, 4), execv_plan.call.argv.len);
    try std.testing.expectEqualStrings("perf", execv_plan.call.argv[0].?);
    try std.testing.expectEqualStrings("record", execv_plan.call.argv[1].?);
    try std.testing.expectEqualStrings("-a", execv_plan.call.argv[2].?);
    try std.testing.expectEqual(@as(?[]const u8, null), execv_plan.call.argv[3]);
}

test "phase 8 exec-cmd focused replay keeps root cwd relative PATH entries single-slashed" {
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

    var execv_plan = try exec_cmd.planDeferredExecvCall(
        std.testing.allocator,
        &env,
        state,
        config,
        "/",
        &[_][]const u8{"record"},
    );
    defer execv_plan.deinit(std.testing.allocator);

    try std.testing.expectEqualStrings(
        "/tools/bin:/scripts:/usr/bin",
        execv_plan.path,
    );
    try std.testing.expectEqualStrings(execv_plan.path, env.get("PATH").?);
}

test "phase 8 exec-cmd focused replay keeps logical PWD path choice aligned with deferred execv handoff" {
    const config = exec_cmd.Config{
        .exec_name = "perf",
        .prefix = "/usr/libexec/perf-core",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };
    const cwd_identity = exec_cmd.FileIdentity{ .device = 3, .inode = 44 };
    const matching_pwd_identity = exec_cmd.FileIdentity{ .device = 3, .inode = 44 };

    var env = exec_cmd.EnvMap.init(std.testing.allocator);
    defer env.deinit();

    var state = exec_cmd.ExecCmdState{};
    defer state.deinit(std.testing.allocator);

    try exec_cmd.execCmdInit(&env, config);
    try exec_cmd.setArgvExecPath(std.testing.allocator, &env, &state, config, "tools/bin");
    try exec_cmd.setArgv0Path(std.testing.allocator, &state, "scripts");
    try env.set("PATH", "/usr/bin");

    var execv_plan = try exec_cmd.planDeferredExecvCallWithPwd(
        std.testing.allocator,
        &env,
        state,
        config,
        "/repo",
        "/logical/repo",
        cwd_identity,
        matching_pwd_identity,
        &[_][]const u8{ "record", "-a" },
    );
    defer execv_plan.deinit(std.testing.allocator);

    try std.testing.expectEqualStrings(
        "/logical/repo/tools/bin:/logical/repo/scripts:/usr/bin",
        execv_plan.path,
    );
    try std.testing.expectEqualStrings(execv_plan.path, env.get("PATH").?);
    try std.testing.expectEqual(@as(usize, 4), execv_plan.call.argv.len);
    try std.testing.expectEqualStrings("perf", execv_plan.call.argv[0].?);
    try std.testing.expectEqualStrings("record", execv_plan.call.argv[1].?);
    try std.testing.expectEqualStrings("-a", execv_plan.call.argv[2].?);
    try std.testing.expectEqual(@as(?[]const u8, null), execv_plan.call.argv[3]);
}

test "phase 8 exec-cmd docs keep the deferred execution boundary explicit" {
    const slice_note = try readWorkspaceFile(std.testing.allocator, "Documentation/zigux/phase8-exec-cmd-slice.md", 32 * 1024);
    defer std.testing.allocator.free(slice_note);
    try expectContains(slice_note, "PHASE8_STATUS=parked");
    try expectContains(slice_note, "PHASE8_SLICE=exec-cmd-tooling-parked");
    try expectContains(slice_note, "tools/lib/subcmd/exec-cmd.zig");
    try expectContains(slice_note, "zigux/tests/phase8_exec_cmd.zig");
    try expectContains(slice_note, "zigux/tests/phase8_exec_cmd_only_build.zig");
    try expectContains(slice_note, "deferred execution");
    try expectContains(slice_note, "make -C zigux phase8-exec-cmd-test");
    try expectContains(slice_note, "Phase 14");
    try expectContains(slice_note, "repo-hosted userspace-adjacent tooling");
    try expectContains(slice_note, "bounded helper-first port");
    try expectContains(slice_note, "output-stable tooling behavior");
    try expectContains(slice_note, "single-slash root-cwd `/tools/bin:/scripts` shape");
    try expectNotContains(slice_note, "`//tools/bin://scripts` shape");
    try expectNotContains(slice_note, "`//relative` output shape");
    try expectContains(slice_note, "kernel/workqueue.c");
    try expectContains(slice_note, "`kernel/workqueue.c` remains a Phase 14 boundary-study target");
    try expectContains(slice_note, "`execv_cmd()`");
    try expectContains(slice_note, "`execvp()`");
    try expectContains(slice_note, "scheduler-facing transport ownership");
    try expectContains(slice_note, "empty-tail `execl_cmd(cmd, NULL)` shape");
    try expectContains(slice_note, "`planDeferredExeclCall()`");
    try expectContains(slice_note, "`planDeferredExecvCallWithPwd()`");
    try expectContains(slice_note, "`planDeferredExeclCallWithPwd()`");
    try expectContains(slice_note, "helper-local `tools/lib/subcmd/exec-cmd.zig` tests own the detailed");
    try expectContains(slice_note, "while the focused Phase 8 replay stays centered on one integrated deferred handoff");
}

test "phase 8 exec-cmd docs keep the validator alias and Phase 14 wording reviewable" {
    const slice_note = try readWorkspaceFile(std.testing.allocator, "Documentation/zigux/phase8-exec-cmd-slice.md", 32 * 1024);
    defer std.testing.allocator.free(slice_note);
    try expectContains(slice_note, "legacy validator alias: `PHASE8_SLICE=exec-cmd-tooling-starter`");
    const review_checklist = try readWorkspaceFile(std.testing.allocator, "Documentation/zigux/review-checklist.md", 64 * 1024);
    defer std.testing.allocator.free(review_checklist);
    try expectContains(review_checklist, "separate `kernel/workqueue.c` Phase 14 boundary-study target");
}

test "phase 8 exec-cmd review checklist keeps deferred handoff review wording aligned" {
    const review_checklist = try readWorkspaceFile(std.testing.allocator, "Documentation/zigux/review-checklist.md", 64 * 1024);
    defer std.testing.allocator.free(review_checklist);
    try expectContains(review_checklist, "parked Phase 8 `exec-cmd` helper packet");
    try expectContains(review_checklist, "Documentation/zigux/phase8-exec-cmd-slice.md");
    try expectContains(review_checklist, "zigux/tests/phase8_exec_cmd.zig");
    try expectContains(review_checklist, "zigux/tests/phase8_exec_cmd_only_build.zig");
    try expectContains(review_checklist, "deferred execution helper-only");
    try expectContains(review_checklist, "make -C zigux phase8-exec-cmd-test");
    try expectContains(review_checklist, "kernel/workqueue.c");
    try expectContains(review_checklist, "separate `kernel/workqueue.c` Phase 14 boundary-study target");
    try expectContains(review_checklist, "`execv_cmd()`");
    try expectContains(review_checklist, "`execl_cmd()`");
    try expectContains(review_checklist, "direct `execvp()` side effects");
    try expectContains(review_checklist, "queue ownership");
    try expectContains(review_checklist, "scheduler-facing transport claims");
}

test "phase 8 exec-cmd build wiring keeps focused and shared gates explicit" {
    const focused_build = try readWorkspaceFile(std.testing.allocator, "zigux/tests/phase8_exec_cmd_only_build.zig", 16 * 1024);
    defer std.testing.allocator.free(focused_build);
    try expectContains(focused_build, "../../tools/lib/subcmd/exec-cmd.zig");
    try expectContains(focused_build, "phase8_exec_cmd.zig");
    try expectContains(focused_build, "phase8-exec-cmd-tests");
    try expectContains(focused_build, "Run focused Phase 8 exec-cmd tests");

    const shared_build = try readWorkspaceFile(std.testing.allocator, "zigux/tests/phase8_build.zig", 32 * 1024);
    defer std.testing.allocator.free(shared_build);
    try expectContains(shared_build, "../../tools/lib/subcmd/exec-cmd.zig");
    try expectContains(shared_build, "phase8_exec_cmd.zig");
    try expectContains(shared_build, "phase8-exec-cmd-tests");

    const makefile = try readWorkspaceFile(std.testing.allocator, "zigux/Makefile", 32 * 1024);
    defer std.testing.allocator.free(makefile);
    try expectContains(makefile, "phase8-exec-cmd-test:");
    try expectContains(makefile, "$(ZIG) test tools/lib/subcmd/exec-cmd.zig");
    try expectContains(makefile, "zigux/tests/phase8_exec_cmd_only_build.zig");
    try expectContains(makefile, "phase8: phase8-validate phase8-exec-cmd-test");
}

test "phase 8 exec-cmd evidence still matches the live C helper anchors" {
    const exec_cmd_c = try readWorkspaceFile(std.testing.allocator, "tools/lib/subcmd/exec-cmd.c", 32 * 1024);
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
