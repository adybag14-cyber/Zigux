const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane05_setup_download_retry_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "lane05-setup-download-retry-contract",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "lane05-setup-download-retry-contract",
        "Run the Lane 05 setup download retry contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 05 setup download retry contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
