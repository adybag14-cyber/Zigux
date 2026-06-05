const std = @import("std");

fn addPhase3AbiMmioZeroLengthRangeContract(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step {
    const mmio_source_path = b.option(
        []const u8,
        "mmio-source-path",
        "Path to the MMIO helper source under review",
    ) orelse "../helpers/mmio.zig";

    const options = b.addOptions();
    options.addOption([]const u8, "mmio_source_path", mmio_source_path);

    const tests = b.addTest(.{
        .name = "phase3_abi_mmio_zero_length_range_contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_abi_mmio_zero_length_range_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addOptions("build_options", options);

    const run = b.addRunArtifact(tests);
    const step = b.step(
        "phase3-abi-mmio-zero-length-range-contract",
        "Run the Phase 3 ABI MMIO zero-length range source contract",
    );
    step.dependOn(&run.step);
    return step;
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_step = addPhase3AbiMmioZeroLengthRangeContract(b, target, optimize);
    const test_step = b.step("test", "Run the Phase 3 ABI MMIO zero-length range contract tests");
    test_step.dependOn(contract_step);
}
