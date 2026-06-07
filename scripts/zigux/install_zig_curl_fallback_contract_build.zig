const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_root_module = b.createModule(.{
        .root_source_file = b.path("install_zig_curl_fallback_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .root_module = contract_root_module,
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);
    const check_step = b.step(
        "install-zig-curl-fallback-contract",
        "Run the Lane 18 install-zig curl fallback contract tests.",
    );
    check_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 18 install-zig curl fallback contract tests.");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}
