const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const closure_note_path = b.option(
        []const u8,
        "closure-note-path",
        "Path to Documentation/zigux/phase1-closure.md relative to the repository root",
    ) orelse "Documentation/zigux/phase1-closure.md";
    const validator_path = b.option(
        []const u8,
        "validator-path",
        "Path to scripts/zigux/validate-phase1-closure.py relative to the repository root",
    ) orelse "scripts/zigux/validate-phase1-closure.py";

    const config = b.addOptions();
    config.addOption([]const u8, "closure_note_path", closure_note_path);
    config.addOption([]const u8, "validator_path", validator_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane17_phase1_closure_validator_marker_boundary_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("config", config);

    const tests = b.addTest(.{
        .name = "lane17-phase1-closure-validator-marker-boundary-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane17-phase1-closure-validator-marker-boundary-contract",
        "Run the Lane 17 Phase 1 closure validator marker-boundary contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 17 Phase 1 closure validator marker-boundary contract");
    test_step.dependOn(&run_tests.step);
}
