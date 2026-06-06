const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const barrier_path = b.option(
        []const u8,
        "barrier-path",
        "Path to the Phase 3 barrier helper under test",
    ) orelse "../helpers/barrier.zig";

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_barrier_alias_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const barrier_module = b.createModule(.{
        .root_source_file = b.path(barrier_path),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("barrier_helpers", barrier_module);

    const tests = b.addTest(.{
        .name = "phase3-abi-barrier-alias-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase3-abi-barrier-alias-contract",
        "Run the Phase 3 ABI barrier alias handoff contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 ABI barrier alias handoff contract");
    test_step.dependOn(&run_tests.step);
}
