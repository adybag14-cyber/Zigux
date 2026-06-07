const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "phase2-closure-genksyms-evidence-contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_closure_genksyms_evidence_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase2-closure-genksyms-evidence-contract",
        "Run the Phase 2 closure genksyms evidence documentation contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 2 closure genksyms evidence contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(test_step);
}
