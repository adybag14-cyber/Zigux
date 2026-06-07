const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_path = b.option(
        []const u8,
        "contract-path",
        "Path to the Phase 3 ABI unsafe window contract",
    ) orelse "phase3_abi_unsafe_window_contract.zig";
    const abi_bindings_path = b.option(
        []const u8,
        "abi-bindings-path",
        "Path to the ABI bindings module",
    ) orelse "../bindings/abi.zig";
    const narrow_path = b.option(
        []const u8,
        "narrow-path",
        "Path to the narrow unsafe helper module",
    ) orelse "../unsafe/narrow.zig";
    const unsafe_policy_path = b.option(
        []const u8,
        "unsafe-policy-path",
        "Path to the unsafe policy helper module",
    ) orelse "../helpers/unsafe_policy.zig";

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path(abi_bindings_path),
        .target = target,
        .optimize = optimize,
    });
    const narrow_module = b.createModule(.{
        .root_source_file = b.path(narrow_path),
        .target = target,
        .optimize = optimize,
    });
    narrow_module.addImport("abi_bindings", abi_bindings_module);

    const unsafe_policy_module = b.createModule(.{
        .root_source_file = b.path(unsafe_policy_path),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy_module.addImport("abi_bindings", abi_bindings_module);
    unsafe_policy_module.addImport("narrow", narrow_module);

    const root_module = b.createModule(.{
        .root_source_file = b.path(contract_path),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings_module);
    root_module.addImport("unsafe_policy", unsafe_policy_module);

    const tests = b.addTest(.{
        .name = "phase3-abi-unsafe-window-contract",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase3-abi-unsafe-window-contract",
        "Run the focused Phase 3 ABI unsafe window contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the focused Phase 3 ABI unsafe window contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
