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

    var trailing_argv0 = (try exec_cmd.extractArgv0Path(std.testing.allocator, "tools/perf/")) orelse unreachable;
    defer trailing_argv0.deinit(std.testing.allocator);
    try std.testing.expectEqualStrings("tools/perf", trailing_argv0.argv0_path.?);
    try std.testing.expectEqual(@as(usize, 0), trailing_argv0.command_name.len);

    var slash_only = (try exec_cmd.extractArgv0Path(std.testing.allocator, "/")) orelse unreachable;
    defer slash_only.deinit(std.testing.allocator);
    try std.testing.expectEqual(@as(usize, 0), slash_only.argv0_path.?.len);
    try std.testing.expectEqual(@as(usize, 0), slash_only.command_name.len);

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

    var inherited_missing_env = exec_cmd.EnvMap.init(std.testing.allocator);
    defer inherited_missing_env.deinit();

    var inherited_missing_state = exec_cmd.ExecCmdState{};
    defer inherited_missing_state.deinit(std.testing.allocator);

    try exec_cmd.execCmdInit(&inherited_missing_env, config);
    try exec_cmd.setArgvExecPath(
        std.testing.allocator,
        &inherited_missing_env,
        &inherited_missing_state,
        config,
        "tools/bin",
    );

    const inherited_missing = try exec_cmd.setupPath(
        std.testing.allocator,
        &inherited_missing_env,
        inherited_missing_state,
        config,
        "/repo",
    );
    defer std.testing.allocator.free(inherited_missing);

    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/usr/local/bin:/usr/bin:/bin",
        inherited_missing,
    );
    try std.testing.expectEqualStrings(inherited_missing, inherited_missing_env.get("PATH").?);

    var inherited_relative_env = exec_cmd.EnvMap.init(std.testing.allocator);
    defer inherited_relative_env.deinit();

    var inherited_relative_state = exec_cmd.ExecCmdState{};
    defer inherited_relative_state.deinit(std.testing.allocator);

    try exec_cmd.execCmdInit(&inherited_relative_env, config);
    try exec_cmd.setArgv0Path(std.testing.allocator, &inherited_relative_state, "scripts");
    try inherited_relative_env.set("PERF_EXEC_PATH", "tools/bin");
    try inherited_relative_env.set("PATH", "/usr/bin");

    const inherited_relative = try exec_cmd.setupPath(
        std.testing.allocator,
        &inherited_relative_env,
        inherited_relative_state,
        config,
        "/repo",
    );
    defer std.testing.allocator.free(inherited_relative);

    try std.testing.expectEqualStrings("tools/bin", inherited_relative_env.get("PERF_EXEC_PATH").?);
    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/repo/scripts:/usr/bin",
        inherited_relative,
    );
    try std.testing.expectEqualStrings(inherited_relative, inherited_relative_env.get("PATH").?);

    var root_cwd_env = exec_cmd.EnvMap.init(std.testing.allocator);
    defer root_cwd_env.deinit();

    var root_cwd_state = exec_cmd.ExecCmdState{};
    defer root_cwd_state.deinit(std.testing.allocator);

    try exec_cmd.execCmdInit(&root_cwd_env, config);
    try exec_cmd.setArgvExecPath(std.testing.allocator, &root_cwd_env, &root_cwd_state, config, "tools/bin");
    try exec_cmd.setArgv0Path(std.testing.allocator, &root_cwd_state, "scripts");
    try root_cwd_env.set("PATH", "/usr/bin");

    const root_cwd = try exec_cmd.setupPath(
        std.testing.allocator,
        &root_cwd_env,
        root_cwd_state,
        config,
        "/",
    );
    defer std.testing.allocator.free(root_cwd);

    try std.testing.expectEqualStrings(
        "//tools/bin://scripts:/usr/bin",
        root_cwd,
    );
    try std.testing.expectEqualStrings(root_cwd, root_cwd_env.get("PATH").?);
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

    var empty_pwd_env = exec_cmd.EnvMap.init(std.testing.allocator);
    defer empty_pwd_env.deinit();

    var empty_pwd_state = exec_cmd.ExecCmdState{};
    defer empty_pwd_state.deinit(std.testing.allocator);

    try exec_cmd.execCmdInit(&empty_pwd_env, config);
    try exec_cmd.setArgvExecPath(std.testing.allocator, &empty_pwd_env, &empty_pwd_state, config, "tools/bin");
    try exec_cmd.setArgv0Path(std.testing.allocator, &empty_pwd_state, "scripts");
    try empty_pwd_env.set("PATH", "/usr/bin");

    const empty_pwd = try exec_cmd.setupPathWithPwd(
        std.testing.allocator,
        &empty_pwd_env,
        empty_pwd_state,
        config,
        "/repo",
        "",
        cwd_identity,
        matching_pwd_identity,
    );
    defer std.testing.allocator.free(empty_pwd);

    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/repo/scripts:/usr/bin",
        empty_pwd,
    );
    try std.testing.expectEqualStrings(empty_pwd, empty_pwd_env.get("PATH").?);
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
    try std.testing.expectEqualStrings(
        "/repo",
        exec_cmd.choosePwdCwd("/repo", "", true),
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

    var last_valid_tail: [30]?[]const u8 = undefined;
    for (last_valid_tail[0..29]) |*slot| {
        slot.* = "x";
    }
    last_valid_tail[29] = null;

    const last_valid = try exec_cmd.collectExeclArgs(
        std.testing.allocator,
        "record",
        &last_valid_tail,
    );
    defer std.testing.allocator.free(last_valid);

    try std.testing.expectEqual(@as(usize, exec_cmd.max_execl_slots - 1), last_valid.len);
    try std.testing.expectEqualStrings("record", last_valid[0].?);
    try std.testing.expectEqualStrings("x", last_valid[exec_cmd.max_execl_slots - 3].?);
    try std.testing.expectEqual(@as(?[]const u8, null), last_valid[exec_cmd.max_execl_slots - 2]);

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

test "phase 8 exec-cmd keeps the deferred execl handoff helper below launch behavior" {
    const config = exec_cmd.Config{
        .exec_name = "perf",
        .prefix = "/usr/libexec/perf-core",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    var deferred = try exec_cmd.buildDeferredExeclCall(
        std.testing.allocator,
        config,
        "record",
        &[_]?[]const u8{ "-a", "--stdio", null, "--ignored" },
    );
    defer deferred.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 5), deferred.argv.len);
    try std.testing.expectEqualStrings("perf", deferred.argv[0].?);
    try std.testing.expectEqualStrings("record", deferred.argv[1].?);
    try std.testing.expectEqualStrings("-a", deferred.argv[2].?);
    try std.testing.expectEqualStrings("--stdio", deferred.argv[3].?);
    try std.testing.expectEqual(@as(?[]const u8, null), deferred.argv[4]);
}

