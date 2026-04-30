const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 8 bridge boundary survey keeps the roadmap-backed cross-slice packet explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const roadmap = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(roadmap);

    const tests_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/README.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(tests_readme);

    const scripts_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/README.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(scripts_readme);

    const docs_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/README.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(docs_readme);

    const bridge_boundary = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(bridge_boundary);

    const phase8_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase8_build.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(phase8_build);

    try expectContains(roadmap, "## Phase 8: Userspace-Adjacent Tooling Expansion");
    try expectContains(roadmap, "tools/lib/subcmd/exec-cmd.c");
    try expectContains(roadmap, "tools/lib/subcmd/help.c");
    try expectContains(roadmap, "tools/lib/bpf/libbpf.c");
    try expectContains(roadmap, "tools/lib/subcmd/*.zig");
    try expectContains(roadmap, "tools/lib/bpf/zigux_segments/");

    try expectContains(tests_readme, "zigux/tests/phase8_bridge_boundary_survey.zig");
    try expectContains(tests_readme, "bridge-boundary survey drift is reviewable");
    try expectContains(tests_readme, "zigux/tests/phase8_build.zig");
    try expectContains(scripts_readme, "zigux/tests/phase8_bridge_boundary_survey.zig");
    try expectContains(scripts_readme, "parked command-preparation and deferred handle-lifecycle boundary");
    try expectContains(docs_readme, "zigux/tests/phase8_bridge_boundary_survey.zig");

    try expectContains(bridge_boundary, "ExtractArgv0Result.command_name");
    try expectContains(bridge_boundary, "Config.exec_path_env");
    try expectContains(bridge_boundary, "buildSearchPath()");
    try expectContains(bridge_boundary, "resolveTerminalDimensions()");
    try expectContains(bridge_boundary, "buildCurrentProcessFdinfoPath()");
    try expectContains(bridge_boundary, "chooseReusedMapName()");
    try expectContains(bridge_boundary, "planTokenPreparation()");
    try expectContains(bridge_boundary, "classifyTokenPreparationFailure()");
    try expectContains(bridge_boundary, "execvp()");
    try expectContains(bridge_boundary, "/proc/.../fdinfo");
    try expectContains(bridge_boundary, "perf_buffer__poll(timeout_ms)");

    try expectContains(phase8_build, "phase8_bridge_boundary_survey.zig");
    try expectContains(phase8_build, "phase8-bridge-boundary-survey-tests");
    try expectContains(phase8_build, "run_bridge_boundary_survey_tests.step");
}

test "phase 8 bridge boundary survey evidence still matches the live helper anchors" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const bridge_boundary = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(bridge_boundary);

    const exec_cmd_helper = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "tools/lib/subcmd/exec-cmd.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(exec_cmd_helper);

    const help_helper = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "tools/lib/subcmd/help.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(help_helper);

    const file_path_handle_bridge = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(file_path_handle_bridge);

    try expectContains(exec_cmd_helper, "pub const ExtractArgv0Result = struct");
    try expectContains(exec_cmd_helper, "command_name: []const u8,");
    try expectContains(exec_cmd_helper, "exec_path_env: []const u8,");
    try expectContains(exec_cmd_helper, "pub fn buildSearchPath(");

    try expectContains(help_helper, "pub fn resolveTerminalDimensions(");

    try expectContains(file_path_handle_bridge, "pub fn buildCurrentProcessFdinfoPath");
    try expectContains(file_path_handle_bridge, "pub fn chooseReusedMapName");
    try expectContains(file_path_handle_bridge, "pub fn planTokenPreparation");
    try expectContains(file_path_handle_bridge, "pub fn classifyTokenPreparationFailure");

    try expectContains(bridge_boundary, "ExtractArgv0Result.command_name");
    try expectContains(bridge_boundary, "Config.exec_path_env");
    try expectContains(bridge_boundary, "buildSearchPath()");
    try expectContains(bridge_boundary, "resolveTerminalDimensions()");
    try expectContains(bridge_boundary, "buildCurrentProcessFdinfoPath()");
    try expectContains(bridge_boundary, "chooseReusedMapName()");
    try expectContains(bridge_boundary, "planTokenPreparation()");
    try expectContains(bridge_boundary, "classifyTokenPreparationFailure()");
    try expectContains(bridge_boundary, "environment reads or writes");
    try expectContains(bridge_boundary, "`open()` or `close()` ownership");
    try expectContains(bridge_boundary, "`bpf_token_create()` handle lifecycle parity");
}
