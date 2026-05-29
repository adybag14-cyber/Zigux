const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("phase15_docs_root_readiness_parity_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase15-docs-root-readiness-parity-contract",
        .root_module = module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const contract = b.step(
        "phase15-docs-root-readiness-parity-contract",
        "Run the Lane 02 docs-root readiness and parity contract",
    );
    contract.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the Lane 02 docs-root readiness and parity contract");
    test_step.dependOn(&run_unit_tests.step);
}
