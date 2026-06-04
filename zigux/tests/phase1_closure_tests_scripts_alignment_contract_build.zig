const std = @import("std");

fn addContract(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const closure_path = b.option(
        []const u8,
        "closure-path",
        "Path to Documentation/zigux/phase1-closure.md",
    ) orelse "Documentation/zigux/phase1-closure.md";
    const scripts_readme_path = b.option(
        []const u8,
        "scripts-readme-path",
        "Path to scripts/zigux/README.md",
    ) orelse "scripts/zigux/README.md";
    const tests_readme_path = b.option(
        []const u8,
        "tests-readme-path",
        "Path to zigux/tests/README.md",
    ) orelse "zigux/tests/README.md";

    const options = b.addOptions();
    options.addOption([]const u8, "closure_path", closure_path);
    options.addOption([]const u8, "scripts_readme_path", scripts_readme_path);
    options.addOption([]const u8, "tests_readme_path", tests_readme_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_closure_tests_scripts_alignment_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("contract_options", options);

    const tests = b.addTest(.{
        .name = "phase1-closure-tests-scripts-alignment-contract",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract = addContract(b, target, optimize);

    const contract_step = b.step(
        "phase1-closure-tests-scripts-alignment-contract",
        "Run the Phase 1 closure scripts/tests alignment contract",
    );
    contract_step.dependOn(&contract.step);

    const test_step = b.step(
        "test",
        "Run the Phase 1 closure scripts/tests alignment contract",
    );
    test_step.dependOn(&contract.step);
}
