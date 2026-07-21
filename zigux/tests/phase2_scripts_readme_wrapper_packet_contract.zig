const std = @import("std");

const max_file_size = 512 * 1024;

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "scripts README keeps the Phase 2 wrapper packet explicit" {
    const allocator = std.testing.allocator;
    const readme = try readFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(readme);

    const markers = [_][]const u8{
        "## Phase 2",
        "the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet",
        "`scripts\zigux/check_phase2_docs_shared_reminder.zig`",
        "`scripts\zigux/check_phase2_required_make_routes.zig`",
        "`scripts\zigux/validate_phase2_closure.zig`",
        "`zigux/Makefile`",
        "`make -C zigux phase2-toolchain`",
        "`make -C zigux phase2-tools`",
        "`make -C zigux phase2-kconfig`",
        "`make -C zigux phase2-cross`",
        "`make -C zigux phase2-genksyms`",
        "`make -C zigux phase2-fixdep`",
        "`make -C zigux phase2-validate`",
        "`make -C zigux phase2`",
        "`scripts\zigux/check_phase2_tool_manifest.zig` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit",
        "`scripts/zigux/install_zig.zig`, `zig run scripts/zigux/install_zig.zig -- --self-test`, `zig run scripts/zigux/check_phase2_cross.zig -- --self-test`, `zig run scripts/zigux/check_phase2_cross.zig`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`",
        "keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
    };

    for (markers) |marker| {
        try expectContains(readme, marker);
    }

    try std.testing.expect(std.mem.indexOf(u8, readme, "stay framed as repo-reality gaps") == null);
}

test "Makefile exposes the required Phase 2 route dependency graph" {
    const allocator = std.testing.allocator;
    const makefile = try readFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);

    const markers = [_][]const u8{
        ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
        "phase2-toolchain:",
        "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig -- --self-test",
        "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig -- --policy-only",
        "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pinning.zig",
        "phase2-tools:",
        "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_docs_shared_reminder.zig",
        "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_required_make_routes.zig",
        "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_artifact_tools_manifest.zig",
        "phase2-kconfig: phase2-toolchain",
        "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kconfig_allconfig_helper_packet.zig",
        "phase2-cross:",
        "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross_selftest_alignment.zig",
        "phase2-genksyms: phase2-toolchain",
        "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_genksyms_bridge.zig",
        "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms.zig",
        "phase2-fixdep: phase2-toolchain",
        "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_fixdep_gate.zig",
        "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_fixdep_diff.zig -- --zig \"$(ZIG_REPO_ROOT)\"",
        "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
        "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/validate_phase2_closure.zig",
        "phase2: phase2-validate",
    };

    for (markers) |marker| {
        try expectContains(makefile, marker);
    }
}

test "required make-route checker protects scripts README route markers" {
    const allocator = std.testing.allocator;
    const checker = try readFile(allocator, "scripts\zigux/check_phase2_required_make_routes.zig");
    defer allocator.free(checker);

    const markers = [_][]const u8{
        "SCRIPTS_README = ROOT / \"scripts\" / \"zigux\" / \"README.md\"",
        "CURRENT_REQUIRED_MAKE_ROUTES = (",
        "\"phase2-toolchain\"",
        "\"phase2-tools\"",
        "\"phase2-kconfig\"",
        "\"phase2-cross\"",
        "\"phase2-genksyms\"",
        "\"phase2-fixdep\"",
        "\"phase2-validate\"",
        "CURRENT_PACKET_ROUTE_MARKERS = (",
        "\"`make -C zigux phase2`\"",
        "FULL_ROUTE_SURFACE_CODES = (",
        "(SCRIPTS_README, \"MISSING_SCRIPTS_README_GAP_MARKERS\", \"MISSING_SCRIPTS_README_ROUTE_MARKERS\")",
        "\"$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_required_make_routes.zig\"",
        "\"phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep\"",
    };

    for (markers) |marker| {
        try expectContains(checker, marker);
    }
}