test "phase 8 exec-cmd keeps the deferred execl handoff explicit for empty command tails" {
    const config = exec_cmd.Config{
        .exec_name = "perf",
        .prefix = "/usr/libexec/perf-core",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };

    var deferred = try exec_cmd.buildDeferredExeclCall(
        std.testing.allocator,
        config,
        "version",
        &[_]?[]const u8{null},
    );
    defer deferred.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 3), deferred.argv.len);
    try std.testing.expectEqualStrings("perf", deferred.argv[0].?);
    try std.testing.expectEqualStrings("version", deferred.argv[1].?);
    try std.testing.expectEqual(@as(?[]const u8, null), deferred.argv[2]);
}

test "phase 8 exec-cmd keeps the combined deferred planner aligned with PATH setup" {
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

    var plan = try exec_cmd.planDeferredExecvCall(
        std.testing.allocator,
        &env,
        state,
        config,
        "/repo",
        &[_][]const u8{ "record", "-a" },
    );
    defer plan.deinit(std.testing.allocator);

    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/repo/scripts:/usr/bin:/bin",
        plan.path,
    );
    try std.testing.expectEqualStrings(plan.path, env.get("PATH").?);
    try std.testing.expectEqual(@as(usize, 4), plan.call.argv.len);
    try std.testing.expectEqualStrings("perf", plan.call.argv[0].?);
    try std.testing.expectEqualStrings("record", plan.call.argv[1].?);
    try std.testing.expectEqualStrings("-a", plan.call.argv[2].?);
    try std.testing.expectEqual(@as(?[]const u8, null), plan.call.argv[3]);
}

test "phase 8 exec-cmd docs keep the deferred execution boundary explicit" {
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
    try expectContains(slice_note, "deferred execution");
    try expectContains(slice_note, "Phase 14");
    try expectContains(slice_note, "kernel/workqueue.c");
    try expectContains(slice_note, "`execv_cmd()`");
    try expectContains(slice_note, "`execvp()`");
    try expectContains(slice_note, "scheduler-facing transport ownership");
    try expectContains(slice_note, "empty-tail `execl_cmd(cmd, NULL)` shape");
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
