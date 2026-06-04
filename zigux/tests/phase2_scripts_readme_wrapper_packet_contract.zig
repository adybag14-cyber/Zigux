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
        "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
        "`scripts/zigux/check-phase2-required-make-routes.py`",
        "`scripts/zigux/validate-phase2-closure.py`",
        "`zigux/Makefile`",
        "`make -C zigux phase2-toolchain`",
        "`make -C zigux phase2-tools`",
        "`make -C zigux phase2-kconfig`",
        "`make -C zigux phase2-cross`",
        "`make -C zigux phase2-genksyms`",
        "`make -C zigux phase2-fixdep`",
        "`make -C zigux phase2-validate`",
        "`make -C zigux phase2`",
        "`scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit",
        "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`",
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
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
        "phase2-tools:",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",
        "phase2-kconfig: phase2-toolchain",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py",
        "phase2-cross:",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
        "phase2-genksyms: phase2-toolchain",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
        "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms.zig",
        "phase2-fixdep: phase2-toolchain",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --zig \"$(ZIG_REPO_ROOT)\"",
        "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
        "phase2: phase2-validate",
    };

    for (markers) |marker| {
        try expectContains(makefile, marker);
    }
}

test "required make-route checker protects scripts README route markers" {
    const allocator = std.testing.allocator;
    const checker = try readFile(allocator, "scripts/zigux/check-phase2-required-make-routes.py");
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
        "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py\"",
        "\"phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep\"",
    };

    for (markers) |marker| {
        try expectContains(checker, marker);
    }
}
