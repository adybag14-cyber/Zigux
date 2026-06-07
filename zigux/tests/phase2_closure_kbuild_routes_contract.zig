const std = @import("std");

const repo_paths = struct {
    const checker = "scripts/zigux/check-phase2-kbuild-routes.py";
    const closure_note = "Documentation/zigux/phase2-closure.md";
    const scripts_readme = "scripts/zigux/README.md";
    const tests_readme = "zigux/tests/README.md";
    const manifest = "zigux/tests/fixtures/phase2_tool_manifest.json";
    const makefile = "zigux/Makefile";
    const workflow = ".github/workflows/zigux-bootstrap.yml";
};

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn indexOfRequired(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    };
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = try indexOfRequired(haystack, earlier);
    const later_index = try indexOfRequired(haystack, later);
    try std.testing.expect(earlier_index < later_index);
}

fn expectExactLine(text: []const u8, marker: []const u8) !void {
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        const trimmed = std.mem.trim(u8, line, " \t\r");
        if (std.mem.eql(u8, trimmed, marker)) return;
    }
    std.debug.print("missing exact line: {s}\n", .{marker});
    return error.MissingExactLine;
}

test "kbuild checker keeps its current public contract vocabulary" {
    const allocator = std.testing.allocator;
    const checker = try readFile(allocator, repo_paths.checker);
    defer allocator.free(checker);

    try expectContains(checker, "\"\"\"Guard the current Phase 2 toolchain and kbuild packet.\"\"\"");
    try expectContains(checker, "SURFACE_PATHS = (");
    try expectContains(checker, "ARCHIVE_SURFACE_PATHS = (");
    try expectContains(checker, "WORKFLOW_LINES = (");
    try expectContains(checker, "README_MARKERS = (");
    try expectContains(checker, "MAKEFILE_LINES = (");
    try expectContains(checker, "FORBIDDEN_MAKEFILE_LINES = (");
    try expectContains(checker, "PHASE2_KBUILD_ROUTES_SELF_TEST=pass");
    try expectContains(checker, "PHASE2_KBUILD_ROUTES=pass");
    try expectContains(checker, "PHASE2_KBUILD_ROUTES=fail");
    try expectContains(checker, "PHASE2_KBUILD_ROUTES_SURFACE_COUNT");
    try expectContains(checker, "PHASE2_KBUILD_ROUTES_README_MARKER_COUNT");
    try expectContains(checker, "scripts/zigux/check-phase2-kbuild-routes.py");
    try expectContains(checker, "run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test");
    try expectContains(checker, "run: python3 scripts/zigux/check-phase2-kbuild-routes.py");
    try expectContains(checker, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py --self-test");
    try expectContains(checker, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py");
}

test "review surfaces expose the kbuild route packet beside the Phase 2 closure tranche" {
    const allocator = std.testing.allocator;
    const closure_note = try readFile(allocator, repo_paths.closure_note);
    defer allocator.free(closure_note);
    const scripts_readme = try readFile(allocator, repo_paths.scripts_readme);
    defer allocator.free(scripts_readme);
    const tests_readme = try readFile(allocator, repo_paths.tests_readme);
    defer allocator.free(tests_readme);
    const manifest = try readFile(allocator, repo_paths.manifest);
    defer allocator.free(manifest);

    try expectContains(closure_note, "PHASE2_STATUS=parked");
    try expectContains(closure_note, "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools");
    try expectContains(closure_note, "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py");

    try expectContains(scripts_readme, "`scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`");
    try expectContains(scripts_readme, "keep the current toolchain and kbuild route guard packet explicit from the scripts root");
    try expectContains(scripts_readme, "keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet");
    try expectNotContains(scripts_readme, "still return missing for `scripts/zigux/check-phase2-kbuild-routes.py`");

    try expectContains(tests_readme, "`scripts/zigux/check-phase2-kbuild-routes.py`");
    try expectContains(tests_readme, "the current directly readable Phase 2 packet is the scripts-root kbuild");
    try expectContains(tests_readme, "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`");

    try expectContains(manifest, "\"scripts/zigux/check-phase2-kbuild-routes.py\"");
    try expectContains(manifest, "\"Keep scripts/zigux/README.md explicit as the shipped scripts-root reminder surface");
    try expectNotContains(manifest, "\"repo_reality_gaps\": [\n    \"scripts/zigux/check-phase2-kbuild-routes.py\"");
}

test "Makefile keeps kbuild checker before downstream Phase 2 route checks" {
    const allocator = std.testing.allocator;
    const makefile = try readFile(allocator, repo_paths.makefile);
    defer allocator.free(makefile);

    try expectExactLine(makefile, "phase2-tools:");
    try expectExactLine(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py --self-test");
    try expectExactLine(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py");
    try expectExactLine(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py --self-test");
    try expectExactLine(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py --self-test");
    try expectExactLine(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
    try expectExactLine(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py");

    try expectBefore(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py --self-test", "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py\n");
    try expectBefore(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py\n", "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py --self-test");
    try expectBefore(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py\n", "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py --self-test");
    try expectBefore(makefile, "phase2-tools:", "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
}

test "bootstrap workflow runs kbuild guard before Phase 2 make routes and validators" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, repo_paths.workflow);
    defer allocator.free(workflow);

    try expectContains(workflow, "Self-test current Phase 2 kbuild routes checker");
    try expectExactLine(workflow, "run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test");
    try expectContains(workflow, "Check current Phase 2 kbuild packet");
    try expectExactLine(workflow, "run: python3 scripts/zigux/check-phase2-kbuild-routes.py");
    try expectExactLine(workflow, "run: make -C zigux phase2-tools");
    try expectExactLine(workflow, "run: python3 scripts/zigux/validate-phase2.py");
    try expectExactLine(workflow, "run: python3 scripts/zigux/validate-phase2-closure.py");

    try expectBefore(workflow, "run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test", "run: python3 scripts/zigux/check-phase2-kbuild-routes.py\n");
    try expectBefore(workflow, "run: python3 scripts/zigux/check-phase2-kbuild-routes.py\n", "run: make -C zigux phase2-tools");
    try expectBefore(workflow, "run: make -C zigux phase2-tools", "run: python3 scripts/zigux/validate-phase2.py");
    try expectBefore(workflow, "run: python3 scripts/zigux/validate-phase2.py", "run: python3 scripts/zigux/validate-phase2-closure.py");
}
