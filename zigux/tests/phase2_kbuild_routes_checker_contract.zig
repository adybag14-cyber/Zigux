const std = @import("std");

const max_file_size = 2 * 1024 * 1024;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn expectExactLineCount(haystack: []const u8, marker: []const u8, expected: usize) !void {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), marker)) {
            count += 1;
        }
    }
    try std.testing.expectEqual(expected, count);
}

fn expectExactLineOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    var first_line: ?usize = null;
    var second_line: ?usize = null;
    var line_index: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| : (line_index += 1) {
        const trimmed = std.mem.trim(u8, line, " \t\r");
        if (first_line == null and std.mem.eql(u8, trimmed, first)) {
            first_line = line_index;
        }
        if (second_line == null and std.mem.eql(u8, trimmed, second)) {
            second_line = line_index;
        }
    }
    try std.testing.expect(first_line != null);
    try std.testing.expect(second_line != null);
    try std.testing.expect(first_line.? < second_line.?);
}

test "kbuild checker owns the current Phase 2 route packet" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase2-kbuild-routes.py");
    defer allocator.free(checker);

    try expectContains(checker, "\"\"\"Guard the current Phase 2 toolchain and kbuild packet.\"\"\"");
    try expectContains(checker, "SURFACE_PATHS = (");
    try expectContains(checker, "ARCHIVE_SURFACE_PATHS = (");
    try expectContains(checker, "WORKFLOW_LINES = (");
    try expectContains(checker, "README_MARKERS = (");
    try expectContains(checker, "MAKEFILE_LINES = (");
    try expectContains(checker, "FORBIDDEN_MAKEFILE_LINES = (");

    try expectContains(checker, "Path(\"Documentation/zigux/phase2-closure.md\")");
    try expectContains(checker, "Path(\"scripts/zigux/check-phase2-required-make-routes.py\")");
    try expectContains(checker, "Path(\"scripts/zigux/check-phase2-docs-shared-reminder.py\")");
    try expectContains(checker, "Path(\"scripts/zigux/check-phase2-bootstrap-workflow-routes.py\")");
    try expectContains(checker, "Path(\"zigux/tests/fixtures/phase2_tool_manifest.json\")");

    try expectContains(checker, "\"run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test\"");
    try expectContains(checker, "\"run: python3 scripts/zigux/check-phase2-kbuild-routes.py\"");
    try expectContains(checker, "\"phase2-tools:\"");
    try expectContains(checker, "\"phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep\"");
    try expectContains(checker, "\"cd $(ZIGUX_ROOT) && zig test scripts/zigux/fixdep.zig\"");

    try expectContains(checker, "PHASE2_KBUILD_ROUTES_SELF_TEST=pass");
    try expectContains(checker, "PHASE2_KBUILD_ROUTES=pass");
    try expectContains(checker, "PHASE2_KBUILD_ROUTES_SURFACE_COUNT=");
    try expectContains(checker, "PHASE2_KBUILD_ROUTES_README_MARKER_COUNT=");

    try expectOrdered(checker, "WORKFLOW_LINES = (", "README_MARKERS = (");
    try expectOrdered(checker, "README_MARKERS = (", "MAKEFILE_LINES = (");
    try expectOrdered(checker, "MAKEFILE_LINES = (", "FORBIDDEN_MAKEFILE_LINES = (");
}

test "scripts and bootstrap docs keep kbuild reminders explicit" {
    const allocator = std.testing.allocator;
    const scripts_readme = try readRepoFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_readme);
    const bootstrap_notes = try readRepoFile(allocator, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    defer allocator.free(bootstrap_notes);
    const closure = try readRepoFile(allocator, "Documentation/zigux/phase2-closure.md");
    defer allocator.free(closure);

    try expectContains(scripts_readme, "`scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-required-make-routes.py`");
    try expectContains(scripts_readme, "`scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-required-make-routes.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`");
    try expectContains(scripts_readme, "keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet");

    try expectContains(bootstrap_notes, "`scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-required-make-routes.py`, `scripts/zigux/check-phase2-bootstrap-workflow-routes.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`");
    try expectContains(bootstrap_notes, "`make -C zigux phase2-toolchain`");
    try expectContains(bootstrap_notes, "`make -C zigux phase2-tools`");
    try expectContains(bootstrap_notes, "`make -C zigux phase2`");
    try expectContains(bootstrap_notes, "kbuild-route reminders");

    try expectContains(closure, "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2");
    try expectContains(closure, "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py");
}

test "workflow and Makefile replay the kbuild route guard exactly once" {
    const allocator = std.testing.allocator;
    const workflow = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);
    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);

    try expectExactLineCount(workflow, "run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test", 1);
    try expectExactLineCount(workflow, "run: python3 scripts/zigux/check-phase2-kbuild-routes.py", 1);
    try expectExactLineOrdered(
        workflow,
        "run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test",
        "run: python3 scripts/zigux/check-phase2-kbuild-routes.py",
    );
    try expectExactLineOrdered(
        workflow,
        "run: python3 scripts/zigux/check-phase2-kbuild-routes.py",
        "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    );

    try expectExactLineCount(makefile, "phase2-tools:", 1);
    try expectExactLineCount(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py --self-test", 1);
    try expectExactLineCount(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py", 1);
    try expectExactLineCount(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep", 1);
    try expectExactLineOrdered(
        makefile,
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py",
    );
    try expectExactLineOrdered(
        makefile,
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py --self-test",
    );
    try expectNotContains(makefile, "cd $(ZIGUX_ROOT) && zig test scripts/zigux/fixdep.zig");
    try expectContains(makefile, "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/fixdep.zig");
}

test "required route companion stays a separate route source of truth" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase2-required-make-routes.py");
    defer allocator.free(checker);

    try expectContains(checker, "Guard the rematerialized Phase 2 make-wrapper packet and toolchain lane boundary");
    try expectContains(checker, "CURRENT_REQUIRED_MAKE_ROUTES = (");
    try expectContains(checker, "\"phase2-tools\"");
    try expectContains(checker, "\"phase2-validate\"");
    try expectContains(checker, "PHASE2_REQUIRED_MAKE_ROUTES_SELF_TEST=pass");
    try expectContains(checker, "PHASE2_TOOLCHAIN_ROUTE_BOUNDARY=bounded");
    try expectOrdered(checker, "CURRENT_REQUIRED_MAKE_ROUTES = (", "TOOLCHAIN_ALLOWED_RECIPE_LINES = (");
    try expectOrdered(checker, "TOOLCHAIN_ALLOWED_RECIPE_LINES = (", "MAKEFILE_MARKERS = (");
}
