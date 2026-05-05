const std = @import("std");
const exec_cmd = @import("exec_cmd");

test "phase 8 exec-cmd module imports cleanly" {
    _ = exec_cmd;
}

test "phase 8 exec-cmd tooling packet covers path resolution and null-terminated argv preparation" {
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

test "phase 8 exec-cmd slice note keeps the tooling-expansion roadmap posture explicit" {
    const io = std.testing.io;
    const slice = try std.Io.Dir.cwd().readFileAlloc(
        io,
        "Documentation/zigux/phase8-exec-cmd-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(slice);

    try std.testing.expect(std.mem.indexOf(u8, slice, "prove Zigux inside serious repo-hosted tooling, not just tiny helpers") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice, "helper-first, output-stable deferred-exec planning") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice, "without widening into process-launch side effects") != null);
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
}

test "phase 8 exec-cmd empty PATH handling preserves the C helper's trailing colon shape" {
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
    try env.set("PATH", "");

    const updated = try exec_cmd.setupPath(
        std.testing.allocator,
        &env,
        state,
        config,
        "/repo",
    );
    defer std.testing.allocator.free(updated);

    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/repo/scripts:",
        updated,
    );
    try std.testing.expectEqualStrings(updated, env.get("PATH").?);
}

test "phase 8 exec-cmd chooses the logical PWD when it resolves to the same directory" {
    const linux = std.os.linux;
    var root_buf: [std.posix.PATH_MAX]u8 = undefined;
    const root = try std.fmt.bufPrintZ(&root_buf, "/tmp/zigux-p8-l06-shared-{d}", .{linux.getpid()});
    try std.testing.expectEqual(.SUCCESS, linux.errno(linux.mkdirat(linux.AT.FDCWD, root, 0o755)));
    defer _ = linux.rmdir(root);

    var repo_buf: [std.posix.PATH_MAX]u8 = undefined;
    const repo = try std.fmt.bufPrintZ(&repo_buf, "{s}/repo", .{root});
    try std.testing.expectEqual(.SUCCESS, linux.errno(linux.mkdirat(linux.AT.FDCWD, repo, 0o755)));
    defer _ = linux.rmdir(repo);

    var link_buf: [std.posix.PATH_MAX]u8 = undefined;
    const link = try std.fmt.bufPrintZ(&link_buf, "{s}/repo-link", .{root});
    try std.testing.expectEqual(.SUCCESS, linux.errno(linux.symlinkat(repo, linux.AT.FDCWD, link)));
    defer _ = linux.unlinkat(linux.AT.FDCWD, link, 0);

    const cwd = repo[0..repo.len];
    const logical_pwd = link[0..link.len];

    try std.testing.expect(exec_cmd.sameLocation(cwd, logical_pwd));
    try std.testing.expectEqualStrings(
        logical_pwd,
        exec_cmd.choosePwdCwdFromFilesystem(cwd, logical_pwd),
    );
    try std.testing.expectEqualStrings(
        cwd,
        exec_cmd.choosePwdCwdFromFilesystem(cwd, "/definitely/missing"),
    );
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
}

test "phase 8 exec-cmd rejects execl-style tails that never terminate" {
    try std.testing.expectError(
        error.MissingNullTerminator,
        exec_cmd.collectExeclArgs(
            std.testing.allocator,
            "record",
            &[_]?[]const u8{ "-a", "--stdio" },
        ),
    );
}
