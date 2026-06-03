const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "phase1-closure-gap-packet-contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_closure_gap_packet_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-closure-gap-packet-contract",
        "Validate the Phase 1 closure gap packet stays parked outside the reminder packet.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 closure gap packet contract.");
    test_step.dependOn(&run_tests.step);
}
