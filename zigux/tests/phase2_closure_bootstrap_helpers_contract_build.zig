const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_closure_bootstrap_helpers_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract = b.addRunArtifact(contract_tests);

    const named = b.step(
        "phase2-closure-bootstrap-helpers-contract",
        "Run the Phase 2 closure bootstrap helper roster contract",
    );
    named.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Phase 2 closure bootstrap helper roster contract");
    test_step.dependOn(&run_contract.step);
}
