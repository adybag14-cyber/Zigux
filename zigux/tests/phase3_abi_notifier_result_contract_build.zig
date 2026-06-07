const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const notifier_abi_path = b.option(
        []const u8,
        "notifier-abi-path",
        "Path to zigux/bindings/notifier_abi.zig",
    ) orelse "../bindings/notifier_abi.zig";
    const abi_bindings_path = b.option(
        []const u8,
        "abi-bindings-path",
        "Path to zigux/bindings/abi.zig",
    ) orelse "../bindings/abi.zig";

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_abi_notifier_result_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const abi_module = b.createModule(.{
        .root_source_file = b.path(abi_bindings_path),
        .target = target,
        .optimize = optimize,
    });
    abi_module.addImport("notifier_abi.zig", b.createModule(.{
        .root_source_file = b.path(notifier_abi_path),
        .target = target,
        .optimize = optimize,
    }));
    tests.root_module.addImport("abi_bindings", abi_module);

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase3-abi-notifier-result-contract",
        "Run the Phase 3 notifier result ABI contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 notifier result ABI contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
