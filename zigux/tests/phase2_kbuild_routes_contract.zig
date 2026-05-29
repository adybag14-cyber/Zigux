const std = @import("std");

const rooted_files = [_][]const u8{
    "scripts/zigux/check-phase2-kbuild-routes.py",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
};

const phase2_routes = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
    "phase2",
};

fn readRooted(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.Options.debug_io, path, allocator, .limited(512 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase2 kbuild routes keep checker, workflow, make, and manifest surfaces aligned" {
    const allocator = std.testing.allocator;

    var opened_files: usize = 0;
    inline for (rooted_files) |path| {
        const content = try readRooted(allocator, path);
        defer allocator.free(content);
        try std.testing.expect(content.len > 0);
        opened_files += 1;
    }
    try std.testing.expectEqual(rooted_files.len, opened_files);

    const checker = try readRooted(allocator, "scripts/zigux/check-phase2-kbuild-routes.py");
    defer allocator.free(checker);
    const workflow = try readRooted(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);
    const makefile = try readRooted(allocator, "zigux/Makefile");
    defer allocator.free(makefile);
    const manifest = try readRooted(allocator, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer allocator.free(manifest);

    try expectContains(checker, "Guard the current Phase 2 toolchain and kbuild packet.");
    try expectContains(checker, "WORKFLOW = Path(\".github/workflows/zigux-bootstrap.yml\")");
    try expectContains(checker, "SCRIPTS_README = Path(\"scripts/zigux/README.md\")");
    try expectContains(checker, "MAKEFILE = Path(\"zigux/Makefile\")");
    try expectContains(checker, "SURFACE_PATHS = (");
    try expectContains(checker, "ARCHIVE_SURFACE_PATHS = (");
    try expectContains(checker, "WORKFLOW_LINES = (");
    try expectContains(checker, "MAKEFILE_LINES = (");
    try expectContains(checker, "README_MARKERS = (");
    try expectContains(checker, "PHASE2_KBUILD_ROUTES=pass");
    try expectContains(checker, "PHASE2_KBUILD_ROUTES_SURFACE_COUNT");
    try expectContains(checker, "PHASE2_KBUILD_ROUTES_README_MARKER_COUNT");

    try expectContains(checker, "scripts/zigux/check-phase2-kbuild-routes.py");
    try expectContains(checker, "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py");
    try expectContains(checker, "scripts/zigux/check-phase2-cross-selftest-alignment.py");
    try expectContains(checker, "zigux/tests/fixtures/phase2_tool_manifest.json");

    try expectContains(workflow, "run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test");
    try expectContains(workflow, "run: python3 scripts/zigux/check-phase2-kbuild-routes.py");
    try expectContains(workflow, "run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test");
    try expectContains(workflow, "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py");

    try expectContains(makefile, "phase2-tools:");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py --self-test");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py");
    try expectContains(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");

    try expectContains(manifest, "\"scripts/zigux/check-phase2-kbuild-routes.py\"");
    try expectContains(manifest, "\"make -C zigux phase2-tools\"");
    try expectContains(manifest, "\"make -C zigux phase2-kconfig\"");
    try expectContains(manifest, "\"make -C zigux phase2-cross\"");

    inline for (phase2_routes) |route| {
        try expectContains(makefile, route);
        try expectContains(manifest, route);
    }
}
