const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("check_phase1_find_bit_review_packet_checker_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "check-phase1-find-bit-review-packet-checker-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "check-phase1-find-bit-review-packet-checker-contract",
        "Validate the Phase 1 find_bit review checker source contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 find_bit review checker source contract");
    test_step.dependOn(&run_tests.step);
}
