const std = @import("std");

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase2 closure keeps docs reconciliation status and replay routes explicit" {
    const phase2_closure = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase2-closure.md");
    defer std.testing.allocator.free(phase2_closure);

    const markers = [_][]const u8{
        "PHASE2_STATUS=parked",
        "PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest",
        "PHASE2_SHARED_TOOLING_CHECKERS=python3 scripts/zigux/check-phase2-tool-manifest.py,python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py,python3 scripts/zigux/check-phase2-artifact-tools-manifest.py,python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py,python3 scripts/zigux/check-phase2-cross.py,python3 scripts/zigux/check-phase2-fixdep-gate.py,python3 scripts/zigux/check-fixdep-diff.py",
        "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2",
        "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py",
        "PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md",
    };

    for (markers) |marker| {
        try expectContains(phase2_closure, marker);
    }
}

test "phase2 closure keeps current genksyms evidence bounded" {
    const phase2_closure = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase2-closure.md");
    defer std.testing.allocator.free(phase2_closure);

    const markers = [_][]const u8{
        "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md",
        "scripts/zigux/check-genksyms-bridge.py",
        "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
        "scripts/zigux/genksyms.zig",
        "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=",
        "still-missing CRC-side evidence",
    };

    for (markers) |marker| {
        try expectContains(phase2_closure, marker);
    }
}

test "artifact diff and scripts readme keep phase2 documentation scope narrow" {
    const artifact_diff = try readRepoFile(std.testing.allocator, "Documentation/zigux/artifact-diff.md");
    defer std.testing.allocator.free(artifact_diff);
    const scripts_readme = try readRepoFile(std.testing.allocator, "scripts/zigux/README.md");
    defer std.testing.allocator.free(scripts_readme);

    const artifact_markers = [_][]const u8{
        "## Current Phase 2 use",
        "validating `fixdep` and the kconfig bridge packet",
        "current `genksyms` bridge packet keeps its fixture comparisons local to `scripts/zigux/check-genksyms-bridge.py`",
    };
    const scripts_markers = [_][]const u8{
        "## Phase 2",
        "current fixdep packet stays reviewable through the dedicated governance guard, parity checker, and shipped `phase2-fixdep` wrapper",
        "scripts/zigux/check-phase2-fixdep-gate.py",
        "scripts/zigux/check-fixdep-diff.py",
        "zig test scripts/zigux/fixdep.zig",
        "make -C zigux phase2-fixdep",
    };

    for (artifact_markers) |marker| {
        try expectContains(artifact_diff, marker);
    }
    for (scripts_markers) |marker| {
        try expectContains(scripts_readme, marker);
    }
}
