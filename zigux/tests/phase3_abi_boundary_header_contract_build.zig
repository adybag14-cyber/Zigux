const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const abi_bindings_path = b.option(
        []const u8,
        "abi-bindings-path",
        "path to zigux/bindings/abi.zig",
    ) orelse "../../zigux/bindings/abi.zig";

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path(abi_bindings_path),
        .target = target,
        .optimize = optimize,
    });

    const contract = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_abi_boundary_header_contract.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{ .name = "abi_bindings", .module = abi_bindings },
            },
        }),
    });

    const run_contract = b.addRunArtifact(contract);

    const contract_step = b.step(
        "phase3-abi-boundary-header-contract",
        "Run the Phase 3 ABI boundary-header contract",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Phase 3 ABI boundary-header contract");
    test_step.dependOn(&run_contract.step);

    b.default_step.dependOn(&run_contract.step);
}
