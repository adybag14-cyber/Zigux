const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const contract_path = b.option(
        []const u8,
        "contract-path",
        "path to the notifier sequence metrics ABI contract",
    ) orelse "phase3_abi_notifier_sequence_metrics_contract.zig";
    const notifier_abi_path = b.option(
        []const u8,
        "notifier-abi-path",
        "path to zigux/bindings/notifier_abi.zig",
    ) orelse "../bindings/notifier_abi.zig";

    const root_mod = b.createModule(.{
        .root_source_file = b.path(contract_path),
        .target = target,
        .optimize = optimize,
    });
    root_mod.addImport("notifier_abi", b.createModule(.{
        .root_source_file = b.path(notifier_abi_path),
        .target = target,
        .optimize = optimize,
    }));

    const tests = b.addTest(.{
        .root_module = root_mod,
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase3-abi-notifier-sequence-metrics-contract",
        "Run the Phase 3 ABI notifier sequence metrics contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 ABI notifier sequence metrics contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
