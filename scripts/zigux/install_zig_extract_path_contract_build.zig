const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("install_zig_extract_path_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "install-zig-extract-path-contract-tests",
        .root_module = contract_module,
    });
    const run_contract = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "install-zig-extract-path-contract",
        "Run the install-zig extract and path handoff contract",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run install-zig extract and path handoff contract tests");
    test_step.dependOn(&run_contract.step);

    b.default_step.dependOn(&run_contract.step);
}
