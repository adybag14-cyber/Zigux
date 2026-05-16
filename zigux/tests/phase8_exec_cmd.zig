const std = @import("std");
const exec_cmd = @import("exec_cmd");

fn readRepoFile(path: []const u8) ![]u8 {
    const io = std.testing.io;
    return std.Io.Dir.cwd().readFileAlloc(
        io,
        path,
        std.testing.allocator,
        .limited(64 * 1024),
    );
}

test "phase 8 exec-cmd module imports cleanly" {
    _ = exec_cmd;
}

test "phase 8 exec-cmd focused replay keeps the integrated deferred-exec packet reviewable" {
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

    var deferred_execv = try exec_cmd.planDeferredExecvCall(
        std.testing.allocator,
        &env,
        state,
        config,
        "/repo",
        &[_][]const u8{ "record", "-a" },
    );
    defer deferred_execv.deinit(std.testing.allocator);

    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/repo/scripts:/usr/bin:/bin",
        deferred_execv.path,
    );
    try std.testing.expectEqualStrings(deferred_execv.path, env.get("PATH").?);
    try std.testing.expectEqualStrings("perf", deferred_execv.call.argv[0].?);
    try std.testing.expectEqualStrings("record", deferred_execv.call.argv[1].?);
    try std.testing.expectEqualStrings("-a", deferred_execv.call.argv[2].?);
    try std.testing.expectEqual(@as(?[]const u8, null), deferred_execv.call.argv[3]);

    try env.set("PATH", "/usr/bin:/bin");

    var deferred_execl = try exec_cmd.planDeferredExeclCall(
        std.testing.allocator,
        &env,
        state,
        config,
        "/repo",
        "record",
        &[_]?[]const u8{ "-a", "--stdio", null, "--ignored" },
    );
    defer deferred_execl.deinit(std.testing.allocator);

    try std.testing.expectEqualStrings(
        "/repo/tools/bin:/repo/scripts:/usr/bin:/bin",
        deferred_execl.path,
    );
    try std.testing.expectEqualStrings(deferred_execl.path, env.get("PATH").?);
    try std.testing.expectEqualStrings("perf", deferred_execl.call.argv[0].?);
    try std.testing.expectEqualStrings("record", deferred_execl.call.argv[1].?);
    try std.testing.expectEqualStrings("-a", deferred_execl.call.argv[2].?);
    try std.testing.expectEqualStrings("--stdio", deferred_execl.call.argv[3].?);
    try std.testing.expectEqual(@as(?[]const u8, null), deferred_execl.call.argv[4]);
}

test "phase 8 exec-cmd focused replay keeps logical PWD deferred planning explicit" {
    const config = exec_cmd.Config{
        .exec_name = "perf",
        .prefix = "/usr/libexec/perf-core",
        .exec_path = "libexec/perf-core",
        .exec_path_env = "PERF_EXEC_PATH",
    };
    const matching_identity = exec_cmd.FileIdentity{ .device = 3, .inode = 44 };

    var env = exec_cmd.EnvMap.init(std.testing.allocator);
    defer env.deinit();

    var state = exec_cmd.ExecCmdState{};
    defer state.deinit(std.testing.allocator);

    try exec_cmd.execCmdInit(&env, config);
    try exec_cmd.setArgvExecPath(std.testing.allocator, &env, &state, config, "tools/bin");
    try exec_cmd.setArgv0Path(std.testing.allocator, &state, "scripts");
    try env.set("PATH", "/usr/bin");

    var deferred_execv = try exec_cmd.planDeferredExecvCallWithPwd(
        std.testing.allocator,
        &env,
        state,
        config,
        "/repo",
        "/logical/repo",
        matching_identity,
        matching_identity,
        &[_][]const u8{ "record", "-a" },
    );
    defer deferred_execv.deinit(std.testing.allocator);

    try std.testing.expectEqualStrings(
        "/logical/repo/tools/bin:/logical/repo/scripts:/usr/bin",
        deferred_execv.path,
    );
    try std.testing.expectEqualStrings(deferred_execv.path, env.get("PATH").?);
    try std.testing.expectEqualStrings("perf", deferred_execv.call.argv[0].?);
    try std.testing.expectEqualStrings("record", deferred_execv.call.argv[1].?);
    try std.testing.expectEqualStrings("-a", deferred_execv.call.argv[2].?);
    try std.testing.expectEqual(@as(?[]const u8, null), deferred_execv.call.argv[3]);

    try env.set("PATH", "/usr/bin");

    var deferred_execl = try exec_cmd.planDeferredExeclCallWithPwd(
        std.testing.allocator,
        &env,
        state,
        config,
        "/repo",
        "/logical/repo",
        matching_identity,
        matching_identity,
        "record",
        &[_]?[]const u8{ "-a", "--stdio", null },
    );
    defer deferred_execl.deinit(std.testing.allocator);

    try std.testing.expectEqualStrings(
        "/logical/repo/tools/bin:/logical/repo/scripts:/usr/bin",
        deferred_execl.path,
    );
    try std.testing.expectEqualStrings(deferred_execl.path, env.get("PATH").?);
    try std.testing.expectEqualStrings("perf", deferred_execl.call.argv[0].?);
    try std.testing.expectEqualStrings("record", deferred_execl.call.argv[1].?);
    try std.testing.expectEqualStrings("-a", deferred_execl.call.argv[2].?);
    try std.testing.expectEqualStrings("--stdio", deferred_execl.call.argv[3].?);
    try std.testing.expectEqual(@as(?[]const u8, null), deferred_execl.call.argv[4]);
}

