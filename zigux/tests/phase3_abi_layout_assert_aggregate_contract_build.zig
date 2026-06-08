const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_path = b.option(
        []const u8,
        "contract-path",
        "Path to the layout assert aggregate contract",
    ) orelse "phase3_abi_layout_assert_aggregate_contract.zig";
    const layout_assert_path = b.option(
        []const u8,
        "layout-assert-path",
        "Path to zigux/helpers/layout_assert.zig",
    ) orelse "../helpers/layout_assert.zig";
    const abi_bindings_path = b.option(
        []const u8,
        "abi-bindings-path",
        "Path to zigux/bindings/abi.zig",
    ) orelse "../bindings/abi.zig";

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path(contract_path),
            .target = target,
            .optimize = optimize,
        }),
    });
    const layout_assert_module = b.createModule(.{
        .root_source_file = b.path(layout_assert_path),
        .target = target,
        .optimize = optimize,
    });
    const abi_module = b.createModule(.{
        .root_source_file = b.path(abi_bindings_path),
        .target = target,
        .optimize = optimize,
    });
    tests.root_module.addImport("layout_assert_helper", layout_assert_module);
    tests.root_module.addImport("abi_bindings", abi_module);
    layout_assert_module.addImport("abi_bindings", abi_module);

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase3-abi-layout-assert-aggregate-contract",
        "Run the Phase 3 ABI layout assert aggregate contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 ABI layout assert aggregate contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
