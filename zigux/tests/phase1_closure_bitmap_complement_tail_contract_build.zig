const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_closure_bitmap_complement_tail_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-closure-bitmap-complement-tail-contract",
        "Validate the Phase 1 closure bitmap complement-tail marker contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 closure bitmap complement-tail contract tests");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
