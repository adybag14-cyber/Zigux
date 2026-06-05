const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const smoke_path = b.option(
        []const u8,
        "smoke-path",
        "Path to zigux/tests/phase1_host_tools_smoke.zig",
    ) orelse "phase1_host_tools_smoke.zig";
    const tests_build_path = b.option(
        []const u8,
        "tests-build-path",
        "Path to zigux/tests/build.zig",
    ) orelse "build.zig";

    const options = b.addOptions();
    options.addOption([]const u8, "smoke_path", smoke_path);
    options.addOption([]const u8, "tests_build_path", tests_build_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_host_tools_smoke_alloc_render_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("contract_config", options);

    const tests = b.addTest(.{
        .name = "phase1-host-tools-smoke-alloc-render-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-host-tools-smoke-alloc-render-contract",
        "Check the Phase 1 host-tools smoke allocation/error/render contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the allocation/error/render smoke contract");
    test_step.dependOn(&run_tests.step);
}
