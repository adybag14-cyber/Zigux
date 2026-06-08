const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const atomic_helper_path = b.option(
        []const u8,
        "atomic-helper-path",
        "Path to zigux/helpers/atomic.zig",
    ) orelse "../helpers/atomic.zig";

    const atomic_helpers = b.createModule(.{
        .root_source_file = b.path(atomic_helper_path),
        .target = target,
        .optimize = optimize,
    });
    const contract = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_abi_atomic_exchange_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    contract.root_module.addImport("atomic_helpers", atomic_helpers);

    const run_contract = b.addRunArtifact(contract);

    const named_step = b.step(
        "phase3-abi-atomic-exchange-contract",
        "Run the Phase 3 ABI atomic exchange contract",
    );
    named_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Phase 3 ABI atomic exchange contract");
    test_step.dependOn(&run_contract.step);

    b.default_step.dependOn(&run_contract.step);
}
