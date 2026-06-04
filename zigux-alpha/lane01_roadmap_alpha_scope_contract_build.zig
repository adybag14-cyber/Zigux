const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane01_roadmap_alpha_scope_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "lane01-roadmap-alpha-scope-contract",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "lane01-roadmap-alpha-scope-contract",
        "Validate the Lane 01 roadmap zigux-alpha scope packet",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run Lane 01 roadmap alpha scope contract tests");
    test_step.dependOn(&run_contract_tests.step);
}
