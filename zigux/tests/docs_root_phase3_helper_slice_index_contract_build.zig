const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("docs_root_phase3_helper_slice_index_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "docs-root-phase3-helper-slice-index-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "docs-root-phase3-helper-slice-index-contract",
        "Run the docs-root Phase 3 helper slice index integrity contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run docs-root Phase 3 helper slice index contract tests");
    test_step.dependOn(&run_tests.step);
}