test "phase 8 exec-cmd focused replay accepts the last deferred execl handoff before overflow" {
    var argv_tail: [30]?[]const u8 = undefined;
    for (argv_tail[0..29]) |*slot| {
        slot.* = "x";
    }
    argv_tail[29] = null;

    const collected = try exec_cmd.collectExeclArgs(
        std.testing.allocator,
        "record",
        &argv_tail,
    );
    defer std.testing.allocator.free(collected);

    try std.testing.expectEqual(@as(usize, exec_cmd.max_execl_slots - 1), collected.len);
    try std.testing.expectEqualStrings("record", collected[0].?);
    try std.testing.expectEqual(@as(?[]const u8, null), collected[exec_cmd.max_execl_slots - 2]);
}

test "phase 8 exec-cmd slice note keeps the helper-vs-phase ownership boundary explicit" {
    const slice = try readRepoFile("Documentation/zigux/phase8-exec-cmd-slice.md");
    defer std.testing.allocator.free(slice);

    try std.testing.expect(std.mem.indexOf(u8, slice, "PHASE8_SLICE=exec-cmd-deferred-exec-packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice, "helper-first, output-stable deferred-exec planning") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice, "path-resolution, injected environment setup") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice, "`zigux/tests/phase8_exec_cmd.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice, "`zigux/tests/phase8_exec_cmd_only_build.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice, "`make -C zigux phase8-exec-cmd-test`") != null);
}

test "phase 8 exec-cmd deferred boundary note still matches the parked review packet" {
    const slice = try readRepoFile("Documentation/zigux/phase8-exec-cmd-slice.md");
    defer std.testing.allocator.free(slice);

    const helper = try readRepoFile("tools/lib/subcmd/exec-cmd.zig");
    defer std.testing.allocator.free(helper);

    try std.testing.expect(std.mem.indexOf(
        u8,
        slice,
        "original `tools/lib/subcmd/exec-cmd.c` behavior boundary",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        slice,
        "parked review packet, checklist hook, and validator route",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        slice,
        "direct `execvp()` parity, `execv_cmd()` ownership, or process-launch behavior",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        slice,
        "any ownership of `execl_cmd()` or the direct varargs launch path",
    ) != null);
    try std.testing.expect(std.mem.indexOf(u8, helper, "pub fn buildDeferredExecvCall(") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper, "pub fn buildDeferredExeclCall(") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper, "pub fn planDeferredExeclCallWithPwd(") != null);
}

test "phase 8 exec-cmd checklist hook keeps the parked deferred-exec packet explicit" {
    const checklist = try readRepoFile("Documentation/zigux/review-checklist.md");
    defer std.testing.allocator.free(checklist);

    try std.testing.expect(std.mem.indexOf(u8, checklist, "if the change touches the parked Phase 8 `exec-cmd` packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "`zigux/tests/phase8_exec_cmd.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "`zigux/tests/phase8_exec_cmd_only_build.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "`make -C zigux phase8-exec-cmd-test`") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "`make -C zigux phase8-validate`") != null);
}

test "phase 8 exec-cmd scripts root summary keeps the focused replay route explicit" {
    const scripts_root = try readRepoFile("scripts/zigux/README.md");
    defer std.testing.allocator.free(scripts_root);

    try std.testing.expect(std.mem.indexOf(u8, scripts_root, "scripts/zigux/check-phase8-exec-cmd-packet.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, scripts_root, "Documentation/zigux/phase8-exec-cmd-slice.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, scripts_root, "zigux/tests/phase8_exec_cmd.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, scripts_root, "zigux/tests/phase8_exec_cmd_only_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, scripts_root, "make -C zigux phase8-exec-cmd-test") != null);
    try std.testing.expect(std.mem.indexOf(u8, scripts_root, "make -C zigux phase8-validate") != null);
}

test "phase 8 exec-cmd workflow keeps the focused replay ahead of the shared phase 8 bundle" {
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    const validate_index = std.mem.indexOf(u8, workflow, "Validate Phase 8 tooling routes") orelse unreachable;
    const exec_index = std.mem.indexOf(u8, workflow, "Run focused Phase 8 exec-cmd tests") orelse unreachable;
    const phase8_index = std.mem.indexOf(u8, workflow, "Run Phase 8 tooling tests") orelse unreachable;

    try std.testing.expect(validate_index < exec_index);
    try std.testing.expect(exec_index < phase8_index);
    try std.testing.expect(std.mem.indexOf(u8, workflow, "zig test tools/lib/subcmd/exec-cmd.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, workflow, "make -C zigux phase8-exec-cmd-test") != null);
}

test "phase 8 exec-cmd docs root summary keeps the focused replay route explicit" {
    const docs_root = try readRepoFile("Documentation/zigux/README.md");
    defer std.testing.allocator.free(docs_root);

    try std.testing.expect(std.mem.indexOf(u8, docs_root, "Documentation/zigux/phase8-exec-cmd-slice.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, docs_root, "zigux/tests/phase8_exec_cmd.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, docs_root, "zigux/tests/phase8_exec_cmd_only_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, docs_root, "make -C zigux phase8-exec-cmd-test") != null);
    try std.testing.expect(std.mem.indexOf(u8, docs_root, "make -C zigux phase8-validate") != null);
}

test "phase 8 exec-cmd tests root summary keeps the focused replay route explicit" {
    const tests_root = try readRepoFile("zigux/tests/README.md");
    defer std.testing.allocator.free(tests_root);

    try std.testing.expect(std.mem.indexOf(u8, tests_root, "Phase 8 flow") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_root, "`zigux/tests/phase8_exec_cmd.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_root, "`zigux/tests/phase8_exec_cmd_only_build.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_root, "`make -C zigux phase8-exec-cmd-test`") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_root, "`make -C zigux phase8-validate`") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_root, "`make -C zigux phase8`") != null);
}
