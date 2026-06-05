const std = @import("std");

const GateFile = struct {
    path: []const u8,
    contents: []u8,
};

const phase2_tail_steps = [_][]const u8{
    "Run current Phase 2 genksyms make route",
    "Run current Phase 2 validate make route",
    "Run current Phase 2 aggregate make route",
    "Validate current Phase 2 tool packet",
    "Self-test current Phase 2 closure validator",
    "Check current Phase 2 closure packet",
    "Self-test current Phase 1 direct-owner checker",
};

const shared_routes = [_][]const u8{
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
};

fn readFile(path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn loadGateFile(path: []const u8, limit: usize) !GateFile {
    return .{
        .path = path,
        .contents = try readFile(path, limit),
    };
}

fn unloadGateFile(file: GateFile) void {
    std.testing.allocator.free(file.contents);
}

fn indexOfRequired(file: GateFile, needle: []const u8) !usize {
    return std.mem.indexOf(u8, file.contents, needle) orelse {
        std.debug.print("missing marker in {s}: {s}\n", .{ file.path, needle });
        return error.MissingMarker;
    };
}

fn expectContains(file: GateFile, needle: []const u8) !void {
    _ = try indexOfRequired(file, needle);
}

fn expectOrdered(file: GateFile, markers: []const []const u8) !void {
    var previous: usize = 0;
    for (markers, 0..) |marker, index| {
        const current = try indexOfRequired(file, marker);
        if (index != 0) {
            try std.testing.expect(previous < current);
        }
        previous = current;
    }
}

test "phase2 closure workflow tail runs shared replay routes before closure validators" {
    const workflow = try loadGateFile(".github/workflows/zigux-bootstrap.yml", 1024 * 1024);
    defer unloadGateFile(workflow);

    try expectOrdered(workflow, &phase2_tail_steps);

    const phase2_tail_commands = [_][]const u8{
        "run: make -C zigux phase2-genksyms",
        "run: make -C zigux phase2-validate",
        "run: make -C zigux phase2",
        "run: python3 scripts/zigux/validate-phase2.py",
        "run: python3 scripts/zigux/validate-phase2-closure.py --self-test",
        "run: python3 scripts/zigux/validate-phase2-closure.py",
    };
    inline for (phase2_tail_commands) |marker| {
        try expectContains(workflow, marker);
    }

    const shared_tooling_checks = [_][]const u8{
        "python3 scripts/zigux/check-phase2-tool-manifest.py --self-test",
        "python3 scripts/zigux/check-phase2-tool-manifest.py",
        "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
        "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    };
    inline for (shared_tooling_checks) |marker| {
        try expectContains(workflow, marker);
    }

    const tool_manifest = try indexOfRequired(workflow, "python3 scripts/zigux/check-phase2-tool-manifest.py");
    const closure_validator = try indexOfRequired(workflow, "python3 scripts/zigux/validate-phase2-closure.py");
    try std.testing.expect(tool_manifest < closure_validator);
}

test "phase2 closure workflow tail remains aligned with Makefile and closure note" {
    const makefile = try loadGateFile("zigux/Makefile", 384 * 1024);
    defer unloadGateFile(makefile);
    const closure_note = try loadGateFile("Documentation/zigux/phase2-closure.md", 128 * 1024);
    defer unloadGateFile(closure_note);
    const closure_validator = try loadGateFile("scripts/zigux/validate-phase2-closure.py", 384 * 1024);
    defer unloadGateFile(closure_validator);

    try expectContains(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py");
    try expectContains(makefile, "phase2: phase2-validate");

    inline for (shared_routes) |route| {
        try expectContains(closure_note, route);
    }
    try expectContains(closure_note, "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py");

    try expectContains(closure_validator, "\"python3 scripts/zigux/validate-phase2.py\"");
    try expectContains(closure_validator, "\"python3 scripts/zigux/validate-phase2-closure.py\"");
    try expectContains(closure_validator, "expected_routes_line = \"PHASE2_SHARED_MAKE_ROUTES=\"");
    try expectContains(closure_validator, "expected_validator_line = \"PHASE2_CLOSURE_VALIDATORS=\"");
}

test "phase2 tool manifest keeps the workflow tail routes visible" {
    const manifest = try loadGateFile("zigux/tests/fixtures/phase2_tool_manifest.json", 1024 * 1024);
    defer unloadGateFile(manifest);

    try expectContains(manifest, "\"phase\": \"Phase 2\"");
    try expectContains(manifest, "\"make_wrappers\"");
    try expectContains(manifest, "\"validators\"");
    try expectContains(manifest, "\"scripts/zigux/validate-phase2.py\"");
    try expectContains(manifest, "\"scripts/zigux/validate-phase2-closure.py\"");

    inline for (shared_routes) |route| {
        try expectContains(manifest, route);
    }
}
