const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("check_phase1_rbtree_review_packet_checker_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);
    const contract_step = b.step(
        "check-phase1-rbtree-review-packet-checker-contract",
        "Validate the Phase 1 rbtree review packet checker source contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the rbtree review packet checker contract");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}
