const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("check_phase1_bitmap_review_packet_checker_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(unit_tests);
    const contract_step = b.step(
        "check-phase1-bitmap-review-packet-checker-contract",
        "Run the Lane 07 bitmap review packet checker source contract.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 07 bitmap review packet checker source contract tests.",
    );
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
