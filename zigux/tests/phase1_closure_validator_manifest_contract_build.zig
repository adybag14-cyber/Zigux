const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const closure_path = b.option(
        []const u8,
        "closure-note-path",
        "Path to the Phase 1 closure note",
    ) orelse "Documentation/zigux/phase1-closure.md";
    const validator_path = b.option(
        []const u8,
        "validator-path",
        "Path to the Phase 1 closure validator",
    ) orelse "scripts/zigux/validate-phase1-closure.py";
    const manifest_path = b.option(
        []const u8,
        "manifest-path",
        "Path to the Phase 1 helper manifest",
    ) orelse "zigux/tests/fixtures/phase1_helper_manifest.json";

    const options = b.addOptions();
    options.addOption([]const u8, "closure_note_path", closure_path);
    options.addOption([]const u8, "validator_path", validator_path);
    options.addOption([]const u8, "manifest_path", manifest_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_closure_validator_manifest_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("build_options", options);

    const tests = b.addTest(.{
        .name = "phase1-closure-validator-manifest-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-closure-validator-manifest-contract",
        "Check Phase 1 closure validator and manifest roster alignment",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 closure validator manifest contract");
    test_step.dependOn(&run_tests.step);
}
