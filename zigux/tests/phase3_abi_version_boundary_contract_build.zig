const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.addModule("abi_bindings", .{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const version_binding = b.addModule("version_binding", .{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    version_binding.addImport("abi_bindings", abi_bindings);

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_abi_version_boundary_contract.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{ .name = "abi_bindings", .module = abi_bindings },
                .{ .name = "version_binding", .module = version_binding },
            },
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase3-abi-version-boundary-contract",
        "Run the Phase 3 ABI UAPI version boundary contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 ABI UAPI version boundary contract tests");
    test_step.dependOn(&run_tests.step);
}
