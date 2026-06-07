const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_parity_success_summary_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const main_step = b.step(
        "phase1-parity-success-summary-contract",
        "Run the Phase 1 parity checker success-summary source contract",
    );
    main_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 parity checker success-summary source contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
