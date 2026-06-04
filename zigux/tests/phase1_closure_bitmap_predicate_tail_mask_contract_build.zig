const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_closure_bitmap_predicate_tail_mask_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-closure-bitmap-predicate-tail-mask-contract",
        "Validate the Phase 1 closure bitmap predicate tail-mask contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 closure bitmap predicate tail-mask contract tests");
    test_step.dependOn(&run_tests.step);
}
