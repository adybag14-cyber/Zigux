const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane05_python_compile_preflight_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "lane05-python-compile-preflight-contract",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "lane05-python-compile-preflight-contract",
        "Run the Lane 05 Python compile preflight contract.",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the focused Lane 05 Python compile preflight contract.");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(test_step);
}
