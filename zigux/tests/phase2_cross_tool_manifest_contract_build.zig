const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase2_cross_tool_manifest_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .root_module = contract_module,
    });
    const run_tests = b.addRunArtifact(tests);
    run_tests.cwd = b.path("../..");

    const contract_step = b.step(
        "phase2-cross-tool-manifest-contract",
        "Run the Phase 2 cross tool-manifest contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 2 cross tool-manifest contract");
    test_step.dependOn(&run_tests.step);
}
