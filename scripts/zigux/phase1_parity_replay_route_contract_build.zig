const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "phase1-parity-replay-route-contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_parity_replay_route_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase1-parity-replay-route-contract",
        "Guard the Phase 1 parity checker replay-route marker contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 parity replay-route contract");
    test_step.dependOn(&run_tests.step);
}
