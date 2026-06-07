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

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_boundary_header_extension_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addImport("abi_bindings", abi_bindings);

    const contract = b.addTest(.{
        .root_module = contract_module,
    });

    const run_contract = b.addRunArtifact(contract);

    const test_step = b.step(
        "phase3-abi-boundary-header-extension-contract",
        "Run the Phase 3 ABI boundary header extension contract",
    );
    test_step.dependOn(&run_contract.step);

    const test_alias = b.step("test", "Run Phase 3 ABI boundary header extension tests");
    test_alias.dependOn(test_step);

    b.default_step.dependOn(test_step);
}
