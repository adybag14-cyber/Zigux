const std = @import("std");
const exec_cmd = @import("exec_cmd");

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

test "phase 8 exec-cmd slice note keeps the helper-vs-phase ownership boundary explicit" {
    const io = std.testing.io;
    const slice = try std.Io.Dir.cwd().readFileAlloc(
        io,
        "Documentation/zigux/phase8-exec-cmd-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(slice);

    try std.testing.expect(std.mem.indexOf(u8, slice, "PHASE8_SLICE=exec-cmd-deferred-exec-packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice, "helper-first, output-stable deferred-exec planning") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice, "helper-local unit tests in `tools/lib/subcmd/exec-cmd.zig` own the low-level trailing-colon `PATH` edge") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice, "rooted `argv[0]` slash-avoidance edge") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice, "logical-`PWD` alias acceptance proof") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice, "the `collectExeclArgs()` overflow and missing-null guards") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice, "focused Phase 8 replay stays on the integrated deferred-exec packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice, "live C helper anchors, checklist hook, and validator route") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice, "without widening into process-launch side effects") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice, "stops before any ownership of `execl_cmd()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice, "direct varargs launch path") != null);
}

test "phase 8 exec-cmd deferred boundary note still matches the live C helper anchors" {
    const io = std.testing.io;
    const slice = try std.Io.Dir.cwd().readFileAlloc(
        io,
        "Documentation/zigux/phase8-exec-cmd-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(slice);

    const c_helper = try std.Io.Dir.cwd().readFileAlloc(
        io,
        "tools/lib/subcmd/exec-cmd.c",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(c_helper);

    try std.testing.expect(std.mem.indexOf(u8, c_helper, "int execv_cmd") != null);
    try std.testing.expect(std.mem.indexOf(u8, c_helper, "execvp(") != null);
    try std.testing.expect(std.mem.indexOf(u8, c_helper, "int execl_cmd") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice, "`execv_cmd()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice, "`execvp()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice, "`execl_cmd()`") != null);
}

test "phase 8 exec-cmd checklist hook keeps the parked deferred-exec packet explicit" {
    const io = std.testing.io;
    const checklist = try std.Io.Dir.cwd().readFileAlloc(
        io,
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(checklist);

    try std.testing.expect(std.mem.indexOf(u8, checklist, "if the change touches the parked Phase 8 `exec-cmd` packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "`make -C zigux phase8-exec-cmd-test`") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "`make -C zigux phase8-validate`") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "helper-first, output-stable deferred-exec planning packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "without widening into direct process-launch parity") != null);
}
