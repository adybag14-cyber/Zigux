const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn countExactLines(text: []const u8, marker: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), marker)) {
            count += 1;
        }
    }
    return count;
}

fn expectExactLineCount(text: []const u8, marker: []const u8, expected: usize) !void {
    try std.testing.expectEqual(expected, countExactLines(text, marker));
}

fn expectJsonArrayContainsString(object: std.json.ObjectMap, key: []const u8, expected: []const u8) !void {
    const value = object.get(key) orelse return error.MissingJsonKey;
    const array = switch (value) {
        .array => |items| items,
        else => return error.UnexpectedJsonValue,
    };
    for (array.items) |item| {
        switch (item) {
            .string => |actual| {
                if (std.mem.eql(u8, actual, expected)) return;
            },
            else => return error.UnexpectedJsonValue,
        }
    }
    return error.MissingJsonArrayValue;
}

fn expectManifestSurfaceContains(
    manifest: std.json.ObjectMap,
    surface: []const u8,
    expected: []const u8,
) !void {
    const present_surfaces = manifest.get("present_surfaces") orelse return error.MissingJsonKey;
    const surfaces = switch (present_surfaces) {
        .object => |value| value,
        else => return error.UnexpectedJsonValue,
    };
    try expectJsonArrayContainsString(surfaces, surface, expected);
}

fn expectRepoRealityGapsEmpty(manifest: std.json.ObjectMap) !void {
    const gaps_value = manifest.get("repo_reality_gaps") orelse return error.MissingJsonKey;
    const gaps = switch (gaps_value) {
        .array => |items| items,
        else => return error.UnexpectedJsonValue,
    };
    try std.testing.expectEqual(@as(usize, 0), gaps.items.len);
}

const shared_tooling_commands = [_][]const u8{
    "python3 scripts/zigux/check-phase2-tool-manifest.py",
    "python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "python3 scripts/zigux/check-phase2-cross.py",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "python3 scripts/zigux/check-fixdep-diff.py",
};

const shared_tooling_paths = [_][]const u8{
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
};

const shared_tooling_line =
    "PHASE2_SHARED_TOOLING_CHECKERS=" ++
    "python3 scripts/zigux/check-phase2-tool-manifest.py," ++
    "python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py," ++
    "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py," ++
    "python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py," ++
    "python3 scripts/zigux/check-phase2-cross.py," ++
    "python3 scripts/zigux/check-phase2-fixdep-gate.py," ++
    "python3 scripts/zigux/check-fixdep-diff.py";

test "phase 2 closure note publishes the shared tooling checker roster" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 192 * 1024);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "## Current Shared Repo-Tooling Evidence");
    try expectContains(closure_note, shared_tooling_line);
    try expectContains(closure_note, "`PHASE2_SHARED_TOOLING_CHECKERS=");
    try expectContains(closure_note, "`PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py`");

    inline for (shared_tooling_commands) |command| {
        try expectContains(closure_note, command);
        try expectContains(closure_note, "`" ++ command ++ "`");
    }

    try expectBefore(
        closure_note,
        "`python3 scripts/zigux/check-phase2-tool-manifest.py`",
        "`python3 scripts/zigux/check-fixdep-diff.py`",
    );
    try expectBefore(
        closure_note,
        "`PHASE2_SHARED_TOOLING_CHECKERS=",
        "`PHASE2_SHARED_MAKE_ROUTES=",
    );
}

test "closure validator derives the same shared tooling line fail-closed" {
    const validator = try readRepoFile("scripts/zigux/validate-phase2-closure.py", 256 * 1024);
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "SHARED_TOOLING_COMMANDS = (");
    try expectContains(validator, "expected_shared_tooling_line = \"PHASE2_SHARED_TOOLING_CHECKERS=\" + \",\".join(");
    try expectContains(validator, "if expected_shared_tooling_line not in closure_text:");
    try expectContains(validator, "issues.append((\"MISSING_CLOSURE_LINE\", expected_shared_tooling_line))");
    try expectContains(validator, "*SHARED_TOOLING_COMMANDS,");

    inline for (shared_tooling_commands) |command| {
        try expectContains(validator, "\"" ++ command ++ "\",");
    }

    try expectBefore(
        validator,
        "\"python3 scripts/zigux/check-phase2-tool-manifest.py\",",
        "\"python3 scripts/zigux/check-fixdep-diff.py\",",
    );
}

test "tool manifest keeps the shared tooling scripts in current surfaces" {
    const tool_manifest = try readRepoFile("zigux/tests/fixtures/phase2_tool_manifest.json", 384 * 1024);
    defer std.testing.allocator.free(tool_manifest);

    const parsed_manifest = try std.json.parseFromSlice(std.json.Value, std.testing.allocator, tool_manifest, .{});
    defer parsed_manifest.deinit();
    const manifest = switch (parsed_manifest.value) {
        .object => |object| object,
        else => return error.UnexpectedJsonValue,
    };

    try expectRepoRealityGapsEmpty(manifest);
    inline for (shared_tooling_paths) |path| {
        try expectManifestSurfaceContains(manifest, "checkers", path);
    }
    try expectManifestSurfaceContains(manifest, "artifact_support", "scripts/zigux/check-phase2-artifact-tools-manifest.py");
    try expectManifestSurfaceContains(manifest, "artifact_support", "scripts/zigux/artifact_diff.py");
    try expectManifestSurfaceContains(manifest, "cross_route_support", "scripts/zigux/check-phase2-cross.py");
    try expectManifestSurfaceContains(manifest, "fixdep_support", "scripts/zigux/check-phase2-fixdep-gate.py");
    try expectManifestSurfaceContains(manifest, "fixdep_support", "scripts/zigux/check-fixdep-diff.py");
    try expectManifestSurfaceContains(manifest, "closure_notes", "Documentation/zigux/phase2-closure.md");
    try expectManifestSurfaceContains(manifest, "validators", "scripts/zigux/validate-phase2-closure.py");
}

test "workflow and Makefile expose each shared tooling checker once" {
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml", 384 * 1024);
    defer std.testing.allocator.free(workflow);

    const makefile = try readRepoFile("zigux/Makefile", 192 * 1024);
    defer std.testing.allocator.free(makefile);

    inline for (shared_tooling_commands, shared_tooling_paths) |command, path| {
        try expectExactLineCount(workflow, "run: " ++ command, 1);
        try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/" ++ path["scripts/zigux/".len..]);
    }

    try expectBefore(
        workflow,
        "run: python3 scripts/zigux/check-phase2-tool-manifest.py",
        "run: python3 scripts/zigux/validate-phase2-closure.py",
    );
    try expectBefore(
        makefile,
        "phase2-tools:",
        "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    );
}

test "tests root and scripts root keep the shared tooling reminder visible" {
    const tests_readme = try readRepoFile("zigux/tests/README.md", 384 * 1024);
    defer std.testing.allocator.free(tests_readme);

    const scripts_readme = try readRepoFile("scripts/zigux/README.md", 384 * 1024);
    defer std.testing.allocator.free(scripts_readme);

    inline for (shared_tooling_paths) |path| {
        try expectContains(tests_readme, path);
    }

    try expectContains(scripts_readme, "current scripts-root bridge packet stays reviewable");
    try expectContains(scripts_readme, "tool-manifest packet");
    try expectContains(scripts_readme, "artifact-support packet");
    try expectContains(scripts_readme, "direct cross-route packet");
    try expectContains(scripts_readme, "fixdep packet");
    try expectContains(scripts_readme, "`make -C zigux phase2-toolchain`");
    try expectContains(scripts_readme, "`make -C zigux phase2`");
}
