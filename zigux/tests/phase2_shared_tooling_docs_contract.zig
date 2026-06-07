const std = @import("std");
const testing = std.testing;

fn readFixture(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, path, allocator, .limited(2 * 1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

fn sectionBetween(haystack: []const u8, start: []const u8, end: []const u8) ![]const u8 {
    const start_index = std.mem.indexOf(u8, haystack, start) orelse return error.MissingSectionStart;
    const after_start = start_index + start.len;
    const rest = haystack[after_start..];
    const end_offset = std.mem.indexOf(u8, rest, end) orelse rest.len;
    return rest[0..end_offset];
}

test "phase2 closure keeps shared tooling packet distinct from genksyms evidence" {
    const closure_note = try readFixture(testing.allocator, "Documentation/zigux/phase2-closure.md");
    defer testing.allocator.free(closure_note);

    const shared_section = try sectionBetween(
        closure_note,
        "## Current Shared Repo-Tooling Evidence",
        "## Shared Replay Routes",
    );

    try expectContains(closure_note, "`PHASE2_STATUS=parked`");
    try expectContains(closure_note, "`PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`");
    try expectBefore(
        closure_note,
        "## Current Genksyms Evidence",
        "## Current Shared Repo-Tooling Evidence",
    );

    const shared_markers = [_][]const u8{
        "`scripts/zigux/check-phase2-tool-manifest.py`",
        "`scripts/zigux/check-phase2-bootstrap-workflow-routes.py`",
        "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
        "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
        "`scripts/zigux/check-phase2-cross.py`",
        "`Documentation/zigux/phase2-fixdep-dual-implementation-survey.md`",
        "`scripts/zigux/check-phase2-fixdep-gate.py`",
        "`scripts/zigux/check-fixdep-diff.py`",
        "`scripts/zigux/artifact_diff.py`",
        "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    };
    for (shared_markers) |marker| {
        try expectContains(shared_section, marker);
    }

    try expectContains(
        shared_section,
        "`PHASE2_SHARED_TOOLING_CHECKERS=python3 scripts/zigux/check-phase2-tool-manifest.py,python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py,python3 scripts/zigux/check-phase2-artifact-tools-manifest.py,python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py,python3 scripts/zigux/check-phase2-cross.py,python3 scripts/zigux/check-phase2-fixdep-gate.py,python3 scripts/zigux/check-fixdep-diff.py`",
    );
}

test "shared replay surfaces agree across scripts root tests root manifest and routes" {
    const scripts_readme = try readFixture(testing.allocator, "scripts/zigux/README.md");
    defer testing.allocator.free(scripts_readme);
    const tests_readme = try readFixture(testing.allocator, "zigux/tests/README.md");
    defer testing.allocator.free(tests_readme);
    const tool_manifest = try readFixture(testing.allocator, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer testing.allocator.free(tool_manifest);

    const scripts_phase2 = try sectionBetween(scripts_readme, "## Phase 2", "## Phase 3");
    const tests_phase2 = try sectionBetween(tests_readme, "## Phase 2 review packet", "## Phase 3 review packet");

    const cross_surface_markers = [_][]const u8{
        "scripts/zigux/check-phase2-tool-manifest.py",
        "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
        "scripts/zigux/check-phase2-cross.py",
        "scripts/zigux/check-phase2-fixdep-gate.py",
        "scripts/zigux/check-fixdep-diff.py",
        "scripts/zigux/artifact_diff.py",
        "zigux/tests/fixtures/phase2_cross_targets.json",
        "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
        "zigux/tests/fixtures/phase2_tool_manifest.json",
        "make -C zigux phase2-toolchain",
        "make -C zigux phase2-tools",
        "make -C zigux phase2-kconfig",
        "make -C zigux phase2-cross",
        "make -C zigux phase2-genksyms",
        "make -C zigux phase2-fixdep",
        "make -C zigux phase2-validate",
        "make -C zigux phase2",
    };

    for (cross_surface_markers) |marker| {
        try expectContains(scripts_phase2, marker);
        try expectContains(tests_phase2, marker);
        try expectContains(tool_manifest, marker);
    }

    try expectContains(tool_manifest, "\"repo_reality_gaps\": []");
    try expectContains(tool_manifest, "\"scope\": \"current directly readable scripts-root toolchain, local-archive, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, fixdep, and tranche-closure reminder packet\"");
    try expectContains(tool_manifest, "\"status\": \"active\"");
}

test "makefile and workflow keep phase2 shared tooling replay routes executable" {
    const makefile = try readFixture(testing.allocator, "zigux/Makefile");
    defer testing.allocator.free(makefile);
    const workflow = try readFixture(testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer testing.allocator.free(workflow);

    const make_markers = [_][]const u8{
        "phase2-tools:",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",
        "phase2-cross:",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
        "phase2-fixdep: phase2-toolchain",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
        "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
        "phase2: phase2-validate",
    };
    for (make_markers) |marker| {
        try expectContains(makefile, marker);
    }

    const workflow_markers = [_][]const u8{
        "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
        "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
        "run: python3 scripts/zigux/check-phase2-cross.py",
        "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
        "run: python3 scripts/zigux/check-fixdep-diff.py",
        "run: make -C zigux phase2-tools",
        "run: make -C zigux phase2-cross",
        "run: make -C zigux phase2-fixdep",
        "run: make -C zigux phase2-validate",
        "run: make -C zigux phase2",
        "run: python3 scripts/zigux/validate-phase2-closure.py",
    };
    for (workflow_markers) |marker| {
        try expectContains(workflow, marker);
    }

    try expectBefore(workflow, "run: make -C zigux phase2-tools", "run: make -C zigux phase2-validate");
    try expectBefore(workflow, "run: make -C zigux phase2-cross", "run: make -C zigux phase2-validate");
    try expectBefore(workflow, "run: make -C zigux phase2-fixdep", "run: make -C zigux phase2-validate");
}
