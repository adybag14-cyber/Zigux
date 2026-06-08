const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const abi_bindings_path = b.option(
        []const u8,
        "abi-bindings-path",
        "Path to zigux/bindings/abi.zig",
    ) orelse "../bindings/abi.zig";

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path(abi_bindings_path),
        .target = target,
        .optimize = optimize,
    });
    const contract = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_abi_export_status_matrix_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    contract.root_module.addImport("abi_bindings", abi_bindings);

    const run_contract = b.addRunArtifact(contract);

    const named_step = b.step(
        "phase3-abi-export-status-matrix-contract",
        "Run the Phase 3 ABI export status matrix contract",
    );
    named_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Phase 3 ABI export status matrix contract");
    test_step.dependOn(&run_contract.step);

    b.default_step.dependOn(&run_contract.step);
}
