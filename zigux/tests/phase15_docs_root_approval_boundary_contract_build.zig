const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("phase15_docs_root_approval_boundary_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase15-docs-root-approval-boundary-contract",
        .root_module = module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    run_unit_tests.setCwd(b.path("../.."));

    const contract = b.step(
        "phase15-docs-root-approval-boundary-contract",
        "Run the focused Phase 15 docs-root approval-boundary contract",
    );
    contract.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the focused Phase 15 docs-root approval-boundary contract");
    test_step.dependOn(&run_unit_tests.step);
}
