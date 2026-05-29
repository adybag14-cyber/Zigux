const std = @import("std");

const closure_note_path = "Documentation/zigux/phase2-closure.md";
const workflow_path = ".github/workflows/zigux-bootstrap.yml";
const makefile_path = "zigux/Makefile";

const closure_replay_commands = [_][]const u8{
    "python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "python3 scripts/zigux/check-genksyms-bridge.py",
    "python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "zig test scripts/zigux/genksyms.zig",
    "make -C zigux phase2-genksyms",
};

const workflow_replay_lines = [_][]const u8{
    "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "run: python3 scripts/zigux/check-genksyms-bridge.py",
    "run: zig test scripts/zigux/genksyms.zig",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "run: make -C zigux phase2-genksyms",
    "run: python3 scripts/zigux/validate-phase2-closure.py --self-test",
    "run: python3 scripts/zigux/validate-phase2-closure.py",
};

const makefile_replay_lines = [_][]const u8{
    "phase2-genksyms: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
};

const shared_make_routes = [_][]const u8{
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
};

const workflow_shared_make_route_lines = [_][]const u8{
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-validate",
    "run: make -C zigux phase2",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(256 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectExactLineOnce(text: []const u8, expected: []const u8) !void {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), expected)) {
            count += 1;
        }
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

test "phase2 closure genksyms replay commands stay mirrored in bootstrap workflow" {
    const closure_note = try readRepoFile(std.testing.allocator, closure_note_path);
    defer std.testing.allocator.free(closure_note);
    const workflow = try readRepoFile(std.testing.allocator, workflow_path);
    defer std.testing.allocator.free(workflow);

    try expectContains(closure_note, "## Current Genksyms Evidence");
    for (closure_replay_commands) |command| {
        try expectContains(closure_note, command);
    }
    for (workflow_replay_lines) |line| {
        try expectExactLineOnce(workflow, line);
    }
}

test "phase2 genksyms make route keeps standalone proof tests before closure validation" {
    const makefile = try readRepoFile(std.testing.allocator, makefile_path);
    defer std.testing.allocator.free(makefile);

    for (makefile_replay_lines) |line| {
        try expectContains(makefile, line);
    }
    try expectContains(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
}

test "phase2 closure shared make routes stay replayable from workflow and makefile" {
    const closure_note = try readRepoFile(std.testing.allocator, closure_note_path);
    defer std.testing.allocator.free(closure_note);
    const workflow = try readRepoFile(std.testing.allocator, workflow_path);
    defer std.testing.allocator.free(workflow);
    const makefile = try readRepoFile(std.testing.allocator, makefile_path);
    defer std.testing.allocator.free(makefile);

    try expectContains(closure_note, "PHASE2_SHARED_MAKE_ROUTES=");
    for (shared_make_routes) |route| {
        try expectContains(closure_note, route);
    }
    for (workflow_shared_make_route_lines) |line| {
        try expectExactLineOnce(workflow, line);
    }
    try expectContains(makefile, ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2");
}
