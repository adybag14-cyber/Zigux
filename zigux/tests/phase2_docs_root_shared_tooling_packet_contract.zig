const std = @import("std");

const FileSpec = struct {
    path: []const u8,
    markers: []const []const u8,
};

const docs_root_markers = [_][]const u8{
    "Phase 2 notes",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/fixdep.zig",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "zigux/tests/fixtures/fixdep/cases.json",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
};

const companion_specs = [_]FileSpec{
    .{
        .path = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
        .markers = &[_][]const u8{
            "Current direct packet",
            "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
            "scripts/zigux/check-phase2-artifact-tools-manifest.py",
            "scripts/zigux/artifact_diff.py",
            "scripts/zigux/install-zig.py",
            "scripts/zigux/stage-pinned-zig-archive.py",
            "scripts/zigux/check-phase2-cross.py",
            "zigux/tests/fixtures/phase2_cross_targets.json",
            "scripts/zigux/check-phase2-fixdep-gate.py",
            "scripts/zigux/check-fixdep-diff.py",
            "scripts/zigux/genksyms.zig",
            "make -C zigux phase2-genksyms",
            "make -C zigux phase2-fixdep",
        },
    },
    .{
        .path = "Documentation/zigux/phase2-closure.md",
        .markers = &[_][]const u8{
            "Current Shared Repo-Tooling Evidence",
            "scripts/zigux/check-phase2-tool-manifest.py",
            "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
            "scripts/zigux/check-phase2-artifact-tools-manifest.py",
            "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
            "scripts/zigux/check-phase2-cross.py",
            "scripts/zigux/check-phase2-fixdep-gate.py",
            "scripts/zigux/check-fixdep-diff.py",
            "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain",
        },
    },
    .{
        .path = "Documentation/zigux/review-checklist.md",
        .markers = &[_][]const u8{
            "if the change touches the shared Phase 2 toolchain packet",
            "Documentation/zigux/README.md",
            "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            "scripts/zigux/check-phase2-docs-shared-reminder.py",
            "scripts/zigux/check-phase2-tool-manifest.py",
            "scripts/zigux/check-phase2-artifact-tools-manifest.py",
            "scripts/zigux/check-phase2-required-make-routes.py",
            "scripts/zigux/check-phase2-fixdep-gate.py",
            "scripts/zigux/check-fixdep-diff.py",
            "make -C zigux phase2-fixdep",
        },
    },
    .{
        .path = "scripts/zigux/README.md",
        .markers = &[_][]const u8{
            "Phase 2 flow",
            "scripts/zigux/check-phase2-tool-manifest.py",
            "scripts/zigux/check-phase2-artifact-tools-manifest.py",
            "scripts/zigux/check-phase2-required-make-routes.py",
            "scripts/zigux/check-phase2-fixdep-gate.py",
            "scripts/zigux/check-fixdep-diff.py",
            "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
            "scripts/zigux/kconfig/confdata_bridge.zig",
            "make -C zigux phase2-tools",
            "make -C zigux phase2-kconfig",
        },
    },
    .{
        .path = "zigux/tests/README.md",
        .markers = &[_][]const u8{
            "Phase 2 review packet",
            "Documentation/zigux/README.md",
            "scripts/zigux/check-phase2-docs-shared-reminder.py",
            "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
            "scripts/zigux/check-phase2-tool-manifest.py",
            "scripts/zigux/check-phase2-artifact-tools-manifest.py",
            "scripts/zigux/check-genksyms-bridge.py",
            "scripts/zigux/check-phase2-fixdep-gate.py",
            "scripts/zigux/check-fixdep-diff.py",
            "zigux/tests/fixtures/phase2_tool_manifest.json",
        },
    },
    .{
        .path = "zigux/tests/fixtures/phase2_tool_manifest.json",
        .markers = &[_][]const u8{
            "Current Phase 2 repo-tooling evidence",
            "scripts/zigux/check-phase2-tool-manifest.py",
            "scripts/zigux/check-phase2-artifact-tools-manifest.py",
            "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
            "scripts/zigux/artifact_diff.py",
            "scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py",
            "scripts/zigux/check-phase2-fixdep-gate.py",
            "scripts/zigux/check-fixdep-diff.py",
            "scripts/zigux/validate-phase2.py",
            "scripts/zigux/validate-phase2-closure.py",
        },
    },
};

test "docs-root Phase 2 shared tooling packet keeps direct owner roster" {
    const docs_root = try readFile("Documentation/zigux/README.md");
    defer std.testing.allocator.free(docs_root);

    try expectAll(docs_root, &docs_root_markers);
    try expectBefore(docs_root, "Phase 2 notes", "Phase 3 notes");
    try expectBefore(docs_root, "scripts/zigux/check-phase2-tool-manifest.py", "scripts/zigux/check-phase2-artifact-tools-manifest.py");
    try expectBefore(docs_root, "make -C zigux phase2-validate", "make -C zigux phase2\n");
}

test "direct Phase 2 companions mirror the docs-root packet" {
    for (companion_specs) |spec| {
        const body = try readFile(spec.path);
        defer std.testing.allocator.free(body);
        try expectAll(body, spec.markers);
    }
}

test "shared tooling contract rejects historical-only Phase 2 wording" {
    const docs_root = try readFile("Documentation/zigux/README.md");
    defer std.testing.allocator.free(docs_root);

    try std.testing.expectEqual(@as(?usize, null), std.mem.indexOf(u8, docs_root, "Phase 2 installer and direct cross-route surfaces remain missing"));
    try std.testing.expectEqual(@as(?usize, null), std.mem.indexOf(u8, docs_root, "phase2-fixdep stays outside the current wrapper packet"));
    try std.testing.expectEqual(@as(?usize, null), std.mem.indexOf(u8, docs_root, "artifact-support remains a repo-reality gap"));
}

fn readFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn expectAll(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
    }
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}
