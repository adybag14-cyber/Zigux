const std = @import("std");

const max_file_size = 256 * 1024;

const ContractFile = struct {
    path: []const u8,
    required_markers: []const []const u8,
};

const scripts_readme_fixdep_markers = [_][]const u8{
    "Phase 2 flow - the current fixdep packet stays reviewable through the dedicated governance guard, parity checker, and shipped `phase2-fixdep` wrapper instead of widening back into older shared reminder churn",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` keep the current fixdep governance, determinism, helper, fixture, and CI packet explicit from the scripts root",
    "`python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`, `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py --self-test`, `python3 scripts/zigux/check-fixdep-diff.py`, `zig test scripts/zigux/fixdep.zig`, and `make -C zigux phase2-fixdep` replay the shipped fixdep lane without widening into unrelated Phase 2 surfaces",
};

const closure_fixdep_markers = [_][]const u8{
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/fixdep.zig",
    "PHASE2_SHARED_TOOLING_CHECKERS=python3 scripts/zigux/check-phase2-tool-manifest.py,python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py,python3 scripts/zigux/check-phase2-artifact-tools-manifest.py,python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py,python3 scripts/zigux/check-phase2-cross.py,python3 scripts/zigux/check-phase2-fixdep-gate.py,python3 scripts/zigux/check-fixdep-diff.py",
    "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2",
};

const makefile_fixdep_markers = [_][]const u8{
    "phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
    "phase2-fixdep: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "phase2: phase2-validate",
};

const workflow_fixdep_markers = [_][]const u8{
    "Self-test current Phase 2 fixdep gate checker",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "Check current Phase 2 fixdep gate packet",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "Self-test current fixdep parity checker",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "Check current fixdep parity packet",
    "run: python3 scripts/zigux/check-fixdep-diff.py",
    "Run current Phase 2 fixdep unit tests",
    "run: zig test scripts/zigux/fixdep.zig",
};

test "scripts README keeps the Phase 2 fixdep packet bounded and replayable" {
    try expectFileContainsAll(std.testing.allocator, .{
        .path = "scripts/zigux/README.md",
        .required_markers = &scripts_readme_fixdep_markers,
    });
}

test "Phase 2 closure keeps fixdep inside the shared checker and route packets" {
    try expectFileContainsAll(std.testing.allocator, .{
        .path = "Documentation/zigux/phase2-closure.md",
        .required_markers = &closure_fixdep_markers,
    });
}

test "Makefile and bootstrap workflow still run the documented fixdep packet" {
    const allocator = std.testing.allocator;
    try expectFileContainsAll(allocator, .{
        .path = "zigux/Makefile",
        .required_markers = &makefile_fixdep_markers,
    });
    try expectFileContainsAll(allocator, .{
        .path = ".github/workflows/zigux-bootstrap.yml",
        .required_markers = &workflow_fixdep_markers,
    });
}

fn expectFileContainsAll(allocator: std.mem.Allocator, contract_file: ContractFile) !void {
    const contents = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, contract_file.path, allocator, .limited(max_file_size));
    defer allocator.free(contents);

    for (contract_file.required_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, contents, marker) != null);
    }
}
