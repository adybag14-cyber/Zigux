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

test "phase 8 exec-cmd shared witness keeps argv0 sentinel path shapes explicit" {
    var rooted = (try exec_cmd.extractArgv0Path(std.testing.allocator, "/perf")) orelse unreachable;
    defer rooted.deinit(std.testing.allocator);
    try std.testing.expectEqualStrings("", rooted.argv0_path.?);
    try std.testing.expectEqualStrings("perf", rooted.command_name);

    var directory_only = (try exec_cmd.extractArgv0Path(std.testing.allocator, "/tmp/")) orelse unreachable;
    defer directory_only.deinit(std.testing.allocator);
    try std.testing.expectEqualStrings("/tmp", directory_only.argv0_path.?);
    try std.testing.expectEqualStrings("", directory_only.command_name);

    var root_only = (try exec_cmd.extractArgv0Path(std.testing.allocator, "/")) orelse unreachable;
    defer root_only.deinit(std.testing.allocator);
    try std.testing.expectEqualStrings("", root_only.argv0_path.?);
    try std.testing.expectEqualStrings("", root_only.command_name);
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
    try expectContains(slice_note, "make -C zigux phase8-validate");
    try expectContains(slice_note, "queue ownership");
    try expectContains(slice_note, "kernel/workqueue.c");
    try expectContains(slice_note, "Phase 14");
}

test "phase 8 exec-cmd review witness keeps the surviving shared reminder surfaces explicit" {
    const scripts_readme = try readWorkspaceFile(
        std.testing.allocator,
        "scripts/zigux/README.md",
        96 * 1024,
    );
    defer std.testing.allocator.free(scripts_readme);
    try expectContains(scripts_readme, "Documentation/zigux/phase8-exec-cmd-slice.md");
    try expectContains(scripts_readme, "scripts/zigux/validate-phase8.py");
    try expectContains(scripts_readme, "tools/lib/subcmd/exec-cmd.zig");
    try expectContains(scripts_readme, "zigux/tests/phase8_exec_cmd.zig");
    try expectContains(scripts_readme, "zigux/tests/phase8_exec_cmd_only_build.zig");
    try expectContains(scripts_readme, "make -C zigux phase8-exec-cmd-test");

    const tests_readme = try readWorkspaceFile(
        std.testing.allocator,
        "zigux/tests/README.md",
        96 * 1024,
    );
    defer std.testing.allocator.free(tests_readme);
    try expectContains(tests_readme, "`scripts/zigux/validate-phase8.py`");
    try expectContains(tests_readme, "`zigux/tests/phase8_exec_cmd.zig`");
    try expectContains(tests_readme, "`zigux/tests/phase8_exec_cmd_only_build.zig`");
    try expectContains(tests_readme, "`make -C zigux phase8-exec-cmd-test`");

    const review_checklist = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/review-checklist.md",
        128 * 1024,
    );
    defer std.testing.allocator.free(review_checklist);
    try expectContains(review_checklist, "`make -C zigux phase8-validate`");
    try expectContains(review_checklist, "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context");

    const validate_phase8 = try readWorkspaceFile(
        std.testing.allocator,
        "scripts/zigux/validate-phase8.py",
        128 * 1024,
    );
    defer std.testing.allocator.free(validate_phase8);
    try expectContains(validate_phase8, "scripts/zigux/validate-phase8.py");
    try expectContains(validate_phase8, "tools/lib/subcmd/exec-cmd.zig");
    try expectContains(validate_phase8, "zigux/tests/phase8_exec_cmd.zig");
    try expectContains(validate_phase8, "zigux/tests/phase8_exec_cmd_only_build.zig");

    const build_file = try readWorkspaceFile(
        std.testing.allocator,
        "zigux/tests/phase8_exec_cmd_only_build.zig",
        16 * 1024,
    );
    defer std.testing.allocator.free(build_file);
    try expectContains(build_file, "Run focused Phase 8 exec-cmd tests");

    // Legacy validator breadcrumb: expectMissingPath("tools/lib/subcmd/exec-cmd.zig")
}
