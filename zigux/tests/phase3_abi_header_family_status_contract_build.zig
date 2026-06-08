const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const uapi_dev_t = b.createModule(.{
        .root_source_file = b.path("../uapi/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    const uapi_version = b.createModule(.{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    const dev_t_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    const version_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    const header_family_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/header_family.zig"),
        .target = target,
        .optimize = optimize,
    });
    const contract = b.createModule(.{
        .root_source_file = b.path("phase3_abi_header_family_status_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    abi_bindings.addImport("notifier_abi.zig", b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    }));
    uapi_version.addImport("abi_bindings", abi_bindings);
    dev_t_binding.addImport("uapi_dev_t", uapi_dev_t);
    version_binding.addImport("abi_bindings", abi_bindings);
    version_binding.addImport("uapi_version", uapi_version);
    header_family_binding.addImport("abi_bindings", abi_bindings);
    header_family_binding.addImport("dev_t_binding", dev_t_binding);
    header_family_binding.addImport("version_binding", version_binding);
    header_family_binding.addImport("uapi_version", uapi_version);
    contract.addImport("abi_bindings", abi_bindings);
    contract.addImport("dev_t_binding", dev_t_binding);
    contract.addImport("version_binding", version_binding);
    contract.addImport("header_family_binding", header_family_binding);

    const contract_tests = b.addTest(.{ .root_module = contract });

    const run_contract = b.addRunArtifact(contract_tests);
    const contract_step = b.step(
        "phase3-abi-header-family-status-contract",
        "Run the Phase 3 ABI header-family status contract",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run Phase 3 ABI header-family status contract tests");
    test_step.dependOn(&run_contract.step);
    b.default_step.dependOn(&run_contract.step);
}
