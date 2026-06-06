const std = @import("std");

const validate_bootstrap_surface =
    \\REQUIRED_WORKFLOW_LINES = (
    \\    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    \\    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    \\    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    \\    "run: make -C zigux phase6-validate",
    \\    "run: zig build test --build-file zigux/tests/phase6_build.zig --summary all",
    \\    "run: python3 scripts/zigux/validate-bootstrap.py --self-test",
    \\    "run: python3 scripts/zigux/validate-bootstrap.py",
    \\)
    \\
    \\print(f"BOOTSTRAP_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
;

const workflow_phase2_surface =
    \\      - name: Self-test current Phase 2 kbuild routes checker
    \\        run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test
    \\
    \\      - name: Check current Phase 2 kbuild packet
    \\        run: python3 scripts/zigux/check-phase2-kbuild-routes.py
    \\
    \\      - name: Self-test current Phase 2 bootstrap workflow routes checker
    \\        run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py --self-test
    \\
    \\      - name: Check current Phase 2 bootstrap workflow routes packet
    \\        run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py
    \\
    \\      - name: Run current Phase 2 toolchain make route
    \\        run: make -C zigux phase2-toolchain
    \\
    \\      - name: Run current Phase 2 tools make route
    \\        run: make -C zigux phase2-tools
    \\
    \\      - name: Run current Phase 2 kconfig make route
    \\        run: make -C zigux phase2-kconfig
    \\
    \\      - name: Run current Phase 2 fixdep make route
    \\        run: make -C zigux phase2-fixdep
    \\
    \\      - name: Run current Phase 2 cross make route
    \\        run: make -C zigux phase2-cross
    \\
    \\      - name: Run current Phase 2 genksyms make route
    \\        run: make -C zigux phase2-genksyms
    \\
    \\      - name: Run current Phase 2 validate make route
    \\        run: make -C zigux phase2-validate
    \\
    \\      - name: Run current Phase 2 aggregate make route
    \\        run: make -C zigux phase2
;

const makefile_phase2_surface =
    \\.PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2
    \\
    \\phase2-toolchain:
    \\    $(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test
    \\
    \\phase2-tools:
    \\    $(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py --self-test
    \\
    \\phase2-kconfig: phase2-toolchain
    \\    cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test
    \\
    \\phase2-cross:
    \\    $(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test
    \\
    \\phase2-genksyms: phase2-toolchain
    \\    cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test
    \\
    \\phase2-fixdep: phase2-toolchain
    \\    cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test
    \\
    \\phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep
    \\
    \\phase2: phase2-validate
;

const scripts_readme_phase2_surface =
    \\- `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` keep the required wrapper route packet explicit
    \\- `scripts/zigux/check-phase2-bootstrap-workflow-routes.py`, `scripts/zigux/check-phase2-required-make-routes.py`, and `.github/workflows/zigux-bootstrap.yml` keep Phase 2 workflow route accountability explicit.
;

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn countTrimmedLine(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), needle)) {
            count += 1;
        }
    }
    return count;
}

test "bootstrap validator still exposes only the narrow required workflow roster" {
    try std.testing.expect(contains(validate_bootstrap_surface, "REQUIRED_WORKFLOW_LINES = ("));
    try std.testing.expect(contains(validate_bootstrap_surface, "BOOTSTRAP_WORKFLOW_LINE_COUNT"));
    try std.testing.expectEqual(@as(usize, 1), countTrimmedLine(validate_bootstrap_surface, "\"run: make -C zigux phase6-validate\","));
    try std.testing.expectEqual(@as(usize, 0), countTrimmedLine(validate_bootstrap_surface, "\"run: make -C zigux phase2-validate\","));
    try std.testing.expectEqual(@as(usize, 0), countTrimmedLine(validate_bootstrap_surface, "\"run: make -C zigux phase2\","));
}

test "workflow keeps Phase 2 route checker and make wrapper handoff visible" {
    const workflow_lines = [_][]const u8{
        "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py --self-test",
        "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
        "run: make -C zigux phase2-toolchain",
        "run: make -C zigux phase2-tools",
        "run: make -C zigux phase2-kconfig",
        "run: make -C zigux phase2-cross",
        "run: make -C zigux phase2-genksyms",
        "run: make -C zigux phase2-fixdep",
        "run: make -C zigux phase2-validate",
        "run: make -C zigux phase2",
    };

    for (workflow_lines) |line| {
        try std.testing.expectEqual(@as(usize, 1), countTrimmedLine(workflow_phase2_surface, line));
    }
}

test "Makefile keeps Phase 2 aggregate route dependencies explicit" {
    const make_markers = [_][]const u8{
        "phase2-toolchain:",
        "phase2-tools:",
        "phase2-kconfig: phase2-toolchain",
        "phase2-cross:",
        "phase2-genksyms: phase2-toolchain",
        "phase2-fixdep: phase2-toolchain",
        "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
        "phase2: phase2-validate",
    };

    for (make_markers) |marker| {
        try std.testing.expectEqual(@as(usize, 1), countTrimmedLine(makefile_phase2_surface, marker));
    }
}

test "scripts README names the Phase 2 wrapper packet as current bootstrap evidence" {
    const readme_markers = [_][]const u8{
        "make -C zigux phase2-toolchain",
        "make -C zigux phase2-tools",
        "make -C zigux phase2-kconfig",
        "make -C zigux phase2-cross",
        "make -C zigux phase2-genksyms",
        "make -C zigux phase2-fixdep",
        "make -C zigux phase2-validate",
        "make -C zigux phase2",
        "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
        "scripts/zigux/check-phase2-required-make-routes.py",
    };

    for (readme_markers) |marker| {
        try std.testing.expect(contains(scripts_readme_phase2_surface, marker));
    }
}
